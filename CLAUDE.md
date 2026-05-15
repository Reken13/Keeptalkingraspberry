# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a physical implementation of "Keep Talking and Nobody Explodes" running on a **Raspberry Pi Pico** with the **Pimoroni Pico Explorer Base**. It's written in **MicroPython** targeting Pimoroni's custom MicroPython firmware with the PicoGraphics display library.

One player sees the Pico's 240×135 display and defuses a bomb; an expert player reads `manual.md` without seeing the screen.

## Deployment

There is no build step. Code runs directly on the Pico via **Thonny IDE**:
1. Flash Pimoroni MicroPython firmware to the Pico.
2. Open `main.py` in Thonny and save it to the Pico (File > Save as > Raspberry Pi Pico).
3. Restart the Pico — `main.py` launches automatically.

`joystick_test.py` is a standalone diagnostic utility uploaded the same way.

## Hardware Wiring

| Component | GPIO Pin |
|-----------|----------|
| Buzzer (PWM) | GP0 |
| Wire inputs (5 cables) | GP1–GP5 |
| Button A | GP12 |
| Button B | GP13 |
| Button X | GP14 |
| Button Y | GP15 |

Wire inputs detect connection to GND (pulled high internally). The Explorer Base provides the display via SPI — no extra wiring needed.

## Architecture

All game logic lives in `main.py` (~376 lines). There are no modules or imports beyond the Pimoroni firmware libraries (`picographics`, `picoexplorer`, `machine`, `utime`, `urandom`).

**Game loop structure:**
- On start, three puzzle modules (CABOS, SIMON, SENHA) are shuffled into a random order.
- Each module runs sequentially; completing all three wins the game.
- A shared 300-second countdown and 3-strike limit apply across all modules.
- The serial number (random, generated at game start) affects puzzle rules — its parity changes Simon button mappings and wire-cut rules per `manual.md`.

**Three puzzle modules:**

- **CABOS (Wires)** — 3–5 colored wires shown on screen; player pulls physical jumper cables (GP1–GP5) in the order determined by the expert's wire-cutting rules.
- **SIMON** — Color sequence memory game. Button-to-color mapping is remapped each round using `SIMON_TABLE` (6 permutations indexed by serial parity + strike count).
- **SENHA (Password)** — 5-column letter selector. Player navigates columns with A/B and rows with X/Y; must spell one of 21 valid English words hardcoded in `WORD_LIST`.

**Key constants (all in `main.py`):**
- `SIMON_TABLE` (lines ~52–59): lookup table driving Simon remapping.
- `WORD_LIST` (lines ~61–65): valid passwords for SENHA module.
- Color palette constants define display colors for wires, buttons, and UI.

## Documentation Language

`README.md` and `manual.md` are written in **Portuguese**. The expert manual (`manual.md`) contains the decision trees and lookup tables the non-defuser player uses; keep it in sync with any game logic changes.
