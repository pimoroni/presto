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
        self.start_button = Button(CX - 56, HEIGHT - 75, CX - 2, 50)
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
                vector.text("Start Task", self.start_button.bounds[0] + 12, self.start_button.bounds[1] + 33)
        elif self.running and self.paused:
            vector.text("Resume", self.start_button.bounds[0] + 22, self.start_button.bounds[1] + 33)
        else:
            vector.text("Pause", self.start_button.bounds[0] + 32, self.start_button.bounds[1] + 33)

        display.set_pen(self.text_colour)
        text = self.return_string()
        vector.set_font_size(96)
        x, y, w, h = vector.measure_text(text, x=0, y=0, angle=None)
        tx = int(CX - (w // 2))
        ty = int(CY - (h // 2)) + 10
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
