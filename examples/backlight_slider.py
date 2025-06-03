# ICON [[(0.0, 7.0), (3.0, 4.0), (8.0, 4.0), (8.0, -1.0), (11.0, -4.0), (8.0, -7.0), (8.0, -12.0), (3.0, -12.0), (0.0, -15.0), (-3.0, -12.0), (-8.0, -12.0), (-8.0, -7.0), (-11.0, -4.0), (-8.0, -1.0), (-8.0, 4.0), (-3.0, 4.0), (0.0, 7.0)], [(0.0, 2.0), (0.0, -10.0), (1.9, -9.71), (3.4, -8.97), (4.8, -7.62), (5.59, -6.24), (5.85, -5.39), (6.0, -4.1), (5.96, -3.3), (5.56, -1.7), (5.04, -0.71), (4.07, 0.42), (2.74, 1.36), (1.84, 1.73), (0.05, 2.0)], [(-16.0, 12.0), (-16.87, 11.91), (-18.0, 11.49), (-18.81, 10.88), (-19.31, 10.27), (-19.82, 9.22), (-20.0, 8.05), (-20.0, -16.0), (-19.91, -16.88), (-19.52, -17.92), (-19.12, -18.51), (-18.19, -19.34), (-16.72, -19.94), (-16.05, -20.0), (16.0, -20.0), (17.35, -19.77), (18.4, -19.17), (19.01, -18.58), (19.8, -17.25), (20.0, -16.05), (20.0, 8.0), (19.89, 8.96), (19.58, 9.79), (18.84, 10.81), (17.99, 11.47), (17.05, 11.87), (16.05, 12.0), (-16.0, 12.0)], [(-16.0, 8.0), (16.0, 8.0), (16.0, -16.0), (-16.0, -16.0), (-16.0, 8.0)]]
# NAME Backlight Control Demo
# DESC Let there be light.
from picovector import ANTIALIAS_BEST, PicoVector, Polygon, Transform
from presto import Presto

# Setup for the Presto display
presto = Presto(ambient_light=False)
display = presto.display
WIDTH, HEIGHT = display.get_bounds()

CX = WIDTH // 2
CY = HEIGHT // 2

# Colours
BLACK = display.create_pen(0, 0, 0)
hue = 0.6
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

# Constants for our slider
BAR_W = 50
BAR_H = 170
BAR_X = CX - BAR_W // 2
BAR_Y = CY - BAR_H // 2
SLIDER_HEIGHT = BAR_H // 4

