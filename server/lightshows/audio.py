#!/usr/bin/env python3

# 8 bar Audio equaliser using MCP2307
 
import alsaaudio as aa
from struct import unpack
import numpy as np
import time
import math

def TurnOffLEDS ():
	#bus.write_byte_data(ADDR, BANKA, 0xFF)  #set all columns high
	#bus.write_byte_data(ADDR, BANKB, 0x00)  #set all rows low
	pass

def Set_Column(row, col):
	print("set column", row, col)
			
# Initialise matrix
TurnOffLEDS()

# Set up audio
sample_rate = 44100
no_channels = 2
chunk = 2048 # Use a multiple of 8
data_in = aa.PCM(aa.PCM_CAPTURE, aa.PCM_NORMAL, cardindex=0)
data_in.setchannels(no_channels)
data_in.setrate(sample_rate)
data_in.setformat(aa.PCM_FORMAT_S16_LE)
data_in.setperiodsize(chunk)

def calculate_levels(data, chunk,sample_rate):
    # Convert raw data to numpy array
    data = unpack("%dh"%(len(data)/2),data)
    data = np.array(data, dtype='h')
    # Apply FFT - real data so rfft used
    fourier=np.fft.rfft(data)
    # Remove last element in array to make it the same size as chunk
    fourier=np.delete(fourier,len(fourier)-1)
    # Find amplitude
    power = np.log10(np.abs(fourier))**2
    # Araange array into 8 rows for the 8 bars on LED matrix
    power = np.reshape(power, (1024, -1))
    matrix= np.int_(np.average(power,axis=1)/4)
    return matrix

def combine_color(red, green, blue):
    """Make one 3*8 byte color value."""

    return (red << 16) + (green << 8) + blue

def wheel(wheel_pos):
    """Get a color from a color wheel; Green -> Red -> Blue -> Green"""

    if wheel_pos > 255:
        wheel_pos = 255 # Safeguard
    if wheel_pos < 85:  # Red -> Green
        return combine_color(255 - wheel_pos * 3, wheel_pos * 3, 0)
    if wheel_pos < 170:  # Green -> Blue
        wheel_pos -= 85
        return combine_color(0, 255 - wheel_pos * 3, wheel_pos * 3)
    # Blue -> Magenta
    wheel_pos -= 170
    return combine_color(0, wheel_pos * 3, 255)

def brightness(value):
    if value < threshold:
        return 0
    if value < 4 * threshold:
        return 1
    return min(value - threshold, 100)

print("Processing.....")

NUM_LEDS = 300

import apa102

s = apa102.APA102(NUM_LEDS)

threshold = 15

def audio():

    while True:
        TurnOffLEDS()
        # Read data from device	
        l,data = data_in.read()

        data_in.pause(1) # Pause capture whilst RPi processes data
        if l:
            # catch frame error
            try:
                matrix=calculate_levels(data, chunk,sample_rate)
                line = [int((1<<matrix[i])-1) for i in range (0,100)]
                #print(" ".join([str(value) for value in line]))
                for index, value in enumerate(line):
                    rgb = wheel(value - threshold)
                    #brightness = int(max(1, math.log(value - threshold + 1))) if value >= threshold else 0
                    #brightness = value - threshold + 1 if value >= threshold else 0
                    bright = brightness(value)
                    s.set_pixel_rgb(index, rgb, bright) 
                    s.set_pixel_rgb(NUM_LEDS - index, rgb, bright) 
                s.show()
            except Exception as e:
                if e.message !="not a whole number of frames":
                    raise e
        time.sleep(0.001)
        data_in.pause(0) # Resume capture

def legend():

    page_count = 8
    total_count = 256

    page_size = total_count // page_count
    page = 0

    while True:
        page = (page + 1) % page_count

        for index in range(0, page_size):
            value = page * page_size + index
            rgb = wheel(value - threshold)
            bright = brightness(value)
            print(value, index, bright)
            s.set_pixel_rgb(index + index // 10, rgb, bright)
            s.set_pixel_rgb(NUM_LEDS - index - index // 10, rgb, bright)
        s.show()
        time.sleep(5)

if __name__ == '__main__':
    #legend()
    audio()
