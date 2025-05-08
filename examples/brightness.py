from presto import Presto
from touch import Button
from time import sleep

presto = Presto()
display = presto.display

FG_COLOR = display.create_pen(0, 0, 255)
BG_COLOR = display.create_pen(255, 255, 255)

touch = presto.touch

button_down = Button(10, 125, 105, 105)
button_up = Button(125, 125, 105, 105)

brightness = 100

while True:
    touch.poll()

    display.set_pen(BG_COLOR)
    display.clear()
    
    display.set_pen(FG_COLOR)
    display.text("brightness: " + str(brightness)+ " %", 10, 10)

    display.rectangle(*button_down.bounds)
    display.rectangle(*button_up.bounds)

    if button_down.is_pressed():
        brightness -= 1
        if brightness < 0: brightness = 0

    if button_up.is_pressed():
        brightness += 1
        if brightness > 100: brightness = 100
        
    presto.set_backlight(brightness / 100)
    
    presto.update()
    sleep(0.02)


