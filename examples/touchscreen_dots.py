from picographics import PicoGraphics, DISPLAY_PRESTO
from presto import Presto
from ft6236 import FT6236
from random import randint
import time
from PrestoLight import Reactive

# Setup for the Presto display
presto = Presto()
display = PicoGraphics(DISPLAY_PRESTO, buffer=memoryview(presto))
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

COLOURS = [BLUE, RED, ORANGE, GREEN, PINK, PURPLE]

# We'll need this for the touch element of the screen
touch = FT6236()

backlight = Reactive()


class DOT(object):
    def __init__(self, x, y, size, colour):
        self.x = x
        self.y = y
        self.size = size
        self.colour = colour


# We'll store any dots in this array
dots = []


while True:

    # Poll the touch so we can see if anything changed since the last time
    touch.poll()

    # If the user is touching the screen we'll do the following
    if touch.state:
        # set the base size to 10 for a single tap
        s = 10
        # While the user is still touching the screen, we'll make the dot bigger!
        while touch.state:
            touch.poll()
            time.sleep(0.02)
            s += 0.5
        # Once the user stops touching the screen
        # We'll add a new dot with the x and y position of the touch,
        # size and a random colour!
        dots.append(DOT(touch.x, touch.y, round(s), COLOURS[randint(0, len(COLOURS) - 1)]))

    # Clear the screen
    display.set_pen(WHITE)
    display.clear()

    # Draw the dots in our array
    for dot in dots:
        display.set_pen(dot.colour)
        display.circle(dot.x, dot.y, dot.size)

    # Some text to let the user know what to do!
    display.set_pen(BLACK)
    display.text("Tap the screen!", 45, 110, WIDTH, 2)

    # Finally we update the screen with our changes :)
    backlight.update(display)
    presto.update(display)
