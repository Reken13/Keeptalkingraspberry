"""Keep Talking and Nobody Explodes - Pico Explorer edition.

Requiere firmware Pimoroni MicroPython (incluye picographics).
Probado en Pimoroni Pico Explorer Base con Pico/Pico W.
"""
import time
import random
import gc
from machine import Pin, PWM

from picographics import PicoGraphics, DISPLAY_PICO_EXPLORER, PEN_RGB332

# ---------------------------------------------------------------- HARDWARE
BTN_A = Pin(12, Pin.IN, Pin.PULL_UP)
BTN_B = Pin(13, Pin.IN, Pin.PULL_UP)
BTN_X = Pin(14, Pin.IN, Pin.PULL_UP)
BTN_Y = Pin(15, Pin.IN, Pin.PULL_UP)
BUZZER = PWM(Pin(0))
BUZZER.duty_u16(0)

# Optional LEDs (Simon mirror). Safe if pins unconnected.
LEDS = [Pin(p, Pin.OUT) for p in (6, 7, 8, 9)]
for l in LEDS:
    l.value(0)

display = PicoGraphics(display=DISPLAY_PICO_EXPLORER, pen_type=PEN_RGB332, rotate=0)
W, H = display.get_bounds()

# Color pens (RGB332)
BLACK  = display.create_pen(0, 0, 0)
WHITE  = display.create_pen(240, 240, 240)
RED    = display.create_pen(220, 30, 30)
GREEN  = display.create_pen(30, 200, 30)
BLUE   = display.create_pen(40, 80, 240)
YELLOW = display.create_pen(240, 220, 0)
ORANGE = display.create_pen(240, 140, 0)
GREY   = display.create_pen(120, 120, 120)
DARK   = display.create_pen(20, 20, 20)

WIRE_COLORS = {
    "R": (RED, "ROJO"),
    "B": (BLUE, "AZUL"),
    "Y": (YELLOW, "AMARILLO"),
    "W": (WHITE, "BLANCO"),
    "K": (GREY, "NEGRO"),
}
SIMON_COLORS = [("R", RED), ("B", BLUE), ("G", GREEN), ("Y", YELLOW)]

# ---------------------------------------------------------------- HELPERS
def beep(freq=880, ms=60):
    if freq <= 0:
        BUZZER.duty_u16(0)
        return
    BUZZER.freq(freq)
    BUZZER.duty_u16(2000)
    time.sleep_ms(ms)
    BUZZER.duty_u16(0)


def any_pressed():
    return not (BTN_A.value() and BTN_B.value() and BTN_X.value() and BTN_Y.value())


def wait_release():
    while any_pressed():
        time.sleep_ms(10)


def read_button(timeout_ms=None):
    """Block until a button is pressed (debounced). Returns 'A','B','X','Y'."""
    start = time.ticks_ms()
    while True:
        if not BTN_A.value():
            wait_release(); return "A"
        if not BTN_B.value():
            wait_release(); return "B"
        if not BTN_X.value():
            wait_release(); return "X"
        if not BTN_Y.value():
            wait_release(); return "Y"
        if timeout_ms and time.ticks_diff(time.ticks_ms(), start) > timeout_ms:
            return None
        time.sleep_ms(10)


def clear(pen=BLACK):
    display.set_pen(pen)
    display.clear()


def text(s, x, y, scale=2, pen=WHITE):
    display.set_pen(pen)
    display.text(s, x, y, W, scale)


def header(state):
    display.set_pen(DARK)
    display.rectangle(0, 0, W, 28)
    display.set_pen(WHITE)
    display.text("#" + state["serial"], 4, 6, W, 2)
    secs = max(0, state["deadline"] - time.ticks_ms()) // 1000
    mm, ss = secs // 60, secs % 60
    pen = RED if secs < 60 else (YELLOW if secs < 180 else GREEN)
    display.set_pen(pen)
    display.text("{:02d}:{:02d}".format(mm, ss), 90, 6, W, 2)
    display.set_pen(WHITE)
    display.text("X" * state["strikes"], 180, 6, W, 2)
    display.set_pen(WHITE)
    display.line(0, 28, W, 28)


def strike(state, msg="FALLO"):
    state["strikes"] += 1
    for f in (220, 180, 140):
        beep(f, 120)
    clear(RED)
    text(msg, 40, 90, 4, WHITE)
    text("strikes: {}".format(state["strikes"]), 40, 140, 2, WHITE)
    display.update()
    time.sleep(1)


def solved(state, name):
    state["solved"].add(name)
    for f in (660, 880, 1320):
        beep(f, 90)
    clear(GREEN)
    text("DESACTIVADO", 18, 100, 3, WHITE)
    display.update()
    time.sleep(1)


