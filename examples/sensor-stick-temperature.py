# ICON [[(-20.0, 16.67), (-20.0, 12.22), (-15.56, 7.78), (-15.56, 16.67), (-20.0, 16.67)], [(-11.11, 16.67), (-11.11, 3.33), (-6.67, -1.11), (-6.67, 16.67), (-11.11, 16.67)], [(-2.22, 16.67), (-2.22, -1.11), (2.22, 3.39), (2.22, 16.67), (-2.22, 16.67)], [(6.67, 16.67), (6.67, 3.39), (11.11, -1.06), (11.11, 16.67), (6.67, 16.67)], [(15.56, 16.67), (15.56, -5.56), (20.0, -10.0), (20.0, 16.67), (15.56, 16.67)], [(-20.0, 5.17), (-20.0, -1.11), (-4.44, -16.67), (4.44, -7.78), (20.0, -23.33), (20.0, -17.06), (4.44, -1.5), (-4.44, -10.39), (-20.0, 5.17)]]
# NAME Temperature
# DESC Display data from your Multi Sensor Stick!

from presto import Presto
from breakout_bme280 import BreakoutBME280
from picovector import ANTIALIAS_BEST, PicoVector, Polygon, Transform
import machine

# Setup for the Presto display
presto = Presto(ambient_light=True)
display = presto.display
WIDTH, HEIGHT = display.get_bounds()

CX = WIDTH // 2
CY = HEIGHT // 2

# Colours
BLACK = display.create_pen(0, 0, 0)
hue = 0.05
BACKGROUND = display.create_pen_hsv(hue, 0.8, 1.0)  # We'll use this one for the background.
FOREGROUND = display.create_pen_hsv(hue, 0.5, 1.0)  # Slightly lighter for foreground elements.
TEXT_COLOUR = display.create_pen_hsv(hue, 0.2, 1.0)

# Pico Vector
vector = PicoVector(display)
vector.set_antialiasing(ANTIALIAS_BEST)
t = Transform()

vector.set_font("Roboto-Medium.af", 96)
vector.set_font_letter_spacing(100)
vector.set_font_word_spacing(100)
vector.set_transform(t)


def show_message(text):
    display.set_pen(BACKGROUND)
    display.clear()
    display.set_pen(FOREGROUND)
    display.text(f"{text}", 5, 10, WIDTH, 2)
    presto.update()


# Setup for the i2c and bme sensor
try:
    bme = BreakoutBME280(machine.I2C())
except RuntimeError:
    while True:
        show_message("No Multi-Sensor stick detected!\n\nConnect and try again.")


class Widget(object):
    def __init__(self, x, y, w, h, radius=10, text_size=42):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.r = radius
        self.text = None
        self.size = text_size
        self.title = None

        self.widget = Polygon()
        self.widget.rectangle(self.x, self.y, self.w, self.h, (self.r, self.r, self.r, self.r))

    def draw(self):

        display.set_pen(FOREGROUND)
        vector.draw(self.widget)

        if self.text:
            display.set_pen(TEXT_COLOUR)
            vector.set_font_size(self.size)
            x, y, w, h = vector.measure_text(self.text)
            tx = int((self.x + self.w // 2) - (w // 2))
            ty = int((self.y + self.h // 2) + (h // 2)) + 5
            vector.text(self.text, tx, ty)

        if self.title:
            display.set_pen(TEXT_COLOUR)
            vector.set_font_size(14)
            x, y, w, h = vector.measure_text(self.title)
            tx = int((self.x + self.w // 2) - (w // 2))
            ty = self.y + 15
            vector.text(self.title, tx, ty)

    def set_label(self, text):
        self.text = text

    def set_title(self, title):
        self.title = title


# We'll use a rect with rounded corners for the background.
background_rect = Polygon()
background_rect.rectangle(0, 0, WIDTH, HEIGHT, (10, 10, 10, 10))

widgets = [
    Widget(10, 7, WIDTH - 20, HEIGHT // 2 - 5, 10, 82),  # Temperature
    Widget(10, CY + 10, (WIDTH // 2) - 15, HEIGHT // 2 - 17, 10, 26),  # Pressure
    Widget(CX + 5, CY + 10, (WIDTH // 2) - 15, HEIGHT // 2 - 17, 10, 52)  # Humidity
]


widgets[0].set_title("Temperature")
widgets[1].set_title("Pressure")
widgets[2].set_title("Humidity")

while True:

    # Clear screen and draw our background rectangle
    display.set_pen(BLACK)
    display.clear()
    display.set_pen(BACKGROUND)
    vector.draw(background_rect)

    # Get readings and format strings
    try:
        reading = bme.read()
    except RuntimeError:
        while True:
            show_message("Failed to get reading from BME280.\n\nCheck connection and reset :)")

    temp_string = f"{reading[0]:.1f}C"
    pressure_string = f"{reading[1] // 100:.0f} hPa"
    humidity_string = f"{reading[2]:.0f}%"

    # Update the widget labels
    widgets[0].set_label(temp_string)
    widgets[1].set_label(pressure_string)
    widgets[2].set_label(humidity_string)

    # Draw all of our widgets to the display
    for w in widgets:
        w.draw()

    # Update the screen so we can see our changes
    presto.update()
