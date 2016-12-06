"""
Fake APA102
(c) 2016 Simon Leiner, Martin Erzberger (original interface)

This driver can be called like the real apa102.py but and behaves like it with the exception that there is no LED strip
"""

import logging as log
from lightshows.utilities import verifyparameters as verify


rgb_map = {'rgb': [3, 2, 1], 'rbg': [3, 1, 2], 'grb': [2, 3, 1], 'gbr': [2, 1, 3], 'brg': [1, 3, 2], 'bgr': [1, 2, 3]}


class APA102:
    def __init__(self, numLEDs, globalBrightness=31, order='rgb', max_spi_speed_hz=8000000, multiprocessing=False):
        self.numLEDs = numLEDs
        order = order.lower()
        self.rgb = rgb_map.get(order, rgb_map['rgb'])
        # LED startframe is three "1" bits, followed by 5 brightness bits
        self.ledstart = (globalBrightness & 0b00011111) | 0b11100000  # Don't validate, just slash of extra bits
        self.leds = [self.ledstart, 0, 0, 0] * self.numLEDs  # Pixel buffer
        self.spi = Empty()  # Init the SPI device
        self.spi.max_speed_hz = max_spi_speed_hz  # Up the speed a bit, so that the LEDs are painted faster
        self.multiprocessing = multiprocessing

        log.info("initialized a strip with {num} LEDs".format(num=numLEDs))

    def getPixel(self, ledNum: int) -> tuple:
        if ledNum < 0:
            return None  # Pixel is invisible, so ignore
        if ledNum >= self.numLEDs:
            return None  # again, invsible
        startIndex = 4 * ledNum
        self.leds[startIndex] = self.ledstart
        red = self.leds[startIndex + self.rgb[0]]
        green = self.leds[startIndex + self.rgb[1]]
        blue = self.leds[startIndex + self.rgb[2]]
        return (red, green, blue)

    def setPixel(self, ledNum, red, green, blue):
        if ledNum < 0:
            return  # Pixel is invisible, so ignore
        if ledNum >= self.numLEDs:
            return  # again, invsible

        for component in (red, green, blue):
            if type(component) is not int:
                log.debug("RGB value for pixel {num} is not an integer!".format(num=ledNum))
                component = int(component)
            if component < 0 or component > 255:
                log.warning("RGB value for pixel {num} is out of bounds! (0-255)".format(num=ledNum))
                return

        startIndex = 4 * ledNum
        self.leds[startIndex] = self.ledstart
        self.leds[startIndex + self.rgb[0]] = red
        self.leds[startIndex + self.rgb[1]] = green
        self.leds[startIndex + self.rgb[2]] = blue
        log.debug("{ledNum} => ({r},{g},{b})".format(ledNum=ledNum, r=red, g=green, b=blue))

    def setPixelRGB(self, ledNum, rgbColor):
        self.setPixel(ledNum, (rgbColor & 0xFF0000) >> 16, (rgbColor & 0x00FF00) >> 8, rgbColor & 0x0000FF)

    def setGlobalBrightness(self, brightness: int, update_buffer: bool = True):
        # validate
        try:
            verify.integer(brightness, "brightness", minimum=0, maximum=31)
        except verify.InvalidParameters as error:
            log.warning(str(error))

        log.debug("Global strip brightness set to {}".format(brightness))

        if update_buffer:
            log.debug("LED buffer updated with new brightness")

    def show(self):
        log.debug("show!")

    def clearBuffer(self):
        for led in range(self.numLEDs):
            self.setPixel(led, 0, 0, 0)

    def clearStrip(self):
        self.clearBuffer()
        self.show()

    def cleanup(self):
        log.debug("cleanup!")

    def combineColor(self, red, green, blue):
        return (red << 16) + (green << 8) + blue

    def wheel(self, wheelPos):
        if wheelPos > 254: wheelPos = 254  # Safeguard
        if wheelPos < 85:  # Green -> Red
            return self.combineColor(wheelPos * 3, 255 - wheelPos * 3, 0)
        elif wheelPos < 170:  # Red -> Blue
            wheelPos -= 85
            return self.combineColor(255 - wheelPos * 3, 0, wheelPos * 3)
        else:  # Blue -> Green
            wheelPos -= 170
            return self.combineColor(0, wheelPos * 3, 255 - wheelPos * 3);
