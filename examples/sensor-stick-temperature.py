# ICON monitoring
# NAME Temperature
# DESC Display data from your Multi Sensor Stick!

from presto import Presto
from breakout_bme280 import BreakoutBME280
from picovector import color, font, shape
import machine

# Setup for the Presto display
presto = Presto(ambient_light=True)
display = presto.display
WIDTH, HEIGHT = display.width, display.height

CX = WIDTH // 2
CY = HEIGHT // 2

# Colours
BLACK = color.rgb(0, 0, 0)
hue = 0.05 * 360
BACKGROUND = color.hsv(hue, 204, 255)  # We'll use this one for the background.
FOREGROUND = color.hsv(hue, 128, 255)  # Slightly lighter for foreground elements.
TEXT_COLOUR = color.hsv(hue, 51, 255)

display.font = font.load("Roboto-Medium.af")


def show_message(text):
    display.pen = BACKGROUND
    display.clear()
    display.pen = FOREGROUND
    display.text(f"{text}", 5, 10, 16)
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

        self.widget = shape.rounded_rectangle(self.x, self.y, self.w, self.h, self.r)

    def draw(self):

        display.pen = FOREGROUND
        display.shape(self.widget)

        if self.text:
            display.pen = TEXT_COLOUR
            w, h = display.measure_text(self.text, self.size)
            display.text(self.text, self.x + (self.w - w) / 2, self.y + (self.h - h) / 2, self.size)

        if self.title:
            display.pen = TEXT_COLOUR
            w, h = display.measure_text(self.title, 14)
            display.text(self.title, self.x + (self.w - w) / 2, self.y + 8, 14)

    def set_label(self, text):
        self.text = text

    def set_title(self, title):
        self.title = title


# We'll use a rect with rounded corners for the background.
background_rect = shape.rounded_rectangle(0, 0, WIDTH, HEIGHT, 10)

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
    display.pen = BLACK
    display.clear()
    display.pen = BACKGROUND
    display.shape(background_rect)

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
