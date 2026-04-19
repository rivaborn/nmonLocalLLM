# Call Graph & Dependency Diagrams

Auto-generated from per-file architecture docs.

## Function Call Graph

Showing functions with 2+ incoming calls. Limited to 150 edges.

```mermaid
%%{ init: { 'theme': 'dark', 'flowchart': { 'curve': 'basis' } } }%%
graph LR

  subgraph Module: `src
    on_button_pressed_event__Button_Pressed_____None["on_button_pressed(event: Button.Pressed) -> None"]
    update_time_range_seconds_____None["update_time_range(seconds) -> None"]
  end

  subgraph Module: src
  end

  subgraph root
  end

  subgraph src
  end

```

## Subsystem Dependencies

Cross-subsystem call edges. Arrow labels show call counts.

```mermaid
%%{ init: { 'theme': 'dark' } }%%
graph TD

  Module___src["Module: `src (86 funcs)"]
  src["src (61 funcs)"]
  root["root (16 funcs)"]
  Module__src["Module: src (14 funcs)"]

```

## Statistics

- Total functions documented: 177
- Total call edges: 2
- Subsystems: 4

