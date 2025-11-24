# ICON [[(-6.0, 2.0), (14.0, 2.0), (7.1, -7.0), (2.5, -1.0), (-0.6, -5.0), (-6.0, 2.0)], [(-8.0, 10.0), (-8.77, 9.93), (-10.0, 9.49), (-10.81, 8.88), (-11.53, 7.91), (-11.87, 7.04), (-12.0, 6.05), (-12.0, -18.0), (-11.72, -19.5), (-11.15, -20.47), (-10.47, -21.14), (-9.78, -21.58), (-8.86, -21.91), (-8.05, -22.0), (16.0, -22.0), (16.82, -21.92), (18.02, -21.44), (18.51, -21.07), (19.42, -20.05), (19.83, -19.17), (20.0, -18.05), (20.0, 6.0), (19.7, 7.54), (19.37, 8.16), (18.65, 8.99), (17.36, 9.77), (16.05, 10.0), (-8.0, 10.0)], [(-8.0, 6.0), (16.0, 6.0), (16.0, -18.0), (-8.0, -18.0), (-8.0, 6.0)], [(-16.0, 18.0), (-16.73, 17.94), (-17.83, 17.58), (-18.81, 16.88), (-19.26, 16.35), (-19.79, 15.31), (-20.0, 14.05), (-20.0, -14.0), (-16.0, -14.0), (-16.0, 14.0), (12.0, 14.0), (12.0, 18.0), (-16.0, 18.0)], [(-8.0, -18.0), (-8.0, -18.0)]]
# NAME Photo Frame
# DESC A touch enabled image gallery

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

# Where our images are located
directory = 'gallery'

# Stores the total number of images in the user gallery
total_image_count = 0

# Store our current location within the user gallery
current_image = 0

lfsr = 1
tap = 0xdc29


# Display an error msg on screen and keep it looping
def display_error(text):
    while 1:
        for i in range(2):
            display.set_layer(i)
            display.set_pen(BACKGROUND)
            display.clear()
        display.set_pen(WHITE)
        display.text(f"Error: {text}", 10, 10, WIDTH - 10, 1)
        presto.update()
        time.sleep(1)


try:
    print('Setting up SD card')
    # Setup for SD Card
    sd_spi = machine.SPI(0, sck=machine.Pin(34, machine.Pin.OUT), mosi=machine.Pin(35, machine.Pin.OUT), miso=machine.Pin(36, machine.Pin.OUT))
    sd = sdcard.SDCard(sd_spi, machine.Pin(39))

    print('Mounting SD Card')
    # Mount the SD to the directory 'sd'
    uos.mount(sd, "/sd")

    # ADD THIS - Give the SD card time to settle
    time.sleep(1)

    # if the gallery folder exists on the SD card we want to use the images in there!
    if os.stat('sd/gallery'):
        print('Found SD Gallery')
        directory = 'sd/gallery'
    else:
        print('Did not find SD Card Gallery')
except OSError as error:
    print(f'Error setting up SD Card - {repr(error)}')
    pass


def numberedfiles(k):
    try:
        return int(k[:-4])
    except ValueError:
        pass
    return 0


try:
    files = list(file for file in sorted(os.listdir(directory), key=numberedfiles) if file.endswith('.jpg') or file.endswith('.jpeg'))
except OSError:
    display_error("Problem loading images.\n\nEnsure that your Presto or SD card contains a 'gallery' folder in the root")

total_image_count = len(files) - 1
print(f'Found {total_image_count} files') 

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
    except:
        return False


def show_image(show_next=False, show_previous=False):
    
    print(f'show_image called')
    
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

    print(f'image index {str(current_image)}/{str(total_image_count)}')

    try:
        img = f"{directory}/{files[current_image]}"
        
        print(f'reading {img} into memory')
        
        # Read the entire JPEG file into memory first
        with open(img, 'rb') as f:
            jpeg_data = f.read()
        
        print(f'read {len(jpeg_data)} bytes, opening with jpegdec')
        
        # Now open from RAM instead of file
        j.open_RAM(jpeg_data)
        
        print(f'opened {img}')

        img_height, img_width = j.get_height(), j.get_width()

        img_x = 0
        img_y = 0

        if img_width < WIDTH:
            img_x = (WIDTH // 2) - (img_width // 2)

        if img_height < HEIGHT:
            img_y = (HEIGHT // 2) - (img_height // 2)

        print(f'img_x: {img_x}')
        print(f'img_y: {img_y}')        
        
        display.set_layer(0)
        display.set_pen(BACKGROUND)
        display.clear()
        j.decode(img_x, img_y, jpegdec.JPEG_SCALE_FULL, dither=True)

        fizzlefade()

        display.set_layer(1)
        j.decode(img_x, img_y, jpegdec.JPEG_SCALE_FULL, dither=True)

    except OSError as e:
        print(f"OSError details: {e}")
        display_error("Unable to find/read file.\n\nCheck that the 'gallery' folder in the root of your SD card contains JPEG images!")
    except IndexError:
        display_error(f"Unable to read images in the '{directory}' folder.\n\nCheck the files are present and are in JPEG format.")


def clear():
    display.set_pen(BACKGROUND)
    display.set_layer(0)
    display.clear()
    display.set_layer(1)
    display.clear()

# Test SD card access before showing images
print("\n=== SD Card Diagnostic Test ===")
try:
    test_files = os.listdir('sd/gallery')
    print(f"✓ Can list directory: {len(test_files)} files")
    
    test_file = f'sd/gallery/{test_files[0]}'
    print(f"Testing file: {test_file}")
    
    # Try opening with standard Python file operations
    with open(test_file, 'rb') as f:
        test_data = f.read(1000)
        print(f"✓ Can read with open(): {len(test_data)} bytes")
    
    # Now try with jpegdec
    print(f"Testing jpegdec.open_file()...")
    j.open_file(test_file)
    print(f"✓ jpegdec opened successfully!")
    print(f"  Image size: {j.get_width()}x{j.get_height()}")
    
except Exception as e:
    print(f"✗ Test failed: {type(e).__name__}: {e}")
    # The jpegdec test failed and corrupted SPI - reinitialize!
    print("Reinitializing SD card after failed jpegdec test...")
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

