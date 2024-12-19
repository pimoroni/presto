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
