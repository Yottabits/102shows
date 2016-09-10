import apa102
import time
import lightshows.spinthebottle

num_leds = 576
strip = apa102.APA102(num_leds, max_spi_speed_hz=4000000)
show = lightshows.spinthebottle.SpinTheBottle(strip)
show.set_borders(0, 493)

show.run()