def expired(state):
    return time.ticks_diff(state["deadline"], time.ticks_ms()) <= 0


# ---------------------------------------------------------------- MODULE 1: WIRES
def mod_wires(state):
    palette = ["R", "B", "Y", "W", "K"]
    n = random.randint(3, 6)
    wires = [random.choice(palette) for _ in range(n)]
    correct = wires_solution(wires, state["serial_odd"])
    cursor = 0
    while True:
        if expired(state):
            return
        clear()
        header(state)
        text("CABLES", 4, 32, 2, ORANGE)
        text("A subir  B bajar  X cortar", 4, 220, 1, GREY)
        for i, c in enumerate(wires):
            y = 56 + i * 26
            pen, _ = WIRE_COLORS[c]
            display.set_pen(pen)
            display.rectangle(60, y, 140, 14)
            display.set_pen(WHITE)
            display.text(str(i + 1), 30, y, W, 2)
            if i == cursor:
                display.set_pen(WHITE)
                display.rectangle(46, y + 4, 8, 6)
        display.update()
        b = read_button()
        if b == "A":
            cursor = (cursor - 1) % n
        elif b == "B":
            cursor = (cursor + 1) % n
        elif b == "X":
            if cursor == correct:
                solved(state, "wires"); return
            strike(state, "CABLE!")
            return
        elif b == "Y":
            return  # skip


def wires_solution(wires, odd):
    def last_idx(c):
        for i in range(len(wires) - 1, -1, -1):
            if wires[i] == c:
                return i
        return -1
    n = len(wires)
    cnt = lambda c: wires.count(c)
    if n == 3:
        if cnt("R") == 0: return 1
        if wires[-1] == "W": return n - 1
        if cnt("B") > 1: return last_idx("B")
        return n - 1
    if n == 4:
        if cnt("R") > 1 and odd: return last_idx("R")
        if wires[-1] == "Y" and cnt("R") == 0: return 0
        if cnt("B") == 1: return 0
        return 1
    if n == 5:
        if wires[-1] == "K" and odd: return 3
        if cnt("R") == 1 and cnt("Y") > 1: return 0
        if cnt("K") == 0: return 1
        return 0
    if n == 6:
        if cnt("Y") == 0 and odd: return 2
        if cnt("Y") == 1 and cnt("W") > 1: return 3
        if cnt("R") == 0: return n - 1
        return 3
    return 0


