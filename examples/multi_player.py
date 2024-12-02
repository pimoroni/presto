import math
from collections import namedtuple

from machine import I2C
from presto import Presto
from qwstpad import ADDRESSES, QwSTPad

"""
A multi-player QwSTPad game demo. Each player drives a tank-like vehicle around an arena
with the goal of hitting other players with projects to get the most points.
Makes use of 1 to 4 QwSTPads and a Pimoroni Presto

Controls:
* U = Move Forward
* D = Move Backward
* R = Turn Right
* L = Turn left
* A = Fire
"""

# Setup for the Presto display
presto = Presto()
display = presto.display
WIDTH, HEIGHT = display.get_bounds()

# General Constants
I2C_PINS = {"id": 0, "sda": 40, "scl": 41}    # The I2C pins the QwSTPad is connected to
BRIGHTNESS = 1.0                              # The brightness of the LCD backlight (from 0.0 to 1.0)

# Colour Constants (RGB565)
WHITE = display.create_pen(255, 255, 255)
BLACK = display.create_pen(0, 0, 0)
CYAN = display.create_pen(0, 255, 255)
MAGENTA = display.create_pen(255, 0, 255)
YELLOW = display.create_pen(255, 255, 0)
GREEN = display.create_pen(0, 255, 0)
RED = display.create_pen(255, 0, 0)
BLUE = display.create_pen(0, 0, 255)
GREY = display.create_pen(115, 115, 115)

# Gameplay Constants
PlayerDef = namedtuple("PlayerDef", ("x", "y", "colour"))
PLAYERS = (PlayerDef(x=30, y=50, colour=GREEN),
           PlayerDef(x=280, y=50, colour=MAGENTA),
           PlayerDef(x=30, y=200, colour=CYAN),
           PlayerDef(x=280, y=200, colour=BLUE))
PLAYER_RADIUS = 10
PLAYER_SPEED = 4
LINE_LENGTH = 25
START_ANGLE = 20
PROJECTILE_LIMIT = 15
PROJECTILE_SPEED = 5
GRID_SPACING = 20
SCORE_TARGET = 1000
TEXT_SHADOW = 2

i2c = I2C(**I2C_PINS)                           # The I2C instance to pass to all QwSTPads
players = []                                    # The list that will store the player objects
complete = False                                # Has the game been completed?


# Classes
class Projectile:
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.direction = direction

    def update(self):
        self.x += PROJECTILE_SPEED * math.cos(self.direction)
        self.y += PROJECTILE_SPEED * math.sin(self.direction)

    def draw(self, display):
        display.pixel(int(self.x), int(self.y))

    def is_on_screen(self):
        return self.x >= 0 and self.x < WIDTH and self.y >= 0 and self.y < HEIGHT

    def has_hit(self, player):
        xdiff = self.x - player.x
        ydiff = self.y - player.y

        sqdist = xdiff ** 2 + ydiff ** 2
        return sqdist < player.size ** 2


class Player:
    def __init__(self, index, x, y, size, colour, pad):
        self.index = index
        self.x = x
        self.y = y
        self.direction = math.radians(START_ANGLE)
        self.size = size
        self.colour = colour
        self.pad = pad

        self.projectiles = []
        self.was_hit = False
        self.score = 0

    def fire(self):
        if len(self.projectiles) < PROJECTILE_LIMIT:
            self.projectiles.append(Projectile(self.x, self.y, self.direction))

    def update(self):
        # Read the player's gamepad
        button = self.pad.read_buttons()

        if button['L']:
            self.direction -= 0.1

        if button['R']:
            self.direction += 0.1

        if button['U']:
            self.x += PLAYER_SPEED * math.cos(self.direction)
            self.y += PLAYER_SPEED * math.sin(self.direction)

        if button['D']:
            self.x -= PLAYER_SPEED * math.cos(self.direction)
            self.y -= PLAYER_SPEED * math.sin(self.direction)

        # Clamp the player to the screen area
        self.x = min(max(self.x, self.size), WIDTH - self.size)
        self.y = min(max(self.y, self.size), HEIGHT - self.size)

        if button['A']:
            self.fire()

        new_proj = []
        for projectile in self.projectiles:
            projectile.update()
            if projectile.is_on_screen():
                new_proj.append(projectile)

        self.projectiles = new_proj

    def hit(self):
        self.was_hit = True
        self.pad.set_leds(0b1111)

    def draw(self, display):
        x, y = int(self.x), int(self.y)
        display.set_pen(WHITE)
        display.circle(x, y, self.size)
        display.set_pen(BLACK) if not self.was_hit else display.set_pen(RED)
        display.circle(x, y, self.size - 1)
        self.was_hit = False
        self.pad.set_leds(self.pad.address_code())

        # Draw the direction line in our colour
        display.set_pen(self.colour)
        display.line(x, y,
                     int(self.x + (LINE_LENGTH * math.cos(self.direction))),
                     int(self.y + (LINE_LENGTH * math.sin(self.direction))))

        # Draw the projectiles in our colour
        display.set_pen(self.colour)
        for p in self.projectiles:
            p.draw(display)

        # Draw our score at the bottom of the screen
        display.set_pen(self.colour)
        display.text(f"P{self.index + 1}: {self.score}", 15 + self.index * 60, 227, WIDTH, 1)

    def check_hits(self, players):
        for other in players:
            if other is not self:
                for projectile in self.projectiles:
                    if projectile.has_hit(other):
                        other.hit()
                        self.score += 1


# Create a player for each connected QwSTPad
for i in range(len(ADDRESSES)):
    try:
        p = PLAYERS[i]
        pad = QwSTPad(i2c, ADDRESSES[i])
        players.append(Player(i, p.x, p.y, PLAYER_RADIUS, p.colour, pad))
        print(f"P{i + 1}: Connected")
    except OSError:
        print(f"P{i + 1}: Not Connected")

if len(players) == 0:
    print("No QwSTPads connected ... Exiting")
    raise SystemExit

print("QwSTPads connected ... Starting")

# Wrap the code in a try block, to catch any exceptions (including KeyboardInterrupt)
try:
    # Loop forever
    while True:
        if not complete:
            # Update all players (and their projectiles)
            for p in players:
                try:
                    p.update()
                # Handle QwSTPads being disconnected unexpectedly
                except OSError:
                    print(f"P{p.index + 1}: Disconnected ... Exiting")
                    raise SystemExit

            # Check if any projectiles have hit players
            for p in players:
                p.check_hits(players)

                # Check if any player has reached the score target
                if p.score >= SCORE_TARGET:
                    complete = True

        # Clear the screen
        display.set_pen(BLACK)
        display.clear()

        # Draw a grid for the background
        display.set_pen(GREY)
        for x in range(10, WIDTH, GRID_SPACING):
            for y in range(10, HEIGHT, GRID_SPACING):
                display.pixel(x, y)

        # Draw players
        for p in players:
            p.draw(display)

        if complete:
            # Draw banner shadow
            display.set_pen(BLACK)
            display.rectangle(4, 94, WIDTH, 50)

            # Draw banner
            display.set_pen(GREEN)
            display.rectangle(0, 90, WIDTH, 50)

            # Draw text shadow
            display.set_pen(BLACK)
            display.text("Game Complete!", 10 + TEXT_SHADOW, 105 + TEXT_SHADOW, WIDTH, 3)

            # Draw text
            display.set_pen(WHITE)
            display.text("Game Complete!", 10, 105, WIDTH, 3)

        # Update the screen
        presto.update()

# Turn off the LEDs of any connected QwSTPads
finally:
    for p in players:
        try:
            p.pad.clear_leds()
        except OSError:
            pass
