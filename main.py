import time
import random
from machine import Pin, PWM

try:
    from picographics import PicoGraphics, DISPLAY_PICO_EXPLORER
except:
    try:
        from picographics import PicoGraphics
        DISPLAY_PICO_EXPLORER = 1
    except:
        print("ERROR: picographics not found")
        raise

BTN_A = Pin(12, Pin.IN, Pin.PULL_UP)
BTN_B = Pin(13, Pin.IN, Pin.PULL_UP)
BTN_X = Pin(14, Pin.IN, Pin.PULL_UP)
BTN_Y = Pin(15, Pin.IN, Pin.PULL_UP)
BUZZER = PWM(Pin(0))
BUZZER.duty_u16(0)

try:
    display = PicoGraphics(display=DISPLAY_PICO_EXPLORER)
except:
    print("ERROR: PicoGraphics init failed")
    raise

W, H = display.get_bounds()

BLACK  = display.create_pen(0, 0, 0)
WHITE  = display.create_pen(255, 255, 255)
RED    = display.create_pen(255, 0, 0)
GREEN  = display.create_pen(0, 255, 0)
BLUE   = display.create_pen(0, 0, 255)
YELLOW = display.create_pen(255, 255, 0)

def beep(f=880, ms=100):
    BUZZER.freq(f)
    BUZZER.duty_u16(1000)
    time.sleep_ms(ms)
    BUZZER.duty_u16(0)

def read_btn():
    while True:
        if not BTN_A.value():
            time.sleep_ms(50)
            if not BTN_A.value():
                while not BTN_A.value():
                    time.sleep_ms(10)
                time.sleep_ms(50)
                return "A"
        if not BTN_B.value():
            time.sleep_ms(50)
            if not BTN_B.value():
                while not BTN_B.value():
                    time.sleep_ms(10)
                time.sleep_ms(50)
                return "B"
        if not BTN_X.value():
            time.sleep_ms(50)
            if not BTN_X.value():
                while not BTN_X.value():
                    time.sleep_ms(10)
                time.sleep_ms(50)
                return "X"
        if not BTN_Y.value():
            time.sleep_ms(50)
            if not BTN_Y.value():
                while not BTN_Y.value():
                    time.sleep_ms(10)
                time.sleep_ms(50)
                return "Y"
        time.sleep_ms(20)

def clr(c=BLACK):
    display.set_pen(c)
    display.clear()
    display.update()

def txt(s, x, y, sc=2, c=WHITE):
    display.set_pen(c)
    display.text(s, x, y, W, sc)

def show_timer(sec, strikes):
    m, s = sec // 60, sec % 60
    txt("{:02d}:{:02d}".format(m, s), 80, 6, 2, RED if sec < 60 else GREEN)
    txt("X" * strikes, 180, 6, 2, WHITE)

def draw_header(strikes, sec):
    display.set_pen(BLACK)
    display.rectangle(0, 0, W, 30)
    show_timer(sec, strikes)

def game_screen():
    clr()
    txt("KEEP TALKING", 20, 50, 3, RED)
    txt("& NOBODY", 40, 100, 3, WHITE)
    txt("EXPLODES", 40, 140, 3, WHITE)
    txt("Y para empezar", 30, 200, 2, GREEN)
    display.update()
    while read_btn() != "Y":
        pass

def end_screen(won):
    clr(GREEN if won else RED)
    txt("GANASTE!" if won else "PERDISTE", 40, 100, 4, WHITE)
    display.update()
    beep(1000, 200)
    time.sleep(1)
    clr()
    txt("Y para reiniciar", 30, 150, 2, WHITE)
    display.update()
    while read_btn() != "Y":
        pass

def simple_game():
    strikes = 0
    solved = 0
    t_end = time.time() + 300
    
    # Game loop
    while strikes < 3 and solved < 5 and time.time() < t_end:
        clr()
        sec_left = int(t_end - time.time())
        draw_header(strikes, sec_left)
        
        txt("TEST", 100, 80, 3, YELLOW)
        txt("Pulsa A/B/X/Y", 40, 150, 2, WHITE)
        txt("Fallos: {}".format(strikes), 40, 200, 2, RED)
        display.update()
        
        b = read_btn()
        if b in ("A", "B", "X", "Y"):
            if random.randint(0, 1) == 0:
                clr(GREEN)
                txt("BIEN!", 80, 100, 4, WHITE)
                display.update()
                beep(1000, 100)
                solved += 1
                time.sleep(1)
            else:
                clr(RED)
                txt("MAL!", 80, 100, 4, WHITE)
                display.update()
                beep(200, 100)
                strikes += 1
                time.sleep(1)
    
    return solved == 5

def main():
    try:
        game_screen()
        won = simple_game()
        end_screen(won)
        main()
    except Exception as e:
        clr(RED)
        txt("ERROR", 50, 100, 3, WHITE)
        txt(str(e)[:25], 10, 150, 1, WHITE)
        display.update()

if __name__ == "__main__":
    main()
