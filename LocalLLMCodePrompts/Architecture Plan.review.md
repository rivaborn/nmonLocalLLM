I'll read all three files in parallel before beginning the audit.Now let me check for the Codebase Summary file.### SUMMARY

```
A OPEN_QUESTIONS_LEAKAGE:            0
B MISSING_DESIGN_DECISIONS:          0
C DUPLICATE_SYMBOL:                 15
D SIGNATURE_DRIFT:                   3
E IMPORT_PATH_DRIFT:                12
F PHANTOM_MODULE:                    5
G CONSTANT_MISPLACED:                0
H HEADING_FORMAT_DRIFT:              0
I MISSING_IMPORTS_BULLET:            0
J MISSING_TESTING_STRATEGY:          0
K STUB_METHOD_BODIES:                0
L PROJECT_STRUCTURE_SCOPE_VIOLATION: 0
TOTAL:                              35
```

---

### FINDINGS

## C. DUPLICATE_SYMBOL (15)

The plan contains a full second (and third) copy of almost every module section, beginning at line 1083. Each duplicate has a pseudocode body — the same class or function implemented twice. Stage 3b will parse every `## Module:` heading it finds, so each duplicate section generates a second conflicting aider prompt for the same file.

- `Settings` class body defined in both `## Module: src/nmon/config.py` (line 186, first) and `## Module: src/nmon/config.py` (line 1120, second). Second section also renames `load_user_prefs()` → `load_prefs()` and `save_user_prefs()` → `save_prefs()`.
- `main()` body defined in both `## Module: src/nmon/main.py` (line 153) and `## Module: src/nmon/main.py` (line 1215).
- `poll()` (gpu, standalone) defined in `## Module: src/nmon/gpu_monitor.py` (line 309); `GpuMonitorProtocol.poll(self)` defined in second `## Module: src/nmon/gpu_monitor.py` (line 1236) — same module, both have method bodies.
- `OllamaMonitor` class defined in `## Module: src/nmon/ollama_monitor.py` (line 340); `OllamaMonitorProtocol` class defined in second `## Module: src/nmon/ollama_monitor.py` (line 1267) — two different classes with full bodies in the same module section.
- `HistoryStore` class body defined in both `## Module: src/nmon/history.py` (line 390) and `## Module: src/nmon/history.py` (line 1300), and again as a class body inside `## Data Pipeline` (line 984).
- `compute_alert()` body defined in both `## Module: src/nmon/alerts.py` (line 449) and `## Module: src/nmon/alerts.py` (line 1351), and again inside `## Data Pipeline` (line 1031).
- `AlertState` dataclass body defined in `## Data Model` (line 61) AND as pseudocode body inside `## Module: src/nmon/alerts.py` (line 452). Canonical owner per Planning Prompt is `alerts.py`; Data Model should list name + canonical location only.
- `init_db()` body defined in both `## Module: src/nmon/db.py` (line 245) and `## Module: src/nmon/db.py` (line 1379).
- `DashboardView` class body defined in `## Module: src/nmon/views/dashboard_view.py` (line 503, first) and again in `## Module: src/nmon/views/dashboard_view.py` (line 1411, third); a separate `render_dashboard_view()` function body appears in the second occurrence (line 1083). Three occurrences total.
- `TempView` class body defined in second `## Module: src/nmon/views/temp_view.py` (line 1438); `render_temp_view()` function body defined in first occurrence (line 551). Same module, two different primary abstractions both with full bodies.
- `PowerView` class body defined in both `## Module: src/nmon/views/power_view.py` (line 596) and `## Module: src/nmon/views/power_view.py` (line 1467).
- `LlmView` class body defined in second `## Module: src/nmon/views/llm_view.py` (line 1495); `render_llm_view()` function body in first (line 640). Same module, two primary abstractions.
- `Sparkline` class body defined in both `## Module: src/nmon/widgets/sparkline.py` (line 706) and `## Module: src/nmon/widgets/sparkline.py` (line 1522).
- `AlertBar` class body defined in both `## Module: src/nmon/widgets/alert_bar.py` (line 769) and `## Module: src/nmon/widgets/alert_bar.py` (line 1549). First defines `__rich__` + `update`; second defines `render` — conflicting APIs.
- `NmonApp` class body defined in both `## Module: src/nmon/app.py` (line 810) and `## Module: src/nmon/app.py` (line 1162). First has 7-parameter `__init__` with `start()/stop()/async` architecture; second has 1-parameter `__init__` with synchronous `run()` — fundamentally different contracts.

## D. SIGNATURE_DRIFT (3)

All three are in duplicate sections (scheduled for C removal), but recorded as pre-patch state:

