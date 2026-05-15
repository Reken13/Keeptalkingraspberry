import time
import random
from machine import Pin, PWM, ADC

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

joy_x   = ADC(26)
joy_y   = ADC(27)
joy_btn = Pin(28, Pin.IN, Pin.PULL_UP)

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
DGN = display.create_pen(0,   90,  0)   # verde escuro – caminho do labirinto

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

# Configuração do labirinto
MZ_COLS  = 7
MZ_ROWS  = 7
MZ_CELL  = 26
MZ_OX    = (W - MZ_COLS * MZ_CELL - 1) // 2   # margem esquerda
MZ_OY    = 40                                   # margem superior
JOY_DEAD = 10000                                # zona morta do joystick

# =============================================================
# UTILITÁRIOS
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

def read_btn(state=None):
    """Aguarda pressão de botão A/B/X/Y. Dispara beep periódico se state dado."""
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
        if state:
            maybe_beep(state)
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

def maybe_beep(state):
    """Beep periódico de tensão: cada 30 s normal, 10 s <60 s, 5 s <30 s."""
    sec = tl(state)
    if sec == 0:
        return
    now = time.time()
    if   sec < 30: interval, freq = 5,  660
    elif sec < 60: interval, freq = 10, 550
    else:          interval, freq = 30, 440
    if now - state.get("last_beep", 0) >= interval:
        beep(freq, 40)
        state["last_beep"] = now

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
# JOYSTICK
# =============================================================
def joy_dir():
    """Retorna (dr, dc) para cima/baixo/esq/dir, ou None se centrado."""
    dx = joy_x.read_u16() - 32768
    dy = joy_y.read_u16() - 32768
    if abs(dx) > abs(dy):
        if dx >  JOY_DEAD: return (0,  1)
        if dx < -JOY_DEAD: return (0, -1)
    else:
        if dy >  JOY_DEAD: return ( 1, 0)
        if dy < -JOY_DEAD: return (-1, 0)
    return None

def joy_wait_center():
    while joy_dir() is not None:
        time.sleep_ms(10)

# =============================================================
# LABIRINTO – GERAÇÃO (DFS iterativo)
# =============================================================
def gen_maze():
    """Devolve (h_walls, v_walls).
    h_walls[r][c] = parede abaixo de (r,c)
    v_walls[r][c] = parede à direita de (r,c)
    """
    hw = [[True] * MZ_COLS for _ in range(MZ_ROWS - 1)]
    vw = [[True] * (MZ_COLS - 1) for _ in range(MZ_ROWS)]
    vis = [[False] * MZ_COLS for _ in range(MZ_ROWS)]
    stk = [(0, 0)]
    vis[0][0] = True
    while stk:
        r, c = stk[-1]
        nb = []
        if r > 0         and not vis[r-1][c]: nb.append((r-1, c))
        if r < MZ_ROWS-1 and not vis[r+1][c]: nb.append((r+1, c))
        if c > 0         and not vis[r][c-1]: nb.append((r, c-1))
        if c < MZ_COLS-1 and not vis[r][c+1]: nb.append((r, c+1))
        if nb:
            nr, nc = nb[random.randint(0, len(nb) - 1)]
            if   nr == r + 1: hw[r][c]   = False  # sul
            elif nr == r - 1: hw[nr][c]  = False  # norte
            elif nc == c + 1: vw[r][c]   = False  # este
            else:              vw[r][nc]  = False  # oeste
            vis[nr][nc] = True
            stk.append((nr, nc))
        else:
            stk.pop()
    return hw, vw

def find_path(hw, vw):
    """BFS de (0,0) até (MZ_ROWS-1, MZ_COLS-1). Devolve lista de células."""
    end = (MZ_ROWS - 1, MZ_COLS - 1)
    q = [(0, 0)]
    came = {(0, 0): None}
    while q:
        r, c = q.pop(0)
        if (r, c) == end:
            break
        if r > 0         and not hw[r-1][c] and (r-1,c) not in came:
            came[(r-1,c)] = (r,c); q.append((r-1,c))
        if r < MZ_ROWS-1 and not hw[r][c]   and (r+1,c) not in came:
            came[(r+1,c)] = (r,c); q.append((r+1,c))
        if c > 0         and not vw[r][c-1] and (r,c-1) not in came:
            came[(r,c-1)] = (r,c); q.append((r,c-1))
        if c < MZ_COLS-1 and not vw[r][c]   and (r,c+1) not in came:
            came[(r,c+1)] = (r,c); q.append((r,c+1))
    path = []; cur = end
    while cur is not None:
        path.append(cur); cur = came.get(cur)
    path.reverse()
    return path

def can_move(hw, vw, r, c, dr, dc):
    nr, nc = r + dr, c + dc
    if not (0 <= nr < MZ_ROWS and 0 <= nc < MZ_COLS): return False
    if dr ==  1 and hw[r][c]:   return False   # parede ao sul
    if dr == -1 and hw[nr][c]:  return False   # parede ao norte
    if dc ==  1 and vw[r][c]:   return False   # parede a leste
    if dc == -1 and vw[r][nc]:  return False   # parede a oeste
    return True

