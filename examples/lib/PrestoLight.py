import plasma
from struct import unpack
from micropython import const


class Section(object):
    # A section of the screen we'll use for sampling.
    # We're using 80 x 80 sections and sampling 49 points within that space
    def __init__(self, x, y):
        self.X = const(x)
        self.Y = const(y)
        self.WIDTH = const(80)
        self.HEIGHT = const(80)
        self.colours = []

        # Pre calculate the range to use later
        self.x_range = range(self.X, self.X + self.WIDTH, 10)
        self.y_range = range(self.Y, self.Y + self.HEIGHT, 10)

    @micropython.native
    def return_avg(self, display):

        # Running total of the RGB values for our average calculation later
        r_value, g_value, b_value = 0, 0, 0

        # Counter
        c = 0

        for x in self.x_range:
            for y in self.y_range:

                # Grab the pixel colour value back from the framebuffer
                offset = (y * 240 + x) * 2
                mv = memoryview(display)
                rgb = mv[offset:offset + 2]
                rgb = unpack("<H", rgb)

                # Now we need to sort and arrange those bits into their R G and B values
                # We can't get back the exact value due to the destructive nature of converting to RGB565
                # But it's close enough for displaying a colour on the backlight :)

                r = (rgb[0] >> 3) & 0b00011111
                g = (rgb[0] >> 13) & 0b00000111 | rgb[0] << 3 & 0b00111000
                b = (rgb[0] >> 8) & 0b00011111

                # Scale the raw RGB values and add them to our running total
                r_value += r << 3
                g_value += g << 2
                b_value += b << 3

                # Add 1 to the counter
                c += 1

        # Now we finish the average calculation and return the value as an integer
        r_value = int(r_value / c)
        g_value = int(g_value / c)
        b_value = int(b_value / c)

        return (r_value, g_value, b_value)


class Reactive(object):
    def __init__(self):

        # Some consts for the max, mid and min points
        MAX = const(160)
        MID = const(80)
        MIN = const(0)

        # The index for each section matches the index for the Backlight LED
        # Section 0 and LED 0 is in the bottom right corner as you're looking at the screen
        self.sections = [Section(MAX, MAX), Section(MAX, MID), Section(MAX, MIN), Section(MID, MIN),
                         Section(MIN, MIN), Section(MIN, MID), Section(MIN, MAX)]

        # Plasma setup
        self.bl = plasma.WS2812(7, 0, 0, 33)
        self.bl.start()

    def update(self, display):
        # For each section we get the average colour in that area and set the backlight LED to that colour
        for i, section in enumerate(self.sections):
            colour = section.return_avg(display)
            self.bl.set_rgb(i, colour[0], colour[1], colour[2])
