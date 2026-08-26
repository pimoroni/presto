import random

from picovector import color

from presto import Presto

# Setup for the Presto display
presto = Presto()
display = presto.display
WIDTH, HEIGHT = display.width, display.height


class Ball:
    def __init__(self, x, y, r, dx, dy, pen):
        self.x = x
        self.y = y
        self.r = r
        self.dx = dx
        self.dy = dy
        self.pen = pen


# initialise shapes
balls = []
for _ in range(170):
    r = random.randint(0, 10) + 3
    balls.append(
        Ball(
            random.randint(r, r + (WIDTH - 2 * r)),
            random.randint(r, r + (HEIGHT - 2 * r)),
            r,
            (14 - r) / 2,
            (14 - r) / 2,
            color.rgb(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)),
        )
    )

BG = color.rgb(40, 40, 40)

while True:

    display.pen = BG
    display.clear()

    for ball in balls:
        ball.x += ball.dx
        ball.y += ball.dy

        xmax = WIDTH - ball.r
        xmin = ball.r
        ymax = HEIGHT - ball.r
        ymin = ball.r

        if ball.x < xmin or ball.x > xmax:
            ball.dx *= -1

        if ball.y < ymin or ball.y > ymax:
            ball.dy *= -1

        display.pen = ball.pen
        display.circle(int(ball.x), int(ball.y), int(ball.r))

    # Finally we update the screen with our changes :)
    presto.update()
