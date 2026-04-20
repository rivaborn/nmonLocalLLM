Create a detailed architecture and implementation plan for a Rich-based Python app named nmon.

Purpose:
nmon monitors all NVIDIA GPUs in the system and also monitors a local Ollama LLM server when present.

Environment:
1. Ollama endpoint: http://192.168.1.126:11434
2. GPU: RTX 3090
3. Model: Devstral Small 2
4. I have aider installed
5. Use Rich (https://github.com/Textualize/rich) — use `rich.live.Live` with `rich.layout.Layout` for the dashboard; translate "tabs" into keyboard-switchable views (1/2/3/4 or arrow keys) rendered into the same Layout
6. Use nvidia-ml-py where appropriate
7. Do not write code yet

Functional requirements:
1. Monitor all NVIDIA GPUs for:
   1.1. Temperature
   1.2. Memory use
   1.3. Power use
2. Retain at least 24 hours of history.
3. Dashboard tab must show:
   3.1. Current temperature
   3.2. Max temperature over 24 hours
   3.3. Average temperature over 1 hour
   3.4. Current memory use
4. Temperature tab must show historical temperature charts.
5. Power tab must show historical power charts.
6. Provide time-range controls for 1h, 4h, 12h, and 24h.
7. Update interval must be adjustable.
8. Every function must have unit tests.

GPU Memory Junction Temperature:
1. For GPUs that support it, monitor GPU Memory Junction Temperature using nvidia-ml-py.
2. Add a separate dashboard section for it below the main GPU section.
3. Show current, 24h max, and 1h average values.
4. On the TEMP tab, show GPU Memory Junction Temperature as a separate series in a different color.
5. Add a toggle to show/hide that series.
6. Show elapsed collection time as Hours, Minutes, and Seconds instead of "pts".
7. Add a configurable threshold line on the TEMP chart:
   7.1. Default 95.0C
   7.2. Toggle on/off
   7.3. Up/Down arrows adjust by 0.5C
   7.4. Persist value across restarts

Ollama / LLM monitoring:
1. Detect Ollama on startup.
2. If present, add a DASHBOARD section labeled exactly "LLM Server".
3. Show:
   3.1. Loaded model
   3.2. Model size
   3.3. GPU use percentage
   3.4. CPU use percentage
4. Display GPU offloading clearly.
5. If GPU use is 100%, color GPU and CPU percentages green.
6. If GPU use is below 100%, color them red.
7. Add a tab labeled "LLM Server".
8. On that tab, show GPU use and CPU use on the same chart.
9. Add chart guide lines at 0% and 100%.
10. Fix any chart-direction issues so increases and decreases render correctly.
11. Query the Ollama server at the same interval as GPU monitoring.
12. Add CTRL+Q to exit.

Global alert bar:
1. If GPU offloading occurs, show an orange status bar at the top of the app on every tab.
2. Keep it visible for at least 1 second after it appears.
3. If GPU offloading exceeds 5%, make the status bar red.

Output requirements:
1. Produce a step-by-step architecture and implementation plan only.
2. Write the plan as if it will be executed incrementally by aider plus a local LLM.
3. Save the plan in: Architecture Plan.md
4. Include:
   4.1. Project structure and file paths
   4.2. Classes, functions, and signatures
   4.3. Parameters and return types
   4.4. Data models and storage approach
   4.5. Error-handling strategy
   4.6. Testing strategy
   4.7. Step-by-step pseudocode
   4.8. Exact files created or modified at each step
   4.9. Dependency order between steps
5. Do not write code yet.
6. Be explicit, concrete, and implementation-ready.