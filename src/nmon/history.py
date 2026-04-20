from collections import deque
from typing import Literal
import time
import logging

from nmon.gpu_monitor import GpuSnapshot
from nmon.ollama_monitor import OllamaSnapshot
from nmon.config import Settings
from nmon.db import DbConnection

class HistoryStore:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._gpu_snapshots: deque[GpuSnapshot] = deque()
        self._ollama_snapshots: deque[OllamaSnapshot] = deque()
        
        # Load existing data from SQLite DB
        try:
            with DbConnection(settings.db_path) as db:
                # Query gpu_metrics table
                gpu_rows = db.execute(
                    "SELECT gpu_index, ts, temp_c, mem_junc_c, mem_used_mb, power_w "
                    "FROM gpu_metrics "
                    "WHERE ts > ?",
                    (time.time() - settings.history_hours * 3600,)
                ).fetchall()
                
                for row in gpu_rows:
                    snapshot = GpuSnapshot(
                        gpu_index=row[0],
                        timestamp=row[1],
                        temp_c=row[2],
                        mem_junc_c=row[3],
                        mem_used_mb=row[4],
                        power_w=row[5]
                    )
                    self._gpu_snapshots.append(snapshot)
                
                # Query ollama_metrics table
                ollama_rows = db.execute(
                    "SELECT ts, gpu_use_pct, cpu_use_pct, gpu_layers, total_layers "
                    "FROM ollama_metrics "
                    "WHERE ts > ?",
                    (time.time() - settings.history_hours * 3600,)
                ).fetchall()
                
                for row in ollama_rows:
                    snapshot = OllamaSnapshot(
                        timestamp=row[0],
                        gpu_use_pct=row[1],
                        cpu_use_pct=row[2],
                        gpu_layers=row[3],
                        total_layers=row[4]
                    )
                    self._ollama_snapshots.append(snapshot)
                    
        except Exception as e:
            logging.warning(f"Failed to load history from DB: {e}")
            # Continue with empty deques

    def add_gpu_samples(self, samples: list[GpuSnapshot]) -> None:
        self._gpu_snapshots.extend(samples)
        
        # Compute max size based on history hours and poll interval
        max_size = int(self._settings.history_hours * 3600 / self._settings.poll_interval_s)
        
        # Trim excess samples
        while len(self._gpu_snapshots) > max_size:
            self._gpu_snapshots.popleft()
        
        # Flush to DB if we're getting close to max size
        if len(self._gpu_snapshots) >= 0.8 * max_size:
            try:
                with DbConnection(self._settings.db_path) as db:
                    self.flush_to_db(db)
            except Exception as e:
                logging.warning(f"Failed to flush GPU samples to DB: {e}")

    def add_ollama_sample(self, sample: OllamaSnapshot) -> None:
        self._ollama_snapshots.append(sample)
        
        # Compute max size based on history hours and poll interval
        max_size = int(self._settings.history_hours * 3600 / self._settings.poll_interval_s)
        
        # Trim excess samples
        while len(self._ollama_snapshots) > max_size:
            self._ollama_snapshots.popleft()

    def gpu_series(self, gpu_index: int, hours: float) -> list[GpuSnapshot]:
        start = time.time() - hours * 3600
        return [s for s in self._gpu_snapshots if s.gpu_index == gpu_index and s.timestamp >= start]

    def ollama_series(self, hours: float) -> list[OllamaSnapshot]:
        start = time.time() - hours * 3600
        return [s for s in self._ollama_snapshots if s.timestamp >= start]

    def gpu_stat(self, gpu_index: int, field: str, hours: float,
                 stat: Literal["max","avg","current"]) -> float | None:
        series = self.gpu_series(gpu_index, hours)
        values = [getattr(s, field) for s in series if getattr(s, field, None) is not None]
        
        if not values:
            return None
            
        if stat == "max":
            return max(values)
        elif stat == "avg":
            return sum(values) / len(values)
        elif stat == "current":
            return values[-1]
        else:
            raise ValueError(f"Unknown stat type: {stat}")

    def flush_to_db(self, db: DbConnection) -> None:
        try:
            # Begin transaction
            with db:
                # Insert GPU snapshots
                for snapshot in self._gpu_snapshots:
                    db.execute(
                        "INSERT OR IGNORE INTO gpu_metrics "
                        "(gpu_index, ts, temp_c, mem_junc_c, mem_used_mb, power_w) "
                        "VALUES (?, ?, ?, ?, ?, ?)",
                        (
                            snapshot.gpu_index,
                            snapshot.timestamp,
                            snapshot.temp_c,
                            snapshot.mem_junc_c,
                            snapshot.mem_used_mb,
                            snapshot.power_w
                        )
                    )
                
                # Insert Ollama snapshots
                for snapshot in self._ollama_snapshots:
                    db.execute(
                        "INSERT OR IGNORE INTO ollama_metrics "
                        "(ts, gpu_use_pct, cpu_use_pct, gpu_layers, total_layers) "
                        "VALUES (?, ?, ?, ?, ?)",
                        (
                            snapshot.timestamp,
                            snapshot.gpu_use_pct,
                            snapshot.cpu_use_pct,
                            snapshot.gpu_layers,
                            snapshot.total_layers
                        )
                    )
                
                # Delete old GPU data
                db.execute(
                    "DELETE FROM gpu_metrics WHERE ts < ?",
                    (time.time() - self._settings.history_hours * 3600,)
                )
                
                # Delete old Ollama data
                db.execute(
                    "DELETE FROM ollama_metrics WHERE ts < ?",
                    (time.time() - self._settings.history_hours * 3600,)
                )
                
                # Commit is handled by the context manager
        except Exception as e:
            logging.warning(f"Failed to flush to DB: {e}")