# Vector icons
BACKLIGHT_MAX_PATHS = [[(-0.0, 9.69), (-2.96, 6.77), (-7.08, 6.77), (-7.08, 2.65), (-10.0, -0.31), (-7.08, -3.27), (-7.08, -7.39), (-2.96, -7.39), (-0.0, -10.31), (2.96, -7.39), (7.08, -7.39), (7.08, -3.27), (10.0, -0.31), (7.08, 2.65), (7.08, 6.77), (2.96, 6.77), (-0.0, 9.69)], [(-0.0, 4.12), (0.94, 4.02), (1.52, 3.86), (1.99, 3.66), (2.67, 3.23), (3.1, 2.85), (3.67, 2.17), (4.07, 1.44), (4.24, 0.98), (4.39, 0.27), (4.42, -0.29), (4.33, -1.25), (4.16, -1.85), (3.84, -2.52), (3.48, -3.03), (3.18, -3.37), (2.7, -3.81), (2.36, -4.06), (1.78, -4.37), (1.2, -4.58), (0.65, -4.69), (-0.2, -4.73), (-0.79, -4.67), (-1.24, -4.57), (-1.93, -4.3), (-2.4, -4.04), (-2.89, -3.67), (-3.57, -2.94), (-3.9, -2.44), (-4.22, -1.68), (-4.39, -0.87), (-4.4, 0.15), (-4.32, 0.7), (-4.17, 1.22), (-3.81, 1.98), (-3.45, 2.49), (-3.16, 2.82), (-2.73, 3.19), (-2.31, 3.48), (-1.82, 3.74), (-1.18, 3.97), (-0.79, 4.05), (-0.02, 4.11)], [(-0.0, 7.21), (2.21, 5.0), (5.31, 5.0), (5.31, 1.9), (7.52, -0.31), (5.31, -2.52), (5.31, -5.62), (2.21, -5.62), (-0.0, -7.83), (-2.21, -5.62), (-5.31, -5.62), (-5.31, -2.52), (-7.52, -0.31), (-5.31, 1.9), (-5.31, 5.0), (-2.21, 5.0), (-0.0, 7.21)]]
BACKLIGHT_MIN_PATHS = [[(-0.0, 9.69), (-2.96, 6.77), (-7.08, 6.77), (-7.08, 2.65), (-10.0, -0.31), (-7.08, -3.27), (-7.08, -7.39), (-2.96, -7.39), (-0.0, -10.31), (2.96, -7.39), (7.08, -7.39), (7.08, -3.27), (10.0, -0.31), (7.08, 2.65), (7.08, 6.77), (2.96, 6.77), (-0.0, 9.69)], [(-0.0, 7.21), (2.21, 5.0), (5.31, 5.0), (5.31, 1.9), (7.52, -0.31), (5.31, -2.52), (5.31, -5.62), (2.21, -5.62), (-0.0, -7.83), (-2.21, -5.62), (-5.31, -5.62), (-5.31, -2.52), (-7.52, -0.31), (-5.31, 1.9), (-5.31, 5.0), (-2.21, 5.0), (-0.0, 7.21)]]
backlight_max_icon = Polygon()
backlight_min_icon = Polygon()

for path in BACKLIGHT_MAX_PATHS:
    backlight_max_icon.path(*path)

for path in BACKLIGHT_MIN_PATHS:
    backlight_min_icon.path(*path)


class Slider(object):
    def __init__(self, x, y, w, h, bar_colour, slider_colour):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.slider_h = self.h // 4
        self.value = 1.0
        self.slider_vector = Polygon().rectangle(self.x, self.y, self.w, self.slider_h, (10, 10, 10, 10))
        self.bar_vector = Polygon().rectangle(self.x, self.y, self.w, self.h, (10, 10, 10, 10))
        self.slider_colour = slider_colour
        self.bar_colour = bar_colour
        self.touch = presto.touch

    def update(self):
        self.touch.poll()

        if self.touch.state and self.touch.x >= self.x and self.touch.x <= self.x + self.w and self.touch.y >= self.y - self.slider_h and self.touch.y <= (self.y + self.h):

            new_pos_y = max(min(self.touch.y, (self.y + self.h) - self.slider_h), self.y)
            self.slider_vector = Polygon().rectangle(self.x, new_pos_y, self.w, self.slider_h, (10, 10, 10, 10))
            self.value = 1.0 - (new_pos_y - self.y) / ((self.y + self.h - self.slider_h) - self.y)

    def draw(self):
        display.set_pen(self.bar_colour)
        vector.draw(self.bar_vector)
        display.set_pen(self.slider_colour)
        vector.draw(self.slider_vector)

    def get_value(self):
        return self.value


# Create our slider object
s = Slider(BAR_X, BAR_Y, BAR_W, BAR_H, FOREGROUND, TEXT_COLOUR)

while True:

    s.update()

    brightness = max(s.get_value(), 0.1)
    presto.set_backlight(brightness)

    # Clear the screen
    display.set_pen(BACKGROUND)
    display.clear()

    # Draw the slider
    s.draw()

    # Draw the min/max brightness icons
    display.set_pen(TEXT_COLOUR)
    t.translate(CX, BAR_Y + 20)
    vector.draw(backlight_max_icon)
    t.reset()
    t.translate(CX, BAR_Y + BAR_H - 20)
    vector.draw(backlight_min_icon)
    t.reset()

    # Draw thhe rounded corners
    display.set_pen(BLACK)
    vector.draw(background_rect)

    presto.update()
