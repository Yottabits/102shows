#!/usr/bin/env python3

# 8 bar Audio equaliser using MCP2307
import logging
from struct import unpack

import alsaaudio as aa
import numpy as np

from drivers import LEDStrip
from lightshows.templates.colorcycle import ColorCycle

log = logging.getLogger(__name__)


def calculate_levels(data, chunk, sample_rate):
    # Convert raw data to numpy array
    data = unpack("%dh" % (len(data) / 2), data)
    data = np.array(data, dtype='h')
    # Apply FFT - real data so rfft used
    fourier = np.fft.rfft(data)
    # Remove last element in array to make it the same size as chunk
    fourier = np.delete(fourier, len(fourier) - 1)
    # Find amplitude
    power = np.log10(np.abs(fourier)) ** 2
    # Araange array into 8 rows for the 8 bars on LED matrix
    power = np.reshape(power, (1024, -1))
    matrix = np.int_(np.average(power, axis=1) / 4)
    return matrix


def combine_color(red, green, blue, brightness: int):
    brightness_factor = brightness / 100
    """Make one 3*8 byte color value."""

    return (np.clip(red * brightness_factor, 0, 255), np.clip(green * brightness_factor, 0, 255),
            np.clip(blue * brightness_factor, 0, 255))


def wheel(value, threshold):
    """Get a color from a color wheel; Green -> Red -> Blue -> Green"""

    wheel_pos = value - threshold
    brightness = value if value > threshold else 0

    if wheel_pos > 255:
        wheel_pos = 255  # Safeguard
    if wheel_pos < 85:  # Red -> Green
        return combine_color(255 - wheel_pos * 3, wheel_pos * 3, 0, brightness)
    if wheel_pos < 170:  # Green -> Blue
        wheel_pos -= 85
        return combine_color(0, 255 - wheel_pos * 3, wheel_pos * 3, brightness)
    # Blue -> Magenta
    wheel_pos -= 170
    return combine_color(0, wheel_pos * 3, 255, brightness)


def brightness(value):
    if value < threshold:
        return 0
    if value < 4 * threshold:
        return 1
    return min(value - threshold, 100)


threshold = 15


class AudioSpectrum(ColorCycle):

    def __init__(self, strip: LEDStrip, parameters: dict):
        super().__init__(strip, parameters)
        self.data_in = None
        self.chunk = 0
        self.sample_rate = 0
        self.first_run = None

    def init_parameters(self):
        super().init_parameters()
        self.set_parameter('num_steps_per_cycle', 255)
        self.set_parameter('pause_sec', 0.001)

    def before_start(self) -> None:
        log.info("set up audio")
        # Set up audio
        self.sample_rate = 44100
        no_channels = 2
        self.chunk = 2048  # Use a multiple of 8
        self.data_in = aa.PCM(aa.PCM_CAPTURE, aa.PCM_NORMAL, cardindex=0)
        self.data_in.setchannels(no_channels)
        self.data_in.setrate(self.sample_rate)
        self.data_in.setformat(aa.PCM_FORMAT_S16_LE)
        self.data_in.setperiodsize(self.chunk)

        self.strip.clear_strip()
        self.first_run = True

    def shutdown(self) -> None:
        pass

    def update(self, current_step: int, current_cycle: int) -> bool:
        if not self.first_run:
            self.data_in.pause(0)  # Resume capture
        else:
            self.first_run = False

        l, data = self.data_in.read()  # Read data from device

        self.data_in.pause(1)  # Pause capture whilst RPi processes data

        if l > 0:
            try:
                matrix = calculate_levels(data, self.chunk, self.sample_rate)
                line = [int((1 << matrix[i]) - 1) for i in range(100)]
                for index, value in enumerate(line):
                    self.layout.set_pixel(index, *(wheel(value, threshold)))
            except Exception as e:
                if not hasattr(e, "message") or e.message != "not a whole number of frames":
                    raise e
                log.info("frame error")
                return False
            return True
        else:
            print(f"skipping l: {l}, data: {data}")
            return False
