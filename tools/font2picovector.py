#!/usr/bin/env python3
import argparse
import math
import freetype
from simplification.cutil import simplify_coords_vwp


"""
Tool for converting a single glyph from a font into a set of PicoVector contours.

Set up a venv and `pip install simplification freetype-py`.

Material Symbols:

Presto icons use MaterialSymbolsOutlined-Regular.ttf. To generate your own:

    - Find your icon from: https://fonts.google.com/icons

    - Click the icon and scroll down the right pane until you see "Code point."

    - Copy the "Code point" - eg: f564 - this is the number you give to font2picovector.py.

Example usage:

    python font2picovector.py --font Some_Font.otf --size 40x40 f564

    > loading font: Some_Font.otf
    > decomposing: f564
    > target bounds: 40.00 x 40.00
    > source bounds: 511.00 x 511.00
    > scale: 12.775000 x 12.775000
    > scale factor: 12.775000
    > scaled bounds: 0.06 -34.98 39.99 5.01
    > offset: -20.03:14.99
    > result: 4 contours with 85 points

    # ICON [[(19.9, -0.04), (17.65, -0.32), ...

To load into PicoVector omit the `# ICON` and instead set the point list to a variable:

    MY_ICON_CONTOURS = [[(19.9, -0.04), (17.65, -0.32), ...

Then load them into a new `Polygon()`:

    my_icon = Polygon()
    for contour in MY_ICON_CONTOURS:
        my_icon.path(*contour)
"""

try:
    from PIL import Image, ImageDraw
    pil_found = True
except ImportError:
    pil_found = False


class Point:
    def __init__(self, *args):
        if isinstance(args[0], (tuple, list)):
            self.x = args[0][0]
            self.y = args[0][1]
        else:
            self.x = args[0]
            self.y = args[1]

    def set(self, other):
        self.x = other.x
        self.y = other.y

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Point(self.x - other.x, self.y - other.y)

    def __div__(self, other):
        if isinstance(other, Point):
            return Point(self.x / other.x, self.y / other.y)
        if isinstance(other, (int, float)):
            return Point(self.x / other, self.y / other)
        raise ValueError

    __truediv__ = __div__

    def __mul__(self, other):
        if isinstance(other, Point):
            return Point(self.x * other.x, self.y * other.y)
        if isinstance(other, (int, float)):
            return Point(self.x * other, self.y * other)
        raise ValueError

    __rmul__ = __mul__

    def __round__(self, dp=0):
        return Point(round(self.x, dp), round(self.y, dp))

    def distance(self, other):
        dx = abs(self.x - other.x)
        dy = abs(self.y - other.y)
        return math.sqrt(dx * dx + dy * dy)

    def __repr__(self):
        return "({}, {})".format(self.x, self.y)

    @staticmethod
    def parse_arg(arg):
        return Point(*(int(c) for c in arg.split("x")))


class Bounds:
    def __init__(self, *args):
        if len(args) == 1 and isinstance(args[0], freetype.BBox):
            bb = args[0]
            self.x = bb.xMin
            self.x2 = bb.xMax
            self.y = bb.yMin
            self.y2 = bb.yMax
        elif len(args) == 2:
            width, height = args
            self.x = -width / 2
            self.y = -height / 2
            self.x2 = width / 2
            self.y2 = height / 2
        else:
            self.x, self.y, self.x2, self.y2 = args

    def update(self, point):
        self.x = min(self.x, point.x)
        self.y = min(self.y, point.y)
        self.x2 = max(self.x2, point.x)
        self.y2 = max(self.y2, point.y)

    @property
    def width(self):
        return self.x2 - self.x

    @property
    def height(self):
        return self.y2 - self.y

    @property
    def contour(self):
        return [
            Point(self.x, self.y),
            Point(self.x2, self.y),
            Point(self.x2, self.y2),
            Point(self.x, self.y2),
        ]

    @staticmethod
    def parse_arg(arg):
        return Bounds(*(int(c) for c in arg.split("x")))


