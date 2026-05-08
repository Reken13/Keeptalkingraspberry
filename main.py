"""
KEEP TALKING AND NOBODY EXPLODES - Pico Explorer
=================================================
CONEXION CABLES FISICOS:
  GP2 -> cable ROJO    (otro extremo a GND)
  GP3 -> cable AMARILLO
  GP4 -> cable VERDE
  GP5 -> cable AZUL
  GP6 -> cable MARRON

MANUAL DEL EXPERTO (imprimir):
------------------------------
MODULO CABLES:
  3 cables:
    Sin rojo          -> cortar 2
    Ultimo=blanco     -> cortar ultimo
    Mas de 1 azul     -> cortar ultimo azul
    Caso base         -> cortar ultimo
  4 cables:
    >1 rojo + impar   -> cortar ultimo rojo
    Ultimo=amarillo + sin rojo -> cortar 1
    Exactamente 1 azul -> cortar 1
    Caso base         -> cortar 2
  5 cables:
    Ultimo=marron + impar -> cortar 4
    1 rojo + >1 amarillo  -> cortar 1
    Sin marron        -> cortar 2
    Caso base         -> cortar 1

MODULO SIMON (0 errores):
  Serial par:   R->A  A->B  V->X  Am->Y
  Serial impar: R->B  A->X  V->Y  Am->A

MODULO CONTRASENA: palabras validas:
  ABOUT AFTER COULD EVERY FIRST GREAT HOUSE
  NEVER OTHER PLACE RIGHT SMALL STILL THEIR
  THERE THING THINK THREE WATER WHERE WORLD
"""

import time
import random
from machine import Pin, PWM

try:
    from picographics import PicoGraphics, DISPLAY_PICO_EXPLORER
except:
    from picographics import PicoGraphics
    DISPLAY_PICO_EXPLORER = 1

# ---------- HARDWARE ----------
BTN_A = Pin(12, Pin.IN, Pin.PULL_UP)
BTN_B = Pin(13, Pin.IN, Pin.PULL_UP)
BTN_X = Pin(14, Pin.IN, Pin.PULL_UP)
BTN_Y = Pin(15, Pin.IN, Pin.PULL_UP)
BUZZER = PWM(Pin(0))
BUZZER.duty_u16(0)

# Cables fisicos: conectar pin -> cable -> GND
# Pin LOW = cable conectado (intacto), HIGH = cortado
WIRE_PINS = [
    Pin(2, Pin.IN, Pin.PULL_UP),
    Pin(3, Pin.IN, Pin.PULL_UP),
    Pin(4, Pin.IN, Pin.PULL_UP),
    Pin(5, Pin.IN, Pin.PULL_UP),
    Pin(6, Pin.IN, Pin.PULL_UP),
]

display = PicoGraphics(display=DISPLAY_PICO_EXPLORER)
W, H = display.get_bounds()

BLK = display.create_pen(0,   0,   0)
WHT = display.create_pen(240, 240, 240)
RED = display.create_pen(220, 30,  30)
GRN = display.create_pen(30,  200, 30)
BLU = display.create_pen(40,  100, 240)
YEL = display.create_pen(240, 220, 0)
ORG = display.create_pen(240, 130, 0)
GRY = display.create_pen(100, 100, 100)
BRN = display.create_pen(140, 80,  30)

WIRE_NAMES = ["ROJO", "AMARILLO", "VERDE", "AZUL", "MARRON"]
WIRE_PENS  = [RED,    YEL,        GRN,     BLU,    BRN]

SIMON_PENS  = [RED, BLU, GRN, YEL]
SIMON_FREQ  = [440, 550, 660, 770]
SIMON_POS   = [(20, 40), (130, 40), (20, 140), (130, 140)]
SIMON_NAMES = ["A", "B", "X", "Y"]
SIMON_BTNS  = [BTN_A, BTN_B, BTN_X, BTN_Y]

WORDS = [
    "ABOUT","AFTER","COULD","EVERY","FIRST","GREAT","HOUSE",
    "NEVER","OTHER","PLACE","RIGHT","SMALL","STILL","THEIR",
    "THERE","THING","THINK","THREE","WATER","WHERE","WORLD",
]

# ---------- UTILS ----------
def beep(f=880, ms=80):
    BUZZER.freq(max(1, f))
    BUZZER.duty_u16(1000)
    time.sleep_ms(ms)
    BUZZER.duty_u16(0)

def shuffle(lst):
    for i in range(len(lst) - 1, 0, -1):
        j = random.randint(0, i)
        lst[i], lst[j] = lst[j], lst[i]

def clr(c=BLK):
    display.set_pen(c)
    display.clear()

def txt(s, x, y, sc=2, c=WHT):
    display.set_pen(c)
    display.text(str(s), x, y, W, sc)

def upd():
    display.update()

def read_btn():
    pairs = [(BTN_A,"A"),(BTN_B,"B"),(BTN_X,"X"),(BTN_Y,"Y")]
    while True:
        for pin, name in pairs:
            if not pin.value():
                time.sleep_ms(40)
                if not pin.value():
                    while not pin.value():
                        time.sleep_ms(10)
                    time.sleep_ms(30)
                    return name
        time.sleep_ms(20)

