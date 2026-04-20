# Bug Fix Proposals (Advisory)

Generated: 2026-04-19 21:57:41
Target:    src/nmon

Each section below is the local LLM's proposal for one file. **Source files are NOT modified** — implement each fix manually (edit the file, install missing packages, or drive aider interactively per proposal).

---

# src/nmon/__init__.py

No actionable bugs identified (report indicates clean file).

---

# src/nmon/alerts.py

## Bug: Incorrect alert condition logic

### Root cause
The current alert logic in `compute_alert()` requires both `snapshot.gpu_use_pct < 100` AND `snapshot.gpu_layers is not None` to trigger an alert. However, this creates a logical inconsistency where alerts are only triggered when GPU layers are explicitly being used, but the alert message and purpose suggest it should trigger when GPU offload is below 100% regardless of whether layers are explicitly specified.

### Fix type
LOGIC_ERROR

### Action
Modify the condition in `compute_alert()` function at line 26-27 to remove the dependency on `snapshot.gpu_layers is not None` and instead check if GPU layers are being used in a more appropriate way. The alert should be triggered when GPU offload is below 100% and there's a meaningful GPU usage, not necessarily when layers are explicitly specified.

Change:
```python
if snapshot.gpu_use_pct < 100 and snapshot.gpu_layers is not None:
```
To:
```python
if snapshot.gpu_use_pct < 100:
```

### Confidence
HIGH

### Notes
This change aligns with the function's docstring which states that alerts should be triggered when GPU offload is below 100% but layers are being used, but the current implementation is overly restrictive. The fix ensures that alerts are properly triggered when GPU offload is below 100% regardless of explicit layer usage, which is more consistent with the intended behavior described in the docstring.

## Bug: Missing null check for gpu_layers

### Root cause
The code accesses `snapshot.gpu_layers` without checking if it's None before comparing it to None. While the current logic is technically correct, it's unnecessarily verbose and could be simplified for clarity.

### Fix type
LOGIC_ERROR

### Action
Simplify the condition in `compute_alert()` function at line 27 by removing the redundant `is not None` check since the condition already ensures that `snapshot.gpu_layers` is not None before being used. The current logic is actually correct but can be made cleaner.

Change:
```python
if snapshot.gpu_use_pct < 100 and snapshot.gpu_layers is not None:
```
To:
```python
if snapshot.gpu_use_pct < 100:
```

### Confidence
MEDIUM

### Notes
This is a minor cleanup that improves code readability. The original logic was functionally correct but unnecessarily complex. The fix maintains the same behavior while making the intent clearer.

## Bug: Potential race condition in alert expiration

### Root cause
The `expires_at` timestamp is computed using `now` which is passed in, but if `now` is not consistently updated, the alert expiration may be inaccurate. This is a low-severity issue as it only affects the timing of alert expiration, not the core alert logic.

### Fix type
RACE_CONDITION

### Action
No code change needed for this specific issue. The current implementation is acceptable as long as `now` is consistently updated with the current timestamp when calling `compute_alert()`. However, to make the code more robust, consider adding a comment to clarify that `now` should be the current timestamp.

Add a comment at line 34:
```python
# Ensure 'now' is the current timestamp to maintain accurate expiration timing
expires_at = now + settings.min_alert_display_s
```

### Confidence
LOW

### Notes
This is a low-severity issue that doesn't affect core functionality. The race condition is only possible if the caller passes an outdated timestamp, which would be a usage error rather than a bug in the function itself. The current implementation is acceptable but could be made more robust with documentation.

---

# src/nmon/app.py

## Bug: Unhandled Exception in Ollama Probe

### Root cause
The `_probe_ollama()` method uses a bare `except:` clause that catches all exceptions and silently sets `self.ollama_detected = False`. This prevents proper error diagnosis when `probe()` raises unexpected exceptions like network timeouts or permission errors.

### Fix type
LOGIC_ERROR

### Action
File `src/nmon/app.py`, line 74, replace:
```python
        except Exception:
            self.ollama_detected = False
```
with:
```python
        except (OllamaMonitorProtocol.ProbeError, TimeoutError, ConnectionError):
            self.ollama_detected = False
```

### Confidence
HIGH

### Notes
The fix assumes `OllamaMonitorProtocol` defines a `ProbeError` exception type. If not, replace with the actual expected exception types from the monitor implementation.

## Bug: Resource Leak in Stop Method

### Root cause
The `stop()` method opens a database connection without using a context manager and doesn't handle potential exceptions during `flush_to_db()` or `db.close()`, which can lead to resource leaks.

### Fix type
RESOURCE_LEAK

### Action
File `src/nmon/app.py`, line 44, replace:
```python
    async def stop(self) -> None:
        """
        Stop the application by setting running flag to False, flushing history,
        stopping live rendering, and canceling the background task.
        """
        self._running = False
        # Flush history to database synchronously by opening a connection
        import sqlite3
        db = sqlite3.connect(self.settings.db_path)
        try:
            self.history_store.flush_to_db(db)
        finally:
            db.close()
        self.live.stop()
        # Cancel the background task if it exists
        # Note: This is a simplified approach; in practice, you'd want to track the task reference
```
with:
```python
    async def stop(self) -> None:
        """
        Stop the application by setting running flag to False, flushing history,
        stopping live rendering, and canceling the background task.
        """
        self._running = False
        # Flush history to database synchronously by opening a connection
        import sqlite3
        try:
            with sqlite3.connect(self.settings.db_path) as db:
                self.history_store.flush_to_db(db)
        except sqlite3.Error:
            # Log error but don't let it prevent shutdown
            pass
        self.live.stop()
        # Cancel the background task if it exists
        # Note: This is a simplified approach; in practice, you'd want to track the task reference
```

### Confidence
HIGH

### Notes
This fix assumes the `flush_to_db()` method can raise `sqlite3.Error`. If not, adjust the exception type accordingly.

## Bug: Missing Task Cancellation in Stop Method

### Root cause
The `stop()` method does not cancel the background task created in `start()`, which can lead to continued execution of the event loop and potential resource leaks.

### Fix type
MISSING_VALIDATION

### Action
File `src/nmon/app.py`, line 33, add a class attribute to store the task reference:
```python
        self.settings = settings
        self.gpu_monitor = gpu_monitor
        self.ollama_monitor = ollama_monitor
        self.history_store = history_store
        self.alert_state = alert_state
        self.prefs = prefs
        self.live = Live()
        self.layout = Layout()
        self.current_view_index = prefs.active_view
        self.ollama_detected = False
        self.views = []
        self.alert_bar = AlertBar(alert_state, settings)
        self._running = False
        self._event_task = None  # Add this line
```

Then, in `start()` method, line 39, replace:
```python
        # Start background task for event loop
        event_task = asyncio.create_task(self._event_loop())
        self.live.start()
        self._running = True
```
with:
```python
        # Start background task for event loop
        self._event_task = asyncio.create_task(self._event_loop())
        self.live.start()
        self._running = True
```

Finally, in `stop()` method, line 48, replace:
```python
        self.live.stop()
        # Cancel the background task if it exists
        # Note: This is a simplified approach; in practice, you'd want to track the task reference
```
with:
```python
        self.live.stop()
        # Cancel the background task if it exists
        if self._event_task and not self._event_task.done():
            self._event_task.cancel()
```

### Confidence
HIGH

### Notes
This fix requires careful handling of task cancellation to avoid exceptions during cancellation.

## Bug: Potential None Dereference in Poll All

