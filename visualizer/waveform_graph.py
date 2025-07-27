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
        self.plot_widget.setYRange(-1.0, 1.0)
        self.plot_widget.showGrid(x=True, y=True)
        self.plot_widget.setMouseEnabled(x=False, y=False)
        self.curve = self.plot_widget.plot(pen=pen)

    def set_data(self, x: np.ndarray, y: np.ndarray) -> None:
        """
        Update the waveform plot data.

        Parameters:
            x (np.ndarray): The data for the x-axis.
            y (np.ndarray): The data for the y-axis.
        """
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
        
    def update(self, ymode: bool, buffer_seconds: float, plot_buffer: np.ndarray) -> None:
        """
        Update the waveform plot with new data.

        Parameters:
            ymode (bool): If True, display the waveform in decibel scale; otherwise, show amplitude.
            buffer_seconds (float): The duration of the buffer in seconds.
            plot_buffer (np.ndarray): The buffer containing waveform data.
        """
        x = np.linspace(0, buffer_seconds, len(plot_buffer))
        if ymode:
            y = 20 * np.log10(np.maximum(np.abs(plot_buffer), 1e-8))
            y = np.clip(y, -80, 0)
        else:
            y = plot_buffer
        self.set_data(x, y)
        self.set_xrange(0, buffer_seconds)