def load_glyph(face, codepoint, quality=30, precision=2, target_bounds=None, offset=None, include_bounding_box=False):
    # glyph doesn't exist in face
    if face.get_char_index(codepoint) == 0:
        return None

    target_bounds = target_bounds or Bounds(50, 50)
    offset = offset or Point(0, 0)

    # load the glyph
    face.load_char(codepoint, freetype.FT_LOAD_PEDANTIC)

    source_bounds = Bounds(face.glyph.outline.get_bbox())

    scale_x = source_bounds.width / target_bounds.width
    scale_y = source_bounds.height / target_bounds.height

    scale_factor = max(scale_x, scale_y)

    print(f"> target bounds: {target_bounds.width:.2f} x {target_bounds.height:.2f}")
    print(f"> source bounds: {source_bounds.width:.2f} x {source_bounds.height:.2f}")
    print(f"> scale: {scale_x:.6f} x {scale_y:.6f}")
    print(f"> scale factor: {scale_factor:.6f}")

    # extract glyph contours
    contours = []

    def move_to(p, ctx):
        # Move to always starts a new contour
        ctx.append([[p.x, p.y]])

    def line_to(a, ctx):
        ctx[-1].append([a.x, a.y])

    def quadratic_bezier(t, src, c1, dst):
        return [
            (1 - t) * (1 - t) * src.x + 2 * (1 - t) * t * c1.x + t * t * dst.x,
            (1 - t) * (1 - t) * src.y + 2 * (1 - t) * t * c1.y + t * t * dst.y,
        ]

    def conic_to(c1, dst, ctx):
        # Draw a quadratic bezier from the previous point to dst, with control c1

        # Get the source point (last point in this contour)
        src = Point(ctx[-1][-1][0], ctx[-1][-1][1])
        c1 = Point(c1.x, c1.y)
        dst = Point(dst.x, dst.y)

        distance = int(src.distance(c1) + c1.distance(dst))
        # print(f"> Decomposing conic curve with approx distance: {distance}")

        # simplify_coords_vwp will discard overlapping/proximal/redundant coords
        for i in range(distance):
            ctx[-1].append(quadratic_bezier(i / distance, src, c1, dst))

    def cubic_bezier(t, src, c1, c2, dst):
        return [
            ((1 - t) ** 3) * src.x
            + 3 * ((1 - t) ** 2) * t * c1.x
            + 3 * (1 - t) * (t**2) * c2.x
            + (t**3) * dst.x,
            ((1 - t) ** 3) * src.y
            + 3 * ((1 - t) ** 2) * t * c1.y
            + 3 * (1 - t) * (t**2) * c2.y
            + (t**3) * dst.y,
        ]

    def cubic_to(c1, c2, dst, ctx):
        # Draw a cubic bezier from the previous point to dst, with controls c1 and c2

        # Get the source point (last point in this contour)
        src = Point(ctx[-1][-1][0], ctx[-1][-1][1])
        c1 = Point(c1.x, c1.y)
        c2 = Point(c2.x, c2.y)
        dst = Point(dst.x, dst.y)

        distance = int(src.distance(c1) + c1.distance(c2) + c2.distance(dst))
        # print(f"> Decomposing cubic curve with approx distance: {distance}")

        # simplify_coords_vwp will discard overlapping/proximal/redundant coords
        for i in range(distance):
            ctx[-1].append(cubic_bezier(i / distance, src, c1, c2, dst))

    face.glyph.outline.decompose(contours, move_to=move_to, line_to=line_to, conic_to=conic_to, cubic_to=cubic_to)

    # Simplify, scale and round the final contours
    for i, c in enumerate(contours):
        contours[i] = [
            Point(p) / Point(scale_factor, -scale_factor)
            for p in simplify_coords_vwp(c, quality)
        ]

    # Get the scaled bounding box
    actual_bounds = Bounds(65535, 65535, -65535, -65535)

    for c in contours:
        for point in c:
            actual_bounds.update(point)

    print(f"> scaled bounds: {actual_bounds.x:.2f} {actual_bounds.y:.2f} {actual_bounds.x2:.2f} {actual_bounds.y2:.2f}")

    # Cancel out any offset to align to the top left
    offset += Point(-actual_bounds.x, -actual_bounds.y)

    # Calculate an offset based on the bounding box and center the result
    offset.x += (target_bounds.width - actual_bounds.width) / 2
    offset.y += (target_bounds.height - actual_bounds.height) / 2

    # Move to the center of our target bounds
    offset.x -= target_bounds.width / 2
    offset.y -= target_bounds.height / 2

    print(f"> offset: {offset.x:.2f}:{offset.y:.2f}")

    for c in contours:
        for p in c:
            p.set(round(p + offset, precision))

    if include_bounding_box:
        contours.insert(0, target_bounds.contour)

    # A contour *must* have at least three points. Discard any invalid contours.
    old_size = len(contours)
    contours = [contour for contour in contours if len(contour) > 2]

    print(f"> result: {len(contours)} contours with {sum(len(c) for c in contours)} points")

    if old_size > len(contours):
        print(f"> result: {old_size - len(contours)} invalid contour(s) skipped!")

    return contours


# parse command line arguments
# ===========================================================================

parser = argparse.ArgumentParser(
    description="Create an PicoVector-compatible contour list from a chosen glyph/font."
)
parser.add_argument(
    "--font",
    type=argparse.FileType("rb"),
    required=True,
    help="the font (.ttf or .otf) that you want to extract glyphs from",
)
parser.add_argument(
    "--size",
    type=Bounds.parse_arg,
    required=False,
    default=Bounds(50, 50),
    help="Target width/height, eg: 50x50."
)
parser.add_argument(
    "--offset",
    type=Point.parse_arg,
    required=False,
    default=Point(0, 0),
    help="Offset x/y, eg: 12x0."
)
parser.add_argument("codepoint", type=lambda n: int(n, 16), help="glyph to output")
args = parser.parse_args()


# load the requested font file
# ===========================================================================

print(f"\n> loading font: {args.font.name}")

font = freetype.Face(args.font.name)

print(f"> decomposing: {args.codepoint:04x}")

contours = load_glyph(font, args.codepoint, target_bounds=args.size, offset=args.offset)
print(f"\n# ICON {contours}\n")

# If PIL is available, output a debug image

if pil_found:
    image_scale = 10
    image_width = int(args.size.width * image_scale)
    image_height = int(args.size.height * image_scale)

    img = Image.new("RGB", (image_width + 2, image_height + 2), (0, 0, 0))
    draw = ImageDraw.Draw(img)

    for contour in contours:
        i_contour = [(c.x * image_scale + (image_width // 2) + 1, c.y * image_scale + (image_height // 2) + 1) for c in contour]
        draw.polygon(i_contour, fill=None, outline=(255, 255, 255))

    img.save(f"test-{args.codepoint:04x}-{int(args.size.width)}x{int(args.size.height)}.png")
