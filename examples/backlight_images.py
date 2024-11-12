'''
A demo that flips between 2 images and changes the backlighting
'''

from picographics import PicoGraphics, DISPLAY_PRESTO
from presto import Presto
import time
import jpegdec
from PrestoLight import Reactive

# Setup for the Presto display
portal = Presto()
display = PicoGraphics(DISPLAY_PRESTO, buffer=memoryview(portal))
WIDTH, HEIGHT = display.get_bounds()

# JPEG
j = jpegdec.JPEG(display)

backlight = Reactive()

# Couple of colours for use later
BLUE = display.create_pen(28, 181, 202)
WHITE = display.create_pen(255, 255, 255)
RED = display.create_pen(230, 60, 45)
ORANGE = display.create_pen(245, 165, 4)
GREEN = display.create_pen(9, 185, 120)
PINK = display.create_pen(250, 125, 180)
PURPLE = display.create_pen(118, 95, 210)
BLACK = display.create_pen(0, 0, 0)

flip = True

while True:

    if flip:
        j.open_file("colour_pencils.jpg")
        j.decode(0, 0, jpegdec.JPEG_SCALE_FULL, dither=True)
        flip = not flip
    else:
        j.open_file("car.jpg")
        j.decode(0, 0, jpegdec.JPEG_SCALE_FULL, dither=True)
        flip = not flip

    backlight.update(display)

    ''''
    display.set_pen(WHITE)

    MAX = const(160)
    MID = const(80)
    MIN = const(0)
    SIZE = 79

    display.rectangle(MAX, MAX, SIZE, SIZE)
    display.rectangle(MAX, MID, SIZE, SIZE)
    display.rectangle(MAX, MIN, SIZE, SIZE)
    display.rectangle(MID, MIN, SIZE, SIZE)
    display.rectangle(MIN, MIN, SIZE, SIZE)
    display.rectangle(MIN, MID, SIZE, SIZE)
    display.rectangle(MIN, MAX, SIZE, SIZE)

    display.set_pen(BLACK)

    for x in range(0, WIDTH, 5):
        for y in range(0, HEIGHT, 14):
            display.pixel(x, y)
    '''

    # Finally we update the screen with our changes :)
    portal.update(display)
    time.sleep(1)
