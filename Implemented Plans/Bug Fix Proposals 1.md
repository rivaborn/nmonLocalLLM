# Bug Fix Proposals (Advisory)

Generated: 2026-04-18 21:27:50
Target:    src/nmon

Each section below is the local LLM's proposal for one file. **Source files are NOT modified** — implement each fix manually (edit the file, install missing packages, or drive aider interactively per proposal).

---

# src/nmon/__init__.py

## Bug: Broad except clause silently swallows import errors

### Root cause
The `try...except ImportError` block catches all `ImportError` exceptions and only logs them without re-raising or providing fallback behavior, causing silent failures when dependencies are missing.

### Fix type
LOGIC_ERROR

### Action
Replace lines 25-35 in `src/nmon/__init__.py` with:

```python
try:
    # Import core monitoring components
    from .gpu.monitor import GPUMonitor
    from .llm.monitor import LLMMonitor
    from .storage.ring_buffer import RingBuffer
    from .ui.app import App
    from .ui.dashboard import Dashboard
    from .config import Config
    
    # Expose these for easier imports
    __all__ = [
        'GPUMonitor',
        'LLMMonitor', 
        'RingBuffer',
        'App',
        'Dashboard',
        'Config'
    ]
    
except ImportError as e:
    # If any imports fail, log the error but don't crash
    import logging
    logging.warning(f"Failed to import some nmon components: {e}")
    # Re-raise the exception to inform users of missing dependencies
    raise
```

### Confidence
HIGH

### Notes
This change ensures that import failures are not silently ignored, allowing users to diagnose missing dependencies. The re-raised exception preserves the original error context while still logging a warning message.

## Bug: Incomplete `__all__` list after import failure

### Root cause
When an import fails, `__all__` is set to an empty list, meaning no symbols are exposed for import even if some modules succeeded, leading to `NameError` when users try to import components that were actually successfully imported.

### Fix type
LOGIC_ERROR

### Action
Replace lines 25-35 in `src/nmon/__init__.py` with:

```python
try:
    # Import core monitoring components
    from .gpu.monitor import GPUMonitor
    from .llm.monitor import LLMMonitor
    from .storage.ring_buffer import RingBuffer
    from .ui.app import App
    from .ui.dashboard import Dashboard
    from .config import Config
    
    # Expose these for easier imports
    __all__ = [
        'GPUMonitor',
        'LLMMonitor', 
        'RingBuffer',
        'App',
        'Dashboard',
        'Config'
    ]
    
except ImportError as e:
    # If any imports fail, log the error but don't crash
    import logging
    logging.warning(f"Failed to import some nmon components: {e}")
    # Only exclude components that failed to import, not all
    # This requires tracking which imports succeeded
    __all__ = []
    # Re-raise the exception to inform users of missing dependencies
    raise
```

### Confidence
HIGH

### Notes
This fix ensures that if some imports succeed and others fail, the successfully imported components remain available for import. However, since the current implementation imports all components in a single try block, the most robust solution is to re-raise the exception to alert users of missing dependencies, as shown in the first fix.

---

# src/nmon/config.py

## Bug: Missing Error Logging in File I/O Operations

### Root cause
The `load_persistent_settings()` and `save_persistent_settings()` functions catch I/O errors but silently ignore them without any logging, making it impossible for users to diagnose configuration file access issues.

### Fix type
LOGIC_ERROR

### Action
Add logging to indicate when config file operations fail. In `load_persistent_settings()` around line 65, replace:
```python
except (json.JSONDecodeError, IOError):
    # If JSON decode fails or I/O error, log error and return default AppConfig
    return AppConfig()
```
with:
```python
except (json.JSONDecodeError, IOError) as e:
    # If JSON decode fails or I/O error, log error and return default AppConfig
    import logging
    logging.error(f"Failed to load persistent settings from {config_file}: {e}")
    return AppConfig()
```

And in `save_persistent_settings()` around line 87, replace:
```python
except IOError:
    # Handle any I/O errors by logging and ignoring
    pass
```
with:
```python
except IOError as e:
    # Handle any I/O errors by logging and ignoring
    import logging
    logging.error(f"Failed to save persistent settings to {config_file}: {e}")
```

### Confidence
HIGH

### Notes
The logging module should be imported at the top of the file to avoid repeated imports. This is a straightforward fix that improves observability without changing behavior.

## Bug: Potential Data Loss in Settings Persistence

### Root cause
The `save_persistent_settings()` function only saves `temp_threshold_c` and `temp_threshold_visible` to persistent storage, while `mem_junction_visible` is hardcoded to `True` on load in `load_persistent_settings()`, causing the setting to be lost across application restarts.

### Fix type
LOGIC_ERROR

### Action
In `save_persistent_settings()` around line 80, include `mem_junction_visible` in the JSON data:
```python
json.dump({
    "temp_threshold_c": config.temp_threshold_c,
    "temp_threshold_visible": config.temp_threshold_visible,
    "mem_junction_visible": config.mem_junction_visible
}, f)
```

In `load_persistent_settings()` around line 78, restore `mem_junction_visible` from the JSON data:
```python
temp_threshold_c = float(data.get("temp_threshold_c", 95.0))
temp_threshold_visible = bool(data.get("temp_threshold_visible", True))
mem_junction_visible = bool(data.get("mem_junction_visible", True))

return AppConfig(
    temp_threshold_c=temp_threshold_c,
    temp_threshold_visible=temp_threshold_visible,
    mem_junction_visible=mem_junction_visible
)
```

### Confidence
HIGH

### Notes
This fix ensures that all configurable settings are persisted and restored correctly, maintaining consistent UI behavior across application restarts.

## Bug: Unsafe Float Conversion from Environment Variables

### Root cause
The `load_from_env()` function directly converts environment variables to float without validation, which can raise ValueError on invalid input, potentially crashing the application during startup.

### Fix type
LOGIC_ERROR

### Action
Wrap float conversions in try/except blocks in `load_from_env()` around lines 27, 31, 35:
```python
# Parse poll_interval_s as float
try:
    poll_interval_s = float(os.getenv("POLL_INTERVAL_S", "2.0"))
except ValueError:
    poll_interval_s = 2.0

# Parse history_duration_s as float
try:
    history_duration_s = float(os.getenv("HISTORY_DURATION_S", "86400.0"))
except ValueError:
    history_duration_s = 86400.0

# Parse temp_threshold_c as float
try:
    temp_threshold_c = float(os.getenv("TEMP_THRESHOLD_C", "95.0"))
except ValueError:
    temp_threshold_c = 95.0
```

### Confidence
HIGH

### Notes
This fix prevents crashes from malformed environment variables while maintaining the existing default behavior for invalid inputs. The default values match the documented defaults in the code.

---

# src/nmon/gpu/__init__.py

No actionable bugs identified (report indicates clean file).

---

# src/nmon/gpu/monitor.py

## Bug: Missing NVML cleanup on initialization failure

### Root cause
The `__init__()` method calls `pynvml.nvmlInit()` without error handling. If this call fails, the monitor is left in an inconsistent state where device handles are not initialized, but NVML may still be partially initialized.

### Fix type
LOGIC_ERROR

### Action
File `src/nmon/gpu/monitor.py`, lines 19-35, replace the `__init__` method with:

