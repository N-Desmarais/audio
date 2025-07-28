from abc import ABC
import numpy as np
from pyqtgraph import GraphicsLayoutWidget, HistogramLUTItem, ImageItem, PlotWidget  
from pyqtgraph.Qt import QtCore, QtWidgets  

class HistogramScale(ABC): 
    @staticmethod
    def default_levels() -> list[float]:
        """
        Return the default value range for the histogram color scale.

        Returns:
            list[float]: The default lower and upper bounds for the scale.
        """
        return []

    @staticmethod        
    def convert(new_audio: np.ndarray, graph: 'SpectrogramGraph') -> None:
        """
        Convert new audio data for the spectrogram graph (to be implemented by subclasses).

        Parameters:
            new_audio (np.ndarray): The new audio data to process.
            graph (SpectrogramGraph): The SpectrogramGraph instance to update.
        """
        pass
    

class DecibelScale(HistogramScale):
    @staticmethod
    def default_levels() -> list[float]:
        """
        Return the default decibel range for the color scale.

        Returns:
            list[float]: The default lower and upper bounds in dB.
        """
        return [-80, 0]
    
    @staticmethod
    def convert(new_audio: np.ndarray, graph: 'SpectrogramGraph') -> None:
        """
        Convert new audio data to decibel scale and update the spectrogram buffer.

        Parameters:
            new_audio (np.ndarray): The new audio data to process.
            graph (SpectrogramGraph): The SpectrogramGraph instance to update.
        """
        audio = new_audio.astype(np.float32)
        for sample in audio:
            graph._spec_audio_buffer[graph._spec_audio_buffer_pos] = sample
            graph._spec_audio_buffer_pos += 1
            while graph._spec_audio_buffer_pos >= graph.spec_nfft:
                windowed = graph._spec_audio_buffer * np.hanning(graph.spec_nfft)
                spectrum = np.abs(np.fft.rfft(windowed))[:graph.spec_nfft // 2]
                spectrum_db = 20 * np.log10(np.maximum(spectrum, 1e-8))
                spectrum_db = np.clip(spectrum_db, -80, 0)
                graph.spec_buffer = np.roll(graph.spec_buffer, -1, axis=1)
                graph.spec_buffer[:, -1] = spectrum_db
                graph._spec_audio_buffer[:graph.spec_nfft - graph.spec_hop] = graph._spec_audio_buffer[graph.spec_hop:]
                graph._spec_audio_buffer_pos -= graph.spec_hop
    

class SpectrogramGraph():
    def __init__(self) -> None:
        """
        Initialize the SpectrogramGraph widget and its buffers.
        """
        
        self.scale: HistogramScale = DecibelScale()
        
        self.spectrogram_plot = PlotWidget()
        self.spectrogram_plot.setMinimumHeight(200)
        self.spectrogram_plot.setMinimumWidth(700)
        self.spectrogram_plot.setMouseEnabled(x=False, y=False)
        self.spectrogram_plot.setLabel('bottom', 'Time', units='s')
        self.spectrogram_plot.setLabel('left', 'Frequency', units='Hz')
        self.spectrogram_img = ImageItem()
        self.spectrogram_plot.addItem(self.spectrogram_img)

        self.spectrogram_colorbar = HistogramLUTItem()
        self.spectrogram_colorbar.setImageItem(self.spectrogram_img)
        self.spectrogram_colorbar.gradient.loadPreset('yellowy')
        self.spectrogram_colorbar.setLevels(*self.scale.default_levels())
        colorbar_widget = GraphicsLayoutWidget()
        colorbar_widget.setFixedWidth(90)
        colorbar_widget.addItem(self.spectrogram_colorbar)

        self.spectrogram_tab = QtWidgets.QWidget()
        spectro_layout = QtWidgets.QHBoxLayout(self.spectrogram_tab)
        spectro_layout.setContentsMargins(0, 0, 0, 0)
        spectro_layout.setSpacing(0)
        spectro_layout.addWidget(self.spectrogram_plot, stretch=10)
        spectro_layout.addWidget(colorbar_widget, stretch=0)
        
        # Spectrogram parameters and buffer
        self.spec_nfft: int = 512
        self.spec_hop: int = 128
        self.spec_buffer_cols: int = 400
        self.spec_buffer = np.zeros((self.spec_nfft // 2, self.spec_buffer_cols), dtype=np.float32)
        self.spec_col: int = 0
        
        self._spec_audio_buffer = np.zeros(self.spec_nfft, dtype=np.float32)
        self._spec_audio_buffer_pos: int = 0
            
    def update(self, new_audio: np.ndarray, buffer_seconds: float, samplerate: int) -> None:      
        """
        Update the spectrogram display with new audio data.

        Parameters:
            new_audio (np.ndarray): The new audio data to process.
            buffer_seconds (float): The duration of the buffer in seconds.
            samplerate (int): The audio sample rate.
        """
        self.scale.convert(new_audio, self)

        levels = self.spectrogram_colorbar.getLevels()
        self.spectrogram_img.setImage(
            self.spec_buffer.T,
            autoLevels=False,
            levels=levels
        )
        freq_extent = (0, samplerate / 2)
        self.spectrogram_img.setRect(
            QtCore.QRectF(
                0, freq_extent[0],
                buffer_seconds, freq_extent[1] - freq_extent[0]
            )
        )
        self.spectrogram_colorbar.setHistogramRange(*levels)
        self.spectrogram_plot.setXRange(0, buffer_seconds, padding=0)