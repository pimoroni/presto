# ICON [[(-0.01, 10.0), (2.24, 9.81), (3.75, 9.44), (4.75, 9.07), (6.15, 8.34), (7.06, 7.74), (8.39, 6.6), (9.5, 5.36), (10.75, 3.41), (11.53, 1.42), (11.85, -0.05), (11.98, -1.31), (11.96, -2.9), (11.84, -4.02), (11.32, -6.07), (10.89, -7.15), (9.93, -8.8), (8.7, -10.29), (7.47, -11.42), (6.58, -12.08), (4.99, -12.96), (4.04, -13.34), (2.41, -13.78), (0.04, -14.0), (-0.01, -2.0), (-8.51, 6.5), (-7.0, 7.73), (-5.84, 8.47), (-4.65, 9.08), (-3.52, 9.48), (-2.22, 9.79), (-0.06, 10.0)], [(-0.01, 18.0), (-2.77, 17.82), (-5.22, 17.33), (-6.81, 16.84), (-9.0, 15.88), (-10.82, 14.83), (-12.37, 13.73), (-13.38, 12.88), (-14.8, 11.47), (-16.53, 9.28), (-17.71, 7.33), (-18.44, 5.84), (-18.93, 4.56), (-19.44, 2.82), (-19.69, 1.62), (-19.93, -0.24), (-19.98, -3.03), (-19.82, -4.82), (-19.36, -7.14), (-18.78, -8.99), (-18.18, -10.41), (-16.87, -12.77), (-15.61, -14.52), (-14.53, -15.77), (-13.03, -17.19), (-11.75, -18.19), (-9.49, -19.6), (-7.63, -20.48), (-5.31, -21.29), (-2.8, -21.81), (-1.17, -21.97), (0.56, -22.0), (2.17, -21.89), (4.17, -21.57), (5.78, -21.15), (6.98, -20.74), (8.54, -20.07), (10.61, -18.95), (12.5, -17.62), (14.56, -15.73), (15.71, -14.38), (16.82, -12.81), (18.11, -10.45), (18.75, -8.94), (19.3, -7.26), (19.84, -4.56), (19.98, -2.76), (19.98, -1.18), (19.8, 0.82), (19.39, 2.89), (18.67, 5.12), (17.97, 6.73), (16.56, 9.2), (15.45, 10.7), (13.58, 12.69), (11.88, 14.09), (10.45, 15.06), (9.16, 15.79), (6.7, 16.87), (5.01, 17.38), (2.25, 17.88), (0.04, 18.0)], [(-0.01, 14.0), (1.92, 13.89), (4.04, 13.53), (6.12, 12.86), (7.5, 12.21), (8.55, 11.61), (9.86, 10.67), (11.86, 8.81), (13.1, 7.28), (14.15, 5.61), (14.75, 4.36), (15.29, 2.88), (15.79, 0.68), (15.96, -0.91), (15.96, -3.16), (15.72, -5.08), (15.17, -7.27), (14.67, -8.56), (13.98, -9.93), (12.87, -11.61), (11.38, -13.32), (9.85, -14.68), (8.89, -15.38), (7.49, -16.22), (5.15, -17.22), (3.7, -17.61), (1.72, -17.92), (0.3, -18.0), (-1.89, -17.9), (-4.1, -17.52), (-5.31, -17.17), (-7.19, -16.38), (-8.13, -15.88), (-9.61, -14.88), (-10.93, -13.76), (-12.29, -12.34), (-13.3, -11.02), (-14.5, -8.96), (-15.22, -7.16), (-15.61, -5.71), (-15.89, -4.07), (-15.99, -1.35), (-15.76, 0.93), (-15.4, 2.54), (-14.53, 4.89), (-13.63, 6.52), (-12.25, 8.38), (-10.86, 9.82), (-9.67, 10.82), (-8.31, 11.75), (-6.16, 12.84), (-5.16, 13.21), (-2.83, 13.77), (-1.35, 13.95), (-0.06, 14.0)], [(-0.01, -2.0)]]
# NAME Tomato Timer
# DESC A pomodoro timer for your Presto

