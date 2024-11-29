import plasma
import micropython


class Reactive(object):
    # Map the seven backlight LEDs to zones in the display buffer.
    # By default we're using 80 x 80 sections and sampling 64 points within that space.
    # The sampled values are averaged to produce a final output colour.
    def __init__(self, surface, width=240, height=240, sample_size=80, sample_every=10):
        self.mv = surface if isinstance(surface, memoryview) else memoryview(surface)

        MAX = width - sample_size
        MID = width // 2 - sample_size // 2
        MIN = 0

        # A section of the screen we'll use for sampling.
        # Define this function locally so we don't need to pass width, sample_size and sample_every.
        def zone(index, x, y):
            # Calculate the X an dY coordinates in terms of RGB56 / two bytes per pixel
            x_range = tuple(range(x * 2, (x + sample_size) * 2, sample_every * 2))
            y_range = tuple(range(y * 2, (y + sample_size) * 2, sample_every * 2))

            # Calculate the offsets for every pixel we need to sample.
            # Coerce to a tuple, it's faster to iterate.
            pixels = tuple([y * width + x for y in y_range for x in x_range])

            return index, pixels

        # The index for each section matches the index for the Backlight LED.
        # Zone 0 is in the bottom right corner LED as you're looking at the screen.
        # The LEDs proceed around the screen counter-clockwise.
        # Use a tuple, it's faster to iterate.
        self.zones = (zone(0, MAX, MAX), zone(1, MAX, MID), zone(2, MAX, MIN),
                      zone(3, MID, MIN), zone(4, MIN, MIN), zone(5, MIN, MID),
                      zone(6, MIN, MAX))

        self.samples = len(self.zones[0][1])

        self.bl = plasma.WS2812(7, 0, 0, 33)
        self.bl.start()

    def clear(self):
        self.bl.clear()

    def set_rgb(self, i, r, g, b):
        self.bl.set_rgb(i, r, g, b)

    @micropython.native
    def update(self):
        mv = self.mv
        _ = self.samples  # It's repeatably faster with this line
        # For each zone, get the average colour in that area and set the corresponding LED to that colour
        for i, pixels in self.zones:
            # Running total of the RGB values
            r_value, g_value, b_value = 0, 0, 0

            for offset in pixels:
                # Grab the pixel colour value back from the framebuffer
                # This will be in RGB565 - RRRRRGGGGGGBBBBB
                # This is faster as 3 separate operations than a single line
                rgb = mv[offset]
                rgb <<= 8
                rgb |= mv[offset + 1]

                # Sort and arrange those bits into their approximate 8bit R G and B values.
                # We can't get back the exact value due to the destructive nature of converting RGB888 to RGB565,
                # but it's close enough for displaying a colour on the backlight :)
                r_value += (rgb >> 8) & 0b11111000
                g_value += (rgb >> 3) & 0b11111100
                b_value += (rgb << 3) & 0b11111000

            # Take the average of our values and set the backlight LED
            # total // samples is faster than int(total / samples)
            self.bl.set_rgb(
                i,
                r_value // self.samples,
                g_value // self.samples,
                b_value // self.samples
            )
