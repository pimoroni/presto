# ICON [[(6.59, 7.4), (9.39, 4.6), (1.99, -2.8), (1.99, -12.0), (-2.01, -12.0), (-2.01, -1.2), (6.59, 7.4)], [(-0.01, 18.0), (-2.77, 17.82), (-5.22, 17.33), (-6.81, 16.84), (-9.0, 15.88), (-10.82, 14.83), (-12.37, 13.73), (-13.38, 12.88), (-14.8, 11.47), (-16.53, 9.28), (-17.71, 7.33), (-18.44, 5.84), (-18.93, 4.56), (-19.44, 2.82), (-19.69, 1.62), (-19.93, -0.24), (-19.98, -3.03), (-19.82, -4.82), (-19.36, -7.14), (-18.78, -8.99), (-18.18, -10.41), (-16.87, -12.77), (-15.61, -14.52), (-14.53, -15.77), (-13.03, -17.19), (-11.75, -18.19), (-9.49, -19.6), (-7.63, -20.48), (-5.31, -21.29), (-2.8, -21.81), (-1.17, -21.97), (0.56, -22.0), (2.17, -21.89), (4.17, -21.57), (5.78, -21.15), (6.98, -20.74), (8.54, -20.07), (10.61, -18.95), (12.5, -17.62), (14.56, -15.73), (15.71, -14.38), (16.82, -12.81), (18.11, -10.45), (18.75, -8.94), (19.3, -7.26), (19.84, -4.56), (19.98, -2.76), (19.98, -1.18), (19.8, 0.82), (19.39, 2.89), (18.67, 5.12), (17.97, 6.73), (16.56, 9.2), (15.45, 10.7), (13.58, 12.69), (11.88, 14.09), (10.45, 15.06), (9.16, 15.79), (6.7, 16.87), (5.01, 17.38), (2.25, 17.88), (0.04, 18.0)], [(-0.01, -2.0)], [(-0.01, 14.0), (1.87, 13.9), (3.1, 13.72), (4.92, 13.27), (6.57, 12.65), (7.85, 12.0), (9.95, 10.56), (11.26, 9.38), (12.07, 8.51), (13.65, 6.4), (14.66, 4.51), (15.18, 3.17), (15.75, 0.9), (15.93, -0.48), (15.99, -2.41), (15.75, -4.87), (15.46, -6.25), (14.87, -8.01), (14.31, -9.23), (13.28, -10.95), (12.42, -12.08), (11.05, -13.55), (9.91, -14.56), (8.05, -15.86), (6.45, -16.69), (4.54, -17.39), (3.36, -17.68), (1.71, -17.92), (0.44, -18.0), (-1.44, -17.94), (-2.97, -17.75), (-5.29, -17.16), (-6.71, -16.59), (-8.07, -15.88), (-10.05, -14.49), (-11.32, -13.34), (-12.48, -12.07), (-13.2, -11.12), (-14.1, -9.69), (-14.72, -8.44), (-15.33, -6.79), (-15.77, -4.91), (-15.98, -3.05), (-16.0, -1.85), (-15.9, -0.04), (-15.44, 2.39), (-14.95, 3.89), (-14.24, 5.45), (-13.24, 7.08), (-12.22, 8.41), (-11.39, 9.31), (-10.07, 10.49), (-8.57, 11.58), (-7.27, 12.32), (-5.83, 12.96), (-4.11, 13.51), (-1.72, 13.91), (-0.06, 14.0)]]
# NAME Analog Clock
# DESC Full resolution vector clock!
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
