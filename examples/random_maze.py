# ICON [[(-11.56, 1.11), (0.0, 7.78), (11.56, 1.11), (2.22, -4.28), (2.22, 3.33), (-2.22, 3.33), (-2.22, -4.28), (-11.56, 1.11)], [(-2.22, -9.39), (-2.22, -10.34), (-3.3, -10.74), (-4.64, -11.51), (-5.8, -12.55), (-6.44, -13.37), (-7.24, -14.88), (-7.71, -16.74), (-7.72, -18.72), (-7.48, -19.97), (-6.64, -21.86), (-5.73, -23.04), (-5.01, -23.73), (-3.61, -24.69), (-1.71, -25.38), (-0.28, -25.55), (1.62, -25.39), (3.12, -24.93), (3.95, -24.5), (5.46, -23.32), (6.53, -22.02), (7.05, -21.11), (7.52, -19.84), (7.78, -17.89), (7.58, -15.97), (6.93, -14.19), (6.25, -13.1), (5.17, -11.94), (4.14, -11.19), (2.28, -10.35), (2.22, -9.39), (17.78, -0.45), (18.8, 0.37), (19.28, 1.03), (19.88, 2.42), (20.0, 3.39), (20.0, 7.66), (19.68, 9.34), (19.09, 10.4), (17.83, 11.52), (2.22, 20.5), (0.49, 21.08), (-0.5, 21.08), (-2.17, 20.53), (-17.78, 11.55), (-18.42, 11.11), (-19.42, 9.99), (-19.91, 8.59), (-20.0, 7.72), (-20.0, 3.44), (-19.95, 2.71), (-19.47, 1.27), (-18.95, 0.53), (-17.83, -0.42), (-2.22, -9.39)], [(-2.22, 11.61), (-15.56, 3.94), (-15.56, 7.66), (0.0, 16.66), (15.56, 7.66), (15.56, 3.94), (2.22, 11.61), (0.98, 12.11), (0.06, 12.22), (-1.26, 12.03), (-2.17, 11.64)], [(0.0, -14.45), (1.16, -14.64), (1.89, -15.01), (2.52, -15.6), (3.12, -16.6), (3.33, -17.73), (3.23, -18.6), (2.76, -19.63), (1.79, -20.58), (0.43, -21.09), (-0.91, -20.99), (-1.63, -20.69), (-2.61, -19.87), (-3.22, -18.68), (-3.33, -17.84), (-3.18, -16.75), (-2.43, -15.43), (-1.73, -14.9), (-0.75, -14.52), (-0.06, -14.45)], [(0.0, 16.66), (0.0, 16.66)]]
# NAME Random Maze
# DESC Escape the randomly generated mazes!

import gc
import random
import time
from collections import namedtuple

from machine import I2C
from presto import Presto
from qwstpad import ADDRESSES, QwSTPad

"""
A single player game demo. Navigate a set of mazes from the start (red) to the goal (green).
Mazes get bigger / harder with each increase in level.
Makes use of 1 QwSTPad and a Pimoroni Presto.

Controls:
* U = Move Forward
* D = Move Backward
* R = Move Right
* L = Move left
* + = Continue (once the current level is complete)
"""

# Setup for the Presto display
presto = Presto(ambient_light=True)
display = presto.display

# Get the width and height from the display
WIDTH, HEIGHT = display.get_bounds()

# General Constants
I2C_PINS = {"id": 0, "sda": 40, "scl": 41}    # The I2C pins the QwSTPad is connected to
I2C_ADDRESS = ADDRESSES[0]                  # The I2C address of the connected QwSTPad
BRIGHTNESS = 1.0                            # The brightness of the LCD backlight (from 0.0 to 1.0)

