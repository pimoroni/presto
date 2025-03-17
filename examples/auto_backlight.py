# ICON [[(-7.43, 6.46), (-4.6, 6.46), (-3.19, 2.39), (3.27, 2.39), (4.69, 6.46), (7.43, 6.46), (1.42, -9.47), (-1.42, -9.47), (-7.43, 6.46)], [(-2.39, 0.09), (-0.09, -6.55), (0.09, -6.55), (2.39, 0.09), (-2.39, 0.09)], [(-0.0, 19.38), (-5.93, 13.54), (-14.16, 13.54), (-14.16, 5.31), (-20.0, -0.62), (-14.16, -6.55), (-14.16, -14.78), (-5.93, -14.78), (-0.0, -20.62), (5.93, -14.78), (14.16, -14.78), (14.16, -6.55), (20.0, -0.62), (14.16, 5.31), (14.16, 13.54), (5.93, 13.54), (-0.0, 19.38)], [(-0.0, 14.42), (4.42, 10.0), (10.62, 10.0), (10.62, 3.81), (15.04, -0.62), (10.62, -5.04), (10.62, -11.24), (4.42, -11.24), (-0.0, -15.66), (-4.42, -11.24), (-10.62, -11.24), (-10.62, -5.04), (-15.04, -0.62), (-10.62, 3.81), (-10.62, 10.0), (-4.42, 10.0), (-0.0, 14.42)]]
# NAME Auto Backlight Demo
# DESC Using the Multi-Sensor Stick
from presto import Presto
from picovector import ANTIALIAS_BEST, PicoVector, Polygon, Transform
from machine import I2C
from breakout_ltr559 import BreakoutLTR559

# Setup for the Presto display
presto = Presto(ambient_light=False)
display = presto.display
WIDTH, HEIGHT = display.get_bounds()

ltr = BreakoutLTR559(I2C())
LUX_MAX = 200
LUX_MIN = 0

CX = WIDTH // 2
CY = HEIGHT // 2

# Colours
BLACK = display.create_pen(0, 0, 0)
hue = 0.8
BACKGROUND = display.create_pen_hsv(hue, 0.8, 1.0)  # We'll use this one for the background.
FOREGROUND = display.create_pen_hsv(hue, 0.5, 1.0)  # Slightly lighter for foreground elements.
TEXT_COLOUR = display.create_pen_hsv(hue, 0.2, 1.0)

# Pico Vector
vector = PicoVector(display)
vector.set_antialiasing(ANTIALIAS_BEST)
t = Transform()
vector.set_transform(t)

# We'll use a rect with rounded corners for the background.
background_rect = Polygon()
background_rect.rectangle(0, 0, WIDTH, HEIGHT)
background_rect.rectangle(0, 0, WIDTH, HEIGHT, (10, 10, 10, 10))

# Vector icon
AUTO_BACKLIGHT_PATHS = [[(-7.43, 6.46), (-4.6, 6.46), (-3.19, 2.39), (3.27, 2.39), (4.69, 6.46), (7.43, 6.46), (1.42, -9.47), (-1.42, -9.47), (-7.43, 6.46)], [(-2.39, 0.09), (-0.09, -6.55), (0.09, -6.55), (2.39, 0.09), (-2.39, 0.09)], [(-0.0, 19.38), (-5.93, 13.54), (-14.16, 13.54), (-14.16, 5.31), (-20.0, -0.62), (-14.16, -6.55), (-14.16, -14.78), (-5.93, -14.78), (-0.0, -20.62), (5.93, -14.78), (14.16, -14.78), (14.16, -6.55), (20.0, -0.62), (14.16, 5.31), (14.16, 13.54), (5.93, 13.54), (-0.0, 19.38)], [(-0.0, 14.42), (4.42, 10.0), (10.62, 10.0), (10.62, 3.81), (15.04, -0.62), (10.62, -5.04), (10.62, -11.24), (4.42, -11.24), (-0.0, -15.66), (-4.42, -11.24), (-10.62, -11.24), (-10.62, -5.04), (-15.04, -0.62), (-10.62, 3.81), (-10.62, 10.0), (-4.42, 10.0), (-0.0, 14.42)]]
auto_backlight_icon = Polygon()

for path in AUTO_BACKLIGHT_PATHS:
    auto_backlight_icon.path(*path)

# Store our last 5 lux readings.
# We've put some low values in to start things off.
lux_readings = [10, 10, 10, 10, 10]


def show_message(text):
    display.set_pen(BACKGROUND)
    display.clear()
    display.set_pen(FOREGROUND)
    display.text(f"{text}", 5, 10, WIDTH, 2)
    presto.update()


while True:

    # Clear the screen
    display.set_pen(BACKGROUND)
    display.clear()

    reading = ltr.get_reading()

    if reading is not None:
        # Lux reading, capped between 0 and 200.
        lux = max(min(round(reading[BreakoutLTR559.LUX]), LUX_MAX), LUX_MIN)
        lux_readings.append(lux)

        # We'll use the average from the last 5 readings to reduce flicker.
        if len(lux_readings) > 5:
            lux_readings.pop(0)

        lux_avg = round(sum(lux_readings) / len(lux_readings))

        # Lux normalised with the lower bounds capped at 0.1 to keep the screen on.
        lux_norm = max((lux_avg - LUX_MIN) / (LUX_MAX - LUX_MIN), 0.1)

        # Set the backlight!
        presto.set_backlight(lux_norm)

        display.set_pen(FOREGROUND)
        display.text(f"Brightness Level: {round(lux_norm * 10)}", 10, CY + 100, WIDTH, 1)

    else:
        display.set_pen(FOREGROUND)
        display.text("Unable to get reading.\nCheck your multi-sensor stick and try again", 7, CY + 90, WIDTH, 1)

    # Draw the min/max brightness icons
    display.set_pen(FOREGROUND)
    t.translate(CX, CY)
    t.scale(3.0, 3.0)
    vector.draw(auto_backlight_icon)
    t.reset()

    # Draw the rounded corners
    display.set_pen(BLACK)
    vector.draw(background_rect)

    presto.update()
