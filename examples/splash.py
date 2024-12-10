from picovector import ANTIALIAS_FAST, PicoVector, Polygon, Transform
from presto import Presto

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
vector.set_transform(t)

circle_inner_1 = Polygon()
circle_inner_2 = Polygon()
circle_inner_3 = Polygon()
circle_inner_4 = Polygon()
circle_inner_1.circle(0, 0, 110)
circle_inner_2.circle(WIDTH, 0, 110)
circle_inner_3.circle(WIDTH, HEIGHT, 110)
circle_inner_4.circle(0, HEIGHT, 110)

circle_outline_1 = Polygon()
circle_outline_2 = Polygon()
circle_outline_3 = Polygon()
circle_outline_4 = Polygon()
circle_outline_1.circle(0, 0, 112, 10)
circle_outline_2.circle(WIDTH, 0, 112, 5)
circle_outline_3.circle(WIDTH, HEIGHT, 112, 5)
circle_outline_4.circle(0, HEIGHT, 112, 5)


while True:
    display.set_pen(WHITE)
    display.clear()

    t.rotate(1, (CX, CY))

    display.set_pen(BLACK)
    vector.draw(circle_outline_4)
    vector.draw(circle_outline_3)
    vector.draw(circle_outline_2)
    vector.draw(circle_outline_1)

    display.set_pen(PINK)
    vector.draw(circle_inner_4)

    display.set_pen(ORANGE)
    vector.draw(circle_inner_3)

    display.set_pen(BLUE)
    vector.draw(circle_inner_2)

    display.set_pen(PURPLE)
    vector.draw(circle_inner_1)

    display.set_pen(BLACK)
    display.text("Hey, Presto!", CX - 55, CY - 10, WIDTH, 2)

    presto.update()
