# ICON lightbulb
# NAME Bulb
# DESC A cheerlight connected desk light.

import time

import requests
from machine import Pin
from picovector import color, font, mat3, shape, vec2
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
WIDTH, HEIGHT = display.width, display.height

touch = presto.touch

display.font = font.load("Roboto-Medium.af")

# Colours for use later
WHITE = color.rgb(255, 255, 255)
BLACK = color.rgb(0, 0, 0)
GRAY = color.rgb(75, 75, 75)
PINK = color.rgb(250, 125, 180)


def show_message(text):
    display.pen = PINK
    display.clear()
    display.pen = WHITE
    display.text(f"{text}", 5, 10, 16)
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
bars = [shape.rounded_rectangle(CX - HALF_BAR_W, BAR_Y_START + offset, 60, 10, 5)
        for offset in (10, 25, 40)]
end = shape.pie(CX - 14, BAR_Y_START + 55, 14, 90, 270)

# Rotate about the pivot: later calls apply first, so this reads
# translate(pivot) then rotate then translate(-pivot).
PIVOT_X, PIVOT_Y = CX - 7, BAR_Y_START + 55
end.transform = mat3().translate(PIVOT_X, PIVOT_Y).rotate(180).translate(-PIVOT_X, -PIVOT_Y)

bulb = shape.custom([vec2(x, y) for x, y in BULB_INNER])
bulb_outline = shape.custom([vec2(x, y) for x, y in BULB_OUTLINE])

bulb_transform = mat3().translate(54, 11).scale(0.5, 0.5)
bulb.transform = bulb_transform
bulb_outline.transform = bulb_transform


def draw_bulb(colour):

    display.pen = GRAY
    display.shape(end)
    display.shape(bars)

    display.pen = BLACK
    display.shape(bulb_outline)

    display.pen = color.rgb(*colour)
    display.shape(bulb)


def get_cheerlight():
    try:
        print("Getting new colour...")
        req = requests.get("http://api.thingspeak.com/channels/1417/field/2/last.json", timeout=None)
        json = req.json()
        req.close()
        print("Success!")

        return tuple(int(json["field2"][i:i + 2], 16) for i in (1, 3, 5))

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
                display.pen = BLACK
            else:
                display.pen = WHITE
            display.clear()

            draw_bulb(colour)

            for i in range(7):
                presto.set_led_rgb(i, *colour)

            time.sleep(0.02)

        else:
            display.pen = BLACK
            display.clear()

            for i in range(7):
                presto.set_led_rgb(i, 0, 0, 0)

            time.sleep(0.02)

            draw_bulb((50, 50, 50))

    else:
        show_message("No network connection!")

    presto.update()
