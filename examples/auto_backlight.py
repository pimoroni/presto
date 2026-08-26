# ICON [[(-7.43, 6.46), (-4.6, 6.46), (-3.19, 2.39), (3.27, 2.39), (4.69, 6.46), (7.43, 6.46), (1.42, -9.47), (-1.42, -9.47), (-7.43, 6.46)], [(-2.39, 0.09), (-0.09, -6.55), (0.09, -6.55), (2.39, 0.09), (-2.39, 0.09)], [(-0.0, 19.38), (-5.93, 13.54), (-14.16, 13.54), (-14.16, 5.31), (-20.0, -0.62), (-14.16, -6.55), (-14.16, -14.78), (-5.93, -14.78), (-0.0, -20.62), (5.93, -14.78), (14.16, -14.78), (14.16, -6.55), (20.0, -0.62), (14.16, 5.31), (14.16, 13.54), (5.93, 13.54), (-0.0, 19.38)], [(-0.0, 14.42), (4.42, 10.0), (10.62, 10.0), (10.62, 3.81), (15.04, -0.62), (10.62, -5.04), (10.62, -11.24), (4.42, -11.24), (-0.0, -15.66), (-4.42, -11.24), (-10.62, -11.24), (-10.62, -5.04), (-15.04, -0.62), (-10.62, 3.81), (-10.62, 10.0), (-4.42, 10.0), (-0.0, 14.42)]]
# NAME Auto Backlight Demo
# DESC Using the Multi-Sensor Stick
import math

from breakout_ltr559 import BreakoutLTR559
from machine import I2C
from picovector import color, font, mat3, shape, vec2
from presto import Presto

# Setup for the Presto display
presto = Presto(ambient_light=False)
display = presto.display
WIDTH, HEIGHT = display.width, display.height

ltr = BreakoutLTR559(I2C())
LUX_MAX = 200
LUX_MIN = 0

CX = WIDTH // 2
CY = HEIGHT // 2

# Colours
BLACK = color.rgb(0, 0, 0)
hue = 0.8 * 360
BACKGROUND = color.hsv(hue, 204, 255)  # We'll use this one for the background.
FOREGROUND = color.hsv(hue, 128, 255)  # Slightly lighter for foreground elements.
TEXT_COLOUR = color.hsv(hue, 51, 255)

display.font = font.load("Roboto-Medium.af")


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

# Vector icon
AUTO_BACKLIGHT_PATHS = [[(-7.43, 6.46), (-4.6, 6.46), (-3.19, 2.39), (3.27, 2.39), (4.69, 6.46), (7.43, 6.46), (1.42, -9.47), (-1.42, -9.47), (-7.43, 6.46)], [(-2.39, 0.09), (-0.09, -6.55), (0.09, -6.55), (2.39, 0.09), (-2.39, 0.09)], [(-0.0, 19.38), (-5.93, 13.54), (-14.16, 13.54), (-14.16, 5.31), (-20.0, -0.62), (-14.16, -6.55), (-14.16, -14.78), (-5.93, -14.78), (-0.0, -20.62), (5.93, -14.78), (14.16, -14.78), (14.16, -6.55), (20.0, -0.62), (14.16, 5.31), (14.16, 13.54), (5.93, 13.54), (-0.0, 19.38)], [(-0.0, 14.42), (4.42, 10.0), (10.62, 10.0), (10.62, 3.81), (15.04, -0.62), (10.62, -5.04), (10.62, -11.24), (4.42, -11.24), (-0.0, -15.66), (-4.42, -11.24), (-10.62, -11.24), (-10.62, -5.04), (-15.04, -0.62), (-10.62, 3.81), (-10.62, 10.0), (-4.42, 10.0), (-0.0, 14.42)]]
auto_backlight_icon = shape.custom(*[[vec2(x, y) for x, y in path] for path in AUTO_BACKLIGHT_PATHS])
auto_backlight_icon.transform = mat3().translate(CX, CY).scale(3.0, 3.0)

# Store our last 5 lux readings.
# We've put some low values in to start things off.
lux_readings = [10, 10, 10, 10, 10]


def show_message(text):
    display.pen = BACKGROUND
    display.clear()
    display.pen = FOREGROUND
    display.text(f"{text}", 5, 10, 16)
    presto.update()


while True:

    # Clear the screen
    display.pen = BACKGROUND
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

        display.pen = FOREGROUND
        display.text(f"Brightness Level: {round(lux_norm * 10)}", 10, CY + 100, 8)

    else:
        display.pen = FOREGROUND
        display.text("Unable to get reading.\nCheck your multi-sensor stick and try again", 7, CY + 90, 8)

    # Draw the min/max brightness icons
    display.pen = FOREGROUND
    display.shape(auto_backlight_icon)

    # Draw the rounded corners
    display.pen = BLACK
    display.shape(background_rect)

    presto.update()
