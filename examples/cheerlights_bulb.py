# ICON [[(0.0, 24.0), (-1.93, 23.66), (-3.75, 22.51), (-4.42, 21.69), (-5.11, 20.23), (-5.33, 18.73), (5.33, 18.67), (4.91, 20.77), (4.06, 22.12), (3.34, 22.82), (2.1, 23.58), (0.07, 24.0)], [(-10.67, 16.0), (-10.67, 10.67), (10.67, 10.67), (10.67, 16.0), (-10.67, 16.0)], [(-10.0, 8.0), (-12.44, 6.31), (-15.06, 3.8), (-16.01, 2.64), (-17.3, 0.72), (-18.55, -1.82), (-19.23, -3.78), (-19.81, -6.5), (-20.0, -9.27), (-19.89, -11.51), (-19.37, -14.52), (-18.51, -17.1), (-17.78, -18.66), (-16.29, -21.03), (-14.06, -23.61), (-12.39, -25.08), (-10.53, -26.4), (-8.18, -27.66), (-6.51, -28.31), (-4.11, -28.95), (-2.22, -29.22), (0.14, -29.33), (1.92, -29.25), (4.76, -28.8), (6.5, -28.31), (8.89, -27.32), (10.67, -26.3), (12.4, -25.04), (13.76, -23.84), (15.55, -21.92), (17.31, -19.45), (18.36, -17.41), (18.97, -15.86), (19.6, -13.52), (19.94, -11.05), (20.0, -9.2), (19.79, -6.43), (19.48, -4.78), (18.72, -2.32), (17.93, -0.54), (16.56, 1.79), (15.4, 3.37), (13.36, 5.52), (11.65, 6.91), (10.06, 7.97), (-10.0, 8.0)], [(-8.4, 2.67), (8.4, 2.67), (10.02, 1.35), (10.94, 0.41), (12.14, -1.14), (13.64, -3.98), (14.23, -5.77), (14.51, -7.17), (14.67, -9.27), (14.51, -11.57), (14.19, -13.19), (13.44, -15.35), (12.77, -16.67), (11.72, -18.23), (10.81, -19.31), (9.38, -20.66), (7.64, -21.92), (6.27, -22.66), (4.72, -23.28), (2.72, -23.77), (0.53, -23.99), (-1.72, -23.91), (-3.36, -23.64), (-5.45, -23.01), (-7.77, -21.85), (-9.2, -20.82), (-10.81, -19.3), (-11.81, -18.11), (-12.99, -16.27), (-13.5, -15.21), (-14.28, -12.86), (-14.62, -10.59), (-14.65, -8.58), (-14.21, -5.65), (-13.82, -4.34), (-13.1, -2.66), (-11.6, -0.36), (-10.56, 0.82), (-8.45, 2.63)], [(0.0, 2.67), (0.0, 2.67)]]
# NAME Bulb
# DESC A cheerlight connected desk light.

import time

import requests
from machine import Pin
from picovector import ANTIALIAS_BEST, PicoVector, Polygon, Transform
from presto import Presto

user_button = Pin(46, Pin.IN)

dark_mode = False

BULB_OUTLINE = [(130.44, 0.0),
                (150.36, 1.51),
                (165.02, 4.64),
                (183.83, 11.41),
                (201.36, 20.97),
                (213.45, 29.85),
                (231.09, 47.51),
                (239.96, 59.6),
                (249.51, 77.14),
                (256.26, 95.95),
                (260.51, 120.55),
                (260.54, 140.53),
                (257.63, 160.3),
                (249.3, 183.81),
                (239.13, 201.01),
                (226.92, 216.84),
                (210.84, 235.98),
                (199.26, 252.27),
                (194.56, 261.09),
                (189.52, 275.19),
                (186.53, 299.95),
                (184.32, 304.38),
                (175.48, 308.37),
                (85.48, 308.37),
                (76.62, 304.46),
                (74.37, 300.04),
                (71.38, 275.29),
                (66.36, 261.17),
                (61.67, 252.35),
                (50.1, 236.05),
                (34.02, 216.92),
                (21.8, 201.09),
                (11.63, 183.89),
                (3.27, 160.39),
                (0.35, 140.63),
                (0.36, 120.64),
                (3.37, 100.89),
                (11.33, 77.23),
                (23.67, 55.53),
                (32.98, 43.78),
                (51.27, 26.8),
                (68.01, 15.9),
                (90.97, 6.09),
                (110.42, 1.53),
                (130.35, 0.0)]

