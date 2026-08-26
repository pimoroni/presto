# ICON photo-library
# NAME Photo Frame
# DESC A touch enabled image gallery

"""
An image gallery demo to turn your Pimoroni Presto into a desktop photo frame!

- Create a folder called 'gallery' on the root of your SD card and fill it with JPEGs.
- The image will change automatically every 5 minutes
- You can also tap the right side of the screen to skip next image and left side to go to the previous :)

"""
import os
import time

import machine
import sdcard
import uos
from picovector import color, font, image

from presto import Presto

# The total number of LEDs to set, the Presto has 7
NUM_LEDS = 7

# Seconds between changing the image on screen
# This interval shows us a new image every 5 minutes
INTERVAL = 60 * 5

LEDS_LEFT = [4, 5, 6]
LEDS_RIGHT = [0, 1, 2]

# Setup for the Presto display
presto = Presto()
display = presto.display
WIDTH, HEIGHT = display.width, display.height

display.font = font.load("Roboto-Medium.af")

BACKGROUND = color.rgb(1, 1, 1)
WHITE = color.rgb(255, 255, 255)
BLACK = color.rgb(0, 0, 0)

# We'll need this for the touch element of the screen
touch = presto.touch

# JPEG Dec

# Where our images are located
directory = "gallery"

# Stores the total number of images in the user gallery
total_image_count = 0

# Store our current location within the user gallery
current_image = 0

lfsr = 1
tap = 0xdc29


# Display an error msg on screen and keep it looping
def display_error(text):
    while 1:
        display.pen = BACKGROUND
        display.clear()
        display.pen = WHITE
        display.text(f"Error: {text}", 10, 10, 8)
        presto.update()
        time.sleep(1)


try:
    print("Setting up SD card")
    # Setup for SD Card
    sd_spi = machine.SPI(0, sck=machine.Pin(34, machine.Pin.OUT), mosi=machine.Pin(35, machine.Pin.OUT), miso=machine.Pin(36, machine.Pin.OUT))
    sd = sdcard.SDCard(sd_spi, machine.Pin(39))

    print("Mounting SD Card")
    # Mount the SD to the directory 'sd'
    uos.mount(sd, "/sd")

    # ADD THIS - Give the SD card time to settle
    time.sleep(1)

    # if the gallery folder exists on the SD card we want to use the images in there!
    if os.stat("sd/gallery"):
        print("Found SD Gallery")
        directory = "sd/gallery"
    else:
        print("Did not find SD Card Gallery")
except OSError as error:
    print(f"Error setting up SD Card - {repr(error)}")


def numberedfiles(k):
    try:
        return int(k[:-4])
    except ValueError:
        pass
    return 0


try:
    files = [file for file in sorted(os.listdir(directory), key=numberedfiles) if file.endswith((".jpg", ".jpeg"))]
except OSError:
    display_error("Problem loading images.\n\nEnsure that your Presto or SD card contains a 'gallery' folder in the root")

total_image_count = len(files) - 1
print(f"Found {total_image_count} files")

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


# Layer 1 used to be dissolved away to reveal the new image on layer 0. There
# are no layers, so the new frame is composed off-screen and copied across
# pixel by pixel instead.
def fizzlefade(frame):
    while True:

        for _ in range(2000):
            x, y = return_point()
            if x > -1 and y > -1:
                display.pen = frame.get(x, y)
                display.put(x, y)
            if lfsr == 1:
                break

        presto.update()
        if lfsr == 1:
            break

def reinit_sd():
    """Reinitialize SD card to recover from SPI errors"""
    global sd_spi, sd
    try:
        # Give the SD card a moment to reset
        time.sleep(0.1)
        # Reinitialize the SPI and SD card
        sd_spi = machine.SPI(0, sck=machine.Pin(34, machine.Pin.OUT), mosi=machine.Pin(35, machine.Pin.OUT), miso=machine.Pin(36, machine.Pin.OUT))
        sd = sdcard.SDCard(sd_spi, machine.Pin(39))
        time.sleep(0.1)
        return True
    except OSError:
        return False


def show_image(show_next=False, show_previous=False):

    print("show_image called")

    global current_image
    global total_image_count

    # Get the next image in the gallery
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

    print(f"image index {str(current_image)}/{str(total_image_count)}")

    try:
        img = f"{directory}/{files[current_image]}"

        print(f"reading {img} into memory")

        # Read the entire JPEG file into memory first
        with open(img, "rb") as f:
            jpeg_data = f.read()

        print(f"read {len(jpeg_data)} bytes, decoding")

        picture = image.load(jpeg_data)

        print(f"opened {img}")

        img_height, img_width = picture.height, picture.width

        img_x = 0
        img_y = 0

        if img_width < WIDTH:
            img_x = (WIDTH // 2) - (img_width // 2)

        if img_height < HEIGHT:
            img_y = (HEIGHT // 2) - (img_height // 2)

        print(f"img_x: {img_x}")
        print(f"img_y: {img_y}")

        frame = image(WIDTH, HEIGHT)
        frame.pen = BACKGROUND
        frame.clear()
        frame.blit(picture, img_x, img_y)

        fizzlefade(frame)

        display.blit(frame, 0, 0)

    except OSError as e:
        print(f"OSError details: {e}")
        display_error("Unable to find/read file.\n\nCheck that the 'gallery' folder in the root of your SD card contains JPEG images!")
    except IndexError:
        display_error(f"Unable to read images in the '{directory}' folder.\n\nCheck the files are present and are in JPEG format.")


def clear():
    display.pen = BACKGROUND
    display.clear()

# Test SD card access before showing images
print("\n=== SD Card Diagnostic Test ===")
try:
    test_files = os.listdir("sd/gallery")
    print(f"✓ Can list directory: {len(test_files)} files")

    test_file = f"sd/gallery/{test_files[0]}"
    print(f"Testing file: {test_file}")

    # Try opening with standard Python file operations
    with open(test_file, "rb") as f:
        test_data = f.read(1000)
        print(f"✓ Can read with open(): {len(test_data)} bytes")

    # Now try decoding
    print("Testing image.load()...")
    test_image = image.load(test_file)
    print("Decoded successfully!")
    print(f"  Image size: {test_image.width}x{test_image.height}")

except Exception as e:  # noqa: BLE001 - example code: report the failure rather than crash the demo
    print(f"✗ Test failed: {type(e).__name__}: {e}")
    # The decode test failed and corrupted SPI - reinitialize!
    print("Reinitializing SD card after failed decode test...")
    reinit_sd()
    time.sleep(0.5)

print("=== End Diagnostic ===\n")

# Store the last time the screen was updated
last_updated = time.time()

# Show the first image on the screen so it's not just noise :)
clear()
show_image()
presto.update()

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
                presto.set_led_rgb(i, 255, 255, 255)
            show_image(show_next=True)
            presto.update()
            last_updated = time.time()
            for i in LEDS_RIGHT:
                presto.set_led_rgb(i, 0, 0, 0)
            time.sleep(0.01)

        # Left half of the screen moves to the previous image
        elif touch.x < WIDTH // 2:
            for i in LEDS_LEFT:
                presto.set_led_rgb(i, 255, 255, 255)
            show_image(show_previous=True)
            presto.update()
            last_updated = time.time()
            for i in LEDS_LEFT:
                presto.set_led_rgb(i, 0, 0, 0)
            time.sleep(0.01)

        # Wait here until the user stops touching the screen
        while touch.state:
            touch.poll()
            time.sleep(0.02)