- `def poll(self) -> list[GpuSnapshot]` in second `## Module: src/nmon/gpu_monitor.py` (line ~1245): Planning Prompt §1.4 specifies standalone `poll() -> list[GpuSnapshot]` with no `self` parameter.
- `async def poll(self, client: httpx.AsyncClient) -> OllamaSnapshot` in second `## Module: src/nmon/ollama_monitor.py` (line ~1281): Planning Prompt §2.5 specifies standalone `async def poll(client: httpx.AsyncClient) -> OllamaSnapshot` with no `self`.
- `def flush_to_db(self, db: sqlite3.Connection) -> None` in second `## Module: src/nmon/history.py` (line ~1334): Planning Prompt §3.3 specifies `flush_to_db(db: DbConnection) -> None`; type changed from `DbConnection` to `sqlite3.Connection`.

## E. IMPORT_PATH_DRIFT (12)

- `## Module: src/nmon/history.py` (line 391): `OllamaSnapshot from nmon.gpu_monitor` — `OllamaSnapshot` is defined in `nmon.ollama_monitor`.
- `## Module: src/nmon/history.py` (line 391): `AppConfig from nmon.config` — no `AppConfig` class exists; canonical name is `Settings` (defined in `nmon.config`).
- `## Module: src/nmon/alerts.py` (line 450): `Settings from nmon.ollama_monitor` — `Settings` is defined in `nmon.config`.
- `## Module: src/nmon/views/dashboard_view.py` first (line 504): `GpuSnapshot from nmon.config` — `GpuSnapshot` is defined in `nmon.gpu_monitor`.
- `## Module: src/nmon/views/dashboard_view.py` first (line 504): `OllamaSnapshot from nmon.config` — `OllamaSnapshot` is defined in `nmon.ollama_monitor`.
- `## Module: src/nmon/views/temp_view.py` (line 552): `AppConfig from nmon.config` — canonical name is `Settings`.
- `## Module: src/nmon/views/power_view.py` (line 597): `HistoryStore from nmon.gpu_monitor` — `HistoryStore` is defined in `nmon.history`.
- `## Module: src/nmon/views/power_view.py` (line 597): `UserPrefs from nmon.gpu_monitor` — `UserPrefs` is defined in `nmon.config`.
- `## Module: src/nmon/views/llm_view.py` (line 641): `HistoryStore from nmon.ollama_monitor` — `HistoryStore` is defined in `nmon.history`.
- `## Module: src/nmon/views/llm_view.py` (line 641): `Settings from nmon.ollama_monitor` — `Settings` is defined in `nmon.config`.
- `## Module: src/nmon/views/llm_view.py` (line 641): `UserPrefs from nmon.ollama_monitor` — `UserPrefs` is defined in `nmon.config`.
- `## Module: src/nmon/widgets/sparkline.py` (line 707): `AppConfig from nmon.config` — canonical name is `Settings`.

## F. PHANTOM_MODULE (5)

- `nmon.gpu.protocol` — cited in `## Module: src/nmon/main.py` (line 154), `## Module: src/nmon/views/dashboard_view.py` first (line 504), `## Module: src/nmon/views/temp_view.py` (line 552), `## Module: src/nmon/app.py` second (line 1163), `## Module: src/nmon/gpu_monitor.py` second (line 1237). No `## Module: src/nmon/gpu/protocol.py` section exists and no such file in Project Structure.
- `nmon.ollamaCompleting FINDINGS then patching in pieces.

- `nmon.ollama.protocol` — cited in `## Module: src/nmon/main.py` (line 154), `## Module: src/nmon/app.py` second (line 1163), `## Module: src/nmon/ollama_monitor.py` second (line 1268). No `## Module: src/nmon/ollama/protocol.py` section exists.
- `nmon.storage.ring_buffer` — cited in `## Module: src/nmon/views/temp_view.py` (line 552) and `## Module: src/nmon/widgets/sparkline.py` (line 707). No such section or file declared.
- `nmon.models` — cited in `## Module: src/nmon/views/temp_view.py` (line 552) for `GpuSnapshot, OllamaSnapshot`. No `nmon.models` module declared anywhere.
- `nmon.gpu.monitor` — cited in `## Module: src/nmon/app.py` first (line 811) as import source for multiple symbols. No such module; the real module is `nmon.gpu_monitor`.

---

Now applying patches in order: E fixes first, then C (duplicate section removal), then D (resolved by C), then Design Decisions enhancement.