# =============================================================
# LABIRINTO – DESENHO
# =============================================================
def draw_maze(hw, vw, highlight=None):
    ox, oy = MZ_OX, MZ_OY
    # Pintar caminho (fase do experto)
    if highlight:
        display.set_pen(DGN)
        for pr, pc in highlight:
            display.rectangle(ox + pc*MZ_CELL + 1, oy + pr*MZ_CELL + 1,
                               MZ_CELL - 1, MZ_CELL - 1)
    # Bordas externas
    display.set_pen(WHT)
    display.line(ox, oy, ox + MZ_COLS*MZ_CELL, oy)
    display.line(ox, oy + MZ_ROWS*MZ_CELL, ox + MZ_COLS*MZ_CELL, oy + MZ_ROWS*MZ_CELL)
    display.line(ox, oy, ox, oy + MZ_ROWS*MZ_CELL)
    display.line(ox + MZ_COLS*MZ_CELL, oy, ox + MZ_COLS*MZ_CELL, oy + MZ_ROWS*MZ_CELL)
    # Paredes horizontais (abaixo de cada célula)
    for r in range(MZ_ROWS - 1):
        for c in range(MZ_COLS):
            if hw[r][c]:
                x1 = ox + c * MZ_CELL
                y1 = oy + (r + 1) * MZ_CELL
                display.line(x1, y1, x1 + MZ_CELL, y1)
    # Paredes verticais (à direita de cada célula)
    for r in range(MZ_ROWS):
        for c in range(MZ_COLS - 1):
            if vw[r][c]:
                x1 = ox + (c + 1) * MZ_CELL
                y1 = oy + r * MZ_CELL
                display.line(x1, y1, x1, y1 + MZ_CELL)

def draw_mz_cell(r, c, pen):
    display.set_pen(pen)
    display.rectangle(MZ_OX + c*MZ_CELL + 4, MZ_OY + r*MZ_CELL + 4,
                      MZ_CELL - 8, MZ_CELL - 8)

# =============================================================
# MÓDULO 4: LABIRINTO COOPERATIVO
# Experto vê o caminho (8 s) → Defusor navega com joystick.
# Comunicam-se verbalmente: defusor diz a posição (linha,col),
# experto guia a direção.
# =============================================================
def mod_labirinto(state):
    hw, vw = gen_maze()
    path   = find_path(hw, vw)

    # ── Fase 1: experto memoriza ──────────────────────────────
    t0 = time.time()
    while time.time() - t0 < 8:
        if tl(state) == 0: return
        rem = int(8 - (time.time() - t0)) + 1
        clr()
        draw_hdr(state)
        txt("EXPERTO VE | DEFUSOR: FECHA OLHOS", 4, 32, 1, YEL)
        txt("{}s".format(rem), 210, 32, 1, RED)
        draw_maze(hw, vw, path)
        # marcador de inicio (azul) e saida (laranja)
        display.set_pen(BLU)
        display.rectangle(MZ_OX + 1, MZ_OY + 1, MZ_CELL - 2, MZ_CELL - 2)
        display.set_pen(ORG)
        display.rectangle(MZ_OX + (MZ_COLS-1)*MZ_CELL + 2,
                          MZ_OY + (MZ_ROWS-1)*MZ_CELL + 2,
                          MZ_CELL - 4, MZ_CELL - 4)
        upd()
        time.sleep_ms(200)

    beep(660, 60); beep(880, 60)   # sinal de início
    joy_wait_center()
    pr, pc = 0, 0

    # ── Fase 2: defusor navega ────────────────────────────────
    while True:
        maybe_beep(state)
        if tl(state) == 0: return

        clr()
        draw_hdr(state)
        txt("LABIRINTO", 4, 32, 1, ORG)
        txt("({},{})".format(pr, pc), 155, 32, 1, GRY)
        draw_maze(hw, vw)
        # saida
        display.set_pen(ORG)
        display.rectangle(MZ_OX + (MZ_COLS-1)*MZ_CELL + 2,
                          MZ_OY + (MZ_ROWS-1)*MZ_CELL + 2,
                          MZ_CELL - 4, MZ_CELL - 4)
        # jogador
        draw_mz_cell(pr, pc, BLU)
        upd()

        if pr == MZ_ROWS - 1 and pc == MZ_COLS - 1:
            show_ok(state)
            return

        jd = joy_dir()
        if jd:
            dr, dc = jd
            if can_move(hw, vw, pr, pc, dr, dc):
                pr += dr; pc += dc
                beep(880, 20)
            else:
                beep(200, 60)   # bate na parede
            joy_wait_center()

        time.sleep_ms(25)

