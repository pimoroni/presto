import presto

import time

from picovector import PicoVector, Polygon, Transform, ANTIALIAS_X16, VALIGN_TOP

presto = presto.Presto(full_res=True)

display = presto.display

vector = PicoVector(display)
t = Transform()
vector.set_transform(t)
vector.set_antialiasing(ANTIALIAS_X16)

vector.set_font("antonio.af", 24)
vector.set_font_align(VALIGN_TOP)
vector.set_font_line_height(100)

WIDTH, HEIGHT = presto.width, presto.height

RED = display.create_pen(200, 0, 0)
BLACK = display.create_pen(0, 0, 0)
GREY = display.create_pen(200, 200, 200)
WHITE = display.create_pen(255, 255, 255)

BLUE = display.create_pen(40, 60, 180)
LBLUE = display.create_pen(40, 140, 180)

ORANGE = display.create_pen(180, 100, 40)
LORANGE = display.create_pen(200, 140, 40)

GRIDLINE = display.create_pen(40, 40, 60)
GRIDLINE_MAJOR = display.create_pen(50, 50, 75)

# 2, 3, 4, 5, 6, 8, 10, 12, 15
GRID_SPACING = 12


def Grid_Units(n):
    return int(n * GRID_SPACING)


class Region:
    def __init__(self, x, y, w, h):
        self.set_region(x, y, w, h)

    def set_region(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def contains(self, x, y):
        if x > self.x and x < self.x + self.w:
            if y > self.y and y < self.y + self.h:
                return True
        return False


class MenuItem(Region):
    def __init__(self, label, fn=None, userdata=None, region=(0, 0, 0, 0)):
        Region.__init__(self, *region)
        self.label = label
        self.selected = False
        self.userdata = userdata
        self.fn = fn

    def test(self, x, y):
        self.selected = self.contains(x, y)

    def render(self):
        if callable(self.fn):
            self.fn(self)


main = Polygon()
main.rectangle(Grid_Units(10), Grid_Units(3), Grid_Units(15), Grid_Units(2), (Grid_Units(2), 0, 0, 0))

top_left = Polygon()
top_left.rectangle(Grid_Units(1), Grid_Units(1), Grid_Units(24), Grid_Units(4), (Grid_Units(2), 0, 0, 0))


def draw_grid(major=5):
    for y in range(WIDTH / GRID_SPACING):
        display.set_pen(GRIDLINE_MAJOR if y % major == 0 else GRIDLINE)
        display.line(0, y * GRID_SPACING, WIDTH, y * GRID_SPACING)
        display.line(y * GRID_SPACING, 0, y * GRID_SPACING, HEIGHT)


def draw_ui(menu_items):
    o_y = 0
    o_x = GRID_SPACING

    display.set_pen(BLUE)

    # Top Ribbon
    vector.draw(top_left)

    # Left-hand Menu
    o_y = Grid_Units(4) + Grid_Units(1) + Grid_Units(1)
    for y in range(len(menu_items)):
        menu_item = menu_items[y]
        display.set_pen(LBLUE if menu_item.selected else BLUE)
        display.rectangle(o_x, o_y, Grid_Units(9), Grid_Units(4))
        menu_item.set_region(o_x, o_y, Grid_Units(9), Grid_Units(4))
        display.set_pen(BLACK)
        o_y += Grid_Units(1)
        tx, ty, tw, th = vector.measure_text(menu_item.label)
        vector.text(menu_item.label, o_x + Grid_Units(8.5) - int(tw), o_y + Grid_Units(3.5) - int(th))
        o_y += Grid_Units(4)

    display.set_pen(BLUE)

    display.rectangle(o_x, o_y, Grid_Units(9), Grid_Units(3))

    o_x += Grid_Units(9) + Grid_Units(1)
    display.set_pen(ORANGE)
    display.rectangle(o_x, o_y, Grid_Units(15), Grid_Units(3))

    o_x += Grid_Units(15) + Grid_Units(0.5)
    display.set_pen(LORANGE)
    display.rectangle(o_x, o_y, Grid_Units(1), Grid_Units(3))

    o_x += Grid_Units(1) + Grid_Units(0.5)
    display.set_pen(ORANGE)
    display.rectangle(o_x, o_y, Grid_Units(11), Grid_Units(3))

    display.set_pen(BLACK)
    vector.draw(main)


def rn_title(title):
    display.set_pen(LORANGE)
    display.rectangle(Grid_Units(25.5), Grid_Units(1), Grid_Units(13.5), Grid_Units(2))
    display.set_pen(BLACK)
    tx, ty, tw, th = vector.measure_text(title)
    vector.text(title, Grid_Units(38.5) - int(tw), Grid_Units(2.5))


def rn_text(menu_item):
    rn_title(menu_item.label)

    display.set_pen(WHITE)
    vector.text(menu_item.userdata, Grid_Units(11), Grid_Units(6), max_width=Grid_Units(28), max_height=Grid_Units(28))


def rn_default(menu_item):
    rn_title(menu_item.label)


menu_items = [
    MenuItem(
        "Test",
        rn_text,
        """It indicates a synchronic distortion in the areas emanating triolic waves.
The cerebellum, the cerebral cortex, the brain stem, the entire nervous system has been depleted of electrochemical energy.
Any device like that would produce high levels of triolic waves. These walls have undergone some kind of selective molecular polarization.
I haven't determined if our phaser energy can generate a stable field. We could alter the photons with phase discriminators.""",
    ),
    MenuItem("Another", rn_text, """This is a test."""),
    MenuItem("Menu", rn_default),
    MenuItem("Item", rn_default),
    MenuItem("To", rn_default),
    MenuItem("Click", rn_default),
]


def draw():
    display.set_pen(BLACK)
    display.clear()
    # draw_grid(5)
    draw_ui(menu_items)

    for menu_item in menu_items:
        if menu_item.selected:
            menu_item.render()
            break

    presto.update()


draw()

while True:
    presto.touch.poll()

    if presto.touch_a.touched:
        print(presto.touch_a.x, presto.touch_a.y)
        if (
            presto.touch_a.x >= Grid_Units(1)
            and presto.touch_a.x <= Grid_Units(10)
            and presto.touch_a.y >= Grid_Units(6)
        ):
            for menu_item in menu_items:
                menu_item.test(presto.touch_a.x, presto.touch_a.y)

        draw()

    time.sleep(1.0 / 60)
