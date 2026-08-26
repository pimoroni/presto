import math
import time

from picovector import color, font, mat3, shape
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

CX = WIDTH // 2
CY = HEIGHT // 2

offset = 20

circles = (
    shape.circle(0 - offset, 0 - offset, 110),
    shape.circle(WIDTH + offset, 0 - offset, 110),
    shape.circle(WIDTH + offset, HEIGHT + offset, 110),
    shape.circle(0 - offset, HEIGHT + offset, 110),
)
circle_inner_1, circle_inner_2, circle_inner_3, circle_inner_4 = circles

display.font = font.load("cherry-hq.af")

angle = 0

while True:

    tick = time.ticks_ms() / 100.0
    sin = math.sin(tick)
    text_y = (CY - 40) + int(sin * 4)

    display.pen = BLACK
    display.clear()

    # The rotation used to accumulate in a shared Transform; each shape carries
    # its own now, so the angle is tracked here and rebuilt every frame.
    angle += 1
    spin = mat3().translate(CX, CY).rotate(angle).translate(-CX, -CY)
    for circle in circles:
        circle.transform = spin

    display.pen = PINK
    display.shape(circle_inner_4)

    display.pen = ORANGE
    display.shape(circle_inner_3)

    display.pen = BLUE
    display.shape(circle_inner_2)

    display.pen = PURPLE
    display.shape(circle_inner_1)

    # Text is anchored at the top of the em box rather than the baseline, so
    # each line moves up by its own size.
    display.pen = WHITE
    display.text("Hey Presto!", CX - 64, text_y - 32, 32)
    display.text("Welcome to the Presto Beta! :)", CX - 95, CY - 20 - 18, 18)
    display.text("This unit is pre-loaded with MicroPython", CX - 105, CY + 10 - 15, 15)
    display.text("Plug in and play!", CX - 41, CY + 25 - 15, 15)

    presto.update()