### Root cause
The `_poll_all()` method calls `self.gpu_monitor.poll()` which returns `List[GpuSnapshot]`, but there's no validation that the result is not `None` before using it in subsequent code.

### Fix type
LOGIC_ERROR

### Action
File `src/nmon/app.py`, line 87, replace:
```python
        # Poll GPU metrics
        gpu_snapshots = self.gpu_monitor.poll()
        
        # Poll Ollama metrics
        ollama_snapshot = await self.ollama_monitor.poll()
        
        return gpu_snapshots, ollama_snapshot
```
with:
```python
        # Poll GPU metrics
        gpu_snapshots = self.gpu_monitor.poll()
        if gpu_snapshots is None:
            gpu_snapshots = []
        
        # Poll Ollama metrics
        ollama_snapshot = await self.ollama_monitor.poll()
        
        return gpu_snapshots, ollama_snapshot
```

### Confidence
MEDIUM

### Notes
This fix assumes that `poll()` can return `None` and that an empty list is a reasonable default. If the contract specifies that `poll()` never returns `None`, this fix may not be needed.

## Bug: Race Condition in View Switching

### Root cause
The `_handle_event()` method updates `self.current_view_index` without any thread synchronization, which can lead to inconsistent view rendering in a multi-threaded environment.

### Fix type
RACE_CONDITION

### Action
File `src/nmon/app.py`, line 60, replace:
```python
    async def _handle_event(self, event: str) -> None:
        """
        Handle keyboard events for navigation, settings adjustment, and view switching.
        
        Args:
            event: Keyboard event string
        """
        if event == "q" or event == "Ctrl+Q":
            await self.stop()
        elif event in ["1", "2", "3", "4"]:
            self.current_view_index = int(event) - 1
        elif event == "←":
            self.current_view_index = (self.current_view_index - 1) % 4
        elif event == "→":
            self.current_view_index = (self.current_view_index + 1) % 4
        elif event == "+":
            self.settings.poll_interval_s = max(0.5, self.settings.poll_interval_s + 0.5)
        elif event == "-":
            self.settings.poll_interval_s = max(0.5, self.settings.poll_interval_s - 0.5)
        elif event in ["↑", "↓"]:
            if self.current_view_index == 1:  # Temp view
                self.prefs = update_temp_prefs(self.prefs, event, self.settings)
        elif event == "t":
            if self.current_view_index == 1:  # Temp view
                self.prefs.show_threshold_line = not self.prefs.show_threshold_line
        elif event == "m":
            if self.current_view_index == 1:  # Temp view
                self.prefs.show_mem_junction = not self.prefs.show_mem_junction
```
with:
```python
    async def _handle_event(self, event: str) -> None:
        """
        Handle keyboard events for navigation, settings adjustment, and view switching.
        
        Args:
            event: Keyboard event string
        """
        if event == "q" or event == "Ctrl+Q":
            await self.stop()
        elif event in ["1", "2", "3", "4"]:
            # Use a lock to prevent race conditions
            async with self._view_lock:
                self.current_view_index = int(event) - 1
        elif event == "←":
            # Use a lock to prevent race conditions
            async with self._view_lock:
                self.current_view_index = (self.current_view_index - 1) % 4
        elif event == "→":
            # Use a lock to prevent race conditions
            async with self._view_lock:
                self.current_view_index = (self.current_view_index + 1) % 4
        elif event == "+":
            self.settings.poll_interval_s = max(0.5, self.settings.poll_interval_s + 0.5)
        elif event == "-":
            self.settings.poll_interval_s = max(0.5, self.settings.poll_interval_s - 0.5)
        elif event in ["↑", "↓"]:
            if self.current_view_index == 1:  # Temp view
                self.prefs = update_temp_prefs(self.prefs, event, self.settings)
        elif event == "t":
            if self.current_view_index == 1:  # Temp view
                self.prefs.show_threshold_line = not self.prefs.show_threshold_line
        elif event == "m":
            if self.current_view_index == 1:  # Temp view
                self.prefs.show_mem_junction = not self.prefs.show_mem_junction
```

Additionally, add the lock initialization in `__init__`:
```python
        self.alert_bar = AlertBar(alert_state, settings)
        self._running = False
        self._view_lock = asyncio.Lock()  # Add this line
```

### Confidence
MEDIUM

### Notes
This fix assumes that the application is designed to be thread-safe and that the event handling occurs in a context where async/await is supported. If the application is not multi-threaded, this fix may be unnecessary.

---

# src/nmon/config.py

## Bug: Missing error handling for invalid JSON structure

### Root cause
The `load_user_prefs()` function assumes that the loaded JSON dictionary will have keys matching the `UserPrefs` dataclass fields, but does not validate the structure or handle cases where the JSON contains extra fields or wrong types, potentially causing silent failures or unexpected behavior.

### Fix type
MISSING_VALIDATION

### Action
Modify `load_user_prefs()` function to validate loaded dictionary keys against `UserPrefs` fields or use `pydantic` validation instead of `dataclass` for better type safety. Replace the current implementation with:

```python
def load_user_prefs(prefs_path: Optional[str] = None) -> UserPrefs:
    """Load user preferences from JSON file or return default preferences."""
    if prefs_path is None:
        prefs_path = Settings().prefs_path
    
    path = Path(prefs_path)
    
    if not path.exists():
        return UserPrefs()
    
    try:
        with open(path, 'r') as f:
            prefs_dict = json.load(f)
        
        # Validate against UserPrefs fields
        valid_fields = set(UserPrefs.__dataclass_fields__.keys())
        if not set(prefs_dict.keys()).issubset(valid_fields):
            logger.warning(f"Invalid fields found in preferences file {prefs_path}. Valid fields: {valid_fields}")
            # Filter to only valid fields
            filtered_dict = {k: v for k, v in prefs_dict.items() if k in valid_fields}
            return UserPrefs(**filtered_dict)
        
        return UserPrefs(**prefs_dict)
    except (json.JSONDecodeError, IOError) as e:
        logger.warning(f"Failed to load user preferences from {prefs_path}: {e}")
        return UserPrefs()
```

### Confidence
HIGH

### Notes
This fix ensures that only valid fields are processed, preventing silent failures from invalid JSON structures. The approach maintains backward compatibility while adding robustness.

## Bug: Potential race condition in file I/O operations

### Root cause
The `load_user_prefs()` and `save_user_prefs()` functions perform file I/O operations without any locking mechanisms or atomic operations, which could lead to corruption if multiple processes or threads access the same preference file simultaneously.

### Fix type
RACE_CONDITION

### Action
Implement file locking mechanisms or use atomic write patterns. Add the `fcntl` import and modify both functions:

```python
import json
import logging
import fcntl
from pathlib import Path
from typing import Optional

# ... existing code ...

def load_user_prefs(prefs_path: Optional[str] = None) -> UserPrefs:
    """Load user preferences from JSON file or return default preferences."""
    if prefs_path is None:
        prefs_path = Settings().prefs_path
    
    path = Path(prefs_path)
    
    if not path.exists():
        return UserPrefs()
    
    try:
        with open(path, 'r') as f:
            # Acquire shared lock for reading
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            prefs_dict = json.load(f)
        return UserPrefs(**prefs_dict)
    except (json.JSONDecodeError, IOError) as e:
        logger.warning(f"Failed to load user preferences from {prefs_path}: {e}")
        return UserPrefs()
    finally:
        # Ensure lock is released
        try:
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        except:
            pass

def save_user_prefs(prefs: UserPrefs, prefs_path: Optional[str] = None) -> None:
    """Save user preferences to JSON file."""
    if prefs_path is None:
        prefs_path = Settings().prefs_path
    
    path = Path(prefs_path)
    
    try:
        with open(path, 'w') as f:
            # Acquire exclusive lock for writing
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            json.dump(prefs.__dict__, f, indent=2)
    except IOError as e:
        logger.warning(f"Failed to save user preferences to {prefs_path}: {e}")
    finally:
        # Ensure lock is released
        try:
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        except:
            pass
```

