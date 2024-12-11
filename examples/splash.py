from picovector import ANTIALIAS_FAST, PicoVector, Polygon, Transform
from presto import Presto
import time
import math

presto = Presto(ambient_light=True)
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

CX = WIDTH // 2
CY = HEIGHT // 2

# Set our initial pen colour
pen = display.create_pen_hsv(1.0, 1.0, 1.0)

# Pico Vector
vector = PicoVector(display)
vector.set_antialiasing(ANTIALIAS_FAST)

t = Transform()
t2 = Transform()
vector.set_transform(t)

circle_inner_1 = Polygon()
circle_inner_2 = Polygon()
circle_inner_3 = Polygon()
circle_inner_4 = Polygon()

offset = 20

circle_inner_1.circle(0 - offset, 0 - offset, 110)
circle_inner_2.circle(WIDTH + offset, 0 - offset, 110)
circle_inner_3.circle(WIDTH + offset, HEIGHT + offset, 110)
circle_inner_4.circle(0 - offset, HEIGHT + offset, 110)

vector.set_font("cherry-hq.af", 54)
vector.set_font_letter_spacing(100)
vector.set_font_word_spacing(100)
vector.set_transform(t)

while True:

    tick = time.ticks_ms() / 100.0
    sin = math.sin(tick)
    text_y = (CY - 40) + int(sin * 4)

    display.set_pen(BLACK)
    display.clear()

    vector.set_transform(t)
    t.rotate(1, (CX, CY))

    display.set_pen(PINK)
    vector.draw(circle_inner_4)

    display.set_pen(ORANGE)
    vector.draw(circle_inner_3)

    display.set_pen(BLUE)
    vector.draw(circle_inner_2)

    display.set_pen(PURPLE)
    vector.draw(circle_inner_1)

    vector.set_transform(t2)
    display.set_pen(WHITE)
    vector.set_font_size(32)
    vector.text("Hey Presto!", CX - 64, text_y)

    vector.set_font_size(18)
    vector.text("Welcome to the Presto Beta! :)", CX - 95, CY - 20)

    vector.set_font_size(15)
    vector.text("This unit is pre-loaded with MicroPython", CX - 105, CY + 10)
    vector.text("Plug in and play!", CX - 41, CY + 25)

    presto.update()
