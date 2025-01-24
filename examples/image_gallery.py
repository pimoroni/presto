'''
An image gallery demo to turn your Pimoroni Presto into a desktop photo frame!

- Create a folder called 'gallery' on the root of your SD card and fill it with JPEGs.
- The image will change automatically every 5 minutes
- You can also tap the right side of the screen to skip next image and left side to go to the previous :)

'''
import os
import time

import jpegdec
import machine
import plasma
import sdcard
import uos
from presto import Presto

# The total number of LEDs to set, the Presto has 7
NUM_LEDS = 7

# Where our images are located on the SD card
DIR = 'sd/gallery'

# Seconds between changing the image on screen
# This interval shows us a new image every 5 minutes
INTERVAL = 60 * 5

LEDS_LEFT = [4, 5, 6]
LEDS_RIGHT = [0, 1, 2]

# Setup for the Presto display
presto = Presto()
display = presto.display
WIDTH, HEIGHT = display.get_bounds()

BACKGROUND = display.create_pen(1, 1, 1)
WHITE = display.create_pen(255, 255, 255)
BLACK = display.create_pen(0, 0, 0)

# We'll need this for the touch element of the screen
touch = presto.touch

# JPEG Dec
j = jpegdec.JPEG(display)

# Plasma setup
bl = plasma.WS2812(7, 0, 0, 33)
bl.start()

# Stores the total number of images in the user gallery
total_image_count = 0

# Store our current location within the user gallery
current_image = 0

lfsr = 1
tap = 0xdc29


# Display an error msg on screen and keep it looping
def display_error(text):
    while 1:
        display.set_pen(BACKGROUND)
        display.clear()
        display.set_pen(WHITE)
        display.text(f"Error: {text}", 10, 10, WIDTH - 10, 1)
        presto.update()
        time.sleep(1)


try:
    # Setup for SD Card
    sd_spi = machine.SPI(0, sck=machine.Pin(34, machine.Pin.OUT), mosi=machine.Pin(35, machine.Pin.OUT), miso=machine.Pin(36, machine.Pin.OUT))
    sd = sdcard.SDCard(sd_spi, machine.Pin(39))

    # Mount the SD to the directory 'sd'
    uos.mount(sd, "/sd")
except OSError:
    display_error("Unable to mount SD card")


def numberedfiles(k):
    try:
        return int(k[:-4])
    except ValueError:
        pass
    return 0


files = list(sorted(os.listdir("sd/gallery"), key=numberedfiles))
total_image_count = len(files) - 1


def return_point():
    global lfsr

    x = lfsr & 0x00ff
    y = (lfsr & 0xff00) >> 8

    lsb = lfsr & 1
    lfsr >>= 1

    if lsb:
        lfsr ^= tap

    if x - 1 < 240 and y < 240:
        return x - 1, y

    return -1, -1


def fizzlefade():
    display.set_pen(BLACK)
    display.set_layer(1)

    while True:

        for i in range(2000):
            x, y = return_point()
            if x > -1 and y > -1:
                display.pixel(x, y)
            if lfsr == 1:
                break

        presto.update()
        if lfsr == 1:
            break


def show_image(show_next=False, show_previous=False):
    global current_image
    global total_image_count

    # Get the next image in the gallery
    # If we're at the end of the gallery, loop back and start from 1.
    if show_next:
        if current_image < total_image_count:
            current_image += 1
        else:
            current_image = 0
    if show_previous:
        if current_image > 0:
            current_image -= 1
        else:
            current_image = total_image_count

    # Open the index file and read lines until we're at the correct position
    try:
        img = f"sd/gallery/{files[current_image]}"

        j.open_file(img)

        img_height, img_width = j.get_height(), j.get_width()

        img_x = 0
        img_y = 0

        # if the image isn't exactly 240x240 then we'll try to centre the image
        if img_width < WIDTH:
            img_x = (WIDTH // 2) - (img_width // 2)

        if img_height < HEIGHT:
            img_y = (HEIGHT // 2) - (img_height // 2)

        display.set_layer(0)
        display.set_pen(BACKGROUND)
        display.clear()
        j.decode(img_x, img_y, jpegdec.JPEG_SCALE_FULL, dither=True)

        fizzlefade()

        # Now draw the current image to Layer 1
        display.set_layer(1)
        # Decode the JPEG
        j.decode(img_x, img_y, jpegdec.JPEG_SCALE_FULL, dither=True)

    except OSError:
        display_error("Unable to find/read file.\n\nCheck that the 'gallery' folder in the root of your SD card contains JPEG images!")


def clear():
    display.set_pen(BACKGROUND)
    display.set_layer(0)
    display.clear()
    display.set_layer(1)
    display.clear()


# Store the last time the screen was updated
last_updated = time.time()

# Show the first image on the screen so it's not just noise :)
# We're not passing the arg for 'show_next' or 'show_previous' so it'll show whichever image is current
clear()
show_image()
presto.update()

while True:

    # Poll the touch so we can see if anything changed since the last time
    touch.poll()

    # Check if it's time to update the image!
    if time.time() - last_updated > INTERVAL:

        last_updated = time.time()
        show_image(show_next=True)
        presto.update()

    # if the screen is reporting that there is touch we want to handle that here
    if touch.state:
        # Right half of the screen moves to the next image
        # The LEDs on the right side of the presto light up to show it is working
        if touch.x > WIDTH // 2:
            for i in LEDS_RIGHT:
                bl.set_rgb(i, 255, 255, 255)
            show_image(show_next=True)
            presto.update()
            last_updated = time.time()
            for i in LEDS_RIGHT:
                bl.set_rgb(i, 0, 0, 0)
            time.sleep(0.01)

        # Left half of the screen moves to the previous image
        elif touch.x < WIDTH // 2:
            for i in LEDS_LEFT:
                bl.set_rgb(i, 255, 255, 255)
            show_image(show_previous=True)
            presto.update()
            last_updated = time.time()
            for i in LEDS_LEFT:
                bl.set_rgb(i, 0, 0, 0)
            time.sleep(0.01)

        # Wait here until the user stops touching the screen
        while touch.state:
            touch.poll()
            time.sleep(0.02)
