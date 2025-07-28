import numpy as np
import copy


class ReverbPlugin():
    def __init__(self, decay: float = 0, delay_samps: int = 1, wet_level: float = 0, taps: int = 0, allow_clipping: bool = True, old_plugin: 'ReverbPlugin' = None, channels: int = 2):
        self.decay = decay
        self.taps = taps
        self.wet_level = max(0.0, min(1.0, wet_level))
        self.delay_samps = delay_samps
        self.channels = channels
        self.allow_clipping = allow_clipping
        
        # dont need new buffers we can smoothly turn this knob
        if old_plugin and old_plugin.taps == taps and old_plugin.delay_samps == delay_samps and old_plugin.channels == channels:
            self.delay_samps_list = copy.deepcopy(old_plugin.delay_samps_list)
            self.buffers = copy.deepcopy(old_plugin.buffers)
            self.buffer_indices = copy.deepcopy(old_plugin.buffer_indices)
        # need new buffers, have to restart rebverb mixing
        else:
            # dither the buffer lengths for natural sound
            self.delay_samps_list = [int(self.delay_samps * (1 + 0.15 * i)) for i in range(self.taps)]
            self.buffers = [
                [np.zeros(delay) for delay in self.delay_samps_list]
                for _ in range(self.channels)
            ]
            self.buffer_indices = [
                [0 for _ in self.delay_samps_list]
                for _ in range(self.channels)
            ]
            
    # https://en.wikipedia.org/wiki/Comb_filter#Feedback_form
    # Multi channel reverb where each tap represents a feedback comb filter with a unique delay
    def apply(self, input: np.ndarray):
        # Wet buffer to apply to input signal
        block_len = input.shape[0]
        output = np.copy(input)
        wet_total = np.zeros_like(output)
        # Apply reverb to all channels
        for ch in range(self.channels):
            wet_sum = np.zeros(block_len)
            # Apply taps
            for tap, delay in enumerate(self.delay_samps_list):
                # Grab circular buffer holding wet signal for this tap and the write index
                buf = self.buffers[ch][tap]
                idx = self.buffer_indices[ch][tap]
                # Grab wet signal portion for this tap from circular buffer
                # the buffers are different length for each tap so we modulo the index
                wet = np.zeros(block_len)
                idxs = (np.arange(idx, idx + block_len) % delay)
                wet[:] = buf[idxs]
                # add the input back and our wet signal potion with delay and decay gain
                buf[idxs] = input[:, ch] + self.decay * wet
                self.buffers[ch][tap] = buf
                # update the write index on the circular buffer
                idx = (idx + block_len) % delay
                self.buffer_indices[ch][tap] = idx
                # update the wet sum for this channel
                wet_sum += wet
            
             # Average wet for this channel across taps
            wet_total[:, ch] = wet_sum / self.taps

        # Mix dry and wet signals
        output = (1 - self.wet_level) * input + self.wet_level * wet_total

        if self.allow_clipping:
            return output
        else:
            return output / max(1.0, np.max(np.abs(output)))



