# ICON travel
# NAME Attitude Indicator
# DESC A Demo for the Multi-Sensor Stick
import math

import machine
from lsm6ds3 import LSM6DS3, NORMAL_MODE_104HZ
from picovector import color, font, mat3, shape, vec2
from presto import Presto

# Setup for the Presto display
presto = Presto(ambient_light=True)
display = presto.display
WIDTH, HEIGHT = display.width, display.height
CX = WIDTH // 2
CY = HEIGHT // 2

# Colours
GRAY = color.rgb(42, 52, 57)
BLACK = color.rgb(0, 0, 0)
SKY_COLOUR = color.rgb(86, 159, 201)
GROUND_COLOUR = color.rgb(101, 81, 63)
WHITE = color.rgb(255, 255, 255)
RED = color.rgb(200, 0, 0)


x, y = 0, CY
x_prev = x
y_prev = y
alpha = 0.15

display.font = font.load("Roboto-Medium.af")


def circle_contour(cx, cy, r, steps=48):
    return [vec2(cx + r * math.cos(math.radians(a * 360 / steps)),
                 cy + r * math.sin(math.radians(a * 360 / steps))) for a in range(steps)]


def rect_contour(x, y, w, h):
    return [vec2(x, y), vec2(x + w, y), vec2(x + w, y + h), vec2(x, y + h)]


# Setup some of our vector shapes.
# Everything outside the instrument circle, so the corners can be masked off.
background_rect = shape.custom(rect_contour(0, 0, WIDTH, HEIGHT), circle_contour(CX, CY, 109))

instrument_outline = shape.circle(CX, CY, 110).stroke(8)

ground = shape.rectangle(0, HEIGHT // 2, WIDTH, HEIGHT)
horizon = shape.rectangle(0, HEIGHT // 2, WIDTH, 2)

pitch_contours = []
for line in range(1, 7):
    width = 20 if line % 2 else 60
    x = CX - width // 2
    pitch_contours.append(rect_contour(x, CY - line * 14, width, 1.5))
    pitch_contours.append(rect_contour(x, CY + line * 14, width, 1.5))
pitch_lines = shape.custom(*pitch_contours)

craft_centre = shape.circle(CX, CY - 1, 2)
craft_left = shape.rounded_rectangle(CX - 70, CY - 1, 50, 2, 2)
craft_right = shape.rounded_rectangle(CX + 20, CY - 1, 50, 2, 2)
craft_arc = shape.arc(CX, CY, 21, 23, -90, 90)


def show_message(text):
    display.pen = GRAY
    display.clear()
    display.pen = WHITE
    display.text(f"{text}", 5, 10, 16)
    presto.update()


try:
    i2c = machine.I2C()
    sensor = LSM6DS3(i2c, mode=NORMAL_MODE_104HZ)
except OSError:
    while True:
        show_message("No Multi-Sensor stick detected!\n\nConnect and try again.")

while True:
    # Clear screen with the SKY colour
    display.pen = SKY_COLOUR
    display.clear()

    try:
        # Get the raw readings from the sensor
        ax, ay, az, gx, gy, gz = sensor.get_readings()
    except OSError:
        while True:
            show_message("Multi-Sensor stick disconnected!\n\nReconnect and reset your Presto.")

    # Apply some smoothing to the X and Y
    # and cap the Y with min/max
    y_axis = max(-11000, min(int(alpha * ay + (1 - alpha) * y_prev), 11000))
    y_prev = y_axis

    x_axis = int(alpha * ax + (1 - alpha) * x_prev)
    x_prev = x_axis

    # Draw the ground. Later matrix calls apply first, so this reads the same
    # way round as the Transform calls it replaces.
    horizon_transform = (mat3()
                         .translate(CX, CY).rotate(-x_axis / 180).translate(-CX, -CY)
                         .translate(0, y_axis / 100))
    ground.transform = horizon_transform
    horizon.transform = horizon_transform
    pitch_lines.transform = horizon_transform

    display.pen = GROUND_COLOUR
    display.shape(ground)
    display.pen = WHITE
    display.shape(horizon)
    display.shape(pitch_lines)

    # Draw the aircraft
    display.pen = RED
    display.shape(craft_centre)
    display.shape(craft_left)
    display.shape(craft_right)
    display.shape(craft_arc)

    display.pen = GRAY
    display.shape(background_rect)
    display.pen = BLACK
    display.shape(instrument_outline)

    # Update the screen so we can see our changes
    presto.update()
