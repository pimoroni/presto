# ICON [[(-20.0, 16.67), (-20.0, 12.22), (-15.56, 7.78), (-15.56, 16.67), (-20.0, 16.67)], [(-11.11, 16.67), (-11.11, 3.33), (-6.67, -1.11), (-6.67, 16.67), (-11.11, 16.67)], [(-2.22, 16.67), (-2.22, -1.11), (2.22, 3.39), (2.22, 16.67), (-2.22, 16.67)], [(6.67, 16.67), (6.67, 3.39), (11.11, -1.06), (11.11, 16.67), (6.67, 16.67)], [(15.56, 16.67), (15.56, -5.56), (20.0, -10.0), (20.0, 16.67), (15.56, 16.67)], [(-20.0, 5.17), (-20.0, -1.11), (-4.44, -16.67), (4.44, -7.78), (20.0, -23.33), (20.0, -17.06), (4.44, -1.5), (-4.44, -10.39), (-20.0, 5.17)]]
# NAME Indoor/Outdoor
# DESC Display the indoor and outdoor temperature

from presto import Presto
from breakout_bme280 import BreakoutBME280
from picovector import ANTIALIAS_BEST, PicoVector, Polygon, Transform
import machine
import urequests
import time

# Set your latitude/longitude here (find yours by right clicking in Google Maps!)
LAT = 53.38609085276884
LNG = -1.4239983439328177

TIMEZONE = "auto"  # determines time zone from lat/long
URL = "http://api.open-meteo.com/v1/forecast?latitude=" + str(LAT) + "&longitude=" + str(LNG) + "&current_weather=true&timezone=" + TIMEZONE

# Setup for the Presto display
presto = Presto(ambient_light=True)
display = presto.display
WIDTH, HEIGHT = display.get_bounds()
CX = WIDTH // 2
CY = HEIGHT // 2

# Colours
BLACK = display.create_pen(0, 0, 0)
hue = 0.90
BACKGROUND = display.create_pen_hsv(hue, 0.8, 1.0)  # We'll use this one for the background.
FOREGROUND = display.create_pen_hsv(hue, 0.5, 1.0)  # Slightly lighter for foreground elements.
TEXT_COLOUR = display.create_pen_hsv(hue, 0.3, 1.0)

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


# We'll use a rect with rounded corners for the background.
background_rect = Polygon()
background_rect.rectangle(0, 0, WIDTH, HEIGHT)
background_rect.rectangle(0, 0, WIDTH, HEIGHT, (10, 10, 10, 10))


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
    display.set_pen(BACKGROUND)
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

    t.rotate(-45, (CX, CY))

    display.set_pen(FOREGROUND)
    half_screen = Polygon().rectangle(-WIDTH // 2, - HEIGHT // 2, WIDTH * 2, HEIGHT)
    vector.draw(half_screen)

    display.set_pen(BACKGROUND)
    vector.set_font_size(92)
    x, y, w, h = vector.measure_text(indoor_temp_string)
    tx = int(CX - (w // 2))
    ty = CY - 5
    vector.text(indoor_temp_string, tx, ty)

    display.set_pen(FOREGROUND)
    x, y, w, h = vector.measure_text(outdoor_temp_string)
    tx = int(CX - (w // 2))
    ty = CY + int(h) + 5
    vector.text(outdoor_temp_string, tx, ty)

    t.reset()

    display.set_pen(BLACK)
    vector.draw(background_rect)

    # Update the screen so we can see our changes
    presto.update()