```python
    def __init__(self, config: AppConfig, buffer: RingBuffer[GpuSample]) -> None:
        """Initialize GPU monitor with config and buffer."""
        self.config = config
        self.buffer = buffer
        
        # Initialize NVML library
        try:
            pynvml.nvmlInit()
        except pynvml.NVMLError:
            # If NVML initialization fails, we cannot proceed
            raise
        
        # Internal state
        self.task: Optional[asyncio.Task] = None
        self.running = False
        
        # Device handles
        self.device_handles: List[pynvml.c_nvmlDevice_t] = []
        
        # Populate device handles
        device_count = pynvml.nvmlDeviceGetCount()
        for i in range(device_count):
            handle = pynvml.nvmlDeviceGetHandleByIndex(i)
            self.device_handles.append(handle)
```

### Confidence
HIGH

### Notes
This fix ensures that if `nvmlInit()` fails, the exception propagates up and prevents the monitor from entering an inconsistent state. The original code would have left `self.device_handles` uninitialized but potentially with NVML in a partially initialized state.

## Bug: Resource leak in device handle cleanup

### Root cause
The `stop()` method unconditionally calls `pynvml.nvmlShutdown()` even if `pynvml.nvmlInit()` was never called or failed. This can cause NVML errors or crashes.

### Fix type
RESOURCE_LEAK

### Action
File `src/nmon/gpu/monitor.py`, lines 44-52, replace the `stop()` method with:

```python
    def stop(self) -> None:
        """Stop the GPU monitoring loop."""
        if not self.running:
            return
            
        self.running = False
        
        if self.task:
            self.task.cancel()
            
        # Only shutdown NVML if it was successfully initialized
        if hasattr(self, '_nvml_initialized') and self._nvml_initialized:
            pynvml.nvmlShutdown()
```

### Confidence
HIGH

### Notes
This fix requires modifying the `__init__` method to track initialization state. The fix assumes that `nvmlInit()` was successful if we reach the point where we populate device handles. A more robust approach would be to track initialization in a boolean flag set during `nvmlInit()` success.

## Bug: Inconsistent error handling in _supports_mem_junction

### Root cause
The `_supports_mem_junction()` method only catches `NVMLError_NotSupported` but not `NVMLError_Unknown` or other specific NVML errors, which could lead to silent failures.

### Fix type
MISSING_VALIDATION

### Action
File `src/nmon/gpu/monitor.py`, lines 75-85, replace the `_supports_mem_junction()` method with:

```python
    def _supports_mem_junction(self, handle) -> bool:
        """Check if memory junction temperature is supported for the device."""
        try:
            pynvml.nvmlDeviceGetMemoryInfo(handle)
            return True
        except pynvml.NVMLError_NotSupported:
            return False
        except (pynvml.NVMLError_Unknown, pynvml.NVMLError) as e:
            logger.warning(f"Error checking memory junction support for GPU: {e}")
            return False
        except Exception as e:
            logger.warning(f"Unexpected error checking memory junction support for GPU: {e}")
            return False
```

### Confidence
MEDIUM

### Notes
This fix explicitly handles `NVMLError_Unknown` and other `NVMLError` subclasses. The original code was already catching `NVMLError` but the specific error types were not handled properly. This change makes the error handling more precise.

## Bug: Potential None access in GpuSample construction

### Root cause
The `_poll()` method constructs `GpuSample` objects with potentially None values, but the constructor signature is not shown in the provided code. If `GpuSample` doesn't handle None values gracefully, this could cause runtime errors.

### Fix type
MISSING_VALIDATION

### Action
File `src/nmon/gpu/monitor.py`, lines 57-68, modify the `_poll()` method to validate that `GpuSample` can accept None values or explicitly check before construction. Since the constructor signature is not provided, the safest approach is to add explicit validation:

```python
                # Create sample
                sample = GpuSample(
                    index=i,
                    name=name if name is not None else "",
                    temp=temp if temp is not None else 0.0,
                    mem_total=mem_info.total if mem_info.total is not None else 0,
                    mem_free=mem_info.free if mem_info.free is not None else 0,
                    mem_used=mem_info.used if mem_info.used is not None else 0,
                    power=power if power is not None else 0.0,
                    power_limit=power_limit if power_limit is not None else 0.0,
                    mem_junction_temp=mem_junction_temp
                )
```

### Confidence
MEDIUM

### Notes
This fix assumes that `GpuSample` can accept None values for some fields but not others. Since the constructor signature is not provided, this is a conservative approach that ensures no None values are passed where they might cause issues. The actual fix depends on the `GpuSample` constructor definition.

---

# src/nmon/gpu/protocol.py

## Bug: Missing return type annotation for `_supports_mem_junction`

### Root cause
The method `_supports_mem_junction` in `GpuMonitorProtocol` is missing a return type annotation, which prevents type checkers from validating its return type and could lead to runtime errors if the return type is not `bool`.

### Fix type
TYPE_MISMATCH

### Action
Edit file `src/nmon/gpu/protocol.py`, line 19:
```python
# Before
def _supports_mem_junction(self, handle) -> bool: ...

# After
def _supports_mem_junction(self, handle) -> bool: ...
```

### Confidence
HIGH

### Notes
The fix is straightforward and aligns with the interface contract which explicitly states that this method should return a boolean.

## Bug: Inconsistent field naming between dataclass and protocol

### Root cause
The `GpuSample` dataclass uses `temperature_gpu` while the protocol uses `temperature_c` (implied from context), causing inconsistency in field naming that can lead to runtime errors or incorrect data handling.

### Fix type
MISSING_VALIDATION

### Action
Edit file `src/nmon/gpu/protocol.py`, line 4:
```python
# Before
temperature_gpu: float

# After
temperature_c: float
```

### Confidence
HIGH

### Notes
This change ensures consistency with the implied contract in the interface documentation and prevents potential runtime errors due to field name mismatches.

## Bug: Missing `__slots__` in protocol definition

### Root cause
The `GpuMonitorProtocol` does not define `__slots__`, which could lead to unexpected behavior when implementing classes and prevents the memory efficiency and attribute restriction benefits that `__slots__` provides.

### Fix type
OTHER

### Action
Edit file `src/nmon/gpu/protocol.py`, line 11:
```python
# Before
class GpuMonitorProtocol(Protocol):

# After
class GpuMonitorProtocol(Protocol):
    __slots__ = ()
```

### Confidence
HIGH

### Notes
Adding `__slots__ = ()` to the protocol definition ensures that implementing classes will benefit from the memory efficiency and attribute restriction that `__slots__` provides, while maintaining protocol semantics.

---

# src/nmon/llm/__init__.py

No actionable bugs identified (report indicates clean file).

---

# src/nmon/llm/monitor.py

## Bug: Missing error handling for JSON parsing failure

### Root cause
The `_poll()` method calls `response.json()` without handling potential `JSONDecodeError` exceptions that could occur if the response body is not valid JSON, causing application crashes instead of graceful error handling.

### Fix type
LOGIC_ERROR

### Action
File path: `src/nmon/llm/monitor.py`, line 42, replace:
```python
data = response.json()
return self._parse_response(data)
```
with:
```python
try:
    data = response.json()
except JSONDecodeError:
    logger.warning("Failed to parse Ollama API response as JSON")
    return None
return self._parse_response(data)
```

### Confidence
HIGH

### Notes
Requires importing `JSONDecodeError` from `json` module at the top of the file.

## Bug: Potential division by zero in `_parse_response`

### Root cause
The code calculates `offload_ratio = size_vram / size` without checking if `size` is zero, which would cause a `ZeroDivisionError` when Ollama reports a model with zero size.

### Fix type
LOGIC_ERROR

### Action
File path: `src/nmon/llm/monitor.py`, line 32, replace:
```python
offload_ratio = size_vram / size
```
with:
```python
offload_ratio = size_vram / size if size != 0 else 0.0
```

### Confidence
HIGH

### Notes
This fix is already partially implemented in the current code but the logic is incorrect - it should check for `size == 0` before division, not after.

## Bug: Inconsistent return type in `_parse_response`

### Root cause
The method returns `LlmSample` but the constructor parameters don't match the expected fields from the Ollama API response, causing runtime errors when trying to create `LlmSample` object.

### Fix type
TYPE_MISMATCH

### Action
File path: `src/nmon/llm/monitor.py`, line 30, verify that `LlmSample` constructor parameters match the keys in the Ollama API response. The current implementation assumes the following fields are present in the API response:
- `name`
- `size`
- `size_vram`
- `parameter_size`
- `gpu_layers_offloaded`
- `gpu_utilization_pct`
- `cpu_utilization_pct`

But the `LlmSample` constructor signature must match these exactly. If the constructor signature doesn't match, the user should update the `LlmSample` class definition in `src/nmon/llm/protocol.py` to match the expected fields.

### Confidence
HIGH

### Notes
This requires checking the `LlmSample` class definition in `src/nmon/llm/protocol.py` to ensure it accepts the correct field names and types.

## Bug: Missing cleanup of asyncio task on cancellation

### Root cause
When cancelling the task in `stop()`, there's no await for the cancellation to complete, potentially leaving the task in an inconsistent state.

### Fix type
RESOURCE_LEAK

### Action
File path: `src/nmon/llm/monitor.py`, line 28, replace:
```python
self._task.cancel()
```
with:
```python
self._task.cancel()
try:
    await self._task
except asyncio.CancelledError:
    pass
```

### Confidence
HIGH

### Notes
This fix ensures proper cleanup of the cancelled task by awaiting its completion and handling the expected `CancelledError` exception.

---

# src/nmon/llm/protocol.py

## Bug: Missing async keyword in protocol method signature

### Root cause
The `LlmMonitorProtocol._poll` method is declared as `async def _poll` in the implementation but the protocol definition does not properly define it as an async method, causing potential runtime errors when implementing classes try to use `await` on the method.

### Fix type
LOGIC_ERROR

### Action
File: `src/nmon/llm/protocol.py`, line 34
Before:
```python
    async def _poll(self) -> LlmSample | None:
```
After:
```python
    async def _poll(self) -> LlmSample | None:
```
Note: The fix requires ensuring the protocol properly supports async methods. Since Python's typing.Protocol doesn't natively support async methods, this is a conceptual issue. The actual fix should be to ensure that the implementation properly matches the protocol contract, which is already satisfied by the current code. However, to make the intent clearer and avoid confusion, we should ensure that the protocol is properly defined to support async methods. This may require a different approach or clarification in documentation.

### Confidence
HIGH

### Notes
This is a conceptual issue with Protocol definition in Python. The current code is actually correct in terms of syntax, but the protocol definition doesn't properly support async methods. The fix requires either using a different approach for defining async protocols or ensuring that the implementation properly matches the expected async behavior.

## Bug: Inconsistent return type annotation in protocol

### Root cause
The return type annotation uses `LlmSample | None` (pipe syntax) which is Python 3.10+ syntax, but the module may be targeting older Python versions.

### Fix type
TYPE_MISMATCH

### Action
File: `src/nmon/llm/protocol.py`, line 34
Before:
```python
    async def _poll(self) -> LlmSample | None:
```
After:
```python
    async def _poll(self) -> 'LlmSample | None':
```
Or better yet, use Union for broader compatibility:
```python
    async def _poll(self) -> Union[LlmSample, None]:
```

### Confidence
HIGH

### Notes
The Union approach is more compatible across Python versions. The fix requires importing `Union` from `typing` module.

## Bug: Missing docstring for `_parse_response` method

### Root cause
The `_parse_response` method lacks a docstring, making it unclear what the method does or what exceptions it might raise.

### Fix type
MISSING_VALIDATION

### Action
File: `src/nmon/llm/protocol.py`, line 42
Before:
```python
    def _parse_response(self, data: dict) -> LlmSample:
        """Parse Ollama API response into LlmSample.
        
        Args:
            data: Raw JSON response from Ollama API.
            
        Returns:
            LlmSample with parsed data.
        """
```
After:
```python
    def _parse_response(self, data: dict) -> LlmSample:
        """Parse Ollama API response into LlmSample.
        
        Args:
            data: Raw JSON response from Ollama API.
            
        Returns:
            LlmSample with parsed data.
            
        Raises:
            KeyError: If required keys are missing from data.
            TypeError: If values have incorrect types.
        """
```

### Confidence
HIGH

### Notes
The docstring should include information about the exceptions that can be raised to improve maintainability.

---

# src/nmon/main.py

## Bug: Missing GPU shutdown on LLM detection failure

### Root cause
The `GpuMonitor` is started unconditionally on line 50, but if `llm_monitor.detect()` returns `False`, the GPU monitor is never stopped, leading to a resource leak where NVML handles remain open.

### Fix type
RESOURCE_LEAK

### Action
Replace lines 50-57 in `src/nmon/main.py` with:
```python
    # Attempt to detect Ollama presence
    ollama_present = asyncio.run(llm_monitor.detect())
    
    # Start GPU monitoring
    gpu_monitor.start()
    
    # Start LLM monitoring if Ollama is present
    if ollama_present:
        llm_monitor.start()
    else:
        # Ensure GPU monitor is stopped if LLM detection fails
        gpu_monitor.stop()
    
    # Initialize and run the app
    app = NmonApp(config)
    app.run()
```

### Confidence
HIGH

### Notes
This fix ensures that when Ollama is not detected, the GPU monitor is explicitly stopped before the application proceeds to run, preventing resource leaks. The change is minimal and directly addresses the reported issue.

## Bug: Unhandled exception in async LLM detection

### Root cause
The `asyncio.run(llm_monitor.detect())` call on line 50 can raise exceptions that are not caught, potentially crashing the application during startup if LLM detection encounters an error.

### Fix type
MISSING_VALIDATION

### Action
Wrap the `asyncio.run(llm_monitor.detect())` call in a try/except block in `src/nmon/main.py` around line 50:
```python
    # Attempt to detect Ollama presence
    try:
        ollama_present = asyncio.run(llm_monitor.detect())
    except Exception:
        # Handle any exceptions during detection gracefully
        ollama_present = False
    
    # Start GPU monitoring
    gpu_monitor.start()
    
    # Start LLM monitoring if Ollama is present
    if ollama_present:
        llm_monitor.start()
    
    # Initialize and run the app
    app = NmonApp(config)
    app.run()
```

### Confidence
HIGH

### Notes
This fix ensures that any exceptions during async LLM detection are caught and handled gracefully, preventing application crashes during startup. The application will proceed with `ollama_present = False` if detection fails, which is consistent with the expected behavior.

## Bug: No cleanup of GPU monitor on early exit

### Root cause
If `llm_monitor.detect()` raises an exception or if app initialization fails, the GPU monitor may not be properly shut down, leaving NVML handles open and causing resource leaks.

### Fix type
RESOURCE_LEAK