def time_left(state):
    return max(0, state["end"] - time.time())

def draw_hdr(state):
    display.set_pen(BLK)
    display.rectangle(0, 0, W, 28)
    sec = time_left(state)
    m, s = sec // 60, sec % 60
    col = RED if sec < 60 else (YEL if sec < 120 else GRN)
    txt("{:02d}:{:02d}".format(m, s), 8, 5, 2, col)
    txt("#" + state["serial"], 90, 5, 2, WHT)
    txt("X" * state["strikes"], 190, 5, 2, RED)
    display.set_pen(GRY)
    display.line(0, 28, W, 28)

def show_ok(state):
    state["solved"] += 1
    clr(GRN)
    txt("DESACTIVADO!", 20, 100, 3, WHT)
    upd()
    beep(880, 80); beep(1100, 80); beep(1320, 80)
    time.sleep(1)

def show_fail(state, msg="FALLO!"):
    state["strikes"] += 1
    clr(RED)
    txt(msg, 30, 100, 3, WHT)
    txt("Errores: " + str(state["strikes"]), 30, 155, 2, WHT)
    upd()
    beep(220, 150); beep(180, 150)
    time.sleep(2)

# ---------- MODULO: CABLES FISICOS ----------
def wires_rule(colors, n, odd):
    """Devuelve el INDICE (0-based) del cable correcto a cortar."""
    def last(c):
        for i in range(n - 1, -1, -1):
            if colors[i] == c: return i
        return -1
    cnt = lambda c: colors.count(c)
    if n == 3:
        if cnt(0) == 0:       return 1
        if colors[n-1] == 4:  return n-1
        if cnt(3) > 1:        return last(3)
        return n-1
    if n == 4:
        if cnt(0) > 1 and odd: return last(0)
        if colors[n-1] == 1 and cnt(0) == 0: return 0
        if cnt(3) == 1:        return 0
        return 1
    # 5
    if colors[n-1] == 4 and odd: return 3
    if cnt(0) == 1 and cnt(1) > 1: return 0
    if cnt(4) == 0: return 1
    return 0

def mod_cables(state):
    # Detectar cuales pines estan conectados a GND (LOW = intacto)
    connected = [i for i in range(5) if WIRE_PINS[i].value() == 0]

    if len(connected) < 3:
        clr()
        draw_hdr(state)
        txt("CABLES", 4, 34, 2, ORG)
        txt("Conecta 3-5 cables", 8, 70, 2, WHT)
        txt("GP2-GP6 -> GND", 8, 100, 2, YEL)
        txt("Y para saltar", 8, 200, 2, GRY)
        upd()
        while read_btn() != "Y":
            time.sleep_ms(50)
        return

    n = len(connected)
    # Asignar color aleatorio a cada cable conectado
    color_pool = list(range(5))
    shuffle(color_pool)
    colors = color_pool[:n]   # color index por posicion de juego

    odd = state["serial_odd"]
    correct = wires_rule(colors, n, odd)

    clr()
    draw_hdr(state)
    txt("CABLES", 4, 34, 2, ORG)
    for i in range(n):
        y = 55 + i * 30
        display.set_pen(WIRE_PENS[colors[i]])
        display.rectangle(38, y + 3, 155, 16)
        txt(str(i + 1), 8, y, 2, WHT)
        txt(WIRE_NAMES[colors[i]], 200, y, 2, GRY)
    txt("Corta el cable", 8, 228, 1, GRY)
    upd()

    # Esperar a que se corte un cable (pin pasa de LOW a HIGH)
    init = [WIRE_PINS[i].value() for i in range(5)]
    cut_phys = None
    while cut_phys is None:
        if time_left(state) == 0:
            return
        time.sleep_ms(30)
        for i in range(5):
            v = WIRE_PINS[i].value()
            if v == 1 and init[i] == 0:
                cut_phys = i
                break

    # Mapear pin fisico al indice de juego
    if cut_phys in connected:
        game_idx = connected.index(cut_phys)
    else:
        game_idx = -1

    if game_idx == correct:
        show_ok(state)
    else:
        show_fail(state, "CABLE MAL!")

# ---------- MODULO: SIMON ----------
SIMON_MAP_PAR  = {"A":0,"B":1,"X":2,"Y":3}
# Par: A=R B=B X=G Y=Am  -> prensa segun color mostrado
SIMON_PAR  = {0:0, 1:1, 2:2, 3:3}   # color -> boton (0=A,1=B,2=X,3=Y)
SIMON_IMPAR = {0:1, 1:2, 2:3, 3:0}  # impar: R->B A->X V->Y Am->A

def simon_draw(highlight=-1):
    clr()
    for i in range(4):
        x, y = SIMON_POS[i]
        pen = SIMON_PENS[i] if highlight == i else GRY
        display.set_pen(pen)
        display.rectangle(x, y, 85, 70)
        display.set_pen(BLK if highlight == i else WHT)
        txt(SIMON_NAMES[i], x + 30, y + 22, 3, BLK if highlight == i else WHT)

