# THIS IS THE DEFAULT CONFIGURATION FILE, DO NOT CHANGE THIS!
# SET YOUR PARAMETERS IN config.py


class Configuration:
    sys_name = None  # string
    shows = None  # dict: string <=> show module

    class mqtt:
        prefix = "led"
        general_path = "{prefix}/{sys_name}/show/{show_name}/{command}"
        notification_path = "{prefix}/{sys_name}/notification"

        class broker:
            host = "localhost"
            port = 1883
            keepalive = 60  # in seconds

    class strip:
        num_leds = None  # integer
        max_spi_speed_hz = 4000000  # maximum for "large" strips of more than 500 LEDs
        global_brightness = 31  # integer from 0 to 31