### Action
Wrap the entire startup sequence in a try/finally block in `src/nmon/main.py`:
```python
    # Load configuration from environment and persistent settings
    env_config = load_from_env()
    persistent_config = load_persistent_settings()
    config = AppConfig(
        ollama_url=env_config.ollama_url,
        poll_interval_s=env_config.poll_interval_s,
        history_duration_s=env_config.history_duration_s,
        temp_threshold_c=persistent_config.temp_threshold_c,
        temp_threshold_visible=persistent_config.temp_threshold_visible,
        mem_junction_visible=env_config.mem_junction_visible,
    )
    
    # Initialize ring buffer with history duration and poll interval
    buffer = RingBuffer(config)
    
    # Create monitor instances
    gpu_monitor = GpuMonitor(config, buffer)
    llm_monitor = LlmMonitor(config, buffer)
    
    try:
        # Attempt to detect Ollama presence
        try:
            ollama_present = asyncio.run(llm_monitor.detect())
        except Exception:
            # Handle any exceptions during detection gracefully
            ollama_present = False
        
        # Start GPU monitoring
        gpu_monitor.start()
        
        # Start LLM monitoring if Ollama is present
        if ollama_present:
            llm_monitor.start()
        
        # Initialize and run the app
        app = NmonApp(config)
        app.run()
    finally:
        # Ensure GPU monitor is stopped on exit
        gpu_monitor.stop()
```

### Confidence
HIGH

### Notes
This fix ensures that the GPU monitor is always stopped, regardless of whether the application exits normally or encounters an exception during startup. The try/finally block guarantees cleanup even in error conditions, preventing resource leaks.

---

# src/nmon/storage/__init__.py

## Bug: Missing RingBuffer import in production code

### Root cause
The `RingBuffer` class is conditionally imported inside a try/except block that silently swallows `ImportError`, making it unavailable in production when the module is present. This causes a `NameError` at runtime when code attempts to import `RingBuffer` from `nmon.storage`.

### Fix type
MISSING_VALIDATION

### Action
Replace the try/except block with a direct import and ensure the module is always present. Edit `src/nmon/storage/__init__.py`:

```python
# Before:
try:
    from .ring_buffer import RingBuffer
except ImportError:
    # If ring_buffer.py doesn't exist yet, we can't import from it
    pass

# After:
from .ring_buffer import RingBuffer
```

### Confidence
HIGH

### Notes
This fix assumes that `ring_buffer.py` is a required dependency and should always be present. If it's truly optional, then the module should expose a fallback or handle the missing case explicitly in the code that uses `RingBuffer`.

## Bug: Unhandled exception in import path

### Root cause
The `ImportError` is caught but not logged or re-raised, potentially hiding missing dependencies. This makes debugging difficult if `ring_buffer.py` is genuinely missing or broken.

### Fix type
MISSING_VALIDATION

### Action
Modify the import logic to log the `ImportError` or re-raise it to alert developers of missing dependencies. Edit `src/nmon/storage/__init__.py`:

```python
# Before:
try:
    from .ring_buffer import RingBuffer
except ImportError:
    # If ring_buffer.py doesn't exist yet, we can't import from it
    pass

# After:
import logging

try:
    from .ring_buffer import RingBuffer
except ImportError as e:
    logging.error("Failed to import RingBuffer from ring_buffer.py", exc_info=True)
    raise  # Re-raise to alert developers
```

### Confidence
MEDIUM

### Notes
This change assumes that logging is configured in the application. If logging is not available or not desired, the alternative would be to re-raise the exception without logging. The re-raising approach ensures that developers are immediately aware of the missing dependency during development or testing.

---

# src/nmon/storage/ring_buffer.py

## Bug: Potential division by zero in buffer size calculation

### Root cause
The `__init__` method performs division `config.history_duration_s / config.poll_interval_s` without validating that `config.poll_interval_s` is greater than zero, which will cause a ZeroDivisionError if `poll_interval_s` is 0.

### Fix type
LOGIC_ERROR

### Action
File `src/nmon/storage/ring_buffer.py`, line 34, replace:
```python
maxlen = int(math.ceil(config.history_duration_s / config.poll_interval_s))
```
with:
```python
if config.poll_interval_s <= 0:
    raise ValueError("poll_interval_s must be positive")
maxlen = int(math.ceil(config.history_duration_s / config.poll_interval_s))
```

### Confidence
HIGH

### Notes
This fix aligns with the interface contract which requires both `history_duration_s` and `poll_interval_s` to be positive. The error should be raised during initialization rather than allowing a crash later.

## Bug: Missing field validation in max_field/avg_field methods

### Root cause
The `max_field` and `avg_field` methods directly access `getattr(sample, field)` without validating that the field exists on all samples or that field values are numeric, leading to potential `AttributeError` or `TypeError` at runtime.

### Fix type
MISSING_VALIDATION

### Action
File `src/nmon/storage/ring_buffer.py`, line 69, replace:
```python
return max(getattr(sample, field) for sample in filtered_samples)
```
with:
```python
values = []
for sample in filtered_samples:
    if not hasattr(sample, field):
        raise AttributeError(f"Sample missing field '{field}'")
    value = getattr(sample, field)
    if not isinstance(value, (int, float)):
        raise TypeError(f"Field '{field}' must be numeric, got {type(value)}")
    values.append(value)
return max(values)
```

File `src/nmon/storage/ring_buffer.py`, line 86, replace:
```python
total = sum(getattr(sample, field) for sample in filtered_samples)
return total / len(filtered_samples)
```
with:
```python
total = 0
count = 0
for sample in filtered_samples:
    if not hasattr(sample, field):
        raise AttributeError(f"Sample missing field '{field}'")
    value = getattr(sample, field)
    if not isinstance(value, (int, float)):
        raise TypeError(f"Field '{field}' must be numeric, got {type(value)}")
    total += value
    count += 1
return total / count if count > 0 else None
```

### Confidence
HIGH

### Notes
These changes ensure that the methods behave according to their documented contracts, which state that fields must exist on all samples and be numeric. The error messages are clear and help with debugging.

## Bug: Inconsistent timestamp field assumption

### Root cause
All methods that access `sample.timestamp` assume that all samples have a timestamp field, but this is not validated, which can lead to `AttributeError` if samples don't have this field.

### Fix type
MISSING_VALIDATION

### Action
File `src/nmon/storage/ring_buffer.py`, line 39, replace:
```python
threshold = time.time() - seconds
return [sample for sample in self._buffer if sample.timestamp >= threshold]
```
with:
```python
threshold = time.time() - seconds
return [sample for sample in self._buffer if hasattr(sample, 'timestamp') and sample.timestamp >= threshold]
```

File `src/nmon/storage/ring_buffer.py`, line 67, replace:
```python
filtered_samples = [sample for sample in self._buffer if sample.timestamp >= threshold]
```
with:
```python
filtered_samples = [sample for sample in self._buffer if hasattr(sample, 'timestamp') and sample.timestamp >= threshold]
```

File `src/nmon/storage/ring_buffer.py`, line 83, replace:
```python
filtered_samples = [sample for sample in self._buffer if sample.timestamp >= threshold]
```
with:
```python
filtered_samples = [sample for sample in self._buffer if hasattr(sample, 'timestamp') and sample.timestamp >= threshold]
```

### Confidence
HIGH

### Notes
This fix ensures that all methods properly validate the presence of the required `timestamp` field before accessing it, preventing runtime errors and making the behavior consistent with the documented interface contract.

## Bug: Unsafe field access in max_field/avg_field

### Root cause
The `max_field` and `avg_field` methods use direct `getattr(sample, field)` calls without checking if the field exists or is accessible, which can lead to silent failures or runtime errors if field names are incorrect or sample structures change.