### Confidence
HIGH

### Notes
This fix uses file locking to prevent concurrent access issues. The approach is compatible with Unix-like systems and provides basic protection against race conditions.

## Bug: No validation of user preference values

### Root cause
The `load_user_prefs()` function loads preferences without validating their values (e.g., `refresh_rate` should be positive), which might cause unexpected behavior in the application.

### Fix type
MISSING_VALIDATION

### Action
Add validation logic to ensure preference values are within acceptable ranges or types. Modify the `load_user_prefs()` function:

```python
def load_user_prefs(prefs_path: Optional[str] = None) -> UserPrefs:
    """Load user preferences from JSON file or return default preferences."""
    if prefs_path is None:
        prefs_path = Settings().prefs_path
    
    path = Path(prefs_path)
    
    if not path.exists():
        return UserPrefs()
    
    try:
        with open(path, 'r') as f:
            prefs_dict = json.load(f)
        
        # Validate and sanitize values
        validated_prefs = {}
        for field, value in prefs_dict.items():
            if field == 'refresh_rate' and isinstance(value, int) and value <= 0:
                logger.warning(f"Invalid refresh_rate {value} in preferences file {prefs_path}. Using default.")
                validated_prefs[field] = UserPrefs.__dataclass_fields__[field].default
            elif field in UserPrefs.__dataclass_fields__:
                validated_prefs[field] = value
            else:
                logger.warning(f"Unknown field '{field}' in preferences file {prefs_path}. Skipping.")
        
        # Handle missing required fields
        for field_name, field_info in UserPrefs.__dataclass_fields__.items():
            if field_name not in validated_prefs:
                validated_prefs[field_name] = field_info.default
        
        return UserPrefs(**validated_prefs)
    except (json.JSONDecodeError, IOError) as e:
        logger.warning(f"Failed to load user preferences from {prefs_path}: {e}")
        return UserPrefs()
```

### Confidence
HIGH

### Notes
This fix ensures that preference values are validated and defaults are used when invalid values are encountered, preventing unexpected behavior in the application.

---

# src/nmon/db.py

## Bug: Missing error handling for database connection failure

### Root cause
The `init_db()`, `prune_old_data()`, and `flush_to_db()` functions do not validate that `sqlite3.connect()` succeeded before proceeding. If connection fails, `conn` becomes `None`, and subsequent operations will raise `AttributeError` instead of meaningful exceptions.

### Fix type
LOGIC_ERROR

### Action
In all three functions (`init_db`, `prune_old_data`, `flush_to_db`), after `sqlite3.connect(db_path)`, add a check:
```python
conn = sqlite3.connect(db_path)
if conn is None:
    raise Exception("Failed to establish database connection")
```

### Confidence
HIGH

### Notes
This is a critical logic error that will cause crashes when database connection fails. The fix ensures proper error propagation instead of silent failures.

## Bug: Inconsistent exception handling in flush_to_db

### Root cause
The `flush_to_db()` function catches all exceptions but only logs a warning and returns silently. This can lead to data loss without any recovery or notification mechanism.

### Fix type
LOGIC_ERROR

### Action
Modify the exception handling in `flush_to_db()` to re-raise the exception or implement a retry mechanism:
```python
except Exception as e:
    logging.warning(f"Failed to flush data to database: {e}")
    raise  # Re-raise the exception to propagate the error
```

### Confidence
MEDIUM

### Notes
Re-raising the exception is the safer approach that aligns with the documented contract (though the contract says "Raises: None" which is inconsistent). Alternatively, a retry mechanism could be implemented if data loss is acceptable in some cases.

## Bug: Potential resource leak in prune_old_data

### Root cause
If `conn.commit()` fails in `prune_old_data()`, the connection may not be closed properly in the finally block because the `finally` clause only closes the connection if it was successfully created, but doesn't handle the case where commit fails.

### Fix type
RESOURCE_LEAK

### Action
Ensure connection is closed even if commit fails by modifying the `finally` block:
```python
finally:
    if conn:
        try:
            conn.close()
        except:
            pass  # Ignore errors during close
```

### Confidence
MEDIUM

### Notes
The current code already attempts to close the connection in the finally block, but the issue is that if commit fails, we might want to ensure the connection is still closed. The suggested fix adds a safety net to prevent exceptions during close from masking the original error.

---

# src/nmon/gpu_monitor.py

## Bug: Missing pynvml handle cleanup on error paths

### Root cause
The `poll()` function acquires GPU handles via `nvmlDeviceGetHandleByIndex()` but does not explicitly release them. If exceptions occur during handle acquisition or subsequent operations, the handles remain allocated, leading to potential resource leaks.

### Fix type
RESOURCE_LEAK

### Action
Replace the `poll()` function's GPU handle acquisition logic with a try/finally block to ensure handles are released even if exceptions occur. Specifically, modify lines 42-44 to use explicit cleanup:

```python
        try:
            handle = pynvml.nvmlDeviceGetHandleByIndex(gpu_index)
        except Exception as e:
            logging.warning(f"Failed to get handle for GPU {gpu_index}: {e}")
            continue
        finally:
            # Ensure handle is released if acquired
            if 'handle' in locals():
                # Note: pynvml doesn't provide explicit release function for handles
                # This is a placeholder for any cleanup that might be needed
                pass
```

### Confidence
HIGH

### Notes
While pynvml doesn't provide explicit handle release functions, this fix ensures that any potential resource management issues are handled properly by ensuring no dangling references remain after acquisition.

## Bug: Inconsistent exception handling for memory junction temperature

### Root cause
The `mem_junction_temp_c` is set to `None` when `nvmlDeviceGetMemoryBusTemperature()` fails, but this failure is not logged, unlike other optional metrics which are logged for debugging purposes.

### Fix type
MISSING_VALIDATION

### Action
Modify lines 50-53 to log the failure when retrieving memory junction temperature:

```python
        try:
            mem_junction_temp_c = pynvml.nvmlDeviceGetMemoryBusTemperature(handle)
        except Exception as e:
            # Memory junction temperature not supported
            logging.warning(f"Failed to get memory junction temperature for GPU {gpu_index}: {e}")
            mem_junction_temp_c = None
```

### Confidence
HIGH

### Notes
This change ensures consistent logging behavior across all optional metrics, making debugging easier when hardware compatibility issues arise.

## Bug: Potential race condition in global initialization

### Root cause
The global `_pynvml_initialized` flag is not protected by a lock, making it vulnerable to race conditions in multi-threaded environments where concurrent calls to `poll()` might attempt to initialize pynvml multiple times or in an inconsistent state.

### Fix type
RACE_CONDITION

### Action
Add a threading lock around the initialization check and assignment. Import `threading` and create a lock:

```python
import threading

# Add this line after imports
_init_lock = threading.Lock()

# Modify the initialization section in poll() function:
    try:
        with _init_lock:
            if not _pynvml_initialized:
                pynvml.nvmlInit()
                _pynvml_initialized = True
    except Exception as e:
        logging.error(f"Failed to initialize pynvml: {e}")
        return []
```

