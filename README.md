# 102shows
_Raspberry Pi + APA102 + MQTT + 102shows = LED awesomeness!_

[![Code Climate](https://codeclimate.com/github/Yottabits/102shows/badges/gpa.svg)](https://codeclimate.com/github/Yottabits/102shows)

102shows is an [APA102](https://www.aliexpress.com/item//32322326979.html) (a.k.a [DotStar](https://www.adafruit.com/products/2240)) LED strip for the Raspberry Pi and also a collection of lightshows.
These lightshows can be controlled over your home network via MQTT.
And for those who do not prefer sending raw MQTT messages from the console, there is a ([Node-RED](https://nodered.org)-based) web interface.
Its responsive layout makes it ideal for both smart phones, tablets and computers.

## Features
- [non-linear brightness perception correction](https://ledshield.wordpress.com/2012/11/13/led-brightness-to-your-eye-gamma-correction-no/) (currently mistaken for _gamma correction_)
- High framerates even with long strips (over 140 refreshes per seconds at a strip length of 500 LEDs)
- sleek looking UI (based on [Node-RED](https://nodered.org))
- easily controllable via MQTT messages
- glitch obliteration
- easily configurable (see a [sample](https://gist.github.com/sleiner/dd967b20d555e78f1d3d67b7aa49324a))
- simple [API](https://github.com/Yottabits/102shows/wiki/Lightshow-modules) for writing your own lightshows
- pure Python 3

## Installation
see [INSTALLING.md](INSTALLING.md)

## Questions? 🤔
Write an e-mail to me: 102shows@leiner.me
