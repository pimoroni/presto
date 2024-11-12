'''
A basic example to show how to set the LED backlights
'''

import plasma

# The total number of LEDs to set, the Presto has 7
NUM_LEDS = 7

# Plasma setup
bl = plasma.WS2812(7, 0, 0, 33)
bl.start()

# Cycle through each LED and set the colour to purple.
for i in range(NUM_LEDS):
    bl.set_rgb(i, 255, 0, 255)