**Patch 1 — E: history.py Imports****Patch 2 — E: alerts.py Imports****Patch 3 — E: dashboard_view.py (first) Imports****Patch 4 — E: temp_view.py Imports****Patch 5 — E: power_view.py Imports****Patch 6 — E: llm_view.py Imports****Patch 7 — E: sparkline.py Imports**Now the C patches — removing duplicate module sections. I'll remove them block by block. First, the block starting at the second `dashboard_view.py` (line ~1083) through to just before `## Design Decisions`. Let me read the exact boundary text.Now I'll remove the entire duplicate block (lines 1083–1670) in one edit. I'll use the Data Pipeline end + the block start + the Design Decisions start as anchors.I'll remove the duplicates in three chunks. Chunk 1: second `dashboard_view.py` + second `config.py` + second `app.py` + second `main.py`.Chunk 2: remove second `gpu_monitor.py` + second `ollama_monitor.py` + second `history.py` + second `alerts.py` + second `db.py`.Chunk 3: remove third `dashboard_view.py` through second `__init__.py` plus duplicate structural sections.Now remove the duplicate tail sections after Design Decisions (second Testing Strategy, second Dependencies, Build/Run Instructions, Error Handling — keeping only what's valuable). Let me read what's there now.Good — the duplicate Testing Strategy, Dependencies, Build/Run Instructions, and Error Handling sections still remain after Design Decisions. Let me read the end of file to see the full extent.Now I'll remove the duplicate Testing Strategy + Dependencies + Build/Run Instructions block (lines 1097–1288), keeping the Error Handling section. Then I'll strip the duplicate pseudocode bodies from within Error Handling.Now strip the duplicate pseudocode bodies from within the Error Handling section. Let me read what's there.Now strip the 4 duplicate pseudocode blocks from the Error Handling section, keeping the scenario text:Now enhance the Design Decisions section to meet Planning Prompt deliverable #8 (each entry needs decision + alternatives + rationale):Now also fix the `AlertState` duplicate body in `alerts.py` module section — the Data Model section should list name + location only, but `alerts.py` section also re-declares the body. Let me check the current state of the alerts.py section:The `AlertState` body is duplicated here — it's defined in `## Data Model` section (canonical) AND re-stated in `## Module: src/nmon/alerts.py`. Remove the body from the module section, leave only a reference:Also remove the duplicate `HistoryStore` and `compute_alert` pseudocode bodies from the `## Data Pipeline` section:Now clean up the blank lines left in the file and verify the final state:File is now 1145 lines vs 2057 original — 912 lines of duplicates removed. Let me do a final verification scan for any remaining duplicate `## Module:` headings:Each module appears exactly once. Now verify no phantom imports remain in canonical sections:Still some phantom/E issues remaining. Fix `main.py` imports (phantom protocol modules):Fix `history.py` — `AppConfig` → `Settings` in `__init__` pseudocode:Fix `app.py` imports — `nmon.gpu.monitor` → `nmon.gpu_monitor`, remove phantom `NmonView`:Final verification:All phantom/wrong-name references cleared. Final module heading check:17 unique module sections, each appearing exactly once. Now output the remaining audit sections.

---

### PATCHES_APPLIED

- `## Module: src/nmon/history.py` [E]: Fixed `OllamaSnapshot` import source from `nmon.gpu_monitor` → `nmon.ollama_monitor`; renamed `AppConfig` → `Settings` throughout file.
- `## Module: src/nmon/alerts.py` [E]: Fixed `Settings` import source from `nmon.ollama_monitor` → `nmon.config`.
- `## Module: src/nmon/views/dashboard_view.py` first [E]: Fixed `GpuSnapshot` import from `nmon.config` → `nmon.gpu_monitor`; `OllamaSnapshot` from `nmon.config` → `nmon.ollama_monitor`; removed phantom `GpuSample, GpuMonitorProtocol from nmon.gpu.protocol`.
- `## Module: src/nmon/views/temp_view.py` [E]: Replaced entire phantom-laden Imports line; `GpuSnapshot` from `nmon.gpu_monitor`, `OllamaSnapshot` from `nmon.ollama_monitor`, `Settings/UserPrefs` from `nmon.config`; removed `nmon.gpu.protocol`, `nmon.storage.ring_buffer`, `nmon.models`.
- `## Module: src/nmon/views/power_view.py` [E]: Fixed `HistoryStore` from `nmon.gpu_monitor` → `nmon.history`; `UserPrefs` from `nmon.gpu_monitor` → `nmon.config`; removed phantom `GpuSample`.
- `## Module: src/nmon/views/llm_view.py` [E]: Fixed `HistoryStore`, `Settings`, `UserPrefs` all from `nmon.ollama_monitor` → correct modules; removed phantom `GpuSample, GpuMonitorProtocol`.
- `## Module: src/nmon/widgets/sparkline.py` [E]: Removed all phantom imports (`nmon.gpu.protocol`, `nmon.storage.ring_buffer`); replaced with note that no intra-project imports are required.
- `## Module: src/nmon/main.py` [E/F]: Removed phantom `GpuMonitorProtocol from nmon.gpu.protocol` and `OllamaMonitorProtocol from nmon.ollama.protocol`.
- `## Module: src/nmon/app.py` [E/F]: Replaced malformed multi-source import line; removed phantom `nmon.gpu.monitor`, `nmon.ollama.monitor`, `NmonView`; correct paths for all symbols.
- `## Module: src/nmon/alerts.py` [C]: Reduced `AlertState` body in module section to a cross-reference; canonical body remains in `## Data Model`.
- `## Data Pipeline` [C]: Replaced `HistoryStore` and `compute_alert` pseudocode bodies with cross-references to canonical module sections.
- Second `## Module: src/nmon/views/dashboard_view.py` (render_dashboard_view function) [C]: Removed entire duplicate section.
- Second `## Module: src/nmon/config.py` [C/D]: Removed entire duplicate section (contained renamed functions `load_prefs`/`save_prefs` diverging from canonical `load_user_prefs`/`save_user_prefs`).
- Second `## Module: src/nmon/app.py` [C/D]: Removed entire duplicate section (contained `NmonApp.__init__(self, settings: Settings)` with D-drifted 1-parameter signature).
- Second `## Module: src/nmon/main.py` [C]: Removed entire duplicate section.
- Second `## Module: src/nmon/gpu_monitor.py` [C/D]: Removed entire duplicate section (contained `GpuMonitorProtocol.poll(self)` with D-drifted `self` parameter).
- Second `## Module: src/nmon/ollama_monitor.py` [C/D]: Removed entire duplicate section (contained `async def poll(self, client)` with D-drifted `self` parameter).
- Second `## Module: src/nmon/history.py` [C/D]: Removed entire duplicate section (contained `flush_to_db(db: sqlite3.Connection)` with D-drifted type).
- Second `## Module: src/nmon/alerts.py` [C]: Removed entire duplicate section.
- Second `## Module: src/nmon/db.py` [C]: Removed entire duplicate section.
- Third `## Module: src/nmon/views/dashboard_view.py` [C]: Removed entire duplicate section.
- Second occurrences of `temp_view.py`, `power_view.py`, `llm_view.py`, `sparkline.py`, `alert_bar.py`, `__init__.py` [C]: All duplicate sections removed.
- Duplicate `## Project Structure`, `## Data Model`, `## SQLite Schema`, `## Dependencies`, `## Build/Run`, `## Testing Strategy` blocks [C]: All removed.
- `## Error Handling` [C]: Stripped 4 pseudocode bodies (`poll()` GPU, `poll()` Ollama, `flush_to_db()`, `compute_alert()`, `handle_input()`); replaced with cross-references to canonical module sections.
- `## Design Decisions` [B-enhancement]: Replaced 9 one-liner entries with 8 fully-specified entries each containing decision, alternatives considered, and rationale, as required by Planning Prompt deliverable #8.

---

### MANUAL_REMAINING

- **F** `nmon.gpu.protocol` (was cited by `## Module: src/nmon/main.py` line 154, `## Module: src/nmon/views/dashboard_view.py`, `## Module: src/nmon/gpu_monitor.py` second — all now removed): The phantom was caused by the plan inventing a `GpuMonitorProtocol` class in a non-existent `gpu/protocol.py` sub-package. The Planning Prompt specifies a standalone `poll() -> list[GpuSnapshot]` function in `gpu_monitor.py`, not a class. No action needed post-patch — phantom references have been removed.
- **F** `nmon.ollama.protocol` (was cited by `## Module: src/nmon/main.py`, `## Module: src/nmon/app.py` second, `## Module: src/nmon/ollama_monitor.py` second — all now removed): Same root cause as above. The Planning Prompt specifies a standalone `async def poll(client: httpx.AsyncClient)` function in `ollama_monitor.py`, not a class in a sub-package. Removed via C patches.
- **F** `nmon.storage.ring_buffer` (was cited by `temp_view.py` and `sparkline.py` — both Imports lines now patched): `RingBuffer` is not specified anywhere in the Planning Prompt. The History Store uses `deque` (§3.1). No `ring_buffer.py` module should be created. Confirm at Stage 3 that no step references this path.
- **F** `nmon.models` (was cited by `temp_view.py` — Imports line now patched): `GpuSnapshot` and `OllamaSnapshot` live in `gpu_monitor.py` and `ollama_monitor.py` respectively per the Planning Prompt. No `models.py` module should be created.
- **F** `nmon.gpu.monitor` (was cited by `app.py` first Imports — now patched): Was a typo for `nmon.gpu_monitor`. Resolved in E/F patch to `app.py`.

---

### VERDICT

VERDICT: PASS