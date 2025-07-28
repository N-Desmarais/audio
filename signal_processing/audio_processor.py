import logging
from sounddevice import sleep
from message_bus import *
from signal_processing.amplifier import AmplifierPlugin
from signal_processing.reverb import ReverbPlugin
from threading import Thread, Lock 
from typing import Any
import numpy as np 

class AudioProcessor():
    def __init__(self, stop_event: Any, message_bus: MessageBus):
        
        self.message_bus = message_bus
        self.plugin_lock = Lock()
        self.stop_event = stop_event
        
        self.reverb = ReverbPlugin()
        self.amplifier = AmplifierPlugin
        
        self.do_reverb = False
        self.do_amplification = False
        
        self.message_listener = Thread(target=self.read_message_bus)
        self.message_listener.start()
        
    def read_message_bus(self):
        while not self.stop_event.is_set():
            message = self.message_bus.receive()
            
            if message is None:
                continue
                
            
            if isinstance(message, ReverbSettingsMessage):
                with self.plugin_lock:
                    self.do_reverb = message.enabled
                    self.reverb = ReverbPlugin(
                        message.decay,
                        message.delay_samps,
                        message.wet_level,
                        message.taps,
                        message.allow_clipping,
                        self.reverb
                    )
                    
            if isinstance(message, AmplifierSettingsMessage):
                with self.plugin_lock:
                    self.do_amplification = message.enabled
                    self.amplifier.set_scale(message.scale)
                    self.amplifier.set_allow_clipping(message.allow_clipping)
            
        
    def process_audio(self, input: np.ndarray):
        with self.plugin_lock:
            if self.do_reverb:
                input = self.reverb.apply(input)
            if self.do_amplification:
                input = self.amplifier.apply(input)

        return input




