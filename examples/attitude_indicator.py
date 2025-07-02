# ICON [[(-4.5, 16.82), (-9.92, 6.75), (-19.99, 1.33), (-16.1, -2.5), (-8.17, -1.13), (-2.58, -6.71), (-19.93, -14.1), (-15.33, -18.8), (5.73, -15.08), (12.52, -21.87), (13.6, -22.66), (15.25, -23.11), (16.46, -23.05), (17.73, -22.63), (19.14, -21.42), (19.62, -20.63), (19.97, -19.45), (19.99, -18.25), (19.79, -17.33), (19.32, -16.37), (18.79, -15.72), (11.92, -8.84), (15.64, 12.17), (10.99, 16.82), (3.54, -0.53), (-2.04, 5.05), (-0.61, 12.93), (-4.5, 16.82)]]
# NAME Attitude Indicator
# DESC A Demo for the Multi-Sensor Stick
from presto import Presto
from picovector import ANTIALIAS_FAST, PicoVector, Polygon, Transform
import machine
from lsm6ds3 import LSM6DS3, NORMAL_MODE_104HZ

# Setup for the Presto display
presto = Presto(ambient_light=True)
display = presto.display
WIDTH, HEIGHT = display.get_bounds()
CX = WIDTH // 2
CY = HEIGHT // 2

# Colours
GRAY = display.create_pen(42, 52, 57)
BLACK = display.create_pen(0, 0, 0)
SKY_COLOUR = display.create_pen(86, 159, 201)
GROUND_COLOUR = display.create_pen(101, 81, 63)
WHITE = display.create_pen(255, 255, 255)
RED = display.create_pen(200, 0, 0)

# Pico Vector
vector = PicoVector(display)
vector.set_antialiasing(ANTIALIAS_FAST)
t = Transform()
normal = Transform()
vector.set_transform(t)

x, y = 0, CY
x_prev = x
y_prev = y
alpha = 0.15

# Setup some of our vector shapes
background_rect = Polygon()
background_rect.rectangle(0, 0, WIDTH, HEIGHT)
background_rect.circle(CX, CY, 109)

instrument_outline = Polygon().circle(CX, CY, 110, stroke=8)

ground = Polygon().rectangle(0, HEIGHT // 2, WIDTH, HEIGHT)
horizon = Polygon().rectangle(0, HEIGHT // 2, WIDTH, 2)
pitch_lines = Polygon()

for line in range(1, 7):
    if line % 2:
        pitch_lines.rectangle(CX - 10, CY - line * 14, 20, 1.5)
        pitch_lines.rectangle(CX - 10, CY + line * 14, 20, 1.5)
    else:
        pitch_lines.rectangle(CX - 30, CY - line * 14, 60, 1.5)
        pitch_lines.rectangle(CX - 30, CY + line * 14, 60, 1.5)

craft_centre = Polygon().circle(CX, CY - 1, 2)
craft_left = Polygon().rectangle(CX - 70, CY - 1, 50, 2, (2, 2, 2, 2))
craft_right = Polygon().rectangle(CX + 20, CY - 1, 50, 2, (2, 2, 2, 2))
craft_arc = Polygon().arc(CX, CY, 22, -90, 90, stroke=2)


def show_message(text):
    display.set_pen(GRAY)
    display.clear()
    display.set_pen(WHITE)
    display.text(f"{text}", 5, 10, WIDTH, 2)
    presto.update()


try:
    i2c = machine.I2C()
    sensor = LSM6DS3(i2c, mode=NORMAL_MODE_104HZ)
except OSError:
    while True:
        show_message("No Multi-Sensor stick detected!\n\nConnect and try again.")

while True:
    # Clear screen with the SKY colour
    display.set_pen(SKY_COLOUR)
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

    # Draw the ground
    t.reset()
    t.rotate(-x_axis / 180, (WIDTH // 2, HEIGHT // 2))
    t.translate(0, y_axis / 100)

    vector.set_transform(t)
    display.set_pen(GROUND_COLOUR)
    vector.draw(ground)
    display.set_pen(WHITE)
    vector.draw(horizon)
    vector.draw(pitch_lines)
    vector.set_transform(normal)

    # Draw the aircraft
    display.set_pen(RED)
    vector.draw(craft_centre)
    vector.draw(craft_left)
    vector.draw(craft_right)
    vector.draw(craft_arc)

    display.set_pen(GRAY)
    vector.draw(background_rect)
    display.set_pen(BLACK)
    vector.draw(instrument_outline)

    # Update the screen so we can see our changes
    presto.update()
