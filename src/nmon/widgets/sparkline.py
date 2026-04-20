"""
Sparkline widget for rendering ASCII/Unicode charts in the terminal.

This module provides the Sparkline class for creating time-series charts
with optional guide lines and threshold lines. It uses Unicode block
characters to render charts in a specified width and height.
"""

from dataclasses import dataclass
from typing import List, Tuple, Optional
import math

from rich.panel import Panel
from rich.text import Text


@dataclass
class ThresholdLine:
    """Represents a horizontal threshold line on a sparkline chart."""
    value: float
    label: str
    visible: bool


class Sparkline:
    """A reusable ASCII/Unicode chart widget for displaying time-series data."""

    def __init__(
        self,
        title: str,
        series: List[Tuple[str, List[float]]],
        y_min: float,
        y_max: float,
        width: int,
        height: int,
        guide_lines: Optional[List[float]] = None,
        threshold: Optional[ThresholdLine] = None
    ) -> None:
        """
        Initialize a Sparkline chart.

        Args:
            title: Chart title to display in the panel header
            series: List of (label, values) tuples for each data series
            y_min: Minimum value for the y-axis
            y_max: Maximum value for the y-axis
            width: Width of the chart in characters
            height: Height of the chart in lines
            guide_lines: Optional list of horizontal guide lines to draw
            threshold: Optional threshold line to display
        """
        self.title = title
        self.series = series
        self.y_min = y_min
        self.y_max = y_max
        self.width = width
        self.height = height
        self.guide_lines = guide_lines
        self.threshold = threshold

    def render(self) -> Panel:
        """
        Render the sparkline chart as a Rich Panel.

        Returns:
            Rich Panel containing the rendered chart
        """
        # Create text object for chart content
        text = Text()
        
        # For each row in height
        for row in range(self.height):
            # Compute row value based on y_min, y_max, and row index
            # Row 0 is top of chart (highest value), row height-1 is bottom (lowest value)
            row_value = self.y_max - (row / (self.height - 1)) * (self.y_max - self.y_min)
            
            # For each column in width
            for col in range(self.width):
                # Compute column value based on x position
                col_value = col / (self.width - 1) if self.width > 1 else 0
                
                # Determine if this cell should be filled based on series data
                # Find the closest data point for this column
                filled = False
                for label, values in self.series:
                    if len(values) > 0:
                        # Map column position to data index
                        data_index = int(col_value * (len(values) - 1)) if len(values) > 1 else 0
                        if data_index < len(values) and values[data_index] is not None:
                            # Check if this data point is close enough to row_value
                            # Use a small tolerance to determine if we should fill this cell
                            if abs(values[data_index] - row_value) <= (self.y_max - self.y_min) / self.height:
                                filled = True
                                break
                
                # Append appropriate Unicode block character to text
                # Use full block for filled cells, space for empty
                if filled:
                    text.append("█")
                else:
                    text.append(" ")
            
            # Append newline to text
            text.append("\n")
        
        # If threshold is not None and threshold.visible:
        if self.threshold is not None and self.threshold.visible:
            # Compute row position for threshold line
            # Convert threshold value to row position
            if self.y_max != self.y_min:
                row_pos = int((self.y_max - self.threshold.value) / (self.y_max - self.y_min) * (self.height - 1))
                row_pos = max(0, min(self.height - 1, row_pos))
                
                # Draw threshold line with label
                # Insert label at the beginning of the row
                if row_pos < len(text.split("\n")):
                    # Get the line content
                    lines = text.split("\n")
                    if row_pos < len(lines):
                        # Prepend label to the row
                        lines[row_pos] = f"{self.threshold.label} " + lines[row_pos]
                        text = Text("\n".join(lines))
        
        # If guide_lines is not None:
        if self.guide_lines is not None:
            # For each guide_line in guide_lines:
            for guide_line in self.guide_lines:
                # Compute row position for guide line
                if self.y_max != self.y_min:
                    row_pos = int((self.y_max - guide_line) / (self.y_max - self.y_min) * (self.height - 1))
                    row_pos = max(0, min(self.height - 1, row_pos))
                    
                    # Draw guide line with label
                    # Insert label at the beginning of the row
                    if row_pos < len(text.split("\n")):
                        lines = text.split("\n")
                        if row_pos < len(lines):
                            # Prepend label to the row
                            lines[row_pos] = f"{guide_line:.1f} " + lines[row_pos]
                            text = Text("\n".join(lines))
        
        # Create rich.panel.Panel with title=self.title and renderable=text
        panel = Panel(text, title=self.title)
        
        # Return panel
        return panel
