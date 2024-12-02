'''
Watch the backlighting react to a ball moving on screen
'''

import math
import time

from presto import Presto

presto = Presto(reactive_backlight=True)
display = presto.display
WIDTH, HEIGHT = display.get_bounds()

# Couple of colours for use later
BLUE = display.create_pen(28, 181, 202)
WHITE = display.create_pen(255, 255, 255)
RED = display.create_pen(230, 60, 45)
ORANGE = display.create_pen(245, 165, 4)
GREEN = display.create_pen(9, 185, 120)
PINK = display.create_pen(250, 125, 180)
PURPLE = display.create_pen(118, 95, 210)
BLACK = display.create_pen(0, 0, 0)

# Set our initial pen colour
pen = display.create_pen_hsv(1.0, 1.0, 1.0)

while True:

    display.set_pen(BLACK)
    display.clear()

    # We'll use this for cycling through the rainbow
    t = time.ticks_ms() / 5000

    degrees = (t * 360) / 5
    rad = math.radians(degrees)

    display.reset_pen(pen)
    pen = display.create_pen_hsv(t, 1.0, 1.0)
    display.set_pen(pen)

    display.circle(WIDTH // 2 + int(math.cos(rad) * 100), HEIGHT // 2 + int(math.sin(rad) * 100), 80)

    # Finally we update the screen with our changes :)
    presto.update()