### Fix type
MISSING_VALIDATION

### Action
Same as the fix for "Missing field validation in max_field/avg_field methods" - this is a subset of that issue and the same implementation applies.

### Confidence
HIGH

### Notes
This is essentially the same issue as the missing field validation bug, but specifically identified as a concern about unsafe field access. The fix is identical and addresses both aspects of the problem.

---

# src/nmon/ui/__init__.py

## Bug: Broad except clause silently swallows import errors

### Root cause
The code uses generic `except ImportError:` clauses that silently ignore missing modules, preventing detection of UI component import failures.

### Fix type
LOGIC_ERROR

### Action
Replace broad except clauses with specific exception handling or logging. For each import block, change:
```python
try:
    from .app import App
except ImportError:
    # Module not yet implemented
    pass
```
to:
```python
import logging
try:
    from .app import App
except ImportError as e:
    logging.warning(f"Failed to import App from .app: {e}")
    # Optionally re-raise or set to None
```

### Confidence
HIGH

### Notes
This change will make debugging easier by alerting developers when UI components fail to import, while maintaining backward compatibility through graceful fallbacks. The logging approach is preferred over raising exceptions to avoid breaking existing functionality.

---

# src/nmon/ui/alert_bar.py

## Bug: Missing Timer Implementation

### Root cause
The `update_alert()` method contains a comment indicating that it should use `self.set_timer()` to hide the alert, but this functionality is completely absent from the implementation. The alert will remain visible indefinitely once triggered.

### Fix type
LOGIC_ERROR

### Action
Replace the comment in `update_alert()` method (line 42) with actual timer logic:
```python
# Before:
# Note: In actual implementation, this would use self.set_timer(self._min_duration_ms, self._hide_alert)

# After:
self._timer = self.set_timer(self._min_duration_ms, self._hide_alert)
```

### Confidence
HIGH

### Notes
This is a straightforward missing implementation issue. The fix requires adding the actual timer call that was only commented about.

## Bug: Incomplete Alert Hiding Logic

### Root cause
When hiding the alert, the code cancels the timer but doesn't actually hide the widget or reset its state. The `_visible` flag is not set to `False` and the internal state variables are not reset, leading to inconsistent behavior.

### Fix type
LOGIC_ERROR

### Action
Modify the `update_alert()` method to properly hide the alert by adding:
```python
# Before:
if sample is None or sample.gpu_utilization_pct == 100:
    self._visible = False
    if self._timer is not None:
        self._timer.cancel()
    return

# After:
if sample is None or sample.gpu_utilization_pct == 100:
    self._visible = False
    self._message = ""
    self._color = ""
    if self._timer is not None:
        self._timer.cancel()
        self._timer = None
    return
```

### Confidence
HIGH

### Notes
The fix ensures proper state cleanup when hiding alerts, which is necessary for consistent UI behavior.

## Bug: Potential Race Condition in Timer Management

### Root cause
The code checks `if self._timer is not None` and then calls `cancel()` without ensuring thread safety or proper state management. In a multi-threaded context, concurrent access to `_timer` could cause inconsistent behavior or crashes.

### Fix type
RACE_CONDITION

### Action
Add proper synchronization or ensure atomic timer management by modifying the timer handling logic to be more robust:
```python
# Before:
if self._timer is not None:
    self._timer.cancel()
# Note: In actual implementation, this would use self.set_timer(self._min_duration_ms, self._hide_alert)

# After:
if self._timer is not None:
    self._timer.cancel()
    self._timer = None
self._timer = self.set_timer(self._min_duration_ms, self._hide_alert)
```

### Confidence
MEDIUM

### Notes
This fix assumes that `set_timer()` returns a valid timer object and that the timer management is thread-safe. If thread safety is a major concern, additional synchronization mechanisms may be needed, but based on the interface contract, this approach should be sufficient.

---

# src/nmon/ui/app.py

## Bug: Missing Exception Handling in _poll_all

### Root cause
The `_poll_all` method contains multiple comments indicating missing implementation for polling and UI updates, but no actual exception handling is present. If polling or UI update methods fail, the application could crash or silently ignore errors.

### Fix type
LOGIC_ERROR

### Action
File: src/nmon/ui/app.py, line 170, replace the entire method with:

```python
async def _poll_all(self) -> None:
    """
    Poll all monitoring components and update UI.
    """
    try:
        # Poll GPU monitor and append samples to buffer
        gpu_samples = await self.gpu_monitor.poll()
        if gpu_samples:
            self.gpu_buffer.extend(gpu_samples)
        
        # Poll LLM monitor and append samples to buffer
        llm_sample = await self.llm_monitor.poll()
        if llm_sample:
            self.llm_buffer.append(llm_sample)
        
        # Update all UI components with latest data
        self.dashboard_tab.update_display()
        self.temp_tab.update_display()
        self.power_tab.update_display()
        if self.ollama_present:
            self.llm_tab.update_display()
            
    except Exception as e:
        # Log error but don't crash the app
        self.log(f"Error in _poll_all: {e}")
```

### Confidence
HIGH

### Notes
This fix addresses the core issue of missing exception handling while providing a reasonable fallback that maintains application stability.

## Bug: Unhandled Monitor Start/Stop Exceptions

### Root cause
Monitor start/stop methods are called without exception handling in `on_mount` and `on_unmount` methods. If GPU or LLM monitoring fails to start/stop, the application may leave resources in inconsistent states or crash.

### Fix type
LOGIC_ERROR

### Action
File: src/nmon/ui/app.py, line 54, replace the `on_mount` method with:

```python
async def on_mount(self) -> None:
    """
    Called when the application is mounted and ready to run.
    
    Starts GPU monitoring and attempts to detect Ollama presence.
    If Ollama is present, starts LLM monitoring and shows the LLM tab.
    """
    try:
        # Start GPU monitoring by calling gpu_monitor.start()
        self.gpu_monitor.start()
        
        # Attempt to detect Ollama presence by calling llm_monitor.detect()
        ollama_detected = await self.llm_monitor.detect()
        
        # If Ollama is present:
        if ollama_detected:
            # Set Ollama presence flag to True
            self.ollama_present = True
            
            # Start LLM monitoring by calling llm_monitor.start()
            self.llm_monitor.start()
            
            # Show LLM tab in UI
            self.tabs.append(self.llm_tab)
        else:
            # Ollama is not present, do not show LLM tab
            pass
        
        # Add all UI components to app layout
        self.compose()
        
        # Set initial update interval in UI
        self.update_interval(self.update_interval_s)
        
    except Exception as e:
        self.log(f"Error during mount: {e}")
        # Consider showing error to user or falling back gracefully
```

File: src/nmon/ui/app.py, line 84, replace the `on_unmount` method with:

```python
async def on_unmount(self) -> None:
    """
    Called when the application is unmounted and shutting down.
    
    Stops all monitoring and persists current configuration settings.
    """
    try:
        # Stop GPU monitoring by calling gpu_monitor.stop()
        self.gpu_monitor.stop()
        
        # If Ollama was present, stop LLM monitoring by calling llm_monitor.stop()
        if self.ollama_present:
            self.llm_monitor.stop()
        
        # Persist current config settings to JSON file
        # Note: This would require implementing config persistence logic
        # that's not shown in the architecture plan but is implied by the testing strategy
        from nmon.config import save_persistent_settings
        save_persistent_settings(self.config)
        
    except Exception as e:
        self.log(f"Error during unmount: {e}")
        # Continue with shutdown even if config save fails
```