import time
from picovector import ANTIALIAS_BEST, PicoVector, Polygon, Transform
from presto import Presto, Buzzer
from touch import Button

presto = Presto(ambient_light=True)
display = presto.display
WIDTH, HEIGHT = display.get_bounds()

# Centre points for the display
CX = WIDTH // 2
CY = HEIGHT // 2

# We'll need this for the touch element of the screen
touch = presto.touch

# Pico Vector
vector = PicoVector(display)
vector.set_antialiasing(ANTIALIAS_BEST)
t = Transform()

vector.set_font("Roboto-Medium.af", 96)
vector.set_font_letter_spacing(100)
vector.set_font_word_spacing(100)
vector.set_transform(t)

BLACK = display.create_pen(0, 0, 0)

# Setup the buzzer. The Presto piezo is on pin 43.
buzzer = Buzzer(43)


class Tomato(object):
    def __init__(self):

        self.hue = 0
        self.background = display.create_pen_hsv(self.hue, 0.8, 1.0)  # We'll use this one for the background.
        self.foreground = display.create_pen_hsv(self.hue, 0.5, 1.0)  # Slightly lighter for foreground elements.
        self.text_colour = display.create_pen_hsv(self.hue, 0.2, 1.0)

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
        self.background_rect = Polygon()
        self.background_rect.rectangle(0, 0, WIDTH, HEIGHT, (10, 10, 10, 10))

        self.foreground_rect = Polygon()
        self.foreground_rect.rectangle(10, 10, WIDTH - 20, HEIGHT - 120, (10, 10, 10, 10))

        # Touch button
        self.start_button = Button(CX // 2, HEIGHT - 75, CX, 50)
        x, y, w, h = self.start_button.bounds
        self.start = Polygon()
        self.start.rectangle(x, y, w, h, (10, 10, 10, 10))
        self.start_shadow = Polygon()
        self.start_shadow.rectangle(x + 3, y + 3, w, h, (10, 10, 10, 10))

    # Update the pens for the background, foreground and text elements based on the given hue.
    def update_pens(self, hue):
        self.hue = hue
        self.background = display.create_pen_hsv(self.hue, 0.8, 1.0)
        self.foreground = display.create_pen_hsv(self.hue, 0.5, 1.0)
        self.text_colour = display.create_pen_hsv(self.hue, 0.2, 1.0)

    def draw(self):

        # Clear the screen
        display.set_pen(BLACK)
        display.clear()

        # Draw the background rect with rounded corners
        display.set_pen(self.background)
        vector.draw(self.background_rect)

        # Draw the foreground rect, this is where we will show the time remaining.
        display.set_pen(self.foreground)
        vector.draw(self.foreground_rect)

        # Draw the button with drop shadow
        vector.draw(self.start_shadow)
        display.set_pen(self.text_colour)
        vector.draw(self.start)

        # Draw the button text, the text shown here depends on the current timer state
        vector.set_font_size(24)
        display.set_pen(self.foreground)

        if not self.running:
            if self.is_break_time:
                vector.text("Start Break", self.start_button.bounds[0] + 8, self.start_button.bounds[1] + 33)
            else:
                vector.text("Start Task", self.start_button.bounds[0] + 13, self.start_button.bounds[1] + 33)
        elif self.running and self.paused:
            vector.text("Resume", self.start_button.bounds[0] + 24, self.start_button.bounds[1] + 33)
        else:
            vector.text("Pause", self.start_button.bounds[0] + 32, self.start_button.bounds[1] + 33)

        display.set_pen(self.text_colour)
        text = self.return_string()
        vector.set_font_size(96)
        tx = int(CX - (205 // 2))
        ty = int(CY - (58 // 2)) + 10
        vector.text(text, tx, ty)

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
