# Iteration Log: src/nmon/config.py

Codebase: nmon -- a Python terminal system/GPU monitor. Collects GPU metrics via NVML and nvidia-smi, stores samples in SQLite, and renders a live TUI (Rich-based) with a dashboard, history view, and configurable widgets. Stack: Python 3.10+, rich, pynvml, readchar, TOML config, pytest test suite.
Analysis: bugs, dataflow, contracts
Max iterations: 3
Started: 2026-04-19 23:33:21

## Iteration 1

**Severity:** HIGH:1  MED:4  LOW:1
**Best so far:** iter 1 (HIGH:1 MED:4)

## Bug Analysis

# src/nmon/config.py

## Findings

### Dataclass extra kwargs crash [HIGH]
- **Where:** `load_user_prefs()` ~line 48
- **Issue:** `UserPrefs(**prefs_dict)` will raise `TypeError` if the JSON contains any keys not defined in the `UserPrefs` dataclass, as standard dataclasses do not ignore extra arguments.
- **Impact:** Application crashes on startup or when loading preferences if the JSON file contains typos, deprecated fields, or future extensions.
- **Fix:** Filter `prefs_dict` to only include `UserPrefs` fields before unpacking, or convert `UserPrefs` to a `pydantic.BaseModel` to safely ignore extra keys.

### Deprecated Pydantic v1 config syntax [MEDIUM]
- **Where:** `Settings` class ~line 23
- **Issue:** `class Config: env_prefix = "NMON_"` is Pydantic v1 syntax. In `pydantic-settings` v2, this is silently ignored, so environment variables will not be loaded.
- **Impact:** Configuration via environment variables fails silently, falling back to hardcoded defaults and breaking deployment overrides.
- **Fix:** Replace with `model_config = ConfigDict(env_prefix="NMON_")` and import `ConfigDict` from `pydantic_settings`.

### Redundant Settings instantiation [LOW]
- **Where:** `load_user_prefs()` and `save_user_prefs()` ~lines 38, 62
- **Issue:** `Settings()` is instantiated twice solely to retrieve `prefs_path`, triggering full env var parsing twice.
- **Impact:** Minor performance overhead and potential side effects if `Settings` has expensive initialization logic.
- **Fix:** Pass `prefs_path` as an explicit argument or cache the resolved path in a module-level variable.

## Verdict

ISSUES FOUND

---

## Data Flow Analysis

# Data Flow Analysis: `src/nmon/config.py`

## Findings

### Unvalidated JSON dict unpacked into dataclass [MEDIUM]
- **Where:** `load_user_prefs`
- **Issue:** `json.load` returns an arbitrary dictionary that is directly unpacked into `UserPrefs(**prefs_dict)` without filtering extra keys or validating field types/ranges, and only catches `json.JSONDecodeError` and `IOError`.
- **Impact:** If the preferences file contains unexpected keys, a `TypeError` is raised and crashes the application instead of falling back to defaults; invalid numeric values (e.g., negative `refresh_rate`) bypass range checks entirely.
- **Fix:** Filter `prefs_dict` to only include keys present in `UserPrefs.__dataclass_fields__`, add `TypeError`/`ValueError` to the exception handler, and enforce explicit range validation on numeric fields.

## Verdict

ISSUES FOUND

---

## Contract Analysis

# Contract Analysis: `src/nmon/config.py`

## Findings

### Silent failure on I/O error [MEDIUM]
- **Where:** `save_user_prefs` function
- **Issue:** Catches `IOError` and logs a warning but returns `None`, silently breaking the persistence contract.
- **Impact:** Callers cannot detect save failures, leading to silent data loss for user preferences.
- **Fix:** Re-raise the exception or return a success/failure indicator to honor the contract.

### Unvalidated JSON schema in `load_user_prefs` [MEDIUM]
- **Where:** `load_user_prefs` function
- **Issue:** Passes raw JSON dictionary directly to `UserPrefs(**prefs_dict)` without key validation, risking `TypeError` or silent field mismatches.
- **Impact:** Crashes on malformed JSON or silently ignores invalid fields, violating the postcondition of returning a valid `UserPrefs` instance.
- **Fix:** Validate `prefs_dict` keys against `UserPrefs` fields or use a strict Pydantic model for parsing.

## Verdict

ISSUES FOUND

**Fix applied.** Lines: 70 -> 72

## Iteration 2

**Severity:** HIGH:0  MED:2  LOW:0
**Best so far:** iter 2 (HIGH:0 MED:2)

## Data Flow Analysis

# Data Flow Analysis: `src/nmon/config.py`

## Findings

### Missing type validation at JSON deserialization boundary [MEDIUM]
- **Where:** `load_user_prefs`
- **Issue:** `json.load` returns raw Python types without schema enforcement; string values for numeric/boolean fields pass the key filter but will cause `TypeError` or silent logical errors when used in arithmetic or boolean contexts.
- **Impact:** Runtime crashes or incorrect monitor behavior (e.g., `refresh_rate` treated as string causing division errors in the TUI loop).
- **Fix:** Add explicit type coercion or validate the loaded dict with a pydantic model before instantiating `UserPrefs`.

### Unhandled serialization failure in `save_user_prefs` [MEDIUM]
- **Where:** `save_user_prefs`
- **Issue:** `json.dump` can raise `TypeError` if `prefs.__dict__` contains non-serializable objects, but only `IOError` is caught.
- **Impact:** Unhandled exception crashes the application during preference saving instead of falling back gracefully.
- **Fix:** Catch `TypeError` alongside `IOError` or validate serializability before writing to disk.

## Verdict

ISSUES FOUND

---

## Contract Analysis

# Contract Analysis: `src/nmon/config.py`

## Findings

None.

## Verdict

CLEAN

**Fix applied.** Lines: 72 -> 80

## Iteration 3

**Severity:** HIGH:0  MED:0  LOW:0
**Best so far:** iter 3 (HIGH:0 MED:0)

## Contract Analysis

# Contract Analysis: `src/nmon/config.py`

## Findings

None.

## Verdict

CLEAN

*Stopped: no HIGH or MEDIUM findings.*

---

**Final status:** CLEAN
**Iterations run:** 3
**Best iteration:** 3 (HIGH:0 MED:0 LOW:0)
**Remaining (best):** HIGH:0  MED:0  LOW:0
**Fixed file:** `bug_fixes/src/nmon/config.py` (content from iteration 3)
**Written back to source:** no (review `bug_fixes/src/nmon/config.py` and copy manually)
