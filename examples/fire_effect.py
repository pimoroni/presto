# ICON [[(-15.79, 3.95), (-15.51, 6.94), (-15.2, 8.26), (-14.43, 10.4), (-13.58, 12.02), (-12.32, 13.83), (-10.51, 15.74), (-10.45, 13.39), (-10.24, 12.17), (-9.76, 10.72), (-8.93, 9.16), (-7.48, 7.35), (0.0, 0.0), (7.44, 7.3), (8.46, 8.47), (9.71, 10.6), (10.17, 11.89), (10.45, 13.35), (10.48, 15.72), (11.66, 14.58), (12.93, 13.03), (14.38, 10.52), (15.19, 8.31), (15.58, 6.54), (15.79, 3.6), (15.52, 0.96), (15.02, -0.98), (13.97, -3.5), (12.52, -5.82), (11.06, -7.5), (9.95, -6.86), (8.36, -6.2), (7.17, -5.94), (5.4, -5.79), (3.33, -5.97), (0.91, -6.72), (-0.4, -7.44), (-1.72, -8.44), (-2.69, -9.42), (-3.63, -10.68), (-4.68, -12.85), (-5.19, -15.13), (-8.01, -12.51), (-9.15, -11.27), (-11.14, -8.83), (-12.74, -6.46), (-14.34, -3.25), (-15.11, -1.05), (-15.44, 0.4), (-15.79, 3.88)], [(0.0, 7.37), (-3.75, 11.05), (-4.84, 12.64), (-5.13, 13.52), (-5.19, 15.45), (-4.87, 16.57), (-4.1, 17.84), (-2.72, 19.0), (-1.72, 19.46), (-0.25, 19.73), (1.41, 19.55), (2.76, 18.97), (3.59, 18.31), (4.51, 17.22), (4.93, 16.41), (5.27, 14.67), (5.08, 13.28), (4.66, 12.27), (3.8, 11.1), (0.0, 7.37)], [(0.0, -25.0), (0.0, -16.32), (0.16, -14.97), (0.71, -13.6), (2.01, -12.15), (3.59, -11.32), (4.69, -11.09), (5.96, -11.09), (7.45, -11.49), (8.86, -12.49), (10.53, -14.47), (11.75, -13.73), (13.55, -12.39), (14.73, -11.32), (16.44, -9.43), (18.19, -6.83), (19.2, -4.86), (19.92, -3.02), (20.68, -0.12), (21.02, 2.7), (21.05, 4.41), (20.83, 7.19), (20.19, 10.17), (19.62, 11.85), (18.53, 14.16), (17.1, 16.38), (15.95, 17.8), (14.14, 19.64), (12.57, 20.94), (11.24, 21.85), (9.38, 22.91), (6.78, 23.96), (3.72, 24.71), (1.77, 24.94), (0.07, 25.0), (-2.09, 24.91), (-3.74, 24.7), (-6.22, 24.14), (-8.29, 23.4), (-9.62, 22.79), (-11.73, 21.54), (-13.32, 20.35), (-15.34, 18.46), (-17.53, 15.76), (-18.96, 13.32), (-20.09, 10.49), (-20.61, 8.46), (-20.98, 5.77), (-21.05, 4.01), (-20.88, 1.05), (-20.51, -1.2), (-20.05, -3.0), (-19.14, -5.6), (-18.27, -7.52), (-16.85, -10.04), (-15.43, -12.12), (-14.45, -13.38), (-12.26, -15.85), (-10.14, -17.92), (-8.54, -19.3), (-6.33, -21.03), (-3.0, -23.27), (-0.06, -24.97)]]
# NAME Fire Effect
# DESC Generated fire effect

#import time
import random
from presto import Presto

'''
A fire effect based on the Pimoroni Galatic Unicorn example
'''

presto = Presto()
display = presto.display

display_width, display_height = display.get_bounds()

# Display is 240 x 240, calculations for flame effect swamp
# the CPU so cut it down to something more managable by
# having colours in blocks of 4 x 4
display_width = display_width // 4
display_height = display_height // 4

# The hotter the particle the higher the colour index used
fire_colours = [display.create_pen(0, 0, 0),		# Background
                display.create_pen(40, 40, 40),		# Smoke
                display.create_pen(255, 50, 0),
                display.create_pen(255, 135, 36),
                display.create_pen(255, 221, 73),
                display.create_pen(255, 238, 127),
                display.create_pen(255, 255, 180)]


def setup():
    global width, height, heat, fire_spawns, damping_factor
    
    width = display_width + 2
    height = display_height + 4
    heat = [[0.0 for y in range(height)] for x in range(width)]
    fire_spawns = width // 4
    damping_factor = 0.97


def update():
    # clear the bottom row and then add a new fire seed to it
    for x in range(width):
        heat[x][height - 1] = 0.0
        heat[x][height - 2] = 0.0

    for c in range(fire_spawns):
        x = random.randint(0, width - 4) + 2
        heat[x + 0][height - 1] += 1.0
        heat[x + 1][height - 1] += 1.0
        heat[x - 1][height - 1] += 1.0
        heat[x + 0][height - 2] += 1.0
        heat[x + 1][height - 2] += 1.0
        heat[x - 1][height - 2] += 1.0

    for y in range(0, height - 2):
        for x in range(1, width - 1):
            # update this pixel by averaging the below pixels
            average = (
                heat[x][y] + heat[x][y + 1] + heat[x][y + 2] + heat[x - 1][y + 1] + heat[x + 1][y + 1]
            ) / 5.0

            # damping factor to ensure flame tapers out towards the top of the displays
            average *= damping_factor

            # update the heat map with our newly averaged value
            heat[x][y] = average


def draw():
    for y in range(display_height):
        for x in range(display_width):
            value = heat[x + 1][y]
            if value < 0.15:
                display.set_pen(fire_colours[0])
            elif value < 0.25:
                display.set_pen(fire_colours[1])
            elif value < 0.35:
                display.set_pen(fire_colours[2])
            elif value < 0.4:
                display.set_pen(fire_colours[3])
            elif value < 0.45:
                display.set_pen(fire_colours[4])
            elif value < 0.60:
                display.set_pen(fire_colours[5])
            else:
                display.set_pen(fire_colours[6])
            # Drawing a rectangle much faster than drawing 16 individual pixels
            display.rectangle(x * 4, y * 4, 4, 4)
            
    presto.update()


setup()

while True:

    update()
    
    draw()