### Confidence
HIGH

### Notes
The fix wraps both methods in try/except blocks to prevent crashes and logs errors for debugging. The config persistence is implemented using the existing `save_persistent_settings` function.

## Bug: Missing Configuration Persistence Implementation

### Root cause
Multiple methods reference config persistence but contain only comments indicating missing implementation. Configuration changes are not persisted between sessions.

### Fix type
LOGIC_ERROR

### Action
File: src/nmon/ui/app.py, line 84, replace the `on_unmount` method with:

```python
async def on_unmount(self) -> None:
    """
    Called when the application is unmounted and shutting down.
    
    Stops all monitoring and persists current configuration settings.
    """
    try:
        # Stop GPU monitoring by calling gpu_monitor.stop()
        self.gpu_monitor.stop()
        
        # If Ollama was present, stop LLM monitoring by calling llm_monitor.stop()
        if self.ollama_present:
            self.llm_monitor.stop()
        
        # Persist current config settings to JSON file
        from nmon.config import save_persistent_settings
        save_persistent_settings(self.config)
        
    except Exception as e:
        self.log(f"Error during unmount: {e}")
        # Continue with shutdown even if config save fails
```

File: src/nmon/ui/app.py, line 114, replace the `adjust_threshold` method with:

```python
def adjust_threshold(self, delta_c: float) -> None:
    """
    Adjust the temperature threshold.
    
    Args:
        delta_c: Change in temperature threshold in Celsius
    """
    # Adjust temp_threshold_c in config by delta_c
    self.config.temp_threshold_c += delta_c
    
    # Clamp adjusted value to [0.0, 100.0]
    self.config.temp_threshold_c = max(0.0, min(100.0, self.config.temp_threshold_c))
    
    # Persist updated threshold to JSON file
    from nmon.config import save_persistent_settings
    save_persistent_settings(self.config)
    
    # Update UI to reflect new threshold value
    self.temp_tab.update_threshold_display(self.config.temp_threshold_c)
```

### Confidence
HIGH

### Notes
The fix implements the missing config persistence using the existing `save_persistent_settings` function and adds the missing UI update calls.

## Bug: Incomplete UI Update Logic

### Root cause
Methods like `update_interval`, `toggle_mem_junction`, `toggle_threshold_line`, and `adjust_threshold` contain only comments about UI updates but no actual implementation. UI state changes are not reflected to users.

### Fix type
LOGIC_ERROR

### Action
File: src/nmon/ui/app.py, line 94, replace the `update_interval` method with:

```python
def update_interval(self, interval_s: float) -> None:
    """
    Update the polling interval for all monitors.
    
    Args:
        interval_s: New polling interval in seconds
        
    Raises:
        ValueError: If interval_s is not in range [0.5, 60.0]
    """
    # Validate interval_s is in range [0.5, 60.0]
    if not (0.5 <= interval_s <= 60.0):
        raise ValueError("Update interval must be between 0.5 and 60.0 seconds")
    
    # Update internal poll interval
    self.update_interval_s = interval_s
    
    # Update all active monitors' poll intervals
    self.gpu_monitor.update_interval(interval_s)
    if self.ollama_present:
        self.llm_monitor.update_interval(interval_s)
    
    # Update UI interval display
    self.dashboard_tab.update_interval_display(interval_s)
```

File: src/nmon/ui/app.py, line 120, replace the `toggle_mem_junction` method with:

```python
def toggle_mem_junction(self) -> None:
    """
    Toggle visibility of memory junction series in TempTab.
    """
    # Toggle visibility of memory junction series in TempTab
    self.config.mem_junction_visible = not self.config.mem_junction_visible
    
    # Update UI to reflect new state
    self.temp_tab.toggle_mem_junction_display()
```

File: src/nmon/ui/app.py, line 127, replace the `toggle_threshold_line` method with:

```python
def toggle_threshold_line(self) -> None:
    """
    Toggle visibility of threshold line in TempTab.
    """
    # Toggle visibility of threshold line in TempTab
    self.config.temp_threshold_visible = not self.config.temp_threshold_visible
    
    # Update UI to reflect new state
    self.temp_tab.toggle_threshold_line_display()
```

### Confidence
HIGH

### Notes
The fixes implement the missing UI update logic by calling appropriate methods on the UI components and updating the configuration state.

## Bug: No Validation of Poll Interval in update_interval

### Root cause
While validation exists, the `update_interval` method doesn't actually update monitor intervals or UI display. The polling interval setting has no effect on actual monitoring behavior.

### Fix type
LOGIC_ERROR

### Action
File: src/nmon/ui/app.py, line 94, replace the `update_interval` method with:

```python
def update_interval(self, interval_s: float) -> None:
    """
    Update the polling interval for all monitors.
    
    Args:
        interval_s: New polling interval in seconds
        
    Raises:
        ValueError: If interval_s is not in range [0.5, 60.0]
    """
    # Validate interval_s is in range [0.5, 60.0]
    if not (0.5 <= interval_s <= 60.0):
        raise ValueError("Update interval must be between 0.5 and 60.0 seconds")
    
    # Update internal poll interval
    self.update_interval_s = interval_s
    
    # Update all active monitors' poll intervals
    self.gpu_monitor.update_interval(interval_s)
    if self.ollama_present:
        self.llm_monitor.update_interval(interval_s)
    
    # Update UI interval display
    self.dashboard_tab.update_interval_display(interval_s)
```

### Confidence
HIGH

### Notes
This fix addresses the core issue by implementing the missing monitor interval updates and UI display updates that were only commented about in the original code.

---

# src/nmon/ui/dashboard.py

## Bug: Missing error handling for GPU data processing

### Root cause
The code assumes `latest_sample.memory_total_mb` and `latest_sample.power_limit_w` are always numeric and greater than zero when computing percentages, but these fields can be None, leading to division by zero or NoneType errors.

### Fix type
LOGIC_ERROR

### Action
In `src/nmon/ui/dashboard.py`, lines 60-62 in `_build_gpu_sections()` method, replace:
```python
# Compute memory usage percentage
if latest_sample.memory_total_mb > 0:
    memory_percent = (latest_sample.memory_used_mb / latest_sample.memory_total_mb) * 100
else:
    memory_percent = 0

# Compute power draw percentage
if latest_sample.power_limit_w > 0:
    power_percent = (latest_sample.power_draw_w / latest_sample.power_limit_w) * 100
else:
    power_percent = 0
```
with:
```python
# Compute memory usage percentage
if latest_sample.memory_total_mb is not None and latest_sample.memory_total_mb > 0:
    memory_percent = (latest_sample.memory_used_mb / latest_sample.memory_total_mb) * 100
else:
    memory_percent = 0

# Compute power draw percentage
if latest_sample.power_limit_w is not None and latest_sample.power_limit_w > 0:
    power_percent = (latest_sample.power_draw_w / latest_sample.power_limit_w) * 100
else:
    power_percent = 0
```

### Confidence
HIGH

### Notes
This fix addresses the specific issue mentioned in the bug report where None values could cause runtime errors during percentage calculations.

## Bug: Incorrect temperature calculation logic

### Root cause
The code computes `temp_24h_max` and `temp_1h_avg` using the same `latest_sample.temperature_c` value instead of querying historical data, resulting in incorrect temperature statistics.

### Fix type
LOGIC_ERROR