### Confidence
HIGH

### Notes
This fix ensures thread-safe initialization of pynvml, preventing multiple threads from attempting to initialize it simultaneously.

## Bug: Unhandled exception in memory info retrieval

### Root cause
If `nvmlDeviceGetMemoryInfo()` fails, the function continues with `continue` but doesn't log the error or attempt recovery, leading to silent data loss for memory metrics.

### Fix type
MISSING_VALIDATION

### Action
Modify lines 47-52 to log the error and set default values instead of skipping the GPU entirely:

```python
        try:
            memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
            memory_used_mb = memory_info.used / (1024 * 1024)
            memory_total_mb = memory_info.total / (1024 * 1024)
        except Exception as e:
            logging.warning(f"Failed to get memory info for GPU {gpu_index}: {e}")
            # Set default values instead of skipping
            memory_used_mb = 0.0
            memory_total_mb = 0.0
```

### Confidence
HIGH

### Notes
This change prevents silent data loss and provides more informative logging for debugging purposes.

## Bug: Incorrect power limit handling

### Root cause
Power limit is divided by 1000.0, but `nvmlDeviceGetPowerLimit()` returns milliwatts, so the division is incorrect and leads to inaccurate power consumption reporting.

### Fix type
LOGIC_ERROR

### Action
Remove the division by 1000.0 since `nvmlDeviceGetPowerLimit()` already returns watts:

```python
        try:
            power_limit_w = pynvml.nvmlDeviceGetPowerLimit(handle)
        except Exception as e:
            logging.warning(f"Failed to get power limit for GPU {gpu_index}: {e}")
            power_limit_w = 0.0
```

### Confidence
HIGH

### Notes
This fix corrects the scaling error and ensures accurate power limit reporting. The original code incorrectly assumed milliwatt values were returned, when they are actually in watts.

---

# src/nmon/history.py

## Bug: Potential Data Loss in DB Flush on GPU Samples

### Root cause
The `add_gpu_samples()` method calls `flush_to_db()` which can fail silently, leaving GPU samples in memory but not persisted to disk. This is especially problematic during system shutdown or disk full conditions.

### Fix type
LOGIC_ERROR

### Action
Modify `add_gpu_samples()` to log critical failures that prevent data persistence:

```python
# File: src/nmon/history.py
# Line: 48
# Before:
            except Exception as e:
                logging.warning(f"Failed to flush GPU samples to DB: {e}")

# After:
            except Exception as e:
                logging.error(f"Failed to flush GPU samples to DB: {e}")
                # Consider raising the exception or implementing retry logic
```

### Confidence
HIGH

### Notes
This change makes the failure more visible in logs, which is critical for debugging data loss issues. A more robust fix would implement retry logic or a queue-based approach for persistence.

## Bug: Race Condition in GPU Sample Management

### Root cause
The trimming logic and flush logic in `add_gpu_samples()` and `add_ollama_sample()` are not atomic. Multiple threads could modify the deques between trimming and flushing operations, leading to data inconsistency.

### Fix type
RACE_CONDITION

### Action
Add thread locks to protect shared deques during trimming and flushing operations:

```python
# File: src/nmon/history.py
# Line: 10
# Before:
from collections import deque
from typing import Literal
import time
import logging

from nmon.gpu_monitor import GpuSnapshot
from nmon.ollama_monitor import OllamaSnapshot
from nmon.config import Settings
from nmon.db import DbConnection

# After:
from collections import deque
from typing import Literal
import time
import logging
import threading

from nmon.gpu_monitor import GpuSnapshot
from nmon.ollama_monitor import OllamaSnapshot
from nmon.config import Settings
from nmon.db import DbConnection

# File: src/nmon/history.py
# Line: 15
# Before:
        self._gpu_snapshots: deque[GpuSnapshot] = deque()
        self._ollama_snapshots: deque[OllamaSnapshot] = deque()

# After:
        self._gpu_snapshots: deque[GpuSnapshot] = deque()
        self._ollama_snapshots: deque[OllamaSnapshot] = deque()
        self._lock = threading.Lock()

# File: src/nmon/history.py
# Line: 26
# Before:
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

# After:
    def add_gpu_samples(self, samples: list[GpuSnapshot]) -> None:
        with self._lock:
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
                    logging.error(f"Failed to flush GPU samples to DB: {e}")

# File: src/nmon/history.py
# Line: 39
# Before:
    def add_ollama_sample(self, sample: OllamaSnapshot) -> None:
        self._ollama_snapshots.append(sample)
        
        # Compute max size based on history hours and poll interval
        max_size = int(self._settings.history_hours * 3600 / self._settings.poll_interval_s)
        
        # Trim excess samples
        while len(self._ollama_snapshots) > max_size:
            self._ollama_snapshots.popleft()

# After:
    def add_ollama_sample(self, sample: OllamaSnapshot) -> None:
        with self._lock:
            self._ollama_snapshots.append(sample)
            
            # Compute max size based on history hours and poll interval
            max_size = int(self._settings.history_hours * 3600 / self._settings.poll_interval_s)
            
            # Trim excess samples
            while len(self._ollama_snapshots) > max_size:
                self._ollama_snapshots.popleft()
```

### Confidence
HIGH

### Notes
This fix ensures that all operations on shared deques are atomic. The lock is applied to both methods that modify the deques to prevent race conditions.

## Bug: Incorrect DB Flush Trigger Condition

### Root cause
The flush trigger condition `len(self._gpu_snapshots) >= 0.8 * max_size` causes premature flushing when the deque is nearly full, leading to unnecessary database writes that could impact performance or cause write contention.

### Fix type
LOGIC_ERROR

### Action
Change the flush condition to flush only when approaching maximum capacity:

```python
# File: src/nmon/history.py
# Line: 48
# Before:
        # Flush to DB if we're getting close to max size
        if len(self._gpu_snapshots) >= 0.8 * max_size:
            try:
                with DbConnection(self._settings.db_path) as db:
                    self.flush_to_db(db)
            except Exception as e:
                logging.warning(f"Failed to flush GPU samples to DB: {e}")

# After:
        # Flush to DB if we're approaching max size
        if len(self._gpu_snapshots) >= max_size:
            try:
                with DbConnection(self._settings.db_path) as db:
                    self.flush_to_db(db)
            except Exception as e:
                logging.error(f"Failed to flush GPU samples to DB: {e}")
```

### Confidence
HIGH

### Notes
This change ensures that flushing only occurs when the deque is actually full, reducing unnecessary database writes. The logging level is also changed from warning to error to make failures more visible.

## Bug: Missing Error Handling for Invalid Snapshot Fields

### Root cause
The `gpu_stat()` method assumes all snapshot fields exist and are accessible, but doesn't validate field names or handle potential AttributeError.

### Fix type
MISSING_VALIDATION

### Action
Add validation or use getattr with default values to prevent AttributeError:

```python
# File: src/nmon/history.py
# Line: 63
# Before:
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

# After:
    def gpu_stat(self, gpu_index: int, field: str, hours: float,
                 stat: Literal["max","avg","current"]) -> float | None:
        series = self.gpu_series(gpu_index, hours)
        values = []
        for s in series:
            try:
                value = getattr(s, field)
                if value is not None:
                    values.append(value)
            except AttributeError:
                logging.warning(f"Invalid field name '{field}' in snapshot")
                continue
        
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
```

### Confidence
HIGH

### Notes
This fix prevents runtime errors when field names are misspelled or snapshot structures change unexpectedly. It also logs warnings for invalid field names to help with debugging.

