import numpy as np
import pyqtgraph as pg  
from typing import Any

class WaveformGraph:
    """
    Provides a wrapper around a pyqtgraph PlotWidget for displaying audio waveforms.
    """

    def __init__(self, parent: Any = None, pen: str = 'c') -> None:
        """
        Construct the waveform graph widget.

        Parameters:
            parent (Any): The parent widget for the plot.
            pen (str): The color of the pen used to draw the waveform.
        """
        self.plot_widget = pg.PlotWidget(parent=parent)
        self.plot_widget.setYRange(-.5, .5)
        self.plot_widget.showGrid(x=True, y=True)
        self.plot_widget.setMouseEnabled(x=False, y=False)
        self.pen = pen
        self.curve = self.plot_widget.plot(pen=self.pen)
        self.area_item = None
        self.area_enabled = False
        self.ymode = False

    def set_data(self, x: np.ndarray, y: np.ndarray) -> None:
        """
        Update the waveform plot data.

        Parameters:
            x (np.ndarray): The data for the x-axis.
            y (np.ndarray): The data for the y-axis.
        """
        if not self.area_enabled and self.area_item is not None:
            self.plot_widget.removeItem(self.area_item)
            self.area_item = None
            
        if self.area_enabled:
            self._draw_area(x, y)
        else:
            self.curve.setData(x, y)
        


    def set_xrange(self, start: float, end: float) -> None:
        """
        Set the visible range of the x-axis.

        Parameters:
            start (float): The minimum value for the x-axis.
            end (float): The maximum value for the x-axis.
        """
        self.plot_widget.setXRange(start, end, padding=0)

    def set_yrange(self, start: float, end: float) -> None:
        """
        Set the visible range of the y-axis.

        Parameters:
            start (float): The minimum value for the y-axis.
            end (float): The maximum value for the y-axis.
        """
        self.plot_widget.setYRange(start, end, padding=0)

    def set_ylabel(self, label: str) -> None:
        """
        Set the label for the y-axis.

        Parameters:
            label (str): The label text for the y-axis.
        """
        self.plot_widget.setLabel('left', label)

    def toggle_area_enabled(self, enabled: bool) -> None:
        """Enable or disable area under curve fill."""
        self.area_enabled = enabled

    def _draw_area(self, x: np.ndarray, y: np.ndarray) -> None:
        """Draw or update the area under the curve."""
        if self.area_item is not None:
            self.plot_widget.removeItem(self.area_item)
        # Fill from y to baseline (0 for amplitude, -80 for dB)
        baseline = -80 if self.ymode else 0 
        area_x = np.concatenate([x, x[::-1]])
        area_y = np.concatenate([y, np.full_like(y, baseline)])
        self.area_item = pg.PlotDataItem(area_x, area_y, fillLevel=baseline, brush=self.pen, pen=self.pen)
        self.plot_widget.addItem(self.area_item)

    def update(self, buffer_seconds: float, plot_buffer: np.ndarray) -> None:
        """
        Update the waveform plot with new data.

        Parameters:
            ymode (bool): If True, display the waveform in decibel scale; otherwise, show amplitude.
            buffer_seconds (float): The duration of the buffer in seconds.
            plot_buffer (np.ndarray): The buffer containing waveform data.
        """
        x = np.linspace(0, buffer_seconds, len(plot_buffer))
        if self.ymode:
            y = 20 * np.log10(np.maximum(np.abs(plot_buffer), 1e-8))
            y = np.clip(y, -80, 0)
            self.set_yrange(-80, 0)
        else:
            y = plot_buffer
            self.set_yrange(-1.0, 1.0)
        self.set_data(x, y)
        self.set_xrange(0, buffer_seconds)

    def set_pen(self, pen: str) -> None:
        """
        Set the pen color for the waveform plot.
        """
        self.curve.setPen(pen)
        self.pen = pen
       