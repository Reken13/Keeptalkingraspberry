import time
import random
from machine import Pin, PWM

try:
    from picographics import PicoGraphics, DISPLAY_PICO_EXPLORER
except:
    from picographics import PicoGraphics
    DISPLAY_PICO_EXPLORER = 1

# =============================================================
# HARDWARE
# =============================================================
BTN_A = Pin(12, Pin.IN, Pin.PULL_UP)
BTN_B = Pin(13, Pin.IN, Pin.PULL_UP)
BTN_X = Pin(14, Pin.IN, Pin.PULL_UP)
BTN_Y = Pin(15, Pin.IN, Pin.PULL_UP)

BUZZER = PWM(Pin(0))   # GP0 = buzzer. NO conectar cable aqui.
BUZZER.duty_u16(0)

# Cables fisicos: pin conectado a GND = intacto (LOW), suelto = cortado (HIGH)
# GP1=MARRON  GP2=VERDE  GP3=AMARILLO  GP4=ROJO  GP5=AZUL
WIRE_PINS = [
    Pin(1, Pin.IN, Pin.PULL_UP),
    Pin(2, Pin.IN, Pin.PULL_UP),
    Pin(3, Pin.IN, Pin.PULL_UP),
    Pin(4, Pin.IN, Pin.PULL_UP),
    Pin(5, Pin.IN, Pin.PULL_UP),
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

# Indice de color = indice de pin (0=MARRON/GP1 ... 4=AZUL/GP5)
C_MARRON, C_VERDE, C_AMARILLO, C_ROJO, C_AZUL = 0, 1, 2, 3, 4
WIRE_NAMES = ["MARRON", "VERDE", "AMARILLO", "ROJO", "AZUL"]
WIRE_PENS  = [BRN,      GRN,     YEL,        RED,    BLU]

# Simon: 4 botones con colores asignados
# Layout: A=arriba-izq  B=abajo-izq  X=arriba-der  Y=abajo-der
SIMON_PENS  = [RED, BLU, GRN, YEL]
SIMON_FREQ  = [440, 550, 660, 770]
SIMON_POS   = [(15, 40), (15, 140), (125, 40), (125, 140)]
SIMON_NAMES = ["A", "B", "X", "Y"]
SIMON_BTNS  = [BTN_A, BTN_B, BTN_X, BTN_Y]

# Tabla Simon: (serial_par, errores_tope2) -> {color: boton}
# Colores: 0=R 1=B 2=G 3=Y | Botones: 0=A 1=B 2=X 3=Y
SIMON_TABLE = {
    (True,  0): {0:0, 1:1, 2:2, 3:3},
    (True,  1): {0:1, 1:0, 2:3, 3:2},
    (True,  2): {0:2, 1:3, 2:0, 3:1},
    (False, 0): {0:1, 1:2, 2:3, 3:0},
    (False, 1): {0:2, 1:3, 2:0, 3:1},
    (False, 2): {0:3, 1:0, 2:1, 3:2},
}

WORDS = [
    "ABOUT","AFTER","COULD","EVERY","FIRST","GREAT","HOUSE",
    "NEVER","OTHER","PLACE","RIGHT","SMALL","STILL","THEIR",
    "THERE","THING","THINK","THREE","WATER","WHERE","WORLD",
]

# =============================================================
# UTILIDADES
# =============================================================
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

def tl(state):
    return max(0, state["end"] - time.time())

def draw_hdr(state):
    display.set_pen(BLK)
    display.rectangle(0, 0, W, 28)
    sec = tl(state)
    m, s = sec // 60, sec % 60
    col = RED if sec < 60 else (YEL if sec < 120 else GRN)
    txt("{:02d}:{:02d}".format(m, s), 8, 5, 2, col)
    txt("#"+state["serial"], 95, 5, 2, WHT)
    txt("X"*state["strikes"], 195, 5, 2, RED)
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
    txt(msg, 30, 90, 3, WHT)
    txt("Errores: "+str(state["strikes"]), 30, 150, 2, WHT)
    upd()
    beep(220, 150); beep(180, 150)
    time.sleep(2)

# =============================================================
# MODULO 1: CABLES FISICOS
# =============================================================
def wires_rule(colors, n, odd):
    cnt = lambda c: colors.count(c)
    def last_of(c):
        for i in range(n-1, -1, -1):
            if colors[i] == c: return i
        return -1
    if n == 3:
        if cnt(C_ROJO) == 0:                               return 1
        if colors[n-1] == C_VERDE:                         return n-1
        if cnt(C_AZUL) > 1:                                return last_of(C_AZUL)
        return n-1
    if n == 4:
        if cnt(C_ROJO) > 1 and odd:                        return last_of(C_ROJO)
        if colors[n-1] == C_AMARILLO and cnt(C_ROJO) == 0: return 0
        if cnt(C_AZUL) == 1:                               return 0
        return 1
    # n == 5
    if colors[n-1] == C_MARRON and odd:                    return 3
    if cnt(C_ROJO) == 1 and cnt(C_AMARILLO) > 1:          return 0
    if cnt(C_MARRON) == 0:                                 return 1
    return 0

def mod_cables(state):
    connected = [i for i in range(5) if WIRE_PINS[i].value() == 0]
    if len(connected) < 3:
        clr(); draw_hdr(state)
        txt("CABLES", 4, 34, 2, ORG)
        txt("Conecta 3-5 cables", 8, 70, 2, WHT)
        txt("GP1-GP5 a GND", 8, 100, 2, YEL)
        txt("Y para saltar", 8, 200, 1, GRY)
        upd()
        while read_btn() != "Y": time.sleep_ms(50)
        return

    n = len(connected)
    colors = connected[:]   # indice pin == indice color en este setup
    correct_pin = connected[wires_rule(colors, n, state["serial_odd"])]

    clr(); draw_hdr(state)
    txt("CABLES", 4, 34, 2, ORG)
    for i, ci in enumerate(colors):
        y = 55 + i * 32
        display.set_pen(WIRE_PENS[ci])
        display.rectangle(38, y+2, 155, 20)
        txt(str(i+1), 8, y, 2, WHT)
    txt("Jala el cable correcto", 8, 228, 1, GRY)
    upd()

    init = [WIRE_PINS[i].value() for i in range(5)]
    cut = None
    while cut is None:
        if tl(state) == 0: return
        time.sleep_ms(30)
        for i in range(5):
            if WIRE_PINS[i].value() == 1 and init[i] == 0:
                cut = i; break

    if cut == correct_pin:
        show_ok(state)
    else:
        show_fail(state, "CABLE MAL!")

# =============================================================
# MODULO 2: SIMON
# =============================================================
def simon_draw(hi=-1):
    clr()
    for i in range(4):
        x, y = SIMON_POS[i]
        display.set_pen(SIMON_PENS[i] if hi == i else GRY)
        display.rectangle(x, y, 85, 75)
        display.set_pen(BLK if hi == i else WHT)
        txt(SIMON_NAMES[i], x+28, y+24, 3, BLK if hi == i else WHT)

def mod_simon(state):
    seq = []
    for _ in range(4):
        seq.append(random.randint(0, 3))
        for ci in seq:
            if tl(state) == 0: return
            simon_draw(ci); draw_hdr(state)
            txt("SIMON", 4, 5, 2, ORG); upd()
            beep(SIMON_FREQ[ci], 280)
            simon_draw(-1); draw_hdr(state)
            txt("SIMON", 4, 5, 2, ORG); upd()
            time.sleep_ms(150)
        for ci in seq:
            if tl(state) == 0: return
            simon_draw(-1); draw_hdr(state)
            txt("SIMON - repite", 4, 5, 2, ORG); upd()
            b = read_btn()
            bi = {"A":0,"B":1,"X":2,"Y":3}[b]
            key = (not state["serial_odd"], min(state["strikes"], 2))
            expected = SIMON_TABLE[key][ci]
            simon_draw(bi); draw_hdr(state); upd()
            beep(SIMON_FREQ[bi], 80); time.sleep_ms(100)
            if bi != expected:
                show_fail(state, "SIMON!"); return
    show_ok(state)

# =============================================================
# MODULO 3: CONTRASENA
# =============================================================
def mod_password(state):
    target = WORDS[random.randint(0, len(WORDS)-1)]
    cols = []
    for i in range(5):
        ch = target[i]
        seen = {ch}; col = [ch]
        for w in WORDS:
            c = w[i]
            if c not in seen:
                seen.add(c); col.append(c)
        shuffle(col)
        cols.append(col[:6] if len(col) > 6 else col)

    idx = [0]*5; sel = 0
    while True:
        if tl(state) == 0: return
        clr(); draw_hdr(state)
        txt("CONTRASENA", 4, 34, 2, ORG)
        for c in range(5):
            x = 8 + c*44
            for r in range(len(cols[c])):
                y = 58 + r*26
                if r == idx[c]:
                    display.set_pen(YEL)
                    display.rectangle(x-2, y-2, 36, 24)
                pen = BLK if r==idx[c] else (WHT if c==sel else GRY)
                txt(cols[c][r], x+4, y+2, 2, pen)
            if c == sel:
                display.set_pen(GRN)
                display.line(x-2, 55, x+34, 55)
        txt("A^ Bv X> Y=OK", 8, 228, 1, GRY)
        upd()
        b = read_btn()
        if   b == "A": idx[sel] = (idx[sel]-1) % len(cols[sel])
        elif b == "B": idx[sel] = (idx[sel]+1) % len(cols[sel])
        elif b == "X": sel = (sel+1) % 5
        elif b == "Y":
            word = "".join(cols[c][idx[c]] for c in range(5))
            if word in WORDS: show_ok(state); return
            else:             show_fail(state, "INCORRECTO!"); return

# =============================================================
# BUCLE PRINCIPAL
# =============================================================
MODULES = [mod_cables, mod_simon, mod_password]

def title():
    clr()
    txt("KEEP TALKING", 14, 40, 3, RED)
    txt("& NOBODY", 40, 90, 3, WHT)
    txt("EXPLODES", 40, 130, 3, WHT)
    txt("Cables GP1-GP5 a GND", 14, 175, 2, YEL)
    txt("Y para empezar", 20, 205, 2, GRN)
    upd()
    while read_btn() != "Y": pass

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
        if tl(state) == 0: break
        order[mi % len(order)](state)
        mi += 1

    won = state["solved"] >= len(MODULES) and state["strikes"] < 3 and tl(state) > 0
    clr(GRN if won else RED)
    txt("GANASTE!" if won else "BOOM...", 25, 80, 4, WHT)
    txt("Errores: "+str(state["strikes"]), 25, 150, 2, WHT)
    txt("Y para reiniciar", 25, 190, 2, WHT)
    upd()
    for _ in range(4):
        beep(1200 if won else 180, 180)
        time.sleep_ms(80)
    time.sleep(1)
    while read_btn() != "Y": pass

while True:
    try:
        title()
        run_game()
    except Exception as e:
        clr(RED)
        txt("ERROR", 50, 70, 4, WHT)
        err = str(e)
        txt(err[:22], 8, 145, 1, WHT)
        txt(err[22:44], 8, 162, 1, WHT)
        upd()
        time.sleep(4)
