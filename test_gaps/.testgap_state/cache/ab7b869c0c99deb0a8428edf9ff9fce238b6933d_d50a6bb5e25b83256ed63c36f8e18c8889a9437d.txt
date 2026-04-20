# src/nmon/main.py

## Overall
PARTIAL - The tests cover the happy path and some error conditions, but miss critical signal handling, database operations, and preference persistence scenarios.

## Untested Public Interface
- `main`: The main function itself is tested but not the actual signal handlers or the full execution flow including cleanup
- `signal_handler`: The signal handler function is not directly tested for its behavior during shutdown
- `Settings.model_validate_env()`: The environment validation is not tested for various environment configurations
- `UserPrefs.model_validate_json()`: The JSON parsing is not tested for malformed input

## Untested Error Paths
- Condition: `pynvml.init()` failure not tested with different error types beyond generic Exception
- Condition: `open(settings.prefs_path, "r")` failure when prefs file doesn't exist or is unreadable
- Condition: `app.run()` exception handling not tested for non-pynvml exceptions
- Condition: `history_store.flush()` not tested for database write failures
- Condition: Signal handler not tested for multiple signals or concurrent shutdown scenarios

## Fixture and Mock Quality
- `mock_load_settings`: Uses a hardcoded mock instead of testing actual environment loading behavior
- `mock_load_user_prefs`: Mocks the file read operation but doesn't test actual JSON parsing edge cases
- `mock_history_store_init`: Mocks the constructor but doesn't test actual database connection behavior
- `mock_app_run`: Mocks the run method but doesn't test actual TUI rendering or event loop behavior

## Broken or Misleading Tests
- `test_main_sigterm_handling`: Tests shutdown but doesn't verify actual signal handling behavior, only mocks the exception
- `test_main_graceful_shutdown`: Tests shutdown but mocks the app.run() behavior instead of actual signal handling
- `test_main_preference_persistence`: Tests save_user_prefs but doesn't verify actual preference file writing behavior

## Priority Gaps
1. [HIGH] Test actual signal handling behavior with real SIGINT/SIGTERM signals instead of mocking exceptions
2. [HIGH] Test pynvml init failure with specific NVML error types that should trigger SystemExit
3. [MEDIUM] Test preference file reading with malformed JSON to ensure proper error handling
4. [MEDIUM] Test database flush operation for actual SQLite write failures
5. [LOW] Test Settings validation with invalid environment variables to ensure proper error propagation
