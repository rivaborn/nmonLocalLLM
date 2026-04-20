# src/nmon/history.py

## Findings

### Potential Data Loss in DB Flush on GPU Samples [HIGH]
- **Where:** `add_gpu_samples()` ~lines 42-52
- **Issue:** The flush_to_db call inside add_gpu_samples can fail silently, leaving data in memory but not persisted to disk.
- **Impact:** GPU metrics may be lost if database write fails, especially during system shutdown or disk full conditions.
- **Fix:** Implement a retry mechanism or at least log critical failures that prevent data persistence.

### Race Condition in GPU Sample Management [MEDIUM]
- **Where:** `add_gpu_samples()` ~lines 26-32, `add_ollama_sample()` ~lines 37-41
- **Issue:** The trimming logic and flush logic are not atomic - multiple threads could modify the deques between trimming and flushing.
- **Impact:** In multi-threaded scenarios, data consistency between memory and database could be compromised.
- **Fix:** Use thread locks or atomic operations when modifying shared deques and performing flush operations.

### Incorrect DB Flush Trigger Condition [MEDIUM]
- **Where:** `add_gpu_samples()` ~line 48
- **Issue:** The flush trigger condition `len(self._gpu_snapshots) >= 0.8 * max_size` may cause premature flushing when the deque is nearly full.
- **Impact:** Unnecessary database writes that could impact performance or cause write contention.
- **Fix:** Change condition to flush only when approaching maximum capacity (e.g., `len(self._gpu_snapshots) >= max_size`) or use a time-based flush strategy.

### Missing Error Handling for Invalid Snapshot Fields [LOW]
- **Where:** `gpu_stat()` ~lines 57-63
- **Issue:** The code assumes all snapshot fields exist and are accessible, but doesn't validate field names or handle potential AttributeError.
- **Impact:** Runtime error if field name is misspelled or snapshot structure changes unexpectedly.
- **Fix:** Add validation or use getattr with default values to prevent AttributeError.

### Potential Memory Leak from Unchecked Deque Growth [LOW]
- **Where:** `add_ollama_sample()` ~line 39
- **Issue:** No explicit size limit enforcement for Ollama snapshots, which could lead to unbounded memory growth.
- **Impact:** Memory usage grows indefinitely if poll interval is very short or history hours is large.
- **Fix:** Apply same trimming logic to Ollama snapshots as used for GPU snapshots.

## Verdict

ISSUES FOUND
