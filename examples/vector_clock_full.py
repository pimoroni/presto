# ICON schedule
# NAME Analog Clock
# DESC Full resolution vector clock!
import presto

import time
import gc

from picovector import color, mat3, shape, vec2


presto = presto.Presto(full_res=True)

display = presto.display


RED = color.rgb(200, 0, 0)
BLACK = color.rgb(0, 0, 0)
DARKGREY = color.rgb(100, 100, 100)
GREY = color.rgb(200, 200, 200)
WHITE = color.rgb(255, 255, 255)

"""
# Redefine colours for a Blue clock
RED = color.rgb(200, 0, 0)
BLACK = color.rgb(135, 159, 169)
GREY = color.rgb(10, 40, 50)
WHITE = color.rgb(14, 60, 76)
"""

WIDTH, HEIGHT = display.width, display.height
MIDDLE = (int(WIDTH / 2), int(HEIGHT / 2))

MX, MY = MIDDLE


def draw_at(item, angle, dx=0, dy=0):
    # One transform per shape, so it is rebuilt for each draw. Later calls apply
    # first, matching the order the Transform calls used to be written in.
    item.transform = (mat3()
                      .translate(MX, MY).rotate(angle).translate(-MX, -MY)
                      .translate(dx, dy))
    display.shape(item)


hub = shape.circle(int(WIDTH / 2), int(HEIGHT / 2), 5)
face = shape.circle(int(WIDTH / 2), int(HEIGHT / 2), int(HEIGHT / 2))
tick_mark = shape.rectangle(int(WIDTH / 2) - 3, 10, 6, int(HEIGHT / 48))
hour_mark = shape.rectangle(int(WIDTH / 2) - 5, 10, 10, int(HEIGHT / 10))

minute_hand_length = int(HEIGHT / 2) - int(HEIGHT / 24)
minute_hand = shape.custom([vec2(-5, -minute_hand_length), vec2(-10, int(HEIGHT / 16)),
                            vec2(10, int(HEIGHT / 16)), vec2(5, -minute_hand_length)])

hour_hand_length = int(HEIGHT / 2) - int(HEIGHT / 8)
hour_hand = shape.custom([vec2(-5, -hour_hand_length), vec2(-10, int(HEIGHT / 16)),
                          vec2(10, int(HEIGHT / 16)), vec2(5, -hour_hand_length)])

second_hand_length = int(HEIGHT / 2) - int(HEIGHT / 8)
second_hand = shape.custom([vec2(-2, -second_hand_length), vec2(-2, int(HEIGHT / 8)),
                            vec2(2, int(HEIGHT / 8)), vec2(2, -second_hand_length)])

print(time.localtime())

last_second = None

display.pen = BLACK
display.clear()
display.pen = WHITE
display.shape(face)


while True:
    t_start = time.ticks_ms()
    year, month, day, hour, minute, second, _, _ = time.localtime()

    if last_second == second:
        time.sleep_ms(10)
        continue

    last_second = second

    display.pen = WHITE
    display.circle(int(WIDTH / 2), int(HEIGHT / 2), int(HEIGHT / 2) - 4)

    display.pen = GREY
    for a in range(60):
        draw_at(tick_mark, 360 / 60.0 * a, 0, 2)

    for a in range(12):
        draw_at(hour_mark, 360 / 12.0 * a, 0, 2)

    display.pen = GREY
    x, y = MIDDLE
    y += 5

    angle_minute = minute * 6
    angle_minute += second / 10.0
    draw_at(minute_hand, angle_minute, x, y)

    angle_hour = (hour % 12) * 30
    angle_hour += minute / 2
    draw_at(hour_hand, angle_hour, x, y)

    angle_second = second * 6
    draw_at(second_hand, angle_second, x, y)

    display.pen = BLACK
    for a in range(60):
        draw_at(tick_mark, 360 / 60.0 * a)

    for a in range(12):
        draw_at(hour_mark, 360 / 12.0 * a)

    x, y = MIDDLE

    draw_at(minute_hand, angle_minute, x, y)

    draw_at(hour_hand, angle_hour, x, y)

    display.pen = RED
    draw_at(second_hand, angle_second, x, y)

    draw_at(hub, 0)

    presto.update()
    gc.collect()

    t_end = time.ticks_ms()
    print(f"Took {t_end - t_start}ms")
