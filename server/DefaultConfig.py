# THIS IS THE DEFAULT CONFIGURATION FILE, DO NOT CHANGE THIS!
# SET YOUR PARAMETERS IN config.py


class Configuration:
    sys_name = None  # string
    shows = None  # dict: string <=> show module

    class MQTT:
        prefix = "led"
        general_path = "{prefix}/{sys_name}/show/{show_name}/{command}"
        notification_path = "{prefix}/{sys_name}/notification"
        username = None
        password = None

        class Broker:
            host = "localhost"
            port = 1883
            keepalive = 60  # in seconds

    class Strip:
        num_leds = None  # integer
        max_clock_speed_hz = 4000000  # 4 MHz is the maximum for "large" strips of more than 500 LEDs.
        initial_brightness = 16  # integer from 0 to 31
        max_brightness = 20  # maximum brightness
