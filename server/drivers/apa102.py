import spidev
import logging as log
from multiprocessing import Array as multiprocessing_array
from lightshows.utilities import verifyparameters as verify

"""
Driver for APA102 LEDS (aka "DotStar").
(c) Martin Erzberger 2016, modified by Simon Leiner 2016
The original version by Martin Erzberger can be found at https://github.com/tinue/APA102_Pi


Public methods are:
 - set_pixel
 - set_pixel_bytes
 - get_pixel
 - set_global_brightness
 - show
 - clear_buffer
 - clear_strip
 - cleanup

Helper methods for color manipulation are:
 - combine_color
 - wheel


If the parameter multiprocessing is enabled in the constructor, the LED buffer is stored in a static array which is
available to all processes of apa102.py

The rest of the methods are used internally and should not be used by the user of the library.

Very brief overview of APA102: An APA102 LED is addressed with SPI. The bits are shifted in one by one,
starting with the least significant bit.

An LED usually just forwards everything that is sent to its data-in to data-out. While doing this, it
remembers its own color and keeps glowing with that color as long as there is power.

An LED can be switched to not forward the data, but instead use the data to change it's own color.
This is done by sending (at least) 32 bits of zeroes to data-in. The LED then accepts the next
correct 32 bit LED frame (with color information) as its new color setting.

After having received the 32 bit color frame, the LED changes color, and then resumes to just copying
data-in to data-out.

The really clever bit is this: While receiving the 32 bit LED frame, the LED sends zeroes on its
data-out line. Because a color frame is 32 bits, the LED sends 32 bits of zeroes to the next LED.
As we have seen above, this means that the next LED is now ready to accept a color frame and
update its color.

So that's really the entire protocol:
- Start by sending 32 bits of zeroes. This prepares LED 1 to update its color.
- Send color information one by one, starting with the color for LED 1, then LED 2 etc.
- Finish off by cycling the clock line a few times to get all data to the very last LED on the strip

The last step is necessary, because each LED delays forwarding the data a bit. Imagine ten people in
a row. When you yell the last color information, i.e. the one for person ten, to the first person in
the line, then you are not finished yet. Person one has to turn around and yell it to person 2, and
so on. So it takes ten additional "dummy" cycles until person ten knows the color. When you look closer,
you will see that not even person 9 knows the color yet. This information is still with person 2.
Essentially the driver sends additional zeroes to LED 1 as long as it takes for the last color frame
to make it down the line to the last LED.
"""

rgb_map = {'rgb': [3, 2, 1], 'rbg': [3, 1, 2], 'grb': [2, 3, 1], 'gbr': [2, 1, 3], 'brg': [1, 3, 2], 'bgr': [1, 2, 3]}


