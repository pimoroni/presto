from picovector import color, font

from presto import Presto

# Setup for the Presto display
presto = Presto(ambient_light=True)
display = presto.display
WIDTH, HEIGHT = display.width, display.height

# Text needs a vector font loaded before it can be drawn
display.font = font.load("Roboto-Medium.af")

# Couple of colours for use later
BLUE = color.rgb(28, 181, 202)
WHITE = color.rgb(255, 255, 255)


while True:

    # Clear the screen and use blue as the background colour
    display.pen = BLUE
    display.clear()
    # Set the pen to a different colour otherwise we won't be able to see the text!
    display.pen = WHITE

    # draw the text
    display.text("Hello!", 10, 85, 48)

    # Finally we update the screen with our changes :)
    presto.update()
