# Bug Hunt Summary

Generated: 2026-04-19 21:57
Codebase: nmon -- a Python terminal system/GPU monitor. Collects GPU metrics via NVML and nvidia-smi, stores samples in SQLite, and renders a live TUI (Rich-based) with a dashboard, history view, and configurable widgets. Stack: Python 3.10+, rich, pynvml, readchar, TOML config, pytest test suite.

## Files with HIGH / MEDIUM findings

- `src/nmon/alerts.py.md` -- HIGH:1 MED:1
- `src/nmon/app.py.md` -- HIGH:2 MED:1
- `src/nmon/config.py.md` -- MED:2
- `src/nmon/db.py.md` -- HIGH:1 MED:2
- `src/nmon/history.py.md` -- HIGH:1 MED:2
- `src/nmon/views/dashboard_view.py.md` -- HIGH:2 MED:2
- `src/nmon/views/llm_view.py.md` -- MED:2
- `src/nmon/views/power_view.py.md` -- HIGH:1 MED:1
- `src/nmon/views/temp_view.py.md` -- MED:3
- `src/nmon/widgets/alert_bar.py.md` -- MED:2
- `src/nmon/widgets/sparkline.py.md` -- HIGH:2 MED:2

## Totals

| Severity | Count |
|----------|-------|
| HIGH     | 10 |
| MEDIUM   | 20 |
| LOW      | 10 |
| CLEAN    | 3 files |

Reports in: `C:\Coding\WorkFolder\nmonLocalLLM2\bug_reports`
