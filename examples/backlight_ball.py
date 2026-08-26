"""
Watch the backlighting react to a ball moving on screen
"""

import math
import time

from picovector import color

from presto import Presto

presto = Presto(ambient_light=True)
display = presto.display
WIDTH, HEIGHT = display.width, display.height

# Couple of colours for use later
BLUE = color.rgb(28, 181, 202)
WHITE = color.rgb(255, 255, 255)
RED = color.rgb(230, 60, 45)
ORANGE = color.rgb(245, 165, 4)
GREEN = color.rgb(9, 185, 120)
PINK = color.rgb(250, 125, 180)
PURPLE = color.rgb(118, 95, 210)
BLACK = color.rgb(0, 0, 0)

while True:

    display.pen = BLACK
    display.clear()

    # We'll use this for cycling through the rainbow
    t = time.ticks_ms() / 5000

    degrees = (t * 360) / 5
    rad = math.radians(degrees)

    display.pen = color.hsv(t * 360, 255, 255)
    display.circle(WIDTH // 2 + int(math.cos(rad) * 100), HEIGHT // 2 + int(math.sin(rad) * 100), 80)

    # Finally we update the screen with our changes :)
    presto.update()
