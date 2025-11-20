# PicoVector

PicoVector is a vector graphics library for the Raspberry Pi Pico.

Instead of painting individual pixels, it deals with points and paths which
make up shapes from simple rectangles to complex UI elements or typography.


## Getting Started

To get started with PicoVector on Presto you must first import and set it up
by passing in your PicoGraphics surface:

```python
from presto import Presto
from picovector import PicoVector, Polygon, Transform, ANTIALIAS_BEST

presto = Presto()
vector = PicoVector(presto.display)

transform = Transform()
vector.set_transform(transform)

vector.set_antialiasing(ANTIALIAS_BEST)
```

## Transforms

Scaling and rotating vectors is accomplished with a `Transform` and happens
when one is drawn. In most cases it will suffice to create one `Transform`
and then apply rotation and scale as needed.

* `rotate(angle, (x, y))` - rotate polygons by `angle` in degrees
around point `(x, y)`.
* `scale(scale_x, scale_y)` - apply a scale, change the size of polygons
* `translate(x, y)` - apply a translation, change the position of polygons
* `matrix([1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0])` - apply an arbitrary matrix transformation
* `reset()` - reset the transform object back to the default (no transform)

Internally transforms are matrix operations, so the order you apply them
both matters and may be counter-intuitive.

If, for example, you want to rotate something in the middle of the screen
you'll find that you need to rotate it *first* and then translate it into
position. Eg:

```python
shape = Polygon()
shape.path((-10, -20), (10, 0), (-10, 20))

transform = Transform()
transform.translate(presto.width // 2, presto.height // 2)
transform.rotate(a, (0, 0))

vector.set_transform(transform)
vector.draw(shape)
```

## Antialiasing

Behind the scenes all of PicoVector's drawing is done by PicoGraphics- by
setting pixels. Unlike just directly drawing shapes with pixels PicoVector
includes anti-aliasing, a smoothing technique that turns diagonal lines
into the crisp, blended edges we'd expect from computers today.

Available options are:

* `ANTIALIAS_NONE` - turns off anti-aliasing for best performance
* `ANTIALIAS_FAST` - 4x anti-aliasing, a good balance between speed & quality
* `ANTIALIAS_BEST` - 16x anti-aliasing, best quality at the expense of speed

## Polygons & Primitives

The basis of all drawing operations in PicoVector is the `Polygon` object.

A `Polygon` is a collection of one or more paths to be drawn together. This
allows for shapes with holes - letters, for example - or more complicated
designs - logos or icons - to be scaled, rotated and drawn at once.

If paths overlap then the top-most path will "punch" out the one underneath.

To use any of the primitives or path drawing methods you must first create
a `Polygon`, for example here's a simple triangle:

```python
from picovector import Polygon
my_shape = Polygon()
my_shape.path((10, 0), (0, 10), (20, 10))
```

### Path

* `path((x, y), (x2, y2), (x3, y3), ...)`

A path is simply an arbitrary list of points that produce a complete closed
shape. It's ideal for drawing complex shapes such as logos or icons. The
shape will be filled.

If you have a list of points you can use Python's spread operator to pass it
into `path`, eg:

```python
my_points = [(10, 0), (0, 10), (20, 10)]
my_shape = Polygon()
my_shape.path(*my_points)
```

### Line

* `line(x1, y1, x2, y2, thickness)`

Creates a single line from one point to the other, drawn at the specified
thickness. This is useful if you want to draw a path but do not want it to
be filled.

### Rectangle

* `rectangle(x, y, w, h, corners=(r1, r2, r3, r4), stroke=0)`

A rectangle is a plain old rectangular shape with optional rounded corners.

If `stroke` is greater than zero then the rectangle outline will be produced.

If any of the corner radii are greater than zero then that corner will be created.

### Regular

* `regular(x, y, radius, sides, stroke=0)`

Creates a regular polygon with the given radius and number of sides. Needs at
least 3 sides (an equilateral triangle) and converges on a circle.

If `stroke` is greater than zero then the regular polygon outline will be created.

### Circle

* `circle(x, y, radius, stroke=0)`

Effectively a regular polygon, approximates a circle by automatically picking
a number of sides that will look smooth for a given radius.

If `stroke` is greater than zero then the circle outline will be created.

### Arc

* `arc(x, y, radius, from, to, stroke=0)`

Create an arc at x, y with radius, from and to angle (degrees).

Great for radial graphs.

If `stroke` is greater than zero then the arc outline will be created.

### Star

* `star(x, y, points, inner_radius, outer_radius, stroke=0)`

Create a star at x, y with given number of points.

The inner and outer radius (in pixels) define where the points start and end.

If `stroke` is greater than zero then the arc outline will be created.

## Fonts & Text

Under the hood PicoVector uses [Alright Fonts](https://github.com/lowfatcode/alright-fonts)
a font-format for embedded and low resource platforms.

Alright Fonts supports converting TTF and OTF fonts into .af format which can
then be displayed using PicoVector. Most of your favourite fonts should work, including silly fonts like [Jokerman](https://en.wikipedia.org/wiki/Jokerman_(typeface)) - but there are some limitations to their complexity.

### Converting

Converting from an OTF or TTF font is done with the `afinate` utility. It's a 
Python script that handles decomposing the font into a simple list of points.

The latest version of this conversion utility can be found at the repo below, along with installation instructions and some pre-converted sample fonts:

- [PicoVector Fonts / Alright Fonts](https://github.com/pimoroni/picovector-fonts)

### Loading & Configuring

```python
vector.set_font("jokerman.af", 24)
```

`set_font` specifies the font and size.

Your *.af font file will need to be present on Presto's file system, you can upload it using Thonny's Files window or another means like `mpremote`.

### Spacing & Alignment

* `set_font_size()` 
* `set_font_word_spacing()`
* `set_font_letter_spacing()`
* `set_font_line_height()`
* `set_font_align()`

### Measuring Text

* `x, y, w, h = measure_text(text, x=0, y=0, angle=None)`

Returns a four tuple with the x, y position, width and height in pixels.

### Drawing Text

* `text(text, x, y, angle=None, max_width=0, max_height=0)`

When you draw text the x, y position and angle are used to create a new
Transform to control the position and rotation of your text. The transform
set with `.set_transform()` is also applied.