# ---------------------------------------------------------------- MODULE 2: BUTTON
def mod_button(state):
    colors = [(BLUE, "AZUL"), (RED, "ROJO"), (YELLOW, "AMARILLO"), (WHITE, "BLANCO")]
    pen, cname = random.choice(colors)
    word = random.choice(["DETONAR", "ABORTAR", "MANTENER", "PULSAR"])
    must_hold = False
    if cname == "AZUL" and word == "ABORTAR": must_hold = True
    elif word == "DETONAR": must_hold = False
    elif cname == "BLANCO" and not state["serial_odd"]: must_hold = True
    elif cname == "AMARILLO": must_hold = True
    elif cname == "ROJO" and word == "MANTENER": must_hold = False
    else: must_hold = False

    release_digit = random.randint(1, 9)
    while True:
        if expired(state):
            return
        clear()
        header(state)
        text("BOTON", 4, 32, 2, ORANGE)
        display.set_pen(pen)
        display.circle(120, 130, 50)
        display.set_pen(BLACK if cname in ("AMARILLO", "BLANCO") else WHITE)
        text(word, 120 - len(word) * 5, 122, 2)
        text("A: pulsar/mantener  Y: skip", 4, 220, 1, GREY)
        display.update()
        # Wait for press
        t0 = None
        while True:
            if expired(state): return
            if not BTN_A.value():
                t0 = time.ticks_ms(); break
            if not BTN_Y.value():
                wait_release(); return
            time.sleep_ms(10)
        beep(440, 30)
        # Determine release time digit
        if not must_hold:
            # quick tap: release before 600 ms
            while not BTN_A.value():
                if time.ticks_diff(time.ticks_ms(), t0) > 600:
                    break
                time.sleep_ms(10)
            held = time.ticks_diff(time.ticks_ms(), t0)
            wait_release()
            if held < 600:
                solved(state, "button"); return
            strike(state, "BOTON!"); return
        else:
            # held mode: show stripe with release digit, must release while clock has digit
            ok = False
            while not BTN_A.value():
                if expired(state): return
                clear()
                header(state)
                text("MANTEN PULSADO", 18, 60, 2, WHITE)
                display.set_pen(YELLOW)
                display.rectangle(W - 40, 32, 40, H - 32)
                display.set_pen(BLACK)
                text(str(release_digit), W - 28, H // 2 - 16, 4)
                display.update()
                time.sleep_ms(40)
            secs = max(0, state["deadline"] - time.ticks_ms()) // 1000
            digits = str(secs // 60) + "{:02d}".format(secs % 60)
            if str(release_digit) in digits:
                ok = True
            wait_release()
            if ok:
                solved(state, "button"); return
            strike(state, "TIEMPO!"); return


# ---------------------------------------------------------------- MODULE 3: SIMON
SIMON_PAR = {
    0: {"R": "B", "B": "R", "G": "Y", "Y": "G"},
    1: {"R": "Y", "B": "G", "G": "B", "Y": "R"},
    2: {"R": "G", "B": "R", "G": "Y", "Y": "B"},
}
SIMON_IMPAR = {
    0: {"R": "B", "B": "Y", "G": "G", "Y": "R"},
    1: {"R": "R", "B": "B", "G": "Y", "Y": "G"},
    2: {"R": "Y", "B": "G", "G": "B", "Y": "R"},
}
SIMON_BTN = {"A": "R", "B": "B", "X": "G", "Y": "Y"}


def simon_draw(highlight=None):
    clear()
    boxes = {
        "R": (40, 60, RED),
        "B": (140, 60, BLUE),
        "G": (40, 150, GREEN),
        "Y": (140, 150, YELLOW),
    }
    for k, (x, y, col) in boxes.items():
        display.set_pen(col if highlight == k else display.create_pen(60, 60, 60))
        display.rectangle(x, y, 60, 60)
    text("SIMON", 4, 32, 2, ORANGE)
    text("A=R B=B X=G Y=Y", 4, 220, 1, GREY)


def mod_simon(state):
    table = SIMON_PAR if not state["serial_odd"] else SIMON_IMPAR
    seq = []
    while len(seq) < 4:
        seq.append(random.choice("RBGY"))
        # play sequence
        for c in seq:
            if expired(state): return
            simon_draw(c)
            header(state)
            display.update()
            beep({"R": 440, "B": 550, "G": 660, "Y": 770}[c], 250)
            simon_draw()
            header(state)
            display.update()
            time.sleep_ms(180)
        # collect input
        for c in seq:
            if expired(state): return
            b = read_button()
            pressed = SIMON_BTN[b]
            expected = table[min(state["strikes"], 2)][c]
            simon_draw(pressed)
            header(state)
            display.update()
            beep(500, 60)
            time.sleep_ms(120)
            if pressed != expected:
                strike(state, "SIMON!")
                return
    solved(state, "simon")


# ---------------------------------------------------------------- MODULE 4: MEMORY
def mod_memory(state):
    history = []  # list of (label, position) per stage 1..5
    for stage in range(1, 6):
        if expired(state): return
        big = random.randint(1, 4)
        digits = random.sample([1, 2, 3, 4], 4)
        clear()
        header(state)
        text("MEMORIA  etapa {}/5".format(stage), 4, 32, 2, ORANGE)
        display.set_pen(WHITE)
        text(str(big), 110, 60, 6, WHITE)
        for i, d in enumerate(digits):
            x = 10 + i * 56
            display.set_pen(BLUE)
            display.rectangle(x, 160, 50, 50)
            display.set_pen(WHITE)
            display.text(str(d), x + 18, 175, W, 3)
        text("A B X Y", 60, 215, 1, GREY)
        display.update()
        b = read_button()
        pos = {"A": 1, "B": 2, "X": 3, "Y": 4}[b]  # 1..4
        label = digits[pos - 1]
        # solution
        ok = memory_check(stage, big, pos, label, history, digits)
        if not ok:
            strike(state, "MEMORIA!")
            return
        history.append((label, pos))
        beep(880, 60)
        time.sleep_ms(150)
    solved(state, "memory")


def memory_check(stage, big, pos, label, history, digits):
    # returns True if pressed button matches manual rule
    if stage == 1:
        target_pos = {1: 2, 2: 2, 3: 3, 4: 4}[big]
        return pos == target_pos
    if stage == 2:
        if big == 1: return label == 4
        if big == 2: return pos == history[0][1]
        if big == 3: return pos == 1
        if big == 4: return pos == history[0][1]
    if stage == 3:
        if big == 1: return label == history[1][0]
        if big == 2: return label == history[0][0]
        if big == 3: return pos == 3
        if big == 4: return label == 4
    if stage == 4:
        if big == 1: return pos == history[0][1]
        if big == 2: return pos == 1
        if big == 3: return pos == history[1][1]
        if big == 4: return pos == history[1][1]
    if stage == 5:
        if big == 1: return label == history[0][0]
        if big == 2: return label == history[1][0]
        if big == 3: return label == history[3][0]
        if big == 4: return label == history[2][0]
    return False


# ---------------------------------------------------------------- MODULE 5: PASSWORD
WORDS = [
    "ABOUT", "AFTER", "AGAIN", "BELOW", "COULD", "EVERY", "FIRST", "FOUND",
    "GREAT", "HOUSE", "LARGE", "LEARN", "NEVER", "OTHER", "PLACE", "PLANT",
    "POINT", "RIGHT", "SMALL", "SOUND", "SPELL", "STILL", "STUDY", "THEIR",
    "THERE", "THESE", "THING", "THINK", "THREE", "WATER", "WHERE", "WHICH",
    "WORLD", "WOULD", "WRITE",
]


def mod_password(state):
    target = random.choice(WORDS)
    cols = []
    for i, ch in enumerate(target):
        # build 6 letters per column, including the correct one,
        # such that letters from other words may appear but only `target`
        # composes a valid word across all columns.
        pool = set([w[i] for w in WORDS])
        letters = [ch]
        pool.discard(ch)
        while len(letters) < 6 and pool:
            x = random.choice(list(pool))
            letters.append(x)
            pool.discard(x)
        random.shuffle(letters)
        cols.append(letters)
    idx = [0] * 5  # current letter index per column
    col = 0
    while True:
        if expired(state): return
        clear()
        header(state)
        text("CONTRASENA", 4, 32, 2, ORANGE)
        for c in range(5):
            x = 10 + c * 44
            for r in range(6):
                ry = 60 + r * 22
                if r == idx[c]:
                    display.set_pen(YELLOW)
                    display.rectangle(x - 4, ry - 2, 36, 22)
                    display.set_pen(BLACK)
                else:
                    display.set_pen(WHITE if c == col else GREY)
                display.text(cols[c][r], x + 4, ry, W, 2)
            if c == col:
                display.set_pen(GREEN)
                display.line(x - 4, 56, x + 32, 56)
        text("A^ Bv X-> Y=ok", 4, 220, 1, GREY)
        display.update()
        b = read_button()
        if b == "A":
            idx[col] = (idx[col] - 1) % 6
        elif b == "B":
            idx[col] = (idx[col] + 1) % 6
        elif b == "X":
            col = (col + 1) % 5
        elif b == "Y":
            word = "".join(cols[c][idx[c]] for c in range(5))
            if word in WORDS:
                solved(state, "password"); return
            strike(state, "PASSWD!"); return


# ---------------------------------------------------------------- GAME LOOP
MODULES = [
    ("wires",    mod_wires),
    ("button",   mod_button),
    ("simon",    mod_simon),
    ("memory",   mod_memory),
    ("password", mod_password),
]


def title_screen():
    while True:
        clear()
        text("KEEP TALKING", 18, 50, 3, RED)
        text("& NOBODY", 50, 90, 3, WHITE)
        text("EXPLODES", 50, 125, 3, WHITE)
        text("Y para empezar", 32, 190, 2, GREEN)
        display.update()
        if read_button() == "Y":
            return


def game_over(state, won):
    for _ in range(6):
        clear(GREEN if won else RED)
        display.update()
        beep(1320 if won else 110, 200)
        time.sleep_ms(120)
    clear()
    text("GANASTE" if won else "BOOM", 50, 80, 4, GREEN if won else RED)
    text("Y para reiniciar", 24, 180, 2, WHITE)
    display.update()
    while read_button() != "Y":
        pass


def new_state():
    serial = "{:04d}".format(random.randint(0, 9999))
    odd = (sum(int(c) for c in serial) % 2) == 1
    return {
        "serial": serial,
        "serial_odd": odd,
        "strikes": 0,
        "solved": set(),
        "deadline": time.ticks_add(time.ticks_ms(), 5 * 60 * 1000),
    }


def main():
    random.seed(time.ticks_us())
    while True:
        title_screen()
        state = new_state()
        order = list(MODULES)
        random.shuffle(order)
        i = 0
        while state["strikes"] < 3 and len(state["solved"]) < len(MODULES) and not expired(state):
            name, fn = order[i % len(order)]
            if name not in state["solved"]:
                fn(state)
            i += 1
            gc.collect()
        won = len(state["solved"]) == len(MODULES) and state["strikes"] < 3 and not expired(state)
        game_over(state, won)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        clear(RED)
        text("ERROR", 60, 80, 3, WHITE)
        text(repr(e)[:30], 4, 140, 1, WHITE)
        display.update()
        raise
