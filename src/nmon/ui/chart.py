from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Sparkline, Static

_CHART_HEIGHT = 8


class Chart(Widget):
    """Sparkline chart with a Y-axis showing min / mid / max labels."""

    DEFAULT_CSS = f"""
    Chart {{
        height: {_CHART_HEIGHT};
        layout: horizontal;
    }}
    Chart > #y-axis {{
        width: 9;
        height: {_CHART_HEIGHT};
        text-align: right;
    }}
    Chart > Sparkline {{
        width: 1fr;
        height: {_CHART_HEIGHT};
    }}
    """

    def __init__(
        self,
        *,
        min_color: str = "green",
        max_color: str = "red",
        unit: str = "",
        id: str | None = None,
    ) -> None:
        self._unit = unit
        self._min_color = min_color
        self._max_color = max_color
        super().__init__(id=id)

    def compose(self) -> ComposeResult:
        yield Static(self._make_axis([]), id="y-axis")
        yield Sparkline(
            [],
            min_color=self._min_color,
            max_color=self._max_color,
            summary_function=max,
        )

    def update_data(self, data: list[float]) -> None:
        import math
        clean = [v for v in data if not math.isnan(v)]
        self.query_one("#y-axis", Static).update(self._make_axis(clean))
        self.query_one(Sparkline).data = clean

    def _make_axis(self, data: list[float]) -> str:
        w = 8
        lines = [" " * w] * _CHART_HEIGHT
        if data:
            hi = max(data)
            lo = min(data)
            mid = (hi + lo) / 2
            u = self._unit
            lines[0] = f"{hi:.0f}{u}".rjust(w)
            lines[_CHART_HEIGHT // 2] = f"{mid:.0f}{u}".rjust(w)
            lines[_CHART_HEIGHT - 1] = f"{lo:.0f}{u}".rjust(w)
        return "\n".join(lines)
