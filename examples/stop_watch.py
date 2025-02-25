# ICON [[(-6.68, -21.11), (-6.68, -25.56), (6.65, -25.56), (6.65, -21.11), (-6.68, -21.11)], [(-2.24, 3.33), (2.21, 3.33), (2.21, -10.0), (-2.24, -10.0), (-2.24, 3.33)], [(-0.01, 21.11), (-1.81, 21.04), (-4.31, 20.66), (-6.31, 20.12), (-7.74, 19.58), (-9.01, 18.96), (-11.19, 17.66), (-13.09, 16.19), (-14.09, 15.26), (-15.63, 13.54), (-16.45, 12.45), (-17.69, 10.44), (-18.44, 8.94), (-19.27, 6.56), (-19.81, 4.04), (-19.98, 2.23), (-19.96, -0.37), (-19.74, -2.24), (-19.26, -4.37), (-18.84, -5.66), (-18.07, -7.44), (-17.05, -9.29), (-15.94, -10.92), (-14.5, -12.61), (-12.53, -14.43), (-11.26, -15.37), (-8.95, -16.74), (-7.69, -17.32), (-5.89, -17.99), (-4.53, -18.37), (-2.66, -18.71), (0.04, -18.89), (1.4, -18.84), (3.65, -18.56), (6.55, -17.8), (8.48, -17.01), (10.52, -15.93), (12.5, -14.59), (15.65, -17.67), (18.76, -14.56), (15.65, -11.44), (16.86, -9.69), (17.83, -7.96), (18.93, -5.34), (19.54, -3.11), (19.83, -1.43), (19.98, 0.78), (19.94, 2.46), (19.72, 4.37), (19.45, 5.71), (18.93, 7.47), (17.98, 9.76), (17.27, 11.08), (16.21, 12.74), (15.1, 14.15), (13.38, 15.9), (11.77, 17.21), (10.65, 17.99), (8.92, 18.98), (6.84, 19.9), (5.13, 20.45), (3.04, 20.88), (0.04, 21.11)], [(-0.01, 16.67), (2.64, 16.46), (4.57, 16.02), (6.73, 15.18), (8.41, 14.23), (9.35, 13.55), (11.26, 11.83), (12.39, 10.51), (13.25, 9.3), (14.08, 7.8), (14.79, 6.03), (15.25, 4.22), (15.54, 1.33), (15.39, -1.12), (14.81, -3.73), (14.22, -5.27), (13.69, -6.34), (12.58, -8.05), (11.48, -9.37), (10.3, -10.53), (8.13, -12.18), (6.44, -13.09), (4.91, -13.69), (2.83, -14.2), (1.19, -14.4), (-0.74, -14.43), (-2.3, -14.29), (-4.61, -13.79), (-7.19, -12.74), (-9.09, -11.55), (-11.13, -9.77), (-12.29, -8.46), (-13.7, -6.36), (-14.42, -4.87), (-15.1, -2.81), (-15.42, -1.16), (-15.57, 1.11), (-15.42, 3.35), (-14.88, 5.81), (-13.86, 8.28), (-12.89, 9.89), (-11.05, 12.07), (-9.71, 13.29), (-8.51, 14.17), (-6.09, 15.48), (-4.09, 16.16), (-2.86, 16.43), (-0.07, 16.67)], [(-0.01, 1.11)]]
# NAME Stopwatch
# DESC A simple stopwatch timer

import datetime
import time

from picovector import ANTIALIAS_BEST, PicoVector, Polygon, Transform
from presto import Presto
from touch import Button

presto = Presto()
display = presto.display
WIDTH, HEIGHT = display.get_bounds()

CX = WIDTH // 2
CY = HEIGHT // 2

# Couple of colours for use later
WHITE = display.create_pen(255, 255, 255)
RED = display.create_pen(230, 60, 45)
GREEN = display.create_pen(9, 185, 120)
BLACK = display.create_pen(0, 0, 0)

# We'll need this for the touch element of the screen
touch = presto.touch

# Pico Vector
vector = PicoVector(display)
vector.set_antialiasing(ANTIALIAS_BEST)
t = Transform()

vector.set_font("Roboto-Medium.af", 54)
vector.set_font_letter_spacing(100)
vector.set_font_word_spacing(100)
vector.set_transform(t)

# Touch buttons
start_button = Button(1, HEIGHT - 50, CX - 2, 49)
stop_button = Button(WIDTH - CX, HEIGHT - 50, CX - 2, 49)

start = Polygon()
start.rectangle(*start_button.bounds, (5, 5, 5, 5))

stop = Polygon()
stop.rectangle(*stop_button.bounds, (5, 5, 5, 5))

outline = Polygon()
outline.rectangle(5, 20, WIDTH - 10, HEIGHT - 100, (5, 5, 5, 5), 2)


class StopWatch(object):

    def __init__(self):
        self.start_time = 0
        self.elapsed = 0
        self.running = False

    def start(self):

        self.running = True
        if self.start_time:
            self.start_time = time.ticks_ms() - self.elapsed
        else:
            self.start_time = time.ticks_ms()

    def stop(self):

        self.running = False

    def reset(self):

        self.start_time = 0
        self.elapsed = 0

    def return_string(self):

        if self.running:
            self.elapsed = time.ticks_ms() - self.start_time

        dt = datetime.timedelta(hours=0, minutes=0, seconds=0, milliseconds=self.elapsed)

        return str(dt)[:10]


timer = StopWatch()

while True:

    display.set_pen(WHITE)
    display.clear()

    display.set_pen(GREEN)
    vector.draw(start)

    display.set_pen(RED)
    vector.draw(stop)

    display.set_pen(BLACK)
    vector.draw(outline)

    vector.set_font_size(32)
    if timer.elapsed and timer.running is False:
        vector.text("Resume", start_button.bounds[0] + 10, start_button.bounds[1] + 33)
    else:
        vector.text("Start", start_button.bounds[0] + 27, start_button.bounds[1] + 33)

    if timer.running:
        vector.text("Stop", stop_button.bounds[0] + 30, stop_button.bounds[1] + 33)
    else:
        vector.text("Reset", stop_button.bounds[0] + 25, stop_button.bounds[1] + 33)

    if start_button.is_pressed() and timer.running is False:
        timer.start()

    if stop_button.is_pressed():
        if timer.running:
            timer.stop()
            while stop_button.is_pressed():
                touch.poll()
        else:
            timer.reset()

    time_string = timer.return_string()
    vector.set_font_size(54)
    vector.text(f"{time_string}", 10, 110)

    presto.update()