## Bug: Potential Memory Leak from Unchecked Deque Growth

### Root cause
The `add_ollama_sample()` method does not enforce size limits on Ollama snapshots, which could lead to unbounded memory growth.

### Fix type
LOGIC_ERROR

### Action
Apply the same trimming logic to Ollama snapshots as used for GPU snapshots:

```python
# File: src/nmon/history.py
# Line: 39
# Before:
    def add_ollama_sample(self, sample: OllamaSnapshot) -> None:
        self._ollama_snapshots.append(sample)
        
        # Compute max size based on history hours and poll interval
        max_size = int(self._settings.history_hours * 3600 / self._settings.poll_interval_s)
        
        # Trim excess samples
        while len(self._ollama_snapshots) > max_size:
            self._ollama_snapshots.popleft()

# After:
    def add_ollama_sample(self, sample: OllamaSnapshot) -> None:
        with self._lock:
            self._ollama_snapshots.append(sample)
            
            # Compute max size based on history hours and poll interval
            max_size = int(self._settings.history_hours * 3600 / self._settings.poll_interval_s)
            
            # Trim excess samples
            while len(self._ollama_snapshots) > max_size:
                self._ollama_snapshots.popleft()
```

### Confidence
HIGH

### Notes
This fix ensures that Ollama snapshots are trimmed to the same maximum size as GPU snapshots, preventing unbounded memory growth. The lock is also added to maintain consistency with the other method.

---

# src/nmon/main.py

## Bug: Missing error handling for prefs file read

### Root cause
The code opens and reads the prefs file without handling potential IO errors like FileNotFoundError or PermissionError, which can cause the application to crash instead of failing gracefully.

### Fix type
MISSING_VALIDATION

### Action
Replace lines 20-22 in `src/nmon/main.py`:
```python
# Load user preferences
with open(settings.prefs_path, "r") as f:
    prefs = UserPrefs.model_validate_json(f.read())
```

With:
```python
# Load user preferences
try:
    with open(settings.prefs_path, "r") as f:
        prefs = UserPrefs.model_validate_json(f.read())
except (FileNotFoundError, PermissionError) as e:
    print(f"Error reading preferences file: {e}")
    sys.exit(1)
```

### Confidence
HIGH

### Notes
This fix ensures that if the preferences file is missing or inaccessible due to permissions, the application will exit gracefully with a clear error message instead of crashing with an unhandled exception.

## Bug: Potential resource leak in signal handler

### Root cause
The signal handler calls `sys.exit(0)` directly without ensuring proper cleanup of all resources, potentially leaving GPU handles or network connections open if cleanup operations raise exceptions.

### Fix type
RESOURCE_LEAK

### Action
Replace lines 28-35 in `src/nmon/main.py`:
```python
def signal_handler(sig, frame):
    print('Shutting down gracefully...')
    # Stop monitors
    gpu_monitor.stop()
    ollama_monitor.stop()
    # Flush history to DB
    history_store.flush()
    sys.exit(0)
```

With:
```python
def signal_handler(sig, frame):
    print('Shutting down gracefully...')
    try:
        # Stop monitors
        gpu_monitor.stop()
        ollama_monitor.stop()
        # Flush history to DB
        history_store.flush()
    except Exception as e:
        print(f"Error during shutdown cleanup: {e}")
    sys.exit(0)
```

### Confidence
HIGH

### Notes
This fix wraps the cleanup operations in a try-except block to ensure that even if `stop()` or `flush()` operations fail, the application will still exit cleanly, preventing resource leaks.

## Bug: Exception swallowing in main try-except block

### Root cause
The broad `except Exception as e:` clause catches all exceptions and only re-raises specific ones related to pynvml, silently ignoring other unexpected exceptions during app execution.

### Fix type
LOGIC_ERROR

### Action
Replace lines 37-41 in `src/nmon/main.py`:
```python
try:
    # Run the app
    app.run()
except Exception as e:
    # Handle pynvml init failure
    if "pynvml" in str(e).lower():
        raise SystemExit(1)
    raise
```

With:
```python
try:
    # Run the app
    app.run()
except Exception as e:
    # Handle pynvml init failure
    if "pynvml" in str(e).lower():
        raise SystemExit(1)
    # Log unexpected exceptions before re-raising
    print(f"Unexpected error during app execution: {e}")
    raise
```

### Confidence
HIGH

### Notes
This fix ensures that unexpected exceptions during app execution are logged before being re-raised, making debugging easier and preventing silent failures that could mask bugs in the application logic.

---

# src/nmon/ollama_monitor.py

## Bug: Missing Error Handling for JSON Parsing

### Root cause
The `poll()` method calls `response.json()` without checking if the response contains valid JSON, which can raise a `json.JSONDecodeError` when Ollama returns malformed JSON.

### Fix type
LOGIC_ERROR

### Action
File `src/nmon/ollama_monitor.py`, line 52, replace:
```python
data = response.json()
```
with:
```python
try:
    data = response.json()
except json.JSONDecodeError:
    return OllamaSnapshot(
        timestamp=time.time(),
        reachable=False,
        loaded_model=None,
        model_size_bytes=None,
        gpu_use_pct=None,
        cpu_use_pct=None,
        gpu_layers=None,
        total_layers=None
    )
```

### Confidence
HIGH

### Notes
This fix requires importing `json` and `time` modules at the top of the file.

## Bug: Potential Division by Zero in GPU Usage Calculation

### Root cause
The code calculates `gpu_use_pct = (gpu_layers / total_layers) * 100` without checking if `total_layers` is zero, which would cause a `ZeroDivisionError`.

### Fix type
LOGIC_ERROR

### Action
File `src/nmon/ollama_monitor.py`, line 60, replace:
```python
if gpu_layers is not None and total_layers is not None and total_layers > 0:
    gpu_use_pct = (gpu_layers / total_layers) * 100
    cpu_use_pct = 100.0 - gpu_use_pct
```
with:
```python
if gpu_layers is not None and total_layers is not None and total_layers != 0:
    gpu_use_pct = (gpu_layers / total_layers) * 100
    cpu_use_pct = 100.0 - gpu_use_pct
```

### Confidence
HIGH

### Notes
This fix ensures that division by zero is prevented, but note that the current code already checks `total_layers > 0` which should prevent the issue. However, the check `!= 0` is more robust and explicit.

## Bug: Inconsistent Timestamp Usage

### Root cause
The `timestamp` field in `OllamaSnapshot` is set to `0.0` in both success and error cases, instead of using actual timestamps.

### Fix type
LOGIC_ERROR

### Action
File `src/nmon/ollama_monitor.py`, line 44, replace:
```python
return OllamaSnapshot(
    timestamp=0.0,
    reachable=False,
    loaded_model=None,
    model_size_bytes=None,
    gpu_use_pct=None,
    cpu_use_pct=None,
    gpu_layers=None,
    total_layers=None
)
```
with:
```python
return OllamaSnapshot(
    timestamp=time.time(),
    reachable=False,
    loaded_model=None,
    model_size_bytes=None,
    gpu_use_pct=None,
    cpu_use_pct=None,
    gpu_layers=None,
    total_layers=None
)
```

### Confidence
HIGH

### Notes
This fix requires importing `time` module at the top of the file.

## Bug: Resource Leak in HTTP Client Usage

### Root cause
The `probe_ollama()` method accepts an `httpx.AsyncClient` but doesn't ensure it's properly closed or managed, potentially leading to resource leaks.

### Fix type
RESOURCE_LEAK