def mod_simon(state):
    table = SIMON_IMPAR if state["serial_odd"] else SIMON_PAR
    seq = []
    rounds = 4

    for _ in range(rounds):
        seq.append(random.randint(0, 3))

        # Mostrar secuencia
        for ci in seq:
            if time_left(state) == 0: return
            simon_draw(ci)
            draw_hdr(state)
            txt("SIMON", 4, 5, 2, ORG)
            upd()
            beep(SIMON_FREQ[ci], 280)
            simon_draw(-1)
            draw_hdr(state)
            txt("SIMON", 4, 5, 2, ORG)
            upd()
            time.sleep_ms(160)

        # Recoger input
        for ci in seq:
            if time_left(state) == 0: return
            simon_draw(-1)
            draw_hdr(state)
            txt("SIMON - repite", 4, 5, 2, ORG)
            upd()

            b = read_btn()
            bi = {"A":0,"B":1,"X":2,"Y":3}[b]
            expected = table[ci]

            simon_draw(bi)
            draw_hdr(state)
            upd()
            beep(SIMON_FREQ[bi], 80)
            time.sleep_ms(100)

            if bi != expected:
                show_fail(state, "SIMON!")
                return

    show_ok(state)

# ---------- MODULO: CONTRASENA ----------
def mod_password(state):
    target = WORDS[random.randint(0, len(WORDS) - 1)]
    cols = []
    for i in range(5):
        ch = target[i]
        seen = set()
        seen.add(ch)
        col = [ch]
        for w in WORDS:
            c = w[i]
            if c not in seen:
                seen.add(c)
                col.append(c)
        shuffle(col)
        cols.append(col[:6] if len(col) > 6 else col)

    idx = [0] * 5
    sel = 0

    while True:
        if time_left(state) == 0: return
        clr()
        draw_hdr(state)
        txt("CONTRASENA", 4, 34, 2, ORG)

        for c in range(5):
            x = 8 + c * 44
            for r in range(len(cols[c])):
                y = 58 + r * 26
                if r == idx[c]:
                    display.set_pen(YEL)
                    display.rectangle(x - 2, y - 2, 36, 24)
                pen = BLK if r == idx[c] else (WHT if c == sel else GRY)
                txt(cols[c][r], x + 4, y + 2, 2, pen)
            if c == sel:
                display.set_pen(GRN)
                display.line(x - 2, 55, x + 34, 55)

        txt("A^ Bv X> Y=OK", 8, 228, 1, GRY)
        upd()

        b = read_btn()
        if b == "A":
            idx[sel] = (idx[sel] - 1) % len(cols[sel])
        elif b == "B":
            idx[sel] = (idx[sel] + 1) % len(cols[sel])
        elif b == "X":
            sel = (sel + 1) % 5
        elif b == "Y":
            word = "".join(cols[c][idx[c]] for c in range(5))
            if word in WORDS:
                show_ok(state)
                return
            else:
                show_fail(state, "INCORRECTO!")
                return

# ---------- GAME LOOP ----------
MODULES = [mod_cables, mod_simon, mod_password]

def title_screen():
    clr()
    txt("KEEP TALKING", 14, 40, 3, RED)
    txt("& NOBODY", 40, 90, 3, WHT)
    txt("EXPLODES", 40, 130, 3, WHT)
    txt("GP2-GP6 a GND", 20, 175, 2, YEL)
    txt("Y para empezar", 20, 205, 2, GRN)
    upd()
    while read_btn() != "Y":
        pass

def run_game():
    serial = "{:04d}".format(random.randint(1000, 9999))
    state = {
        "serial": serial,
        "serial_odd": (sum(int(c) for c in serial) % 2) == 1,
        "strikes": 0,
        "solved": 0,
        "end": time.time() + 300,
    }

    order = list(MODULES)
    shuffle(order)
    mi = 0

    while state["strikes"] < 3 and state["solved"] < len(MODULES):
        if time_left(state) == 0:
            break
        order[mi % len(order)](state)
        mi += 1

    won = (state["solved"] >= len(MODULES)
           and state["strikes"] < 3
           and time_left(state) > 0)

    clr(GRN if won else RED)
    txt("GANASTE!" if won else "BOOM...", 25, 80, 4, WHT)
    txt("Errores: " + str(state["strikes"]), 25, 150, 2, WHT)
    txt("Y para reiniciar", 25, 190, 2, WHT)
    upd()
    for _ in range(4):
        beep(1200 if won else 180, 180)
        time.sleep_ms(80)
    time.sleep(1)
    while read_btn() != "Y":
        pass

# ---------- MAIN ----------
while True:
    try:
        title_screen()
        run_game()
    except Exception as e:
        clr(RED)
        txt("ERROR", 50, 70, 4, WHT)
        err = str(e)
        txt(err[:22], 8, 145, 1, WHT)
        txt(err[22:44], 8, 162, 1, WHT)
        upd()
        time.sleep(4)
