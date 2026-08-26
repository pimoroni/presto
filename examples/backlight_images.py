"""
A demo that flips between 2 images and changes the backlighting
"""

import time

from picovector import image

from presto import Presto

# File names for your 2 images. The reactive backlighting works best with images that match the resolution of the screen
# In this example we're running at 240 x 240

IMAGE_1 = "image1.jpg"
IMAGE_2 = "image2.jpg"

# Setup for the Presto display
presto = Presto(ambient_light=True)
display = presto.display
WIDTH, HEIGHT = display.width, display.height

# Decode both up front rather than once per frame
images = (image.load(IMAGE_1), image.load(IMAGE_2))

flip = True

while True:

    # Select opposite image to what's currently shown
    display.blit(images[0] if flip else images[1], 0, 0)
    flip = not flip

    # Finally we update the screen with our changes :)
    presto.update()
    time.sleep(1)