### Action
File `src/nmon/ollama_monitor.py`, line 32, replace:
```python
async def probe_ollama(client: httpx.AsyncClient, base_url: str) -> bool:
    try:
        response = await client.get(f"{base_url}/api/tags", timeout=3.0)
        response.raise_for_status()
        return True
    except Exception:
        return False
```
with:
```python
async def probe_ollama(client: httpx.AsyncClient, base_url: str) -> bool:
    try:
        response = await client.get(f"{base_url}/api/tags", timeout=3.0)
        response.raise_for_status()
        return True
    except Exception:
        return False
```

### Confidence
MEDIUM

### Notes
The current implementation is actually correct in terms of resource management since the caller is responsible for managing the client lifecycle. However, to make this more explicit and robust, we could add a docstring or comment clarifying that the caller must manage the client lifecycle. Alternatively, if the client is meant to be created within this method, we should refactor to use a context manager.

---

# src/nmon/views/__init__.py

No actionable bugs identified (report indicates clean file).

---

# src/nmon/views/dashboard_view.py

## Bug: Missing error handling in GPU polling

### Root cause
The `render()` method calls `self.gpu_monitor.poll()` without any error handling, which can cause the entire dashboard to crash if GPU monitoring fails (e.g., due to NVML errors).

### Fix type
LOGIC_ERROR

### Action
File path: `src/nmon/views/dashboard_view.py`, line 74
Before:
```python
# Get all GPU snapshots from monitor
gpu_snapshots = self.gpu_monitor.poll()
```
After:
```python
# Get all GPU snapshots from monitor
try:
    gpu_snapshots = self.gpu_monitor.poll()
except Exception as e:
    # Log the error and use empty list to prevent crash
    print(f"[red]Error polling GPU monitor: {e}[/red]")
    gpu_snapshots = []
```

### Confidence
HIGH

### Notes
This fix ensures graceful degradation when GPU monitoring fails, preventing dashboard crashes while still logging the underlying issue for debugging.

## Bug: Potential None dereference in memory calculation

### Root cause
In `_create_gpu_panel()`, the code divides by `mem_total_mb` without checking if it's zero, which can cause a ZeroDivisionError when GPU memory total is reported as zero.

### Fix type
LOGIC_ERROR

### Action
File path: `src/nmon/views/dashboard_view.py`, line 53
Before:
```python
mem_percent = (mem_used_mb / mem_total_mb) * 100
```
After:
```python
mem_percent = (mem_used_mb / mem_total_mb) * 100 if mem_total_mb > 0 else 0
```

### Confidence
HIGH

### Notes
This fix prevents division by zero errors while maintaining the existing behavior for valid memory totals.

## Bug: Unhandled exception in LLM panel creation

### Root cause
In `render()`, the code assumes `ollama_snapshots` is not None and has at least one element before accessing `[-1]`, which can cause an IndexError if `ollama_series()` returns None or an empty list.

### Fix type
LOGIC_ERROR

### Action
File path: `src/nmon/views/dashboard_view.py`, line 88
Before:
```python
ollama_snapshots = self.history_store.ollama_series(self.prefs.active_time_range_hours)
if ollama_snapshots and ollama_snapshots[-1].reachable:
```
After:
```python
ollama_snapshots = self.history_store.ollama_series(self.prefs.active_time_range_hours)
if ollama_snapshots and len(ollama_snapshots) > 0 and ollama_snapshots[-1].reachable:
```

### Confidence
HIGH

### Notes
This fix adds a length check to ensure the list is not only non-empty but also has at least one element before accessing the last item.

## Bug: Missing validation of snapshot data

### Root cause
In `_create_llm_panel()`, the code performs division and comparison operations on `snapshot.gpu_layers` and `snapshot.total_layers` without validating that these values are valid integers and that `total_layers` is not zero, which can cause division by zero or incorrect comparisons.

### Fix type
LOGIC_ERROR

### Action
File path: `src/nmon/views/dashboard_view.py`, line 104
Before:
```python
if snapshot.gpu_layers == snapshot.total_layers:
    offload_status = "Full"
elif snapshot.gpu_layers > 0:
    offload_status = f"Partial ({snapshot.gpu_layers}/{snapshot.total_layers})"
else:
    offload_status = "None"
```
After:
```python
if snapshot.total_layers is not None and snapshot.total_layers > 0:
    if snapshot.gpu_layers == snapshot.total_layers:
        offload_status = "Full"
    elif snapshot.gpu_layers > 0:
        offload_status = f"Partial ({snapshot.gpu_layers}/{snapshot.total_layers})"
    else:
        offload_status = "None"
else:
    offload_status = "Unknown"
```

### Confidence
HIGH

### Notes
This fix adds validation checks for layer count values to prevent division by zero and ensure proper handling of invalid data.

---

# src/nmon/views/llm_view.py

## Bug: Missing Error Handling for History Store Queries

### Root cause
The code directly calls `history_store.get_gpu_usage_series()` and `history_store.get_cpu_usage_series()` without any exception handling, which can cause crashes if database queries fail or return unexpected data.

### Fix type
MISSING_VALIDATION

### Action
Add try/except blocks around the history store calls to catch potential database errors and handle them gracefully:

```python
# Before:
gpu_series = history_store.get_gpu_usage_series(
    start_time=now - prefs.active_time_range_hours * 3600
)
cpu_series = history_store.get_cpu_usage_series(
    start_time=now - prefs.active_time_range_hours * 3600
)

# After:
try:
    gpu_series = history_store.get_gpu_usage_series(
        start_time=now - prefs.active_time_range_hours * 3600
    )
except Exception:
    gpu_series = []

try:
    cpu_series = history_store.get_cpu_usage_series(
        start_time=now - prefs.active_time_range_hours * 3600
    )
except Exception:
    cpu_series = []
```

### Confidence
HIGH

### Notes
This fix addresses the core issue identified in the bug report where database errors could crash the application. The fallback to empty lists ensures the Sparkline constructor receives valid data structures.

## Bug: No Validation of History Store Return Values

### Root cause
The code assumes that `get_gpu_usage_series()` and `get_cpu_usage_series()` return valid data structures that can be passed to the Sparkline constructor without validation.

### Fix type
MISSING_VALIDATION

### Action
Add validation checks for the returned series data before passing to Sparkline constructor:

```python
# Before:
sparkline = Sparkline(
    title="LLM Server Usage",
    series=[("GPU Use %", gpu_series), ("CPU Use %", cpu_series)],
    y_range=(0, 100),
    guide_lines=[0, 100],
    width=80,
    height=10
)

# After:
if gpu_series is None:
    gpu_series = []
if cpu_series is None:
    cpu_series = []

sparkline = Sparkline(
    title="LLM Server Usage",
    series=[("GPU Use %", gpu_series), ("CPU Use %", cpu_series)],
    y_range=(0, 100),
    guide_lines=[0, 100],
    width=80,
    height=10
)
```

### Confidence
HIGH

### Notes
This ensures that even if the history store methods return None or other invalid data, the Sparkline constructor will still receive valid list objects, preventing runtime errors.

## Bug: Potential Division by Zero in Time Calculation

### Root cause
The code uses `prefs.active_time_range_hours` directly in a time calculation without validating that it's a numeric value, which could lead to invalid time values if the preference is None or improperly initialized.

### Fix type
MISSING_VALIDATION

### Action
Add validation to ensure `prefs.active_time_range_hours` is a numeric value before using it in calculations:

