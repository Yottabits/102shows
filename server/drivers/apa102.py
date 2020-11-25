# Driver for APA102 LED strips (aka "DotStar")
# (c) 2015 Martin Erzberger, 2016-2017 Simon Leiner
# licensed under the GNU Public License, version 2

from multiprocessing import Array as SyncedArray
from typing import Callable, Tuple

from drivers import LEDStrip
from helpers.color import grayscale_correction

class APA102(LEDStrip):
    """\
    .. note::
        **A very brief overview of the APA102**


        An APA102 LED is addressed with SPI. The bits are shifted in one by one,
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

    Restrictions of this driver:
        - strips cannot have more than 1024 LEDs

    The constructor initializes the strip connection via SPI
    """

    def __init__(self, num_leds: int, max_clock_speed_hz: int = 4000000, max_global_brightness: float = 1.0):
        super().__init__(num_leds, max_clock_speed_hz, max_global_brightness)

        # check if we do not have too much LEDs in the strip
        if self.num_leds > 1024:
            raise Exception("The APA102 LED driver does not support strips of more than 1024 LEDs")

        # SPI connection
        self.spi_transmit, self.spi_close = self.init_spi()

        self.leds = [self.led_prefix(self._global_brightness), 0, 0, 0] * self.num_leds  # 4 bytes per LED
        self.synced_buffer = SyncedArray('i', self.leds)

        # Strip parameters
        self.max_refresh_time_sec = 25E-6 * self.num_leds  #: the maximum time the whole strip takes to refresh
        self.__sk9822_compatibility_mode = True  #: be compatible with SK9822 chips? see: https://goo.gl/ePlcaI

    def init_spi(self) -> Tuple[Callable, Callable]:
        try:
            import Adafruit_GPIO.SPI as SPI
            spi = SPI.SpiDev(0, 0, self.max_clock_speed_hz)
            return spi.write, spi.close
        except ImportError:
            import spidev
            spi = spidev.SpiDev()  # Init the SPI device
            spi.open(0, 1)  # Open SPI port 0, slave device (CS)  1
            spi.max_speed_hz = self.max_clock_speed_hz  # should not be higher than 8000000
            return spi.xfer2, spi.close

    def on_color_change(self, led_num, red: float, green: float, blue: float) -> None:
        """\
        Changes the message buffer after a pixel was changed in the global color buffer.
        Also, a grayscale correction is performed.
        To send the message buffer to the strip and show the changes, you must invoke :func:`show`

        :param led_num: index of the pixel to be set
        :param red: red component of the pixel (``0.0 - 255.0``)
        :param green: green component of the pixel (``0.0 - 255.0``)
        :param blue: blue component of the pixel (``0.0 - 255.0``)
        """
        # get correct duty cycle for desired lightness
        r_duty = grayscale_correction(red)
        g_duty = grayscale_correction(green)
        b_duty = grayscale_correction(blue)

        # for each led the spi message consists of 4 bytes:
        #   1. Prefix: as generated by led_prefix(brightness) - not set in this function
        #   2. Blue grayscale:  8 bits <=> 256 steps
        #   3. Green grayscale: 8 bits <=> 256 steps
        #   4. Red grayscale:   8 bits <=> 256 steps
        start_index = 4 * led_num  # 4 bytes per LED
        self.leds[start_index + 3] = r_duty
        self.leds[start_index + 2] = g_duty
        self.leds[start_index + 1] = b_duty

    def on_brightness_change(self, led_num: int) -> None:
        """
        For the LED at ``led_num``, regenerate the prefix and store the new prefix to the message buffer

        :param led_num: The index of the LED whose prefix should be regenerated
        """

        brightness = self._global_brightness * self.brightness_buffer[led_num]
        self.leds[4 * led_num] = self.led_prefix(brightness)

    @classmethod
    def led_prefix(cls, brightness: float) -> int:
        """
        generates the first byte of a 4-byte SPI message to a single APA102 module

        :param brightness: float from 0.0 (off) to 1.0 (full brightness)
        :return: the brightness byte
        """

        # map 0 - 1 brightness parameter to 0 - 31 integer as used in the APA102 prefix byte
        brightness_byte = grayscale_correction(brightness, max_in=1, max_out=31)

        # structure of the prefix byte: (1 1 1 b4 b3 b2 b1 b0)
        #    - the first three ones are fixed
        #    - (b4, b3, b2, b1, b0) is the binary brightness value (5 bit <=> 32 steps - from 0 to 31)
        prefix_byte = (brightness_byte & 0b00011111) | 0b11100000

        return prefix_byte

    def close(self) -> None:
        """Closes the SPI connection to the strip."""
        self.spi_close()

    @staticmethod
    def spi_start_frame() -> list:
        """
        To start a transmission, one must send 32 empty bits

        :return: The 32-bit start frame to be sent at the beginning of a transmission
        """
        return [0, 0, 0, 0]  # Start frame, 4 empty bytes <=> 32 zero bits

    def show(self) -> None:
        """sends the buffered color and brightness values to the strip"""
        self.spi_transmit(self.spi_start_frame())
        self.spi_transmit(self.leds)  # SPI takes up to 4096 Integers. So we are fine for up to 1024 LEDs.
        if self.__sk9822_compatibility_mode:
            self.spi_transmit(self.spi_start_frame())
        self.spi_transmit(self.spi_end_frame(self.num_leds))

    @staticmethod
    def spi_end_frame(num_leds) -> list:
        """\
        As explained above, dummy data must be sent after the last real color information so that all of the data
        can reach its destination down the line.
        The delay is not as bad as with the human example above. It is only 1/2 bit per LED. This is because the
        SPI clock line needs to be inverted.

        Say a bit is ready on the SPI data line. The sender communicates this by toggling the clock line. The bit
        is read by the LED, and immediately forwarded to the output data line. When the clock goes down again
        on the input side, the LED will toggle the clock up on the output to tell the next LED that the bit is ready.

        After one LED the clock is inverted, and after two LEDs it is in sync again, but one cycle behind. Therefore,
        for every two LEDs, one bit of delay gets accumulated. For 300 LEDs, 150 additional bits must be fed to
        the input of LED one so that the data can reach the last LED. In this implementation we add a few more zero
        bytes at the end, just to be sure.

        Ultimately, we need to send additional *num_leds/2* arbitrary data bits, in order to trigger *num_leds/2*
        additional clock changes. This driver sends zeroes, which has the benefit of getting LED one partially or
        fully ready for the next update to the strip. An optimized version of the driver could omit the
        :py:func:`spi_start_frame` method if enough zeroes have been sent as part of :py:func:`spi_end_frame`.

        :return: The end frame to be sent at the end of each SPI transmission
        """
        return [0x00] * ((num_leds + 15) // 16)  # Round up num_leds/2 bits (or num_leds/16 bytes)
