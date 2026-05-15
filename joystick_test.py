import time
from machine import ADC, Pin
from picographics import PicoGraphics, DISPLAY_PICO_EXPLORER

display = PicoGraphics(display=DISPLAY_PICO_EXPLORER)
W, H = display.get_bounds()

BLK = display.create_pen(0,   0,   0)
WHT = display.create_pen(240, 240, 240)
RED = display.create_pen(220, 30,  30)
GRN = display.create_pen(30,  200, 30)
YEL = display.create_pen(240, 220, 0)
GRY = display.create_pen(100, 100, 100)
BLU = display.create_pen(40,  100, 240)

joy_x = ADC(26)
joy_y = ADC(27)
joy_btn = Pin(28, Pin.IN, Pin.PULL_UP)

px, py = W // 2, H // 2
DEAD = 3000
SPEED = 3

while True:
    xr = joy_x.read_u16()
    yr = joy_y.read_u16()
    btn = joy_btn.value()

    dx = xr - 32768
    dy = yr - 32768

    if abs(dx) > DEAD:
        px += SPEED if dx > 0 else -SPEED
    if abs(dy) > DEAD:
        py += SPEED if dy > 0 else -SPEED

    px = max(8, min(W - 8, px))
    py = max(40, min(H - 8, py))

    display.set_pen(BLK)
    display.clear()

    display.set_pen(GRY)
    display.line(0, 30, W, 30)
    display.set_pen(WHT)
    display.text("TESTE JOYSTICK", 10, 8, W, 2)

    display.set_pen(GRY)
    display.line(W // 2, 35, W // 2, H)
    display.line(0, H // 2, W, H // 2)

    dot_pen = GRN if not btn else RED
    display.set_pen(dot_pen)
    display.rectangle(px - 6, py - 6, 12, 12)

    display.set_pen(YEL)
    display.text("X: {:5d}".format(xr), 5, H - 55, W, 1)
    display.text("Y: {:5d}".format(yr), 5, H - 40, W, 1)
    display.set_pen(GRN if not btn else RED)
    display.text("SW: {}".format("PREMIDO" if not btn else "SOLTO"), 5, H - 25, W, 1)

    display.update()
    time.sleep_ms(30)