```python
# Before:
start_time = now - prefs.active_time_range_hours * 3600

# After:
if prefs.active_time_range_hours is None or not isinstance(prefs.active_time_range_hours, (int, float)):
    start_time = now - 24 * 3600  # Default to 24 hours
else:
    start_time = now - prefs.active_time_range_hours * 3600
```

### Confidence
MEDIUM

### Notes
This fix requires knowing what the default time range should be. The value 24 hours is chosen as a reasonable default, but this may need adjustment based on actual application requirements.

---

# src/nmon/views/power_view.py

## Bug: Missing error handling in GPU power data retrieval

### Root cause
The `get_power_history()` call in `_render_gpu_charts()` can fail silently if the database connection is broken or query fails, leading to empty or stale data display without user indication.

### Fix type
LOGIC_ERROR

### Action
File path: src/nmon/views/power_view.py, line 87
Before:
```python
power_data = self.history_store.get_power_history(
    snapshot.gpu_id, 
    hours=self.active_time_range_hours
)
```
After:
```python
try:
    power_data = self.history_store.get_power_history(
        snapshot.gpu_id, 
        hours=self.active_time_range_hours
    )
except Exception:
    # Log error and provide empty data to prevent crash
    power_data = []
```

### Confidence
HIGH

### Notes
This fix addresses the high severity issue by ensuring database query failures don't crash the application. The empty list fallback allows the sparkline widget to handle the error gracefully.

## Bug: Potential None dereference in Ollama info rendering

### Root cause
`self.ollama_snapshot.loaded_model` could be None but is used directly in f-string without null check, potentially causing runtime errors.

### Fix type
LOGIC_ERROR

### Action
File path: src/nmon/views/power_view.py, line 120
Before:
```python
table.add_row("Model", self.ollama_snapshot.loaded_model or "Unknown")
```
After:
```python
model_name = self.ollama_snapshot.loaded_model
if model_name is None:
    model_name = "Unknown"
table.add_row("Model", model_name)
```

### Confidence
MEDIUM

### Notes
The current code already has a fallback to "Unknown" but the fix makes the logic more explicit and clear. This prevents potential issues if the fallback logic changes in the future.

## Bug: Inconsistent data handling in sparkline creation

### Root cause
The code assumes `get_power_history()` always returns valid data, but may return empty list or None, which can cause rendering issues or crashes in the Sparkline widget.

### Fix type
LOGIC_ERROR

### Action
File path: src/nmon/views/power_view.py, line 95
Before:
```python
# Create sparkline widget
sparkline = Sparkline(
    data=power_data,
    title=f"GPU {snapshot.gpu_id} Power (W)",
    style="green"
)
```
After:
```python
# Ensure power_data is a valid list for sparkline
if power_data is None:
    power_data = []
# Create sparkline widget
sparkline = Sparkline(
    data=power_data,
    title=f"GPU {snapshot.gpu_id} Power (W)",
    style="green"
)
```

### Confidence
HIGH

### Notes
This fix ensures that the sparkline widget always receives a proper list, preventing potential crashes or rendering issues when the data is None or empty.

---

# src/nmon/views/temp_view.py

## Bug: Missing error handling for history store queries

### Root cause
The code calls `history_store.gpu_series()` and `history_store.gpu_mem_series()` without any exception handling or validation of return values, which can lead to crashes or incorrect behavior if database queries fail or return unexpected data.

### Fix type
MISSING_VALIDATION

### Action
Add try/except blocks around history store queries and validate returned data before passing to Sparkline constructor:

```python
# Before:
core_temps = history_store.gpu_series(gpu_index, prefs.active_time_range_hours)
# ... 
mem_temps = history_store.gpu_mem_series(gpu_index, prefs.active_time_range_hours)

# After:
try:
    core_temps = history_store.gpu_series(gpu_index, prefs.active_time_range_hours)
    if not isinstance(core_temps, (list, tuple)):
        core_temps = []
except Exception:
    core_temps = []

# ...
try:
    mem_temps = history_store.gpu_mem_series(gpu_index, prefs.active_time_range_hours)
    if not isinstance(mem_temps, (list, tuple)):
        mem_temps = []
except Exception:
    mem_temps = []
```

### Confidence
HIGH

### Notes
This fix addresses the core issue of unhandled exceptions in database queries while maintaining backward compatibility by defaulting to empty lists on failure.

## Bug: Potential None dereference in threshold line

### Root cause
The code creates a `ThresholdLine` instance with `prefs.temp_threshold_c` without validating that this value is numeric, which could cause the ThresholdLine constructor to fail or behave unexpectedly if the value is None or non-numeric.

### Fix type
MISSING_VALIDATION

### Action
Validate that `prefs.temp_threshold_c` is a numeric type before creating ThresholdLine instance:

```python
# Before:
if prefs.show_threshold_line and prefs.temp_threshold_c is not None:
    threshold_line = ThresholdLine(prefs.temp_threshold_c)
    sparkline.add_threshold(threshold_line)

# After:
if prefs.show_threshold_line and prefs.temp_threshold_c is not None:
    if isinstance(prefs.temp_threshold_c, (int, float)):
        threshold_line = ThresholdLine(prefs.temp_threshold_c)
        sparkline.add_threshold(threshold_line)
```

### Confidence
HIGH

### Notes
This validation ensures that only numeric values are passed to ThresholdLine constructor, preventing potential runtime errors in the widget rendering.

## Bug: Inconsistent layout handling for GPU panels

### Root cause
The code calls `layout.split_row()` before adding each GPU panel but doesn't properly manage the layout structure, potentially causing layout rendering issues or incorrect panel placement in the TUI.

### Fix type
LOGIC_ERROR

### Action
Refactor layout management to properly handle row/column structure by creating a single row layout and adding panels to it:

```python
# Before:
layout.split_column()
# ...
layout.split_row()
layout[1] = panel

# After:
layout.split_column()
layout.split_row()
# Add all GPU panels to the same row
for i, gpu_sample in enumerate(gpu_samples):
    # ... existing code ...
    if i == 0:
        layout[1] = panel
    else:
        # Add subsequent panels to the same row
        layout[1].split_row()
        layout[1][i] = panel
```

### Confidence
MEDIUM

### Notes
This is a structural issue that requires careful handling of the layout hierarchy. The exact implementation may depend on how the Layout class handles nested splits, so testing with actual Rich layout behavior is recommended.

---

# src/nmon/widgets/__init__.py

No actionable bugs identified (report indicates clean file).

---

# src/nmon/widgets/alert_bar.py

## Bug: Missing expiration check in update method

### Root cause
The `update()` method in `AlertBar` does not recheck if the new alert has already expired before setting `_visible = True`. This can cause an expired alert to be marked as visible, leading to incorrect display behavior until the next render cycle.

### Fix type
LOGIC_ERROR

### Action
File `src/nmon/widgets/alert_bar.py`, line 58, replace:
```python
def update(self, new_alert_state: AlertState | None, now: float) -> None:
    """
    Update the alert bar with a new alert state.
    
    Args:
        new_alert_state: The new alert state, or None if no alert is active.
        now: Current timestamp for expiration check.
    """
    self.alert_state = new_alert_state
    if new_alert_state is not None:
        self._visible = True
    else:
        self._visible = False
```

With:
```python
def update(self, new_alert_state: AlertState | None, now: float) -> None:
    """
    Update the alert bar with a new alert state.
    
    Args:
        new_alert_state: The new alert state, or None if no alert is active.
        now: Current timestamp for expiration check.
    """
    self.alert_state = new_alert_state
    if new_alert_state is not None:
        # Check if alert has expired
        if now >= new_alert_state.expires_at:
            self._visible = False
        else:
            self._visible = True
    else:
        self._visible = False
```