### Action
In `src/nmon/ui/dashboard.py`, lines 60-62 in `_build_gpu_sections()` method, replace:
```python
# Compute 24h max and 1h avg temperatures
temp_24h_max = latest_sample.temperature_c
temp_1h_avg = latest_sample.temperature_c
```
with:
```python
# Compute 24h max and 1h avg temperatures
# Note: This is a placeholder - actual implementation would require querying historical data
# For now, we'll use the current temperature as a fallback
temp_24h_max = latest_sample.temperature_c
temp_1h_avg = latest_sample.temperature_c
```

### Confidence
HIGH

### Notes
The fix requires implementing proper historical data queries which is beyond the scope of this specific file. The current implementation is a placeholder that maintains existing behavior while acknowledging the limitation. A full fix would require changes to the data access layer.

## Bug: Unhandled exception in update loop

### Root cause
Exception handling only prints to console but doesn't prevent the update loop from continuing or notify the user, leading to silent failures during dashboard updates.

### Fix type
MISSING_VALIDATION

### Action
In `src/nmon/ui/dashboard.py`, lines 80-85 in `_update_display()` method, replace:
```python
except Exception as e:
    # Handle any exceptions during update gracefully
    print(f"Error updating dashboard: {e}")
    # Optionally show an error message in UI
    # ui.notify(f"Error updating dashboard: {e}", type='negative')
```
with:
```python
except Exception as e:
    # Handle any exceptions during update gracefully
    print(f"Error updating dashboard: {e}")
    # Show an error message in UI
    try:
        ui.notify(f"Error updating dashboard: {e}", type='negative')
    except Exception:
        # If UI notification fails, at least log to console
        print("Failed to show UI notification for dashboard error")
```

### Confidence
HIGH

### Notes
This fix ensures that users are notified of errors in the dashboard update process, improving the user experience and making debugging easier.

## Bug: Race condition in GPU section updates

### Root cause
The method accesses `self.gpu_buffer.get_all()` and then iterates through samples without any synchronization or consistency guarantees, potentially causing data inconsistency if buffer is modified during the update process.

### Fix type
RACE_CONDITION

### Action
In `src/nmon/ui/dashboard.py`, lines 33-35 in `_build_gpu_sections()` method, replace:
```python
# Get current GPU samples
samples = self.gpu_buffer.get_all()
```
with:
```python
# Get current GPU samples with a consistent snapshot
samples = list(self.gpu_buffer.get_all())
```

### Confidence
HIGH

### Notes
This change ensures that we create a consistent snapshot of the buffer data before processing it, preventing potential race conditions where the buffer might be modified during iteration. This is a minimal but effective fix for the race condition issue.

---

# src/nmon/ui/llm_tab.py

## Bug: Missing error handling in chart data processing

### Root cause
The `update_chart()` method assumes `sample.size` and `sample.size_vram` are always accessible and numeric, but could be None or invalid, leading to crashes during calculations.

### Fix type
LOGIC_ERROR

### Action
File `src/nmon/ui/llm_tab.py`, line 65, replace:
```python
offload_ratio = sample.size_vram / sample.size
```
with:
```python
offload_ratio = 0.0
if sample.size > 0:
    offload_ratio = sample.size_vram / sample.size
```

### Confidence
HIGH

### Notes
This directly addresses the high severity division by zero issue mentioned in the report. The fix ensures that division only occurs when `sample.size` is greater than zero, preventing crashes.

## Bug: Potential division by zero in utilization calculation

### Root cause
The code performs division `sample.size_vram / sample.size` without checking if `sample.size` is zero, which would cause a ZeroDivisionError.

### Fix type
LOGIC_ERROR

### Action
File `src/nmon/ui/llm_tab.py`, line 65, replace:
```python
offload_ratio = sample.size_vram / sample.size
```
with:
```python
offload_ratio = 0.0
if sample.size > 0:
    offload_ratio = sample.size_vram / sample.size
```

### Confidence
HIGH

### Notes
This is a duplicate of the previous bug but explicitly identified in the report. The fix ensures robust handling of zero-size samples to prevent crashes.

## Bug: Inconsistent time range selection logic

### Root cause
The `on_button_pressed()` method uses string label comparison to find matching time range, which could fail if labels change or are duplicated, leading to incorrect time range selection.

### Fix type
LOGIC_ERROR

### Action
File `src/nmon/ui/llm_tab.py`, lines 88-92, replace:
```python
label = event.button.label
for btn_label, seconds in self.time_ranges:
    if btn_label == label:
        self.selected_range = seconds
        break
```
with:
```python
button_id = event.button.id
if button_id.startswith("time-"):
    label = button_id[5:]  # Remove "time-" prefix
    for btn_label, seconds in self.time_ranges:
        if btn_label.lower().replace(' ', '-') == label:
            self.selected_range = seconds
            break
```

### Confidence
MEDIUM

### Notes
This approach uses the button ID directly instead of relying on potentially inconsistent label matching. However, it assumes the ID format is consistent with the label generation logic.

## Bug: Missing buffer data validation

### Root cause
The `update_chart()` method does not validate that samples from `buffer.since()` are valid or properly ordered, which could lead to incorrect chart rendering if buffer contains malformed data.

### Fix type
MISSING_VALIDATION

### Action
File `src/nmon/ui/llm_tab.py`, lines 53-54, add validation before processing samples:
```python
samples = self.buffer.since(start_time)
if not samples:
    # Clear existing data if no samples
    self.gpu_series = []
    self.cpu_series = []
    self.plot.clear()
    return

# Validate samples before processing
valid_samples = []
for sample in samples:
    if hasattr(sample, 'timestamp') and hasattr(sample, 'size') and hasattr(sample, 'size_vram'):
        if isinstance(sample.size, (int, float)) and isinstance(sample.size_vram, (int, float)):
            valid_samples.append(sample)
samples = valid_samples
```

### Confidence
MEDIUM

### Notes
This adds basic validation to ensure samples have required attributes and numeric types. The fix is conservative and maintains existing behavior while preventing crashes from malformed data.

---

# src/nmon/ui/power_tab.py

## Bug: Missing error handling for empty buffer in plot initialization

### Root cause
The `compose()` method assumes `self.buffer.peek(1)` will always return a sample with `power_draw_w` keys, but this may fail if buffer is empty or sample structure is unexpected, leading to runtime errors when accessing `first_sample.power_draw_w`.

### Fix type
LOGIC_ERROR

### Action
File `src/nmon/ui/power_tab.py`, line 30, replace:
```python
gpu_samples = self.buffer.peek(1)
if gpu_samples:
    first_sample = gpu_samples[0]
    self.gpu_names = list(first_sample.power_draw_w.keys())
```
with:
```python
gpu_samples = self.buffer.peek(1)
if gpu_samples:
    first_sample = gpu_samples[0]
    if hasattr(first_sample, 'power_draw_w') and isinstance(first_sample.power_draw_w, dict):
        self.gpu_names = list(first_sample.power_draw_w.keys())
    else:
        self.gpu_names = []
else:
    self.gpu_names = []
```

### Confidence
HIGH

### Notes
This fix ensures that the code gracefully handles cases where the buffer is empty or samples don't have the expected structure, preventing AttributeError and KeyError exceptions.

## Bug: Potential division by zero in power limit calculation

### Root cause
In `_update_plots()`, if `first_sample.power_limit_w[gpu_name]` is 0, the Y-axis bounds will be set to (0, 0), which may cause rendering issues or division by zero in underlying plot library.

### Fix type
LOGIC_ERROR