class APA102:
    def __init__(self, num_leds, global_brightness=31, order='rgb', max_clock_speed_hz=8000000, multiprocessing=False):
        self.numLEDs = num_leds
        order = order.lower()
        self.rgb = rgb_map.get(order, rgb_map['rgb'])
        # LED startframe is three "1" bits, followed by 5 brightness bits
        self.ledstart = None  # this is set by self.set_global_brightness()
        self.set_global_brightness(brightness=global_brightness, update_buffer=False)
        self.leds = [self.ledstart, 0, 0, 0] * self.numLEDs  # Pixel buffer
        self.multiprocessing = multiprocessing  # if multiprocessing enabled: convert array to a shared state
        if self.multiprocessing:
            self.leds = multiprocessing_array('i', self.leds)
        self.spi = spidev.SpiDev()  # Init the SPI device
        self.spi.open(0, 1)  # Open SPI port 0, slave device (CS)  1
        self.spi.max_speed_hz = max_clock_speed_hz  # should not be higher than 8000000

    """
    void clock_start_frame()
    This method clocks out a start frame, telling the receiving LED that it must update its own color now.
    """

    def clock_start_frame(self):
        self.spi.xfer2([0] * 4)  # Start frame, 32 zero bits

    """
    void clock_end_frame()
    As explained above, dummy data must be sent after the last real color information so that all of the data
    can reach its destination down the line.
    The delay is not as bad as with the human example above. It is only 1/2 bit per LED. This is because the
    SPI clock line needs to be inverted.

    Say a bit is ready on the SPI data line. The sender communicates this by toggling the clock line. The bit
    is read by the LED, and immediately forwarded to the output data line. When the clock goes down again
    on the input side, the LED will toggle the clock up on the output to tell the next LED that the bit is ready.

    After one LED the clock is inverted, and after two LEDs it is in sync again, but one cycle behind. Therefore,
    for every two LEDs, one bit of delay gets accumulated. For 300 LEDs, 150 additional bits must be fed to
    the input of LED one so that the data can reach the last LED.

    Ultimately, we need to send additional numLEDs/2 arbitrary data bits, in order to trigger numLEDs/2 additional clock
    changes. This driver sends zeroes, which has the benefit of getting LED one partially or fully ready for the next
    update to the strip. An optimized version of the driver could omit the "clock_start_frame" method if enough zeroes
    have been sent as part of "clock_end_frame".
    """

    def clock_end_frame(self):
        for _ in range((self.numLEDs + 15) // 16):  # Round up numLEDs/2 bits (or numLEDs/16 bytes)
            self.spi.xfer2([0x00])

    """
    void clear_buffer()
    Clears the entire buffer without displaying the result
    """

    def clear_buffer(self):
        for led in range(self.numLEDs):
            self.set_pixel(led, 0, 0, 0)

    """
    void clear_strip()
    Sets the color for the entire strip to black, and immediately shows the result.
    """

    def clear_strip(self):
        self.clear_buffer()
        self.show()

    """
    void get_pixel(ledNum)
    Returns the color of the pixel at ledNum as a tuple. Note that the data returned come from the pixel buffer,
    so it is possible that the output does not match the actual color of the LED if strip.show() was not
    called recently.
    """

    def get_pixel(self, led_num: int) -> tuple:
        if led_num < 0:
            raise IndexError("led_num cannot be < 0!")
        if led_num >= self.numLEDs:
            raise IndexError("led_num is out of bounds!")
        startIndex = 4 * led_num
        red = self.leds[startIndex + self.rgb[0]]
        green = self.leds[startIndex + self.rgb[1]]
        blue = self.leds[startIndex + self.rgb[2]]
        return red, green, blue

    """
    void set_global_brightness(brightness)
    Writes the global ledstart prefix that defines the brightness of all pixels.
    If update_buffer is false, the new prefixes are not written to the buffer.
    """

    def set_global_brightness(self, brightness: int, update_buffer: bool = True):
        # validate
        try:
            verify.integer(brightness, "brightness", minimum=0, maximum=31)
        except verify.InvalidParameters as error:
            log.warning(str(error))

        # set bitmask ledstart
        self.ledstart = (brightness & 0b00011111) | 0b11100000

        # write to buffer
        if update_buffer:
            for ledNum in range(self.numLEDs):
                self.leds[4 * ledNum] = self.ledstart

    """
    void set_pixel(ledNum, red, green, blue)
    Sets the color of one pixel in the LED stripe. The changed pixel is not shown yet on the Stripe, it is only
    written to the pixel buffer. Colors are passed individually.
    """

    def set_pixel(self, led_num, red, green, blue):
        if led_num < 0:
            return  # Pixel is invisible, so ignore
        if led_num >= self.numLEDs:
            return  # again, invsible

        for component in (red, green, blue):
            if type(component) is not int:
                log.debug("RGB value for pixel {num} is not an integer!".format(num=led_num))
                component = int(component)
            if component < 0 or component > 255:
                log.warning("RGB value for pixel {num} is out of bounds! (0-255)".format(num=led_num))
                return

        startIndex = 4 * led_num
        self.leds[startIndex] = self.ledstart
        self.leds[startIndex + self.rgb[0]] = red
        self.leds[startIndex + self.rgb[1]] = green
        self.leds[startIndex + self.rgb[2]] = blue

    """
    void set_pixel_bytes(ledNum,rgbColor)
    Sets the color of one pixel in the LED stripe. The changed pixel is not shown yet on the Stripe, it is only
    written to the pixel buffer. Colors are passed combined (3 bytes concatenated)
    """

    def set_pixel_bytes(self, led_num, rgb_color):
        self.set_pixel(led_num, (rgb_color & 0xFF0000) >> 16, (rgb_color & 0x00FF00) >> 8, rgb_color & 0x0000FF)

    """
    void rotate(positions)
    Treating the internal leds array as a circular buffer, rotate it by the specified number of positions.
    The number could be negative, which means rotating in the opposite direction.
    """

    def rotate(self, positions=1):
        cutoff = 4 * (positions % self.numLEDs)
        self.leds = self.leds[cutoff:] + self.leds[:cutoff]
        if self.multiprocessing:
            self.leds = multiprocessing_array('i', self.leds)

    """
    void show()
    Sends the content of the pixel buffer to the strip.
    Todo: More than 1024 LEDs requires more than one xfer operation.
    """

    def show(self):
        self.clock_start_frame()
        self.spi.xfer2(list(self.leds))  # SPI takes up to 4096 Integers. So we are fine for up to 1024 LEDs.
        self.clock_end_frame()

    """
    void cleanup()
    This method should be called at the end of a program in order to release the SPI device
    """

    def cleanup(self):
        self.spi.close()  # ... close SPI port

    """
    color combine_color(red,green,blue)
    Make one 3*8 byte color value
    """

    @staticmethod
    def combine_color(red, green, blue):
        return (red << 16) + (green << 8) + blue

    def wheel(self, wheel_pos):
        """
        color wheel(wheelPos)
        Get a color from a color wheel
        Green -> Red -> Blue -> Green
        """
        if wheel_pos > 254:
            wheel_pos = 254  # Safeguard
        if wheel_pos < 85:  # Green -> Red
            return self.combine_color(wheel_pos * 3, 255 - wheel_pos * 3, 0)
        elif wheel_pos < 170:  # Red -> Blue
            wheel_pos -= 85
            return self.combine_color(255 - wheel_pos * 3, 0, wheel_pos * 3)
        else:  # Blue -> Green
            wheel_pos -= 170
            return self.combine_color(0, wheel_pos * 3, 255 - wheel_pos * 3)
