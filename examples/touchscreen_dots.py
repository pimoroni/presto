import time
from random import randint

from picovector import color, font

from presto import Presto

# Setup for the Presto display
presto = Presto(ambient_light=True)
display = presto.display
WIDTH, HEIGHT = display.width, display.height

display.font = font.load("Roboto-Medium.af")

# Couple of colours for use later
BLUE = color.rgb(28, 181, 202)
WHITE = color.rgb(255, 255, 255)
RED = color.rgb(230, 60, 45)
ORANGE = color.rgb(245, 165, 4)
GREEN = color.rgb(9, 185, 120)
PINK = color.rgb(250, 125, 180)
PURPLE = color.rgb(118, 95, 210)
BLACK = color.rgb(0, 0, 0)

COLOURS = [BLUE, RED, ORANGE, GREEN, PINK, PURPLE]

# We'll need this for the touch element of the screen
touch = presto.touch


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
    display.pen = WHITE
    display.clear()

    # Draw the dots in our array
    for dot in dots:
        display.pen = dot.colour
        display.circle(dot.x, dot.y, dot.size)

    # Some text to let the user know what to do!
    display.pen = BLACK
    display.text("Tap the screen!", 45, 110, 16)

    # Finally we update the screen with our changes :)
    presto.update()