# Colour Constants (RGB565)
WHITE = display.create_pen(255, 255, 255)
BLACK = display.create_pen(0, 0, 0)
RED = display.create_pen(255, 0, 0)
GREEN = display.create_pen(0, 255, 0)
PLAYER = display.create_pen(227, 231, 110)
WALL = display.create_pen(127, 125, 244)
BACKGROUND = display.create_pen(60, 57, 169)
PATH = display.create_pen((227 + 60) // 2, (231 + 57) // 2, (110 + 169) // 2)


def show_message(text):
    display.set_pen(BACKGROUND)
    display.clear()
    display.set_pen(WALL)
    display.text(f"{text}", 5, 10, WIDTH, 2)
    presto.update()


# Gameplay Constants
Position = namedtuple("Position", ("x", "y"))
MIN_MAZE_WIDTH = 2
MAX_MAZE_WIDTH = 5
MIN_MAZE_HEIGHT = 2
MAX_MAZE_HEIGHT = 5
WALL_SHADOW = 2
WALL_GAP = 1
TEXT_SHADOW = 2
MOVEMENT_SLEEP = 0.1
DIFFICULT_SCALE = 0.5

# Variables
i2c = I2C(**I2C_PINS)                           # The I2C instance to pass to the QwSTPad
complete = False                                # Has the game been completed?
level = 0                                       # The current "level" the player is on (affects difficulty)


# Classes
class Cell:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.bottom = True
        self.right = True
        self.visited = False

    @staticmethod
    def remove_walls(current, next):
        dx, dy = current.x - next.x, current.y - next.y
        if dx == 1:
            next.right = False
        if dx == -1:
            current.right = False
        if dy == 1:
            next.bottom = False
        if dy == -1:
            current.bottom = False


class MazeBuilder:
    def __init__(self):
        self.width = 0
        self.height = 0
        self.cell_grid = []
        self.maze = []

    def build(self, width, height):
        if width <= 0:
            raise ValueError("width out of range. Expected greater than 0")

        if height <= 0:
            raise ValueError("height out of range. Expected greater than 0")

        self.width = width
        self.height = height

        # Set the starting cell to the centre
        cx = (self.width - 1) // 2
        cy = (self.height - 1) // 2

        gc.collect()

        # Create a grid of cells for building a maze
        self.cell_grid = [[Cell(x, y) for y in range(self.height)] for x in range(self.width)]
        cell_stack = []

        # Retrieve the starting cell and mark it as visited
        current = self.cell_grid[cx][cy]
        current.visited = True

        # Loop until every cell has been visited
        while True:
            next = self.choose_neighbour(current)
            # Was a valid neighbour found?
            if next is not None:
                # Move to the next cell, removing walls in the process
                next.visited = True
                cell_stack.append(current)
                Cell.remove_walls(current, next)
                current = next

            # No valid neighbour. Backtrack to a previous cell
            elif len(cell_stack) > 0:
                current = cell_stack.pop()

            # No previous cells, so exit
            else:
                break

        gc.collect()

        # Use the cell grid to create a maze grid of 0's and 1s
        self.maze = []

        row = [1]
        for _ in range(0, self.width):
            row.append(1)
            row.append(1)
        self.maze.append(row)

        for y in range(0, self.height):
            row = [1]
            for x in range(0, self.width):
                row.append(0)
                row.append(1 if self.cell_grid[x][y].right else 0)
            self.maze.append(row)

            row = [1]
            for x in range(0, self.width):
                row.append(1 if self.cell_grid[x][y].bottom else 0)
                row.append(1)
            self.maze.append(row)

        self.cell_grid.clear()
        gc.collect()

        self.grid_columns = (self.width * 2 + 1)
        self.grid_rows = (self.height * 2 + 1)

    def choose_neighbour(self, current):
        unvisited = []
        for dx in range(-1, 2, 2):
            x = current.x + dx
            if x >= 0 and x < self.width and not self.cell_grid[x][current.y].visited:
                unvisited.append((x, current.y))

        for dy in range(-1, 2, 2):
            y = current.y + dy
            if y >= 0 and y < self.height and not self.cell_grid[current.x][y].visited:
                unvisited.append((current.x, y))

        if len(unvisited) > 0:
            x, y = random.choice(unvisited)
            return self.cell_grid[x][y]

        return None

    def maze_width(self):
        return (self.width * 2) + 1

    def maze_height(self):
        return (self.height * 2) + 1

    def draw(self, display):
        # Draw the maze we have built. Each '1' in the array represents a wall
        for row in range(self.grid_rows):
            for col in range(self.grid_columns):
                # Calculate the screen coordinates
                x = (col * wall_separation) + offset_x
                y = (row * wall_separation) + offset_y

                if self.maze[row][col] == 1:
                    # Draw a wall shadow
                    display.set_pen(BLACK)
                    display.rectangle(x + WALL_SHADOW, y + WALL_SHADOW, wall_size, wall_size)

                    # Draw a wall top
                    display.set_pen(WALL)
                    display.rectangle(x, y, wall_size, wall_size)

                if self.maze[row][col] == 2:
                    # Draw the player path
                    display.set_pen(PATH)
                    display.rectangle(x, y, wall_size, wall_size)


class Player(object):
    def __init__(self, x, y, colour, pad):
        self.x = x
        self.y = y
        self.colour = colour
        self.pad = pad

    def position(self, x, y):
        self.x = x
        self.y = y

    def update(self, maze):
        # Read the player's gamepad
        button = self.pad.read_buttons()

        if button["L"] and maze[self.y][self.x - 1] != 1:
            self.x -= 1
            time.sleep(MOVEMENT_SLEEP)

        elif button["R"] and maze[self.y][self.x + 1] != 1:
            self.x += 1
            time.sleep(MOVEMENT_SLEEP)

        elif button["U"] and maze[self.y - 1][self.x] != 1:
            self.y -= 1
            time.sleep(MOVEMENT_SLEEP)

        elif button["D"] and maze[self.y + 1][self.x] != 1:
            self.y += 1
            time.sleep(MOVEMENT_SLEEP)

        maze[self.y][self.x] = 2

    def draw(self, display):
        display.set_pen(self.colour)
        display.rectangle(self.x * wall_separation + offset_x,
                          self.y * wall_separation + offset_y,
                          wall_size, wall_size)


def build_maze():
    global wall_separation
    global wall_size
    global offset_x
    global offset_y
    global start
    global goal

    difficulty = int(level * DIFFICULT_SCALE)
    width = random.randrange(MIN_MAZE_WIDTH, MAX_MAZE_WIDTH)
    height = random.randrange(MIN_MAZE_HEIGHT, MAX_MAZE_HEIGHT)
    builder.build(width + difficulty, height + difficulty)

    wall_separation = min(HEIGHT // builder.grid_rows,
                          WIDTH // builder.grid_columns)
    wall_size = wall_separation - WALL_GAP

    offset_x = (WIDTH - (builder.grid_columns * wall_separation) + WALL_GAP) // 2
    offset_y = (HEIGHT - (builder.grid_rows * wall_separation) + WALL_GAP) // 2

    start = Position(1, builder.grid_rows - 2)
    goal = Position(builder.grid_columns - 2, 1)


# Create the maze builder and build the first maze and put
builder = MazeBuilder()
build_maze()

# Create the player object if a QwSTPad is connected
try:
    player = Player(*start, PLAYER, QwSTPad(i2c, I2C_ADDRESS))
except OSError:
    while True:
        show_message("QwSTPad: Not Found!\n\nConnect a QwSTPad and try again :)")

print("QwSTPad: Connected ... Starting")

# Store text strings and calculate centre location
text_1_string = "Maze Complete!"
text_1_size = display.measure_text(text_1_string, 3)

text_2_string = "Press + to continue"
text_2_size = display.measure_text(text_2_string, 2)

text_1_location = ((WIDTH // 2) - (text_1_size // 2), 96)
text_2_location = ((WIDTH // 2) - (text_2_size // 2), 120)

# Wrap the code in a try block, to catch any exceptions (including KeyboardInterrupt)
try:
    # Loop forever
    while True:
        if not complete:
            # Update the player's position in the maze
            player.update(builder.maze)

            # Check if any player has reached the goal position
            if player.x == goal.x and player.y == goal.y:
                complete = True
        else:
            # Check for the player wanting to continue
            if player.pad.read_buttons()["+"]:
                complete = False
                level += 1
                build_maze()
                player.position(*start)

        # Clear the screen to the background colour
        display.set_pen(BACKGROUND)
        display.clear()

        # Draw the maze walls
        builder.draw(display)

        # Draw the start location square
        display.set_pen(RED)
        display.rectangle(start.x * wall_separation + offset_x,
                          start.y * wall_separation + offset_y,
                          wall_size, wall_size)

        # Draw the goal location square
        display.set_pen(GREEN)
        display.rectangle(goal.x * wall_separation + offset_x,
                          goal.y * wall_separation + offset_y,
                          wall_size, wall_size)

        # Draw the player
        player.draw(display)

        # Display the level
        display.set_pen(BLACK)
        display.text(f"Lvl: {level}", 2 + TEXT_SHADOW, 2 + TEXT_SHADOW, WIDTH, 1)
        display.set_pen(WHITE)
        display.text(f"Lvl: {level}", 2, 2, WIDTH, 1)

        if complete:
            # Draw banner shadow
            display.set_pen(BLACK)
            display.rectangle(4, 94, WIDTH, 50)
            # Draw banner
            display.set_pen(PLAYER)
            display.rectangle(0, 90, WIDTH, 50)

            # Draw text shadow
            display.set_pen(BLACK)
            display.text(f"{text_1_string}", text_1_location[0] + TEXT_SHADOW, text_1_location[1] + TEXT_SHADOW, WIDTH, 3)
            display.text(f"{text_2_string}", text_2_location[0] + TEXT_SHADOW, text_2_location[1] + TEXT_SHADOW, WIDTH, 2)

            # Draw text
            display.set_pen(WHITE)
            display.text(f"{text_1_string}", text_1_location[0], text_1_location[1], WIDTH, 3)
            display.text(f"{text_2_string}", text_2_location[0], text_2_location[1], WIDTH, 2)

        # Finally we update the screen with our changes :)
        presto.update()

# Handle the QwSTPad being disconnected unexpectedly
except OSError:
    while True:
        show_message("QwSTPad: Disconnected!")

# Turn off the LEDs of the connected QwSTPad
finally:
    try:
        player.pad.clear_leds()
    except OSError:
        pass
