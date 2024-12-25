"""
Add a SCD41 sensor breakout to Presto to make a handy CO2 detector!
https://shop.pimoroni.com/products/scd41-co2-sensor-breakout
Touch and hold the screen to reset the high/low values.

You will need the osansb.af font saved to your Presto alongside this script.
"""

from presto import Presto
from pimoroni_i2c import PimoroniI2C
import breakout_scd41
from picovector import Transform, Polygon, PicoVector, ANTIALIAS_X16

i2c = PimoroniI2C(sda=40, scl=41)

presto = Presto(full_res=True)
display = presto.display
vector = PicoVector(display)

WIDTH, HEIGHT = display.get_bounds()

t = Transform()
vector.set_font_letter_spacing(100)
vector.set_font_word_spacing(100)
vector.set_font_line_height(110)
vector.set_transform(t)

BLACK = display.create_pen(0, 0, 0)
WHITE = display.create_pen(255, 255, 255)
RED = display.create_pen(127, 0, 0)
GREEN = display.create_pen(0, 127, 0)

# pick what bits of the colour wheel to use (from 0-360°)
# https://www.cssscript.com/demo/hsv-hsl-color-wheel-picker-reinvented/
CO2_HUE_START = 100  # green
CO2_HUE_END = 0  # red
TEMPERATURE_HUE_START = 240
TEMPERATURE_HUE_END = 359
HUMIDITY_SATURATION_START = 0
HUMIDITY_SATURATION_END = 360

# the range of readings to map to colours (and scale our graphs to)
# https://www.kane.co.uk/knowledge-centre/what-are-safe-levels-of-co-and-co2-in-rooms
CO2_MIN = 300
CO2_MAX = 2000
TEMPERATURE_MIN = 10
TEMPERATURE_MAX = 33
HUMIDITY_MIN = 10
HUMIDITY_MAX = 90
# use these to draw indicator lines on the CO2 graph
OK_CO2_LEVEL = 800
BAD_CO2_LEVEL = 1500

MAX_READINGS = 120  # how many readings to store (and draw on the graph)

# the areas of the screen we want to draw our graphs into
CO2_GRAPH_TOP = HEIGHT * 0.2
CO2_GRAPH_BOTTOM = HEIGHT * 0.75
TEMPERATURE_GRAPH_TOP = HEIGHT * 0.75
TEMPERATURE_GRAPH_BOTTOM = HEIGHT
HUMIDITY_GRAPH_TOP = HEIGHT * 0.75
HUMIDITY_GRAPH_BOTTOM = HEIGHT
PADDING = 5

LINE_THICKNESS = 3  # thickness of indicator and graph lines


def graph_polygon(top, bottom, min, max, readings, y_offset=0):
    # function to generate a filled graph polygon and scale it to the available space
    points = []
    for r in range(len(readings)):
        x = round(r * (WIDTH / len(readings)))
        y = round(bottom + ((readings[r] - min) * (top - bottom) / (max - min)))
        points.append((x, y))
    points.append((x, round(bottom)))
    points.append((0, round(bottom)))
    if y_offset != 0:
        for r in range(len(readings)):
            x = round(r * (WIDTH / len(readings)))
            y = round(bottom + ((readings[r] - min) * (top - bottom) / (max - min)) + y_offset)
            points.append((x, y))
        points.append((x, round(bottom)))
        points.append((0, round(bottom)))    
    poly = Polygon()
    poly.path(*points)
    return poly


def line_polygon(top, bottom, min, max, value):
    # function to generate a straight line on our graph at a specific value
    points = []
    points.append((0, round(bottom + ((value - min) * (top - bottom) / (max - min)))))
    points.append((WIDTH, round(bottom + ((value - min) * (top - bottom) / (max - min)))))
    points.append((WIDTH, round(bottom + ((value - min) * (top - bottom) / (max - min))) + LINE_THICKNESS))
    points.append((0, round(bottom + ((value - min) * (top - bottom) / (max - min))) + LINE_THICKNESS))
    poly = Polygon()
    poly.path(*points)
    return poly


highest_co2 = 0.0
lowest_co2 = 4000.0
co2_readings = []
temperature_readings = []
humidity_readings = []

# set up
vector.set_antialiasing(ANTIALIAS_X16)
vector.set_font("osansb.af", 50)
display.set_pen(WHITE)

try:
    breakout_scd41.init(i2c)
    breakout_scd41.start()
    vector.text("Waiting for sensor to be ready", 0, 0)
    display.update()
except RuntimeError as e:
    print(e)
    vector.text("SCD41 breakout not detected :(", 0, 0)
    vector.text("but you could buy one at pimoroni.com ;)", 0, HEIGHT - 120)
    display.update()

