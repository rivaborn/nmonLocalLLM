import sqlite3
import time
import logging
from typing import List, Optional

from nmon.gpu_monitor import GpuSnapshot
from nmon.ollama_monitor import OllamaSnapshot

DbConnection = sqlite3.Connection

def init_db(db_path: str) -> None:
    """Initialize the database with required tables."""
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS gpu_metrics (
                id INTEGER PRIMARY KEY,
                gpu_index INTEGER NOT NULL,
                ts REAL NOT NULL,
                temp_c REAL,
                mem_junc_c REAL,
                mem_used_mb REAL,
                power_w REAL
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ollama_metrics (
                id INTEGER PRIMARY KEY,
                ts REAL NOT NULL,
                gpu_use_pct REAL,
                cpu_use_pct REAL,
                gpu_layers INTEGER,
                total_layers INTEGER
            )
        """)
        
        conn.commit()
    except Exception as e:
        logging.error(f"Failed to initialize database: {e}")
        raise
    finally:
        if conn:
            conn.close()

def prune_old_data(db_path: str, history_hours: int) -> None:
    """Remove data older than history_hours from the database."""
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cutoff = time.time() - history_hours * 3600
        
        cursor.execute("DELETE FROM gpu_metrics WHERE ts < ?", (cutoff,))
        cursor.execute("DELETE FROM ollama_metrics WHERE ts < ?", (cutoff,))
        
        conn.commit()
    except Exception as e:
        logging.warning(f"Failed to prune old data: {e}")
        return
    finally:
        if conn:
            conn.close()

def flush_to_db(db_path: str, gpu_snapshots: List[GpuSnapshot], ollama_snapshot: Optional[OllamaSnapshot]) -> None:
    """Flush GPU and Ollama snapshots to the database."""
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        for snap in gpu_snapshots:
            cursor.execute("""
                INSERT INTO gpu_metrics (gpu_index, ts, temp_c, mem_junc_c, mem_used_mb, power_w)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                snap.gpu_index,
                snap.timestamp,
                snap.temperature_c,
                snap.mem_junction_temp_c,
                snap.memory_used_mb,
                snap.power_draw_w
            ))
        
        if ollama_snapshot is not None:
            cursor.execute("""
                INSERT INTO ollama_metrics (ts, gpu_use_pct, cpu_use_pct, gpu_layers, total_layers)
                VALUES (?, ?, ?, ?, ?)
            """, (
                ollama_snapshot.timestamp,
                ollama_snapshot.gpu_use_pct,
                ollama_snapshot.cpu_use_pct,
                ollama_snapshot.gpu_layers,
                ollama_snapshot.total_layers
            ))
        
        conn.commit()
    except Exception as e:
        logging.warning(f"Failed to flush data to database: {e}")
        return
    finally:
        if conn:
            conn.close()
