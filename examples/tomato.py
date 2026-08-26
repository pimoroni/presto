# ICON description
# NAME Tomato Timer
# DESC A pomodoro timer for your Presto

import time

from picovector import color, font, shape
from presto import Buzzer, Presto
from touch import Button

presto = Presto(ambient_light=True)
display = presto.display
WIDTH, HEIGHT = display.width, display.height

# Centre points for the display
CX = WIDTH // 2
CY = HEIGHT // 2

# We'll need this for the touch element of the screen
touch = presto.touch

display.font = font.load("Roboto-Medium.af")


def text_in_button(text, bounds, size):
    # The new text anchor is the top of the em box, so buttons centre their
    # labels rather than working from a baseline offset.
    x, y, w, h = bounds
    display.text(text, x + (w - display.measure_text(text, size)[0]) / 2, y + (h - size) / 2, size)

BLACK = color.rgb(0, 0, 0)

# Setup the buzzer. The Presto piezo is on pin 43.
buzzer = Buzzer(43)


class Tomato(object):
    def __init__(self):

        self.hue = 0
        self.background = color.hsv(self.hue * 360, 204, 255)  # We'll use this one for the background.
        self.foreground = color.hsv(self.hue * 360, 128, 255)  # Slightly lighter for foreground elements.
        self.text_colour = color.hsv(self.hue * 360, 51, 255)

        # Time constants.
        # Feel free to change these to ones that work better for you.
        self.TASK = 25 * 60
        self.SHORT = 10 * 60
        self.LONG = 30 * 60

        # How long the completion alert should be played (seconds)
        self.alert_duration = 2
        self.alert_start_time = 0

        self.is_break_time = False
        self.start_time = 0
        self.tasks_complete = 0
        self.running = False
        self.paused = False
        self.time_elapsed = 0
        self.current_timer = self.TASK

        # We'll use a rect with rounded corners for the background.
        self.background_rect = shape.rounded_rectangle(0, 0, WIDTH, HEIGHT, 10)
        self.foreground_rect = shape.rounded_rectangle(10, 10, WIDTH - 20, HEIGHT - 120, 10)

        # Touch button
        self.start_button = Button(CX // 2, HEIGHT - 75, CX, 50)
        x, y, w, h = self.start_button.bounds
        self.start = shape.rounded_rectangle(x, y, w, h, 10)
        self.start_shadow = shape.rounded_rectangle(x + 3, y + 3, w, h, 10)

    # Update the pens for the background, foreground and text elements based on the given hue.
    def update_pens(self, hue):
        self.hue = hue
        self.background = color.hsv(self.hue * 360, 204, 255)
        self.foreground = color.hsv(self.hue * 360, 128, 255)
        self.text_colour = color.hsv(self.hue * 360, 51, 255)

    def draw(self):

        # Clear the screen
        display.pen = BLACK
        display.clear()

        # Draw the background rect with rounded corners
        display.pen = self.background
        display.shape(self.background_rect)

        # Draw the foreground rect, this is where we will show the time remaining.
        display.pen = self.foreground
        display.shape(self.foreground_rect)

        # Draw the button with drop shadow
        display.shape(self.start_shadow)
        display.pen = self.text_colour
        display.shape(self.start)

        # Draw the button text, the text shown here depends on the current timer state
        display.pen = self.foreground
        if not self.running:
            if self.is_break_time:
                text_in_button("Start Break", self.start_button.bounds, 24)
            else:
                text_in_button("Start Task", self.start_button.bounds, 24)
        elif self.running and self.paused:
            text_in_button("Resume", self.start_button.bounds, 24)
        else:
            text_in_button("Pause", self.start_button.bounds, 24)

        display.pen = self.text_colour
        text = self.return_string()
        tw, th = display.measure_text(text, 96)
        display.text(text, CX - tw / 2, CY - th / 2, 96)

    def run(self):
        self.stop_buzzer()

        if self.is_break_time:
            if self.tasks_complete < 4:
                self.current_timer = self.SHORT
                self.update_pens(0.55)
            else:
                self.current_timer = self.LONG
                self.update_pens(0.55)
        else:
            self.current_timer = self.TASK
            self.update_pens(0.0)

        if not self.running:
            self.reset()
            self.running = True
            self.start_time = time.time()
        elif self.running and not self.paused:
            self.paused = True
        elif self.running and self.paused:
            self.paused = False
            self.start_time = time.time() - self.time_elapsed

    def reset(self):
        self.start_time = 0
        self.time_elapsed = 0

    def start_buzzer(self):
        self.alert_start_time = time.time()
        buzzer.set_tone(150)

    def stop_buzzer(self):
        buzzer.set_tone(-1)
        self.alert_start_time = 0

    def update(self):

        if time.time() - self.alert_start_time >= self.alert_duration:
            self.stop_buzzer()

        if self.running and not self.paused:

            self.time_elapsed = time.time() - self.start_time

            if self.time_elapsed >= self.current_timer:
                self.running = False
                self.start_buzzer()
                if not self.is_break_time:
                    if self.tasks_complete < 4:
                        self.tasks_complete += 1
                    else:
                        self.tasks_complete = 0
                self.is_break_time = not self.is_break_time

    # Return the remaining time formatted in a string for displaying with vector text.
    def return_string(self):
        minutes, seconds = divmod(self.current_timer - self.time_elapsed, 60)
        return f"{minutes:02d}:{seconds:02d}"

    def pressed(self):
        return self.start_button.is_pressed()


# Create an instance of our timer object
timer = Tomato()

while True:

    if timer.pressed():
        while timer.pressed():
            touch.poll()
        timer.run()

    timer.draw()
    timer.update()
    presto.update()
