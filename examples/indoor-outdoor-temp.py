# ICON [[(-20.0, 16.67), (-20.0, 12.22), (-15.56, 7.78), (-15.56, 16.67), (-20.0, 16.67)], [(-11.11, 16.67), (-11.11, 3.33), (-6.67, -1.11), (-6.67, 16.67), (-11.11, 16.67)], [(-2.22, 16.67), (-2.22, -1.11), (2.22, 3.39), (2.22, 16.67), (-2.22, 16.67)], [(6.67, 16.67), (6.67, 3.39), (11.11, -1.06), (11.11, 16.67), (6.67, 16.67)], [(15.56, 16.67), (15.56, -5.56), (20.0, -10.0), (20.0, 16.67), (15.56, 16.67)], [(-20.0, 5.17), (-20.0, -1.11), (-4.44, -16.67), (4.44, -7.78), (20.0, -23.33), (20.0, -17.06), (4.44, -1.5), (-4.44, -10.39), (-20.0, 5.17)]]
# NAME Indoor/Outdoor
# DESC Display the indoor and outdoor temperature

import time

import machine
import urequests
from breakout_bme280 import BreakoutBME280
import math

from picovector import color, font, mat3, shape, vec2
from presto import Presto

# Set your latitude/longitude here (find yours by right clicking in Google Maps!)
LAT = 53.38609085276884
LNG = -1.4239983439328177

TIMEZONE = "auto"  # determines time zone from lat/long
URL = "http://api.open-meteo.com/v1/forecast?latitude=" + str(LAT) + "&longitude=" + str(LNG) + "&current_weather=true&timezone=" + TIMEZONE

# Setup for the Presto display
presto = Presto(ambient_light=True)
display = presto.display
WIDTH, HEIGHT = display.width, display.height
CX = WIDTH // 2
CY = HEIGHT // 2

# Colours
BLACK = color.rgb(0, 0, 0)
hue = 0.90 * 360
BACKGROUND = color.hsv(hue, 204, 255)  # We'll use this one for the background.
FOREGROUND = color.hsv(hue, 128, 255)  # Slightly lighter for foreground elements.
TEXT_COLOUR = color.hsv(hue, 76, 255)

display.font = font.load("Roboto-Medium.af")


def show_message(text):
    display.pen = BACKGROUND
    display.clear()
    display.pen = FOREGROUND
    display.text(f"{text}", 5, 10, 16)
    presto.update()


# Connect to the network and get time.
show_message("Connecting...")

try:
    presto.connect()
except ValueError as e:
    while True:
        show_message(e)
except ImportError as e:
    while True:
        show_message(e)


# Setup for the i2c and bme sensor
try:
    bme = BreakoutBME280(machine.I2C())
except RuntimeError:
    while True:
        show_message("No Multi-Sensor stick detected!\n\nConnect and try again.")




def rounded_contour(x, y, w, h, r, steps=6):
    points = []
    for cx, cy, start in ((x + w - r, y + h - r, 0), (x + r, y + h - r, 90),
                          (x + r, y + r, 180), (x + w - r, y + r, 270)):
        for step in range(steps + 1):
            a = math.radians(start + 90 * step / steps)
            points.append(vec2(cx + r * math.cos(a), cy + r * math.sin(a)))
    return points


# Everything outside a rounded rectangle, so the screen corners can be masked.
background_rect = shape.custom(
    [vec2(0, 0), vec2(WIDTH, 0), vec2(WIDTH, HEIGHT), vec2(0, HEIGHT)],
    rounded_contour(0, 0, WIDTH, HEIGHT, 10),
)

# The diagonal band the two readings sit either side of.
half_screen = shape.rectangle(-WIDTH // 2, -HEIGHT // 2, WIDTH * 2, HEIGHT)
half_screen.transform = mat3().translate(CX, CY).rotate(-45).translate(-CX, -CY)


# get the current outdoor temperature
def get_data():
    try:

        r = urequests.get(URL)
        # open the json data
        j = r.json()

        # parse relevant data from JSON
        current = j["current_weather"]
        temperature = current["temperature"]

        r.close()

        return temperature
    except OSError:
        return None


# Keep a record of the last time we updated.
# We only want to be requesting new data every 15 minutes.
last_updated = time.time()

# Get the first outdoor reading
out = get_data()
outdoor_temp_string = f"{out}C" if out else "N/A"

while True:

    # Clear screen and draw our background rectangle
    display.pen = BACKGROUND
    display.clear()

    # Get readings and format strings
    try:
        reading = bme.read()
    except RuntimeError:
        while True:
            show_message("Failed to get reading from BME280.\n\nCheck connection and reset :)")

    indoor_temp_string = f"{reading[0]:.1f}C"

    if time.time() - last_updated > 900:  # 15 minutes in seconds
        out = get_data()
        outdoor_temp_string = f"{out}C" if out else "N/A"
        last_updated = time.time()

    display.pen = FOREGROUND
    display.shape(half_screen)

    # Both readings used to share the band's 45 degree transform. Text takes no
    # transform here, so they are drawn upright either side of the diagonal.
    display.pen = BACKGROUND
    w, h = display.measure_text(indoor_temp_string, 92)
    display.text(indoor_temp_string, CX - w / 2, CY - h - 5, 92)

    display.pen = FOREGROUND
    w, h = display.measure_text(outdoor_temp_string, 92)
    display.text(outdoor_temp_string, CX - w / 2, CY + 5, 92)

    display.pen = BLACK
    display.shape(background_rect)

    # Update the screen so we can see our changes
    presto.update()
