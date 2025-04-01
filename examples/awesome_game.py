# NAME awesome_game
# DESC tufty2040 port of awesome_game.py
"""
This is a port of awesome_game.py from the tufty2040 examples
https://github.com/pimoroni/pimoroni-pico/blob/main/micropython/examples/tufty2040/awesome_game.py
"""

import math
from time import sleep
from presto import Presto
import random
import time

# Setup for the Presto display
presto = Presto()
display = presto.display
WIDTH, HEIGHT = display.get_bounds()

# We'll need this for the touch element of the screen
touch = presto.touch

# Load the spreadsheets so we can flip between them
tilemap = bytearray(32_768)
open("s4m_ur4i-pirate-tilemap.16bpp", "rb").readinto(tilemap)

character = bytearray(32_768)
open("s4m_ur4i-pirate-characters.16bpp", "rb").readinto(character)

display.set_spritesheet(character)

class Player():
    def __init__(self):
        self.reset()

    def reset(self):
        self.x = 150
        self.y = 180
        self.w = 15
        self.h = 30
        self.speed = 5
        self.is_alive = True
        self.lives = 3
        self.score = 0
        self.moving = 0

    def move(self, x, y):
        if self.x + x > 0 - self.w and self.x + x < WIDTH - self.w:
            self.x += x
            self.y += y

    def sprite(self):
        display.set_spritesheet(character)
        display.sprite(1, 1 if self.moving else 0, self.x, self.y, 4, 0)


class Treasure():
    def __init__(self):
        self.w = 16
        self.h = 16
        self.randomize()

    def sprite(self):
        if not self.enabled:
            return
        display.set_spritesheet(tilemap)
        display.sprite(4, 2, self.x, self.y, 3, 0)

    def randomize(self):
        self.enabled = True
        self.x = random.randint(15, WIDTH - 60)
        self.y = HEIGHT - 50


class Block():
    def __init__(self):
        self.w = 16
        self.h = 16
        self.is_alive = True
        self.randomize()

    def move(self):
        self.y += self.speed

    def sprite(self):
        display.set_spritesheet(character)
        display.sprite(10, 8, self.x, self.y, 4, 0)

    def randomize(self):
        self.last_update = time.time()
        self.x = random.randint(10, WIDTH - self.w - 10)
        self.y = -self.h
        # was originally 4-12, but 12 felt too fast
        # self.speed = random.randint(4, 12)
        self.speed = random.randint(2, 4)



class Game():
    def __init__(self, FPS_COUNTER=False):
        self.player = Player()
        self.block = []
        self.last_new_block = 0

        self.treasure = Treasure()
        self.last_treasure = 0

        self.SKY = display.create_pen(72, 180, 224)
        #FPS setup
        self.show_fps = FPS_COUNTER
        self.fps_start_time = time.time()
        self.fps_counter = 0
        self.current_fps = 0

        for _i in range(5):
            self.block.append(Block())

    def reset(self):
        for i in range(7):
            presto.set_led_rgb(i, 0, 0, 0)
        for block in self.block:
            block.randomize()

        self.treasure.randomize()
        self.player.reset()
        if self.show_fps:
            self.current_fps = 0
            self.fps_counter = 0
            self.fps_start_time = time.time()

    def get_input(self):
        x = touch.x
        if x > 120:
            self.player.move(self.player.speed, 0)
            self.player.moving = 0
        if x < 120:
            self.player.move(-self.player.speed, 0)
            self.player.moving = 1

    def background(self):
        display.set_spritesheet(tilemap)
        display.set_pen(self.SKY)
        display.clear()

        for i in range(WIDTH / 32):
            display.sprite(1, 2, i * 32, 210, 4, 0)

    def draw(self):
        self.background()
        for block in self.block:
            block.sprite()
        display.set_pen(0xFFFF)
        display.text("Score: " + str(self.player.score), 10, 10, 320, 2)
        self.treasure.sprite()
        display.set_pen(0)
        self.player.sprite()
        if self.show_fps:
            #1 for every second
            self.fps_counter += 1
            if (time.time() - self.fps_start_time) > 1:
                self.current_fps = self.fps_counter / (time.time() - self.fps_start_time)
                self.fps_counter = 0
                self.fps_start_time = time.time()
            display.set_pen(0xFFFF)
            display.text("FPS: " + str(math.floor(self.current_fps)), 175, 10, 320, 2)
        display.update()

    def check_collision(self, a, b):
        return a.x + a.w >= b.x and a.x <= b.x + b.w and a.y + a.h >= b.y and a.y <= b.y + b.h

    def update(self):
        for block in self.block:
            block.move()
            if block.y > HEIGHT:
                block.randomize()

            if block.y + block.h >= self.player.y and self.check_collision(self.player, block):
                block.randomize()
                self.player.is_alive = False

        if self.treasure.enabled:
            if self.check_collision(self.player, self.treasure):
                self.player.score += 1
                if 0 < self.player.score < 8:
                    for i in range(self.player.score):
                        # turn a light gold
                        presto.set_led_rgb(i, 255, 215, 0)
                self.treasure.enabled = False
                self.last_treasure = time.time()

        if time.time() - self.last_treasure > 2:
            if not self.treasure.enabled:
                self.treasure.randomize()

        if self.player.lives == 0:
            self.player.is_alive = False



game = Game(FPS_COUNTER=True)
while True:

    touch.poll()
    game.background()
    display.set_pen(0xFFFF)
    display.text("ARGH!", 40, 35, 200, 5)
    display.text("Touch screen to Start", 80, 150, 180, 1)
    display.update()

    while not touch.state:
        presto.update()

    while game.player.is_alive:
        if touch.state:
            game.get_input()
        game.update()
        game.draw()
        presto.update()

    game.background()
    display.set_pen(0xFFFF)
    display.text("OOPS!", 40, 35, 200, 5)
    display.text("Your score:  " + str(game.player.score), 50, 150, 180, 2)
    display.update()
    presto.update()
    #Added a because if you are still touching the screen may breeze pass the scoring screen
    sleep(.5)
    # See if the display is still being touched after the sleep
    touch.poll()
    while not touch.state:
        presto.update()

    game.reset()
    presto.update()
