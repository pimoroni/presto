import plasma
import micropython


class Zone(object):
    SIZE = 80

    # A section of the screen we'll use for sampling.
    # We're using 80 x 80 sections and sampling 49 points within that space
    def __init__(self, x, y, width=240):
        self.colours = []

        # Pre calculate the ranges to use later
        # Calculates the coordinates in terms of RGB56 / two bytes per pixel
        self.x_range = range(x * 2, (x + self.SIZE) * 2, 10 * 2)
        self.y_range = range(y * 2, (y + self.SIZE) * 2, 10 * 2)

        # Calculate the offsets for every pixel we need to sample
        # A tuple is slightly less expensive than a list to iterate
        self.pixels = tuple([y * width + x for y in self.y_range for x in self.x_range])
        self.samples = len(self.pixels)

    @micropython.native
    def return_avg(self, mv):
        # Running total of the RGB values for our average calculation later
        r_value, g_value, b_value = 0, 0, 0

        for offset in self.pixels:
            # Grab the pixel colour value back from the framebuffer
            # This will be in RGB565 - RRRRRGGGGGGBBBBB
            rgb = (mv[offset] << 8) | mv[offset + 1]

            # Now we need to sort and arrange those bits into their R G and B values
            # We can't get back the exact value due to the destructive nature of converting to RGB565
            # But it's close enough for displaying a colour on the backlight :)
            # We're shifting the 5, 6 and 5 bits into the most significant places
            r_value += (rgb >> 8) & 0b11111000
            g_value += (rgb >> 3) & 0b11111100
            b_value += (rgb << 3) & 0b11111000

        # Now we finish the average calculation and return the value as an integer
        return (
            int(r_value / self.samples),
            int(g_value / self.samples),
            int(b_value / self.samples)
        )


class Reactive(object):
    def __init__(self, surface, width=240, height=240):
        self.mv = surface if isinstance(surface, memoryview) else memoryview(surface)

        MAX = width - Zone.SIZE
        MID = width // 2 - Zone.SIZE // 2
        MIN = 0
        W = width

        # The index for each section matches the index for the Backlight LED
        # Zone 0 is in the bottom right corner LED as you're looking at the screen
        # And the LEDs proceed around counter-clockwise
        # A tuple is slightly less expensive than a list to iterate
        self.zones = (Zone(MAX, MAX, W), Zone(MAX, MID, W), Zone(MAX, MIN, W), Zone(MID, MIN, W),
                      Zone(MIN, MIN, W), Zone(MIN, MID, W), Zone(MIN, MAX, W))

        self.bl = plasma.WS2812(7, 0, 0, 33)
        self.bl.start()

    @micropython.native
    def update(self):
        mv = self.mv
        i = 0
        # For each section we get the average colour in that area and set the backlight LED to that colour
        for zone in self.zones:
            self.bl.set_rgb(i, *zone.return_avg(mv))
            i += 1
