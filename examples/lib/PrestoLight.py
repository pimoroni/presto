import plasma
from struct import unpack


class Section(object):
    # A section is an 30 x 30 area of the screen
    # Of this section we will then use 100 sample points to get the average colour
    def __init__(self, x, y):
        self.X = const(x)
        self.Y = const(y)
        self.WIDTH = const(80)
        self.HEIGHT = const(80)
        self.colours = []
        self.x_range = range(self.X, self.X + self.WIDTH, 12)
        self.y_range = range(self.Y, self.Y + self.HEIGHT, 12)

    @micropython.native
    def return_avg(self, display):

        r_value, g_value, b_value = 0, 0, 0
        c = 0

        for x in self.x_range:
            for y in self.y_range:

                offset = (y * 240 + x) * 2
                mv = memoryview(display)
                rgb = mv[offset:offset + 2]
                rgb = unpack("<H", rgb)

                # GGGBBBBBRRRRRGGG
                r = (rgb[0] >> 3) & 0b00011111
                g = (rgb[0] >> 13) & 0b00000111 | rgb[0] << 3 & 0b00111000
                b = (rgb[0] >> 8) & 0b00011111

                # Scale and add to total
                r_value += r << 3
                g_value += g << 2
                b_value += b << 3

                c += 1

        r_value = int(r_value / c)
        g_value = int(g_value / c)
        b_value = int(b_value / c)

        return (r_value, g_value, b_value)


class Reactive(object):
    def __init__(self):

        MAX = const(160)
        MID = const(80)
        MIN = const(0)

        self.sections = [Section(MAX, MAX), Section(MAX, MID), Section(MAX, MIN), Section(MID, MIN),
                         Section(MIN, MIN), Section(MIN, MID), Section(MIN, MAX)]

        # Plasma setup
        self.bl = plasma.WS2812(7, 0, 0, 33)
        self.bl.start()

    def update(self, display):
        for i, section in enumerate(self.sections):
            colour = section.return_avg(display)
            self.bl.set_rgb(i, colour[0], colour[1], colour[2])
