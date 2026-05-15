import time
import random
from machine import ADC, Pin, PWM
from picographics import PicoGraphics, DISPLAY_PICO_EXPLORER

# ---------------------------------------------------------------------------
# Hardware
# ---------------------------------------------------------------------------
display  = PicoGraphics(display=DISPLAY_PICO_EXPLORER)
W, H     = display.get_bounds()

joy_x    = ADC(26)
joy_y    = ADC(27)
joy_btn  = Pin(28, Pin.IN, Pin.PULL_UP)
BTN_Y    = Pin(15, Pin.IN, Pin.PULL_UP)   # extra start/restart button

BUZZER   = PWM(Pin(0))
BUZZER.duty_u16(0)

# ---------------------------------------------------------------------------
# Pens
# ---------------------------------------------------------------------------
BLK  = display.create_pen(0,   0,   0)
WHT  = display.create_pen(240, 240, 240)
RED  = display.create_pen(220, 30,  30)
GRN  = display.create_pen(30,  200, 30)
BLU  = display.create_pen(40,  100, 240)
YEL  = display.create_pen(240, 220, 0)
ORG  = display.create_pen(240, 130, 0)
GRY  = display.create_pen(80,  80,  80)
DRK  = display.create_pen(18,  18,  18)
LGN  = display.create_pen(20,  140, 20)   # snake body
HGN  = display.create_pen(60,  240, 60)   # snake head
DGRY = display.create_pen(35,  35,  35)   # grid dot

# ---------------------------------------------------------------------------
# Grid config
# ---------------------------------------------------------------------------
CELL   = 8
HEADER = 28
COLS   = W // CELL            # 30 on a 240-px wide display
ROWS   = (H - HEADER) // CELL # 26 on a 240-px tall display

# ---------------------------------------------------------------------------
# Timing / difficulty
# ---------------------------------------------------------------------------
DEAD_ZONE = 8000  # joystick dead zone for direction detection
TICK_START = 200  # ms between moves at start
TICK_MIN   = 70   # fastest possible tick
TICK_STEP  = 8    # ms shaved per food eaten

# ---------------------------------------------------------------------------
# States
# ---------------------------------------------------------------------------
ST_TITLE   = 0
ST_PLAYING = 1
ST_DEAD    = 2

# ---------------------------------------------------------------------------
# Audio helpers
# ---------------------------------------------------------------------------
def _beep(freq, dur):
    BUZZER.freq(freq)
    BUZZER.duty_u16(3000)
    time.sleep_ms(dur)
    BUZZER.duty_u16(0)

def snd_eat():
    _beep(660, 25)

def snd_die():
    for f in (440, 330, 220):
        _beep(f, 70)
        time.sleep_ms(15)

def snd_start():
    for f in (330, 440, 550, 660):
        _beep(f, 40)
        time.sleep_ms(10)

# ---------------------------------------------------------------------------
# Drawing helpers
# ---------------------------------------------------------------------------
def _cell_rect(cx, cy, pen):
    display.set_pen(pen)
    display.rectangle(cx * CELL + 1, cy * CELL + HEADER + 1, CELL - 2, CELL - 2)

