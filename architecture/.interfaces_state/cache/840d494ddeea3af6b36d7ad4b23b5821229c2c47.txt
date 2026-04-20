# Module: `src/nmon/widgets/sparkline.py`

## Role
Provides a reusable ASCII/Unicode chart widget for displaying time-series data with optional guide and threshold lines.

## Contract: `Sparkline`

### `__init__(title, series, y_min, y_max, width, height, guide_lines, threshold)`
- **Requires:** `title` is str; `series` is list of (str, list[float]) tuples; `y_min` and `y_max` are float; `width` and `height` are int > 0; `guide_lines` is list of float or None; `threshold` is ThresholdLine or None
- **Establishes:** All parameters are stored as instance attributes; `series` data is not validated for consistency
- **Raises:** None

### `render() -> Panel`
- **Requires:** `self.y_min` and `self.y_max` are not both None; `self.width` and `self.height` are positive integers; `self.series` contains valid data points
- **Guarantees:** Returns a Rich Panel with rendered sparkline chart; chart respects specified dimensions and data ranges
- **Raises:** None
- **Silent failure:** If `self.width` is 1, division by zero occurs in `col_value` calculation; if `self.height` is 1, division by zero occurs in `row_value` calculation; if `self.series` contains empty lists, no data is rendered for that series; if `self.threshold.value` or `guide_line` values are outside the y-axis range, positioning may be incorrect; if `self.series` data points are None, they are skipped without error
- **Thread safety:** Safe

## Module Invariants
None

## Resource Lifecycle
None
