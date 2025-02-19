#!/bin/env python3
from PIL import Image
import numpy
import sys
import pathlib

# This scripts takes and converts an image to a format you can load with the PicoGraphics sprite methods
# https://github.com/pimoroni/pimoroni-pico/blob/main/micropython/modules/picographics/README.md#sprites
# The sprite sheets displays and loads best if your image is 128x128 with each sprite being 8x8
# An example can be seen in the assets of 32blint-games repo
# https://github.com/mikerr/32blit-games/tree/37daeaacdb661e2f9a47e3682859234b9b849226/sprite-browser/assets

# Run with `./filename.py source-image.jpg`
IMAGE_PATH = pathlib.Path(sys.argv[1])
OUTPUT_PATH = IMAGE_PATH.with_suffix(".16bpp")


def image_to_data(image):
    """Generator function to convert a PIL image to 16-bit 565 RGB bytes."""
    # Convert the image to RGB (ignoring alpha if present)
    image = image.convert('RGB')

    # Convert the image to a NumPy array
    pb = numpy.array(image).astype('uint16')

    # Extract the RGB channels
    r = (pb[:, :, 0] >> 3) & 0x1F  # 5 bits for red
    g = (pb[:, :, 1] >> 2) & 0x3F  # 6 bits for green
    b = (pb[:, :, 2] >> 3) & 0x1F  # 5 bits for blue

    # Pack the RGB channels into a 16-bit 565 format
    color = (r << 11) | (g << 5) | b

    # Flatten the array and convert to bytes
    return color.byteswap().tobytes()

img = Image.open(IMAGE_PATH)
w, h = img.size
data = image_to_data(img)

print(f"Converted: {w}x{h} {len(data)} bytes")

with open(OUTPUT_PATH, "wb") as f:
    f.write(data)

print(f"Written to: {OUTPUT_PATH}")