def _draw_header(score, hi):
    display.set_pen(DRK)
    display.rectangle(0, 0, W, HEADER)
    display.set_pen(HGN)
    display.text("SNAKE", 4, 5, 80, 2)
    display.set_pen(YEL)
    score_str = "{:04d}".format(score)
    display.text(score_str, W // 2 - 16, 5, 60, 2)
    display.set_pen(GRY)
    display.text("HI:{:04d}".format(hi), W - 74, 5, 80, 2)

def _draw_grid():
    display.set_pen(DGRY)
    for r in range(ROWS):
        for c in range(COLS):
            display.pixel(c * CELL + CELL // 2, r * CELL + HEADER + CELL // 2)

def draw_game(snake, food, score, hi):
    display.set_pen(BLK)
    display.clear()
    _draw_grid()
    _cell_rect(food[0], food[1], ORG)
    for seg in snake[1:]:
        _cell_rect(seg[0], seg[1], LGN)
    _cell_rect(snake[0][0], snake[0][1], HGN)
    _draw_header(score, hi)
    display.update()

def draw_title(hi):
    display.set_pen(BLK)
    display.clear()
    # Title
    display.set_pen(HGN)
    display.text("SNAKE", 48, H // 2 - 65, W, 4)
    # Instructions
    display.set_pen(WHT)
    display.text("Mova o joystick", 30, H // 2 - 5, W, 1)
    display.text("para controlar a cobra.", 20, H // 2 + 12, W, 1)
    display.set_pen(YEL)
    display.text("Coma a comida laranja.", 20, H // 2 + 30, W, 1)
    display.set_pen(GRY)
    display.text("Nao bata nas paredes", 25, H // 2 + 48, W, 1)
    display.text("nem em si mesmo!", 38, H // 2 + 62, W, 1)
    # Prompt
    display.set_pen(GRN)
    display.text("[ Botao joystick / Y ]", 18, H // 2 + 88, W, 1)
    display.text("para iniciar", 62, H // 2 + 102, W, 1)
    # Hi-score
    if hi > 0:
        display.set_pen(ORG)
        display.text("Recorde: {:04d}".format(hi), 62, H - 22, W, 1)
    display.update()

def draw_dead(score, hi):
    display.set_pen(BLK)
    display.clear()
    display.set_pen(RED)
    display.text("FIM DE JOGO", 22, H // 2 - 55, W, 2)
    display.set_pen(WHT)
    display.text("Pontos: {:04d}".format(score), 60, H // 2 - 5, W, 2)
    if score >= hi and score > 0:
        display.set_pen(YEL)
        display.text("** NOVO RECORDE! **", 20, H // 2 + 28, W, 1)
    display.set_pen(GRY)
    display.text("Recorde: {:04d}".format(hi), 64, H // 2 + 46, W, 1)
    display.set_pen(GRN)
    display.text("[ Botao ] jogar de novo", 14, H // 2 + 75, W, 1)
    display.update()

# ---------------------------------------------------------------------------
# Input helpers
# ---------------------------------------------------------------------------
def read_dir():
    """Return (dx, dy) direction from joystick, or None if centred."""
    xr = joy_x.read_u16()
    yr = joy_y.read_u16()
    dx = xr - 32768
    dy = yr - 32768
    if abs(dx) > abs(dy):
        if dx > DEAD_ZONE:
            return (1, 0)
        if dx < -DEAD_ZONE:
            return (-1, 0)
    else:
        if dy > DEAD_ZONE:
            return (0, 1)
        if dy < -DEAD_ZONE:
            return (0, -1)
    return None

def any_pressed():
    return joy_btn.value() == 0 or BTN_Y.value() == 0

def wait_release():
    while any_pressed():
        time.sleep_ms(20)
    time.sleep_ms(60)

def new_food(snake):
    while True:
        pos = (random.randint(0, COLS - 1), random.randint(0, ROWS - 1))
        if pos not in snake:
            return pos

# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------
hi_score = 0
state    = ST_TITLE

while True:

    # ── Title screen ────────────────────────────────────────────────────────
    if state == ST_TITLE:
        draw_title(hi_score)
        while not any_pressed():
            time.sleep_ms(30)
        wait_release()
        snd_start()
        state = ST_PLAYING

    # ── Playing ─────────────────────────────────────────────────────────────
    elif state == ST_PLAYING:
        cx, cy    = COLS // 2, ROWS // 2
        snake     = [(cx, cy), (cx - 1, cy), (cx - 2, cy)]
        direction = (1, 0)
        pending   = (1, 0)
        food      = new_food(snake)
        score     = 0
        tick_ms   = TICK_START
        last_tick = time.ticks_ms()
        alive     = True

        draw_game(snake, food, score, hi_score)

        while alive:
            # Read joystick – only queue direction change if not reversing
            jd = read_dir()
            if jd is not None:
                if not (jd[0] == -direction[0] and jd[1] == -direction[1]):
                    pending = jd

            now = time.ticks_ms()
            if time.ticks_diff(now, last_tick) >= tick_ms:
                last_tick  = now
                direction  = pending
                hx = snake[0][0] + direction[0]
                hy = snake[0][1] + direction[1]

                # Wall collision
                if hx < 0 or hx >= COLS or hy < 0 or hy >= ROWS:
                    alive = False
                    break

                # Self collision
                if (hx, hy) in snake:
                    alive = False
                    break

                snake.insert(0, (hx, hy))

                if (hx, hy) == food:
                    score   += 10
                    tick_ms  = max(TICK_MIN, tick_ms - TICK_STEP)
                    food     = new_food(snake)
                    snd_eat()
                else:
                    snake.pop()

                draw_game(snake, food, score, hi_score)

            time.sleep_ms(14)

        snd_die()
        if score > hi_score:
            hi_score = score
        state = ST_DEAD

    # ── Game-over screen ────────────────────────────────────────────────────
    elif state == ST_DEAD:
        draw_dead(score, hi_score)
        while not any_pressed():
            time.sleep_ms(30)
        wait_release()
        state = ST_PLAYING