BULB_INNER = [(130.44, 6.81),
              (150.35, 8.47),
              (164.95, 11.87),
              (183.54, 19.17),
              (200.7, 29.4),
              (216.02, 42.22),
              (226.08, 53.33),
              (237.34, 69.85),
              (245.83, 87.92),
              (251.31, 107.14),
              (253.57, 126.99),
              (252.61, 146.94),
              (248.29, 166.44),
              (244.81, 175.81),
              (235.5, 193.48),
              (223.9, 209.77),
              (208.12, 229.16),
              (196.2, 245.21),
              (186.84, 262.85),
              (183.75, 272.35),
              (180.29, 297.0),
              (172.24, 302.02),
              (92.24, 302.05),
              (82.74, 299.85),
              (80.07, 295.69),
              (76.77, 270.99),
              (69.14, 252.56),
              (58.07, 235.92),
              (36.12, 208.67),
              (24.64, 192.3),
              (15.53, 174.52),
              (12.17, 165.1),
              (7.62, 140.58),
              (7.67, 120.59),
              (8.92, 110.68),
              (13.83, 91.31),
              (21.8, 72.99),
              (32.58, 56.17),
              (45.86, 41.25),
              (61.32, 28.59),
              (78.6, 18.56),
              (97.28, 11.47),
              (106.99, 9.12),
              (126.84, 6.86)]

# How long we'll wait between updates
INTERVAL = 60

# Setup for the Presto display
presto = Presto()
display = presto.display
WIDTH, HEIGHT = display.get_bounds()

touch = presto.touch

# Pico Vector
vector = PicoVector(display)
vector.set_antialiasing(ANTIALIAS_BEST)

# Colours for use later
WHITE = display.create_pen(255, 255, 255)
BLACK = display.create_pen(0, 0, 0)
GRAY = display.create_pen(75, 75, 75)
PINK = display.create_pen(250, 125, 180)


def show_message(text):
    display.set_pen(PINK)
    display.clear()
    display.set_pen(WHITE)
    display.text(f"{text}", 5, 10, WIDTH - 10, 2)
    presto.update()


show_message("Connecting...")

try:
    wifi = presto.connect()
except ValueError as e:
    while True:
        show_message(e)
except ImportError as e:
    while True:
        show_message(e)

# Centre points
CX = WIDTH // 2
CY = HEIGHT // 2

# Shape constants
BAR_W = 60
BAR_H = 10
HALF_BAR_W = BAR_W // 2
HALF_BAR_H = BAR_H // 2
BAR_Y_START = 160

# Define our vector shapes
bars = Polygon()
bars.rectangle(CX - HALF_BAR_W, BAR_Y_START + 10, 60, 10, (5, 5, 5, 5))
bars.rectangle(CX - HALF_BAR_W, BAR_Y_START + 25, 60, 10, (5, 5, 5, 5))
bars.rectangle(CX - HALF_BAR_W, BAR_Y_START + 40, 60, 10, (5, 5, 5, 5))
end = Polygon()
end.arc(CX - 14, BAR_Y_START + 55, 14, 90, 270)

bulb = Polygon()
bulb.path(*BULB_INNER)
bulb_outline = Polygon()
bulb_outline.path(*BULB_OUTLINE)

transform = Transform()


def draw_bulb(colour):

    display.set_pen(GRAY)

    transform.reset()
    vector.set_transform(transform)
    transform.rotate(180, (CX - 7, BAR_Y_START + 55))
    vector.draw(end)

    transform.reset()

    vector.draw(bars)

    cl = display.create_pen(*colour)

    transform.reset()

    transform.translate(54, 11)
    transform.scale(0.5, 0.5)

    display.set_pen(BLACK)
    vector.draw(bulb_outline)

    display.set_pen(cl)
    vector.draw(bulb)


def get_cheerlight():
    try:
        print("Getting new colour...")
        req = requests.get("http://api.thingspeak.com/channels/1417/field/2/last.json", timeout=None)
        json = req.json()
        req.close()
        print("Success!")

        colour = tuple(int(json['field2'][i:i + 2], 16) for i in (1, 3, 5))

        return colour

    except OSError:
        print("Error: Failed to get new colour")
        return (255, 255, 255)


bulb_on = True
last_updated = time.time()

# Get the first colour from cheerlights
colour = get_cheerlight()

while True:

    touch.poll()

    if user_button.value() == 0:
        dark_mode = not dark_mode
        time.sleep(0.2)

    if wifi:
        # If the user is touching the screen we'll do the following
        if touch.state:
            bulb_on = not bulb_on
            # Wait for the user to stop touching the screen
            while touch.state:
                touch.poll()

        if bulb_on:
            if time.time() - last_updated > INTERVAL:
                colour = get_cheerlight()
                last_updated = time.time()

            if dark_mode:
                display.set_pen(BLACK)
            else:
                display.set_pen(WHITE)

            display.clear()

            draw_bulb(colour)

            for i in range(7):
                presto.set_led_rgb(i, *colour)

            time.sleep(0.02)

        else:
            display.set_pen(BLACK)
            display.clear()

            for i in range(7):
                presto.set_led_rgb(i, 0, 0, 0)

            time.sleep(0.02)

            draw_bulb((50, 50, 50))

    else:
        show_message("No network connection!")

    presto.update()
