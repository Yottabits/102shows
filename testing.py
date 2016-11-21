import apa102
import time
import lightshows.spinthebottle
import lightshows.utilities
import lightshows.strandtest

num_leds = 576
strip = apa102.APA102(num_leds, max_spi_speed_hz=4000000)
show = lightshows.spinthebottle.SpinTheBottle(strip)

show.highlight_sections = 80
show.run(5, fadeout=True)