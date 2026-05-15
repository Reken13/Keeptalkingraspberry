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

BUZZER = PWM(Pin(0))
BUZZER.duty_u16(0)

# GP1=AZUL  GP2=CASTANHO  GP3=AMARELO  GP4=VERDE  GP5=VERMELHO
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

# Mapeamento fixo: indice do pino -> cor fisica do cabo
WIRE_NAMES = ["AZUL",  "CASTANHO", "AMARELO", "VERDE", "VERMELHO"]
WIRE_PENS  = [BLU,     BRN,        YEL,       GRN,     RED]

SIMON_PENS  = [RED, BLU, GRN, YEL]
SIMON_FREQ  = [440, 550, 660, 770]
SIMON_POS   = [(15, 35), (15, 135), (125, 35), (125, 135)]
SIMON_NAMES = ["A", "B", "X", "Y"]

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
# UTILITARIOS
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
    display.rectangle(0, 0, W, 30)
    sec = tl(state)
    m, s = sec // 60, sec % 60
    col = RED if sec < 60 else (YEL if sec < 120 else GRN)
    txt("{:02d}:{:02d}".format(m, s), 8, 6, 2, col)
    txt("#"+state["serial"], 95, 6, 2, WHT)
    txt("X"*state["strikes"], 195, 6, 2, RED)
    display.set_pen(GRY)
    display.line(0, 30, W, 30)

def show_ok(state):
    state["solved"] += 1
    clr(GRN)
    txt("DESATIVADO!", 20, 100, 3, WHT)
    upd()
    beep(880, 80); beep(1100, 80); beep(1320, 80)
    time.sleep(1)

def show_fail(state, msg="FALHOU!"):
    state["strikes"] += 1
    clr(RED)
    txt(msg, 20, 90, 3, WHT)
    txt("Erros: "+str(state["strikes"]), 30, 155, 2, WHT)
    upd()
    beep(220, 150); beep(180, 150)
    time.sleep(2)

# =============================================================
# MODULO 1: SEQUENCIA DE CABOS
#
# O ecra mostra todos os cabos ligados e a sequencia a puxar
# (indicada com numeros de ordem sobre cada cabo).
# O jogador puxa os cabos fisicamente na ordem correta.
# Puxar o errado = erro imediato.
# =============================================================
def draw_cables(connected, seq, step):
    """
    connected : lista de indices de pinos ligados
    seq       : lista de indices (dentro de connected) que formam a sequencia
    step      : quantos cabos da sequencia ja foram puxados corretamente
    """
    clr()
    n = len(connected)
    row_h = 185 // n

    for row, pin_idx in enumerate(connected):
        y = 38 + row * row_h
        pen = WIRE_PENS[pin_idx]

        # Determinar a posicao desta sequencia (1-based), se existir
        seq_pos = None
        for k, s in enumerate(seq):
            if s == row:          # row = posicao dentro de connected
                seq_pos = k + 1
                break

        # Barra do cabo: cinzenta se ja puxado, colorida se ainda ativo
        already_pulled = (seq_pos is not None and seq_pos <= step)
        display.set_pen(GRY if already_pulled else pen)
        display.rectangle(30, y + 2, 130, row_h - 6)

        # Numero de ordem da sequencia
        if seq_pos is not None:
            label_col = GRY if already_pulled else BLK
            txt(str(seq_pos), 40, y + (row_h - 6)//2 - 8, 2, label_col)

        # Nome da cor a direita
        name_col = GRY if already_pulled else WIRE_PENS[pin_idx]
        txt(WIRE_NAMES[pin_idx], 165, y + 4, 1, name_col)

    # Seta para o proximo cabo
    if step < len(seq):
        next_row = seq[step]
        arrow_y = 38 + next_row * row_h + row_h // 2 - 8
        txt(">", 8, arrow_y, 2, YEL)


def mod_cabos(state):
    connected = [i for i in range(5) if WIRE_PINS[i].value() == 0]
    n = len(connected)

    if n < 3:
        clr(); draw_hdr(state)
        txt("CABOS", 4, 36, 2, ORG)
        txt("Liga 3-5 cabos", 8, 75, 2, WHT)
        txt("GP1-GP5 ao GND", 8, 105, 2, YEL)
        txt("Y para saltar", 8, 205, 1, GRY)
        upd()
        while read_btn() != "Y": time.sleep_ms(50)
        return

    # Gerar sequencia aleatoria: permutacao dos indices dentro de 'connected'
    seq = list(range(n))
    shuffle(seq)
    # Usar apenas 3 cabos se houver 5 ligados (mais desafiante)
    seq_len = 3 if n == 5 else n
    seq = seq[:seq_len]

    step = 0          # quantos cabos da sequencia ja foram puxados
    init = [WIRE_PINS[i].value() for i in range(5)]

    while step < seq_len:
        if tl(state) == 0: return

        draw_cables(connected, seq, step)
        draw_hdr(state)
        txt("CABOS  {}/{}".format(step, seq_len), 4, 36, 2, ORG)
        upd()

        # Esperar que um cabo seja puxado
        pulled = None
        while pulled is None:
            if tl(state) == 0: return
            time.sleep_ms(30)
            for i in range(5):
                if WIRE_PINS[i].value() == 1 and init[i] == 0:
                    pulled = i
                    init[i] = 1   # marcar como puxado
                    break

        # Verificar se o cabo puxado corresponde ao proximo da sequencia
        expected_pin = connected[seq[step]]
        if pulled == expected_pin:
            beep(660 + step * 110, 80)
            step += 1
        else:
            show_fail(state, "ORDEM ERRADA!")
            return

    show_ok(state)

# =============================================================
# MODULO 2: SIMON
# =============================================================
def simon_draw(hi=-1):
    clr()
    for i in range(4):
        x, y = SIMON_POS[i]
        display.set_pen(SIMON_PENS[i] if hi == i else GRY)
        display.rectangle(x, y, 85, 80)
        display.set_pen(BLK if hi == i else WHT)
        txt(SIMON_NAMES[i], x+28, y+25, 3, BLK if hi == i else WHT)

def mod_simon(state):
    seq = []
    for _ in range(4):
        seq.append(random.randint(0, 3))

        for ci in seq:
            if tl(state) == 0: return
            simon_draw(ci); draw_hdr(state)
            txt("OBSERVA", 75, 232, 1, GRY); upd()
            beep(SIMON_FREQ[ci], 350)
            simon_draw(-1); draw_hdr(state)
            txt("OBSERVA", 75, 232, 1, GRY); upd()
            time.sleep_ms(250)

        time.sleep_ms(300)

        for pos, ci in enumerate(seq):
            if tl(state) == 0: return
            simon_draw(-1); draw_hdr(state)
            txt("REPETE {}/{}".format(pos+1, len(seq)), 50, 232, 1, YEL); upd()

            b = read_btn()
            bi = {"A":0,"B":1,"X":2,"Y":3}[b]
            simon_draw(bi); draw_hdr(state)
            txt("REPETE {}/{}".format(pos+1, len(seq)), 50, 232, 1, YEL); upd()
            beep(SIMON_FREQ[bi], 100); time.sleep_ms(150)

            key = (not state["serial_odd"], min(state["strikes"], 2))
            if bi != SIMON_TABLE[key][ci]:
                show_fail(state, "SIMON!"); return

        time.sleep_ms(500)

    show_ok(state)

# =============================================================
# MODULO 3: SENHA
# =============================================================
def mod_senha(state):
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
        txt("SENHA", 4, 36, 2, ORG)
        for c in range(5):
            x = 8 + c*44
            for r in range(len(cols[c])):
                y = 60 + r*26
                if r == idx[c]:
                    display.set_pen(YEL)
                    display.rectangle(x-2, y-2, 36, 24)
                pen = BLK if r==idx[c] else (WHT if c==sel else GRY)
                txt(cols[c][r], x+4, y+2, 2, pen)
            if c == sel:
                display.set_pen(GRN)
                display.line(x-2, 57, x+34, 57)
        txt("A^ Bv X> Y=OK", 8, 228, 1, GRY); upd()
        b = read_btn()
        if   b == "A": idx[sel] = (idx[sel]-1) % len(cols[sel])
        elif b == "B": idx[sel] = (idx[sel]+1) % len(cols[sel])
        elif b == "X": sel = (sel+1) % 5
        elif b == "Y":
            word = "".join(cols[c][idx[c]] for c in range(5))
            if word in WORDS: show_ok(state); return
            else:             show_fail(state, "ERRADA!"); return

# =============================================================
# CICLO PRINCIPAL
# =============================================================
MODULES = [mod_cabos, mod_simon, mod_senha]

def titulo():
    clr()
    txt("KEEP TALKING", 14, 40, 3, RED)
    txt("& NOBODY", 40, 90, 3, WHT)
    txt("EXPLODES", 40, 130, 3, WHT)
    txt("Cabos GP1-GP5 ao GND", 10, 175, 2, YEL)
    txt("Y para comecar", 25, 205, 2, GRN)
    upd()
    while read_btn() != "Y": pass

def jogar():
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
    txt("GANHOU!" if won else "BOOM...", 30, 80, 4, WHT)
    txt("Erros: "+str(state["strikes"]), 30, 155, 2, WHT)
    txt("Y para reiniciar", 20, 195, 2, WHT)
    upd()
    for _ in range(4):
        beep(1200 if won else 180, 180)
        time.sleep_ms(80)
    time.sleep(1)
    while read_btn() != "Y": pass

while True:
    try:
        titulo()
        jogar()
    except Exception as e:
        clr(RED)
        txt("ERRO", 60, 70, 4, WHT)
        err = str(e)
        txt(err[:22], 8, 145, 1, WHT)
        txt(err[22:44], 8, 162, 1, WHT)
        upd()
        time.sleep(4)
