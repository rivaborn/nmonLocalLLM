# src/nmon/ollama_monitor.py

## Overall
POOR - Tests only cover the OllamaSnapshot dataclass, missing all core monitoring logic and error handling paths.

## Untested Public Interface
- `OllamaMonitor.probe_ollama`: Async HTTP probing logic not tested
- `OllamaMonitor.poll`: Main monitoring method with complex conditional logic not tested
- `OllamaMonitorProtocol.poll`: Abstract method not tested

## Untested Error Paths
- Exception handling in `probe_ollama` when HTTP calls fail
- Timeout handling in `poll` method when `/api/ps` endpoint fails
- Division by zero when `total_layers=0` in GPU usage calculation
- Missing validation for malformed JSON responses from Ollama API
- No test coverage for when `models` key is missing from response

## Fixture and Mock Quality
- `mock_httpx_client`: Only mocks the client class, not the actual async behavior or response objects
- `mock_settings`: Provides base URL but doesn't test different URL configurations
- No mock for `httpx.AsyncClient` response objects with different status codes or JSON structures

## Broken or Misleading Tests
None.

## Priority Gaps
1. [HIGH] Test `OllamaMonitor.poll` with reachable Ollama and valid response data
2. [HIGH] Test `OllamaMonitor.poll` with unreachable Ollama (should return snapshot with reachable=False)
3. [HIGH] Test `OllamaMonitor.probe_ollama` with HTTP timeout and connection errors
4. [MEDIUM] Test `OllamaMonitor.poll` with malformed JSON response from Ollama API
5. [MEDIUM] Test `OllamaMonitor.poll` with zero total_layers to verify division by zero protection