# =============================================================
# DIAGNÓSTICO DE PINOS
# =============================================================
def pin_diagnostics():
    while True:
        clr()
        txt("DIAGNOSTICO", 10, 10, 2, ORG)
        txt("0=GND  1=solto", 10, 35, 1, GRY)
        for i in range(5):
            vval = WIRE_PINS[i].value()
            pen = GRN if vval == 0 else RED
            txt("GP{}  {}  {}".format(i+1, vval, WIRE_NAMES[i]),
                10, 60 + i*34, 2, pen)
        txt("A para sair", 10, 230, 1, GRY)
        upd()
        time.sleep_ms(200)
        if not BTN_A.value():
            while not BTN_A.value(): time.sleep_ms(10)
            return

# =============================================================
# MÓDULO 1: SEQUÊNCIA DE CABOS
# =============================================================
def draw_cables(connected, seq, step):
    clr()
    n = len(connected)
    row_h = 185 // n
    for row, pin_idx in enumerate(connected):
        y = 38 + row * row_h
        seq_pos = None
        for k, s in enumerate(seq):
            if s == row:
                seq_pos = k + 1
                break
        already = (seq_pos is not None and seq_pos <= step)
        display.set_pen(GRY if already else WIRE_PENS[pin_idx])
        display.rectangle(30, y + 2, 130, row_h - 6)
        if seq_pos is not None:
            txt(str(seq_pos), 40, y + (row_h-6)//2 - 8, 2,
                GRY if already else BLK)
        txt(WIRE_NAMES[pin_idx], 165, y + 4, 1,
            GRY if already else WIRE_PENS[pin_idx])
    if step < len(seq):
        arrow_y = 38 + seq[step] * row_h + row_h // 2 - 8
        txt(">", 8, arrow_y, 2, YEL)

def mod_cabos(state):
    connected = [i for i in range(5) if WIRE_PINS[i].value() == 0]
    n = len(connected)

    if n < 3:
        clr(); draw_hdr(state)
        txt("CABOS", 4, 36, 2, ORG)
        txt("Liga 3-5 cabos", 8, 75, 2, WHT)
        txt("GP1-GP5 ao GND", 8, 105, 2, YEL)
        for i in range(5):
            vval = WIRE_PINS[i].value()
            pen = GRN if vval == 0 else RED
            txt("GP{} = {}".format(i+1, vval), 8, 135 + i*18, 1, pen)
        txt("A=diagnostico  Y=saltar", 8, 228, 1, GRY)
        upd()
        b = read_btn(state)
        if b == "A":
            pin_diagnostics()
        return

    seq = list(range(n))
    shuffle(seq)
    seq_len = 3 if n == 5 else n
    seq = seq[:seq_len]

    step = 0
    init = [WIRE_PINS[i].value() for i in range(5)]

    while step < seq_len:
        maybe_beep(state)
        if tl(state) == 0: return
        draw_cables(connected, seq, step)
        draw_hdr(state)
        txt("CABOS  {}/{}".format(step, seq_len), 4, 36, 2, ORG)
        upd()

        pulled = None
        while pulled is None:
            maybe_beep(state)
            if tl(state) == 0: return
            time.sleep_ms(30)
            for i in range(5):
                if WIRE_PINS[i].value() == 1 and init[i] == 0:
                    pulled = i
                    init[i] = 1
                    break

        expected_pin = connected[seq[step]]
        if pulled == expected_pin:
            beep(660 + step * 110, 80)
            step += 1
        else:
            show_fail(state, "ORDEM ERRADA!")
            return

    show_ok(state)

# =============================================================
# MÓDULO 2: SIMON
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
            maybe_beep(state)
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
            b = read_btn(state)
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
# MÓDULO 3: SENHA
# =============================================================
def mod_senha(state):
    target = WORDS[random.randint(0, len(WORDS)-1)]
    cols = []
    for i in range(5):
        ch = target[i]
        seen = {ch}; col = [ch]
        for w in WORDS:
            lc = w[i]
            if lc not in seen:
                seen.add(lc); col.append(lc)
        shuffle(col)
        cols.append(col[:6] if len(col) > 6 else col)
    idx = [0]*5; sel = 0
    while True:
        maybe_beep(state)
        if tl(state) == 0: return
        clr(); draw_hdr(state)
        txt("SENHA", 4, 36, 2, ORG)
        for col in range(5):
            x = 8 + col*44
            for row in range(len(cols[col])):
                y = 60 + row*26
                if row == idx[col]:
                    display.set_pen(YEL)
                    display.rectangle(x-2, y-2, 36, 24)
                pen = BLK if row==idx[col] else (WHT if col==sel else GRY)
                txt(cols[col][row], x+4, y+2, 2, pen)
            if col == sel:
                display.set_pen(GRN)
                display.line(x-2, 57, x+34, 57)
        txt("A^ Bv X> Y=OK", 8, 228, 1, GRY); upd()
        b = read_btn(state)
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
MODULES = [mod_cabos, mod_simon, mod_senha, mod_labirinto]

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
        "serial":     serial,
        "serial_odd": (sum(int(c) for c in serial) % 2) == 1,
        "strikes":    0,
        "solved":     0,
        "end":        time.time() + 300,
        "last_beep":  time.time(),   # referência para beeps periódicos
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