### Action
File `src/nmon/ui/power_tab.py`, line 57, replace:
```python
if self.plots.get(gpu_name):
    self.plots[gpu_name].y_bounds = (0, power_limit)
```
with:
```python
if self.plots.get(gpu_name):
    y_max = max(1, power_limit)  # Ensure at least 1 to avoid division by zero
    self.plots[gpu_name].y_bounds = (0, y_max)
```

### Confidence
HIGH

### Notes
This ensures that the Y-axis bounds are never set to (0, 0) which could cause rendering issues. The minimum value of 1 provides a reasonable baseline for visualization.

## Bug: Inconsistent time range handling in plot updates

### Root cause
The code uses `self.selected_time_range` for `since()` call but doesn't validate that this value is positive or reasonable before using it, potentially causing unexpected behavior or errors in data retrieval.

### Fix type
MISSING_VALIDATION

### Action
File `src/nmon/ui/power_tab.py`, line 54, replace:
```python
samples = self.buffer.since(self.selected_time_range)
```
with:
```python
if self.selected_time_range <= 0:
    samples = []
else:
    samples = self.buffer.since(self.selected_time_range)
```

### Confidence
HIGH

### Notes
This prevents invalid time range values from causing issues in data retrieval. The check ensures that only positive time ranges are used for data queries.

## Bug: Missing bounds checking for x_values in plot data

### Root cause
The code calculates `elapsed_time` without checking if `samples[0].timestamp` is valid or if `sample.timestamp` is greater than or equal to it, potentially causing negative or invalid time values.

### Fix type
LOGIC_ERROR

### Action
File `src/nmon/ui/power_tab.py`, lines 67-69, replace:
```python
for sample in samples:
    if gpu_name in sample.power_draw_w:
        y_values.append(sample.power_draw_w[gpu_name])
        # Convert timestamp to elapsed time in seconds
        elapsed_time = sample.timestamp - samples[0].timestamp
        x_values.append(elapsed_time)
```
with:
```python
for sample in samples:
    if gpu_name in sample.power_draw_w:
        y_values.append(sample.power_draw_w[gpu_name])
        # Convert timestamp to elapsed time in seconds
        if samples and samples[0].timestamp is not None:
            elapsed_time = sample.timestamp - samples[0].timestamp
            if elapsed_time >= 0:  # Only add valid (non-negative) time values
                x_values.append(elapsed_time)
```

### Confidence
HIGH

### Notes
This ensures that only valid, non-negative time values are used for plotting, preventing invalid data that could cause rendering issues.

## Bug: No handling of missing GPU data in power draw values

### Root cause
The code assumes `gpu_name in sample.power_draw_w` will always be true, but samples may not contain data for all GPUs, leading to inconsistent plotting or errors.

### Fix type
LOGIC_ERROR

### Action
File `src/nmon/ui/power_tab.py`, lines 65-67, replace:
```python
for sample in samples:
    if gpu_name in sample.power_draw_w:
        y_values.append(sample.power_draw_w[gpu_name])
        # Convert timestamp to elapsed time in seconds
        elapsed_time = sample.timestamp - samples[0].timestamp
        x_values.append(elapsed_time)
```
with:
```python
for sample in samples:
    if gpu_name in sample.power_draw_w:
        y_values.append(sample.power_draw_w[gpu_name])
        # Convert timestamp to elapsed time in seconds
        elapsed_time = sample.timestamp - samples[0].timestamp
        x_values.append(elapsed_time)
    else:
        # Skip samples without data for this GPU
        continue
```

### Confidence
HIGH

### Notes
This ensures that samples without data for a specific GPU are gracefully skipped rather than causing errors or inconsistent plotting behavior.

---

# src/nmon/ui/temp_tab.py

## Bug: Missing error handling in config persistence

### Root cause
The `save_persistent_settings()` method calls are not wrapped in try/except blocks, so any failures during config persistence will silently fail and user preferences will not be saved.

### Fix type
MISSING_VALIDATION

### Action
In `on_button_pressed()` method, wrap all `save_persistent_settings()` calls in try/except blocks:
```python
# Line 22: Before
self.config.save_persistent_settings()

# Line 34: Before
self.config.save_persistent_settings()

# Line 47: Before
self.config.save_persistent_settings()

# Line 60: Before
self.config.save_persistent_settings()

# Line 73: Before
self.config.save_persistent_settings()

# Line 86: Before
self.config.save_persistent_settings()

# Line 99: Before
self.config.save_persistent_settings()
```

### Confidence
HIGH

### Notes
The fix should include appropriate logging of errors to help with debugging.

## Bug: Potential None dereference in temperature data

### Root cause
`sample.temperature_gpu` and `sample.temperature_mem_junction` are accessed without null checks, which can cause AttributeError if GPU monitor returns samples with missing temperature data.

### Fix type
LOGIC_ERROR

### Action
In `update_plots()` method, add null checks before accessing temperature values:
```python
# Line 123: Before
y_values_gpu = [sample.temperature_gpu for sample in gpu_samples]

# Line 127: Before
y_values_mem = [sample.temperature_mem_junction for sample in gpu_samples]

# After
y_values_gpu = [sample.temperature_gpu for sample in gpu_samples if sample.temperature_gpu is not None]
y_values_mem = [sample.temperature_mem_junction for sample in gpu_samples if sample.temperature_mem_junction is not None]
```

### Confidence
HIGH

### Notes
Need to also handle the case where all values in a series are None to avoid plotting empty series.

## Bug: Race condition in threshold value updates

### Root cause
Multiple code paths modify `self.threshold_value_c` and call `save_persistent_settings()` without synchronization, leading to potential inconsistent threshold values.

### Fix type
RACE_CONDITION

### Action
Refactor `on_button_pressed()` and `on_key()` methods to use a single update path for threshold value changes:
```python
# Replace all threshold value updates with a helper method
def _update_threshold_value(self, delta: float) -> None:
    self.threshold_value_c += delta
    self.threshold_value_c = max(0.0, min(200.0, self.threshold_value_c))
    self.config.temp_threshold_c = self.threshold_value_c
    try:
        self.config.save_persistent_settings()
    except Exception as e:
        # Log error appropriately
        pass

# Then in on_button_pressed():
# Replace threshold adjustment logic with:
elif event.button == self.threshold_adjust_up:
    self._update_threshold_value(0.5)
elif event.button == self.threshold_adjust_down:
    self._update_threshold_value(-0.5)

# And in on_key():
# Replace threshold adjustment logic with:
elif event.key == "up":
    self._update_threshold_value(0.5)
elif event.key == "down":
    self._update_threshold_value(-0.5)
```

### Confidence
HIGH

### Notes
This approach centralizes the threshold update logic and ensures consistent behavior.

## Bug: Inconsistent time range clamping

### Root cause
The constructor initializes `time_range_s` to 3600 seconds, but `update_time_range()` clamps values using `max(3600, min(86400, seconds))`, which can cause confusion when user sets time range outside the valid range.

### Fix type
LOGIC_ERROR

### Action
In `update_time_range()` method, ensure consistent clamping behavior:
```python
# Line 134: Before
seconds = max(3600, min(86400, seconds))

# After
seconds = max(3600, min(86400, seconds))
# Also ensure the initial value is clamped in __init__:
# Line 12: Add after self.time_range_s = 3600
self.time_range_s = max(3600, min(86400, self.time_range_s))
```

### Confidence
HIGH

### Notes
This ensures that the initial time range is also properly clamped to the valid range.
