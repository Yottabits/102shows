import apa102
import time
import lightshows.spinthebottle
import lightshows.utilities

num_leds = 576
strip = apa102.APA102(num_leds, max_spi_speed_hz=4000000)
measurement = lightshows.utilities.MeasureFPS(strip)

fps = measurement.run()

print("Framerate: {}".format(fps))