while True:
    if presto.touch.state:
        # reset recorded high / low values
        highest_co2 = 0.0
        lowest_co2 = 4000.0

    if breakout_scd41.ready():
        # read the sensor
        co2, temperature, humidity = breakout_scd41.measure()

        # if lists are empty, populate the list with the current readings
        if len(co2_readings) == 0:
            for i in range(MAX_READINGS):
                co2_readings.append(co2)
                temperature_readings.append(temperature)
                humidity_readings.append(humidity)

        # update highest / lowest values
        if co2 < lowest_co2:
            lowest_co2 = co2
        if co2 > highest_co2:
            highest_co2 = co2

        # calculates some colours from the sensor readings
        co2_hue = max(0, CO2_HUE_START + ((co2 - CO2_MIN) * (CO2_HUE_END - CO2_HUE_START) / (CO2_MAX - CO2_MIN)))
        temperature_hue = max(0, TEMPERATURE_HUE_START + ((temperature - TEMPERATURE_MIN) * (TEMPERATURE_HUE_END - TEMPERATURE_HUE_START) / (TEMPERATURE_MAX - TEMPERATURE_MIN)))
        humidity_hue = max(0, HUMIDITY_SATURATION_START + ((humidity - HUMIDITY_MIN) * (HUMIDITY_SATURATION_END - HUMIDITY_SATURATION_START) / (HUMIDITY_MAX - HUMIDITY_MIN)))

        # keep track of readings in a list (so we can draw the graph)
        co2_readings.append(co2)
        temperature_readings.append(temperature)
        humidity_readings.append(humidity)

        # we only need to save a screen's worth of readings, so delete the oldest
        if len(co2_readings) > MAX_READINGS:
            co2_readings.pop(0)
        if len(temperature_readings) > MAX_READINGS:
            temperature_readings.pop(0)
        if len(humidity_readings) > MAX_READINGS:
            humidity_readings.pop(0)

        # clear to black
        display.set_pen(BLACK)
        display.clear()

        # draw the graphs and text
        # draw the CO2 indicator lines
        display.set_pen(RED)
        vector.draw(line_polygon(CO2_GRAPH_TOP, CO2_GRAPH_BOTTOM, CO2_MIN, CO2_MAX, BAD_CO2_LEVEL))
        display.set_pen(GREEN)
        vector.draw(line_polygon(CO2_GRAPH_TOP, CO2_GRAPH_BOTTOM, CO2_MIN, CO2_MAX, OK_CO2_LEVEL))
        # draw the CO2 graph
        display.set_pen(display.create_pen_hsv(co2_hue / 360, 1.0, 1.0))
        co2_graph = graph_polygon(CO2_GRAPH_TOP, CO2_GRAPH_BOTTOM, CO2_MIN, CO2_MAX, co2_readings)
        vector.draw(co2_graph)
        # draw the CO2 text
        vector.set_font_size(80)
        vector.text("CO2", PADDING, -30)
        vector.text(f"{co2:.0f}ppm", WIDTH // 2, -30)
        display.set_pen(BLACK)
        vector.set_font_size(30)
        vector.text(f"Low {lowest_co2:.0f}ppm", PADDING, round(TEMPERATURE_GRAPH_TOP) - 52)
        vector.text(f"High {highest_co2:.0f}ppm", PADDING, round(TEMPERATURE_GRAPH_TOP) - 14)

        # draw the humidity graph
        # here we're using the 'hue' value to affect the saturation (so light blue to dark blue)
        display.set_pen(display.create_pen_hsv(240 / 360, humidity_hue / 360, 1.0))
        # draw this polygon twice, applying an offset to make a line rather than a filled shape
        humidity_graph = graph_polygon(HUMIDITY_GRAPH_TOP, HUMIDITY_GRAPH_BOTTOM, HUMIDITY_MIN, HUMIDITY_MAX, humidity_readings, LINE_THICKNESS)
        vector.draw(humidity_graph)
        #display.set_pen(WHITE)
        humidity_text = f"{humidity:.0f}% Humidity"
        text_width = int(vector.measure_text(humidity_text)[2])
        vector.text(humidity_text, WIDTH - PADDING - text_width, int(HUMIDITY_GRAPH_BOTTOM) - 15)

        # draw the temperature graph
        display.set_pen(display.create_pen_hsv(temperature_hue / 360, 1.0, 1.0))
        # draw this polygon twice, applying an offset to make a line rather than a filled shape
        temperature_graph = graph_polygon(TEMPERATURE_GRAPH_TOP, TEMPERATURE_GRAPH_BOTTOM, TEMPERATURE_MIN, TEMPERATURE_MAX, temperature_readings, LINE_THICKNESS)
        vector.draw(temperature_graph)
        #display.set_pen(WHITE)
        vector.text(f"Temp: {temperature:.0f}°C", PADDING, int(TEMPERATURE_GRAPH_BOTTOM) - 15)

        presto.update()