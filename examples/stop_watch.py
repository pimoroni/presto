# ICON timer
# NAME Stopwatch
# DESC A simple stopwatch timer

import datetime
import time

from picovector import color, font, image, shape
from presto import Presto
from touch import Button

presto = Presto()
display = presto.display
WIDTH, HEIGHT = display.width, display.height

CX = WIDTH // 2
CY = HEIGHT // 2

# Couple of colours for use later
BLACK = color.rgb(0, 0, 0)
hue = 0.09 * 360
background = color.hsv(hue, 204, 255)
foreground = color.hsv(hue, 128, 255)
text_colour = color.hsv(hue, 51, 255)

# We'll need this for the touch element of the screen
touch = presto.touch

display.font = font.load("Roboto-Medium.af")
display.antialias = image.X4


def text_in_button(text, bounds, size):
    # The new text anchor is the top of the em box, so buttons centre their
    # labels rather than working from a baseline offset.
    x, y, w, h = bounds
    display.text(text, x + (w - display.measure_text(text, size)[0]) / 2, y + (h - size) / 2, size)

# Touch buttons
start_button = Button(3, HEIGHT - 55, CX - 5, 49)
stop_button = Button((WIDTH - CX) + 1, HEIGHT - 55, CX - 5, 49)

start = shape.rounded_rectangle(*start_button.bounds, 10)
stop = shape.rounded_rectangle(*stop_button.bounds, 10)
outline = shape.rounded_rectangle(5, 20, WIDTH - 10, HEIGHT - 100, 10).stroke(2)

# We'll use a rect with rounded corners for the background.
background_rect = shape.rounded_rectangle(0, 0, WIDTH, HEIGHT, 10)


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

    display.pen = BLACK
    display.clear()

    display.pen = background
    display.shape(background_rect)

    display.pen = foreground
    display.shape(start)

    display.pen = foreground
    display.shape(stop)

    display.pen = text_colour
    display.shape(outline)

    if timer.elapsed and timer.running is False:
        text_in_button("Resume", start_button.bounds, 32)
    else:
        text_in_button("Start", start_button.bounds, 32)

    if timer.running:
        text_in_button("Stop", stop_button.bounds, 32)
    else:
        text_in_button("Reset", stop_button.bounds, 32)

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
    display.text(f"{time_string}", 10, 110 - 54, 54)

    presto.update()
