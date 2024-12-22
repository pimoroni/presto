'''
A demo that flips between 2 images and changes the backlighting
'''

import time

import jpegdec
from presto import Presto

# File names for your 2 images. The reactive backlighting works best with images that match the resolution of the screen
# In this example we're running at 240 x 240

IMAGE_1 = "image1.jpg"
IMAGE_2 = "image2.jpg"

# Setup for the Presto display
presto = Presto(ambient_light=True)
display = presto.display
WIDTH, HEIGHT = display.get_bounds()

# Setup JPEG decoder
j = jpegdec.JPEG(display)

flip = True

while True:

    # Select opposite image to what's currently shown
    if flip:
        j.open_file(IMAGE_1)

    else:
        j.open_file(IMAGE_2)

    j.decode(0, 0, jpegdec.JPEG_SCALE_FULL, dither=True)
    flip = not flip

    # Finally we update the screen with our changes :)
    presto.update()
    time.sleep(1)