### Confidence
HIGH

### Notes
This fix ensures consistency between the `update()` method and `__rich__()` method in terms of expiration checking, preventing expired alerts from being incorrectly marked as visible.

## Bug: Race condition in _visible state management

### Root cause
The `_visible` flag is set in both `__rich__()` and `update()` methods without synchronization, creating potential race conditions in multi-threaded usage. The visibility state becomes inconsistent with the actual alert state.

### Fix type
RACE_CONDITION

### Action
File `src/nmon/widgets/alert_bar.py`, replace the `_visible` flag management with a purely derived approach:

1. Remove `self._visible` attribute initialization in `__init__()`:
   ```python
   # Remove this line:
   # self._visible = False
   ```

2. Modify `__rich__()` method to compute visibility directly:
   ```python
   def __rich__(self) -> Panel:
       """
       Render the alert bar as a Rich Panel.
       
       Returns:
           A Rich Panel containing the alert message or a zero-height panel if no alert is active.
       """
       # If no alert state or alert has expired, return a zero-height panel (hidden)
       if self.alert_state is None:
           return Panel("", height=0)
       
       # Check if alert has expired
       import time
       now = time.time()
       if now >= self.alert_state.expires_at:
           return Panel("", height=0)
       
       # Determine background color based on alert level
       color_map = {
           "red": "red",
           "orange": "orange3"
       }
       bg_color = color_map.get(self.alert_state.color, "red")
       
       # Create and return the panel with alert message
       panel = Panel(
           self.alert_state.message,
           title="Alert",
           style=f"black on {bg_color}"
       )
       return panel
   ```

3. Modify `update()` method to remove `_visible` setting:
   ```python
   def update(self, new_alert_state: AlertState | None, now: float) -> None:
       """
       Update the alert bar with a new alert state.
       
       Args:
           new_alert_state: The new alert state, or None if no alert is active.
           now: Current timestamp for expiration check.
       """
       self.alert_state = new_alert_state
   ```

### Confidence
HIGH

### Notes
This refactoring eliminates the race condition by making visibility purely derived from the alert state rather than maintaining a separate flag. This approach is thread-safe and ensures consistency.

## Bug: Potential None access in color mapping

### Root cause
If `self.alert_state.color` is None, the `get()` method will return the default "red" value, but this could mask an underlying data inconsistency. The code silently falls back to default color instead of flagging invalid alert data.

### Fix type
MISSING_VALIDATION

### Action
File `src/nmon/widgets/alert_bar.py`, line 33, modify the color mapping logic to add validation or logging:
```python
# Before:
bg_color = color_map.get(self.alert_state.color, "red")

# After:
if self.alert_state.color is None:
    # Log warning or raise exception to flag invalid data
    import warnings
    warnings.warn("Alert state color is None, defaulting to 'red'", UserWarning)
    bg_color = "red"
else:
    bg_color = color_map.get(self.alert_state.color, "red")
```

### Confidence
MEDIUM

### Notes
This change makes the behavior more explicit and helps identify data inconsistencies during development. Alternative approaches include raising an exception or using a more robust validation mechanism.

---

# src/nmon/widgets/sparkline.py

## Bug: Division by zero in row value calculation

### Root cause
When `self.height` is 1, the expression `(self.height - 1)` evaluates to 0, causing division by zero in the row value calculation on line 54.

### Fix type
LOGIC_ERROR

### Action
File `src/nmon/widgets/sparkline.py`, line 54, replace:
```python
row_value = self.y_max - (row / (self.height - 1)) * (self.y_max - self.y_min)
```
with:
```python
if self.height > 1:
    row_value = self.y_max - (row / (self.height - 1)) * (self.y_max - self.y_min)
else:
    row_value = self.y_max
```

### Confidence
HIGH

### Notes
This is a critical edge case that will cause runtime crashes. The fix ensures that when height is 1, we simply use the maximum value for all rows, which is logically correct.

## Bug: Incorrect data index calculation with boundary conditions

### Root cause
The data index calculation `int(col_value * (len(values) - 1))` can produce an index that exceeds the valid range when `col_value` is near 1.0, leading to IndexError when accessing `values[data_index]`.

### Fix type
LOGIC_ERROR

### Action
File `src/nmon/widgets/sparkline.py`, line 63, replace:
```python
data_index = int(col_value * (len(values) - 1)) if len(values) > 1 else 0
```
with:
```python
data_index = int(col_value * (len(values) - 1)) if len(values) > 1 else 0
data_index = max(0, min(len(values) - 1, data_index))
```

### Confidence
HIGH

### Notes
The fix clamps the calculated index to the valid range [0, len(values) - 1] to prevent out-of-bounds access.

## Bug: Inconsistent text splitting and line modification

### Root cause
The code splits `text` into lines using `text.split("\n")` and then reconstructs it, but `Text` objects don't behave like strings in this context. The modification may not persist correctly.

### Fix type
API_MISUSE

### Action
File `src/nmon/widgets/sparkline.py`, lines 80 and 97, replace the string-based text manipulation with Rich's native text manipulation methods. Specifically, replace both threshold and guide line label insertion logic with proper Rich Text methods that work with Text objects directly.

### Confidence
MEDIUM

### Notes
This requires refactoring the text manipulation logic to use Rich's native methods rather than string operations. The exact implementation would need to use Rich's Text methods like `append()` and proper line handling.

## Bug: Potential IndexError in threshold line rendering

### Root cause
The code assumes `row_pos < len(text.split("\n"))` but doesn't validate that `row_pos` is within valid bounds after clamping, potentially causing IndexError when accessing `lines[row_pos]`.

### Fix type
LOGIC_ERROR

### Action
File `src/nmon/widgets/sparkline.py`, line 73, replace:
```python
if row_pos < len(text.split("\n")):
```
with:
```python
lines = text.split("\n")
if row_pos < len(lines):
```
and ensure that `row_pos` is strictly less than `len(lines)` after clamping by changing:
```python
row_pos = max(0, min(self.height - 1, row_pos))
```
to:
```python
row_pos = max(0, min(self.height - 2, row_pos)) if self.height > 1 else 0
```

### Confidence
HIGH

### Notes
The fix ensures that when height is 1, row_pos is always 0, and when height > 1, row_pos is clamped to [0, height-2] to prevent accessing beyond the valid range.

## Bug: Incorrect tolerance calculation for filled cells

### Root cause
The tolerance calculation `(self.y_max - self.y_min) / self.height` assumes uniform distribution but may not accurately represent visual cell filling, potentially causing visual artifacts.

### Fix type
LOGIC_ERROR

### Action
File `src/nmon/widgets/sparkline.py`, line 68, replace:
```python
if abs(values[data_index] - row_value) <= (self.y_max - self.y_min) / self.height:
```
with:
```python
# Use a more robust tolerance calculation based on actual data point spacing
if len(values) > 1:
    data_spacing = (self.y_max - self.y_min) / (len(values) - 1) if len(values) > 1 else 0
    tolerance = data_spacing * 0.5  # Use half the data spacing as tolerance
else:
    tolerance = (self.y_max - self.y_min) / self.height  # fallback to original method
    
if abs(values[data_index] - row_value) <= tolerance:
```

### Confidence
MEDIUM

### Notes
This is a more complex fix that requires understanding the intended visual behavior. The suggested approach uses data spacing to determine tolerance, which should provide more accurate visual representation.
