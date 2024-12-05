import presto

import time
import gc

from picovector import PicoVector, Polygon, Transform, ANTIALIAS_X16


presto = presto.Presto(full_res=True)

display = presto.display

vector = PicoVector(display)
t = Transform()
vector.set_transform(t)
vector.set_antialiasing(ANTIALIAS_X16)

RED = display.create_pen(200, 0, 0)
BLACK = display.create_pen(0, 0, 0)
DARKGREY = display.create_pen(100, 100, 100)
GREY = display.create_pen(200, 200, 200)
WHITE = display.create_pen(255, 255, 255)

"""
# Redefine colours for a Blue clock
RED = display.create_pen(200, 0, 0)
BLACK = display.create_pen(135, 159, 169)
GREY = display.create_pen(10, 40, 50)
WHITE = display.create_pen(14, 60, 76)
"""

WIDTH, HEIGHT = display.get_bounds()
MIDDLE = (int(WIDTH / 2), int(HEIGHT / 2))

hub = Polygon()
hub.circle(int(WIDTH / 2), int(HEIGHT / 2), 5)

face = Polygon()
face.circle(int(WIDTH / 2), int(HEIGHT / 2), int(HEIGHT / 2))

tick_mark = Polygon()
tick_mark.rectangle(int(WIDTH / 2) - 3, 10, 6, int(HEIGHT / 48))

hour_mark = Polygon()
hour_mark.rectangle(int(WIDTH / 2) - 5, 10, 10, int(HEIGHT / 10))

minute_hand_length = int(HEIGHT / 2) - int(HEIGHT / 24)
minute_hand = Polygon()
minute_hand.path((-5, -minute_hand_length), (-10, int(HEIGHT / 16)), (10, int(HEIGHT / 16)), (5, -minute_hand_length))

hour_hand_length = int(HEIGHT / 2) - int(HEIGHT / 8)
hour_hand = Polygon()
hour_hand.path((-5, -hour_hand_length), (-10, int(HEIGHT / 16)), (10, int(HEIGHT / 16)), (5, -hour_hand_length))

second_hand_length = int(HEIGHT / 2) - int(HEIGHT / 8)
second_hand = Polygon()
second_hand.path((-2, -second_hand_length), (-2, int(HEIGHT / 8)), (2, int(HEIGHT / 8)), (2, -second_hand_length))

print(time.localtime())

last_second = None

display.set_pen(BLACK)
display.clear()
display.set_pen(WHITE)
vector.draw(face)


while True:
    t_start = time.ticks_ms()
    year, month, day, hour, minute, second, _, _ = time.localtime()

    if last_second == second:
        time.sleep_ms(10)
        continue

    last_second = second

    t.reset()

    display.set_pen(WHITE)
    display.circle(int(WIDTH / 2), int(HEIGHT / 2), int(HEIGHT / 2) - 4)

    display.set_pen(GREY)

    for a in range(60):
        t.rotate(360 / 60.0 * a, MIDDLE)
        t.translate(0, 2)
        vector.draw(tick_mark)
        t.reset()

    for a in range(12):
        t.rotate(360 / 12.0 * a, MIDDLE)
        t.translate(0, 2)
        vector.draw(hour_mark)
        t.reset()

    display.set_pen(GREY)

    x, y = MIDDLE
    y += 5

    angle_minute = minute * 6
    angle_minute += second / 10.0
    t.rotate(angle_minute, MIDDLE)
    t.translate(x, y)
    vector.draw(minute_hand)
    t.reset()

    angle_hour = (hour % 12) * 30
    angle_hour += minute / 2
    t.rotate(angle_hour, MIDDLE)
    t.translate(x, y)
    vector.draw(hour_hand)
    t.reset()

    angle_second = second * 6
    t.rotate(angle_second, MIDDLE)
    t.translate(x, y)
    vector.draw(second_hand)
    t.reset()

    display.set_pen(BLACK)

    for a in range(60):
        t.rotate(360 / 60.0 * a, MIDDLE)
        vector.draw(tick_mark)
        t.reset()

    for a in range(12):
        t.rotate(360 / 12.0 * a, MIDDLE)
        vector.draw(hour_mark)
        t.reset()

    x, y = MIDDLE

    t.rotate(angle_minute, MIDDLE)
    t.translate(x, y)
    vector.draw(minute_hand)
    t.reset()

    t.rotate(angle_hour, MIDDLE)
    t.translate(x, y)
    vector.draw(hour_hand)
    t.reset()

    display.set_pen(RED)
    t.rotate(angle_second, MIDDLE)
    t.translate(x, y)
    vector.draw(second_hand)

    t.reset()
    vector.draw(hub)

    presto.update()
    gc.collect()

    t_end = time.ticks_ms()
    print(f"Took {t_end - t_start}ms")
