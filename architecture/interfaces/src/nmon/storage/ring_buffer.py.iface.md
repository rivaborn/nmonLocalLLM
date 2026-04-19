# Module: `src/nmon/storage/ring_buffer.py`

## Role
Thread-safe time-series storage container implementing a ring buffer for GPU and LLM samples with time-windowed aggregation operations.

## Contract: `RingBuffer`

### `__init__(config)`
- **Requires:** `config` must be an `AppConfig` instance with `history_duration_s` and `poll_interval_s` attributes of type `float` and both must be positive
- **Establishes:** Internal `_buffer` as a `deque` with `maxlen` computed as `ceil(history_duration_s / poll_interval_s)`; `_lock` as a `threading.Lock`; `_config` as the provided `AppConfig` instance
- **Raises:** `TypeError` if `config` is not an `AppConfig` instance or if `history_duration_s` or `poll_interval_s` are not `float` types

### `append(sample)`
- **Requires:** `sample` must be of type `T` (dataclass with `timestamp` field of type `float`)
- **Guarantees:** Sample is appended to internal buffer; buffer maintains maximum length as configured
- **Raises:** None
- **Silent failure:** None
- **Thread safety:** Requires external lock; internal lock acquired

### `since(seconds)`
- **Requires:** `seconds` must be a `float` type and non-negative
- **Guarantees:** Returns list of samples with `timestamp >= (time.time() - seconds)`
- **Raises:** None
- **Silent failure:** None
- **Thread safety:** Safe with internal lock

### `latest()`
- **Requires:** None
- **Guarantees:** Returns most recent sample or `None` if buffer is empty
- **Raises:** None
- **Silent failure:** None
- **Thread safety:** Safe with internal lock

### `max_field(field, seconds)`
- **Requires:** `field` must be a `str` naming a field present on all samples; `seconds` must be a `float` type and non-negative
- **Guarantees:** Returns maximum value of `field` from samples within time window or `None` if no samples match
- **Raises:** `AttributeError` if `field` does not exist on any sample; `TypeError` if field values are not comparable
- **Silent failure:** None
- **Thread safety:** Safe with internal lock

### `avg_field(field, seconds)`
- **Requires:** `field` must be a `str` naming a field present on all samples; `seconds` must be a `float` type and non-negative
- **Guarantees:** Returns average value of `field` from samples within time window or `None` if no samples match
- **Raises:** `AttributeError` if `field` does not exist on any sample; `TypeError` if field values are not numeric
- **Silent failure:** None
- **Thread safety:** Safe with internal lock

## Module Invariants
- Internal `_buffer` always maintains maximum length as configured
- All public methods acquire `_lock` before accessing internal state
- `timestamp` field on all samples must be of type `float`
- `field` arguments to aggregation methods must exist on all samples

## Resource Lifecycle
- `threading.Lock` acquired during initialization and held for
