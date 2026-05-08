# Keep Talking and Nobody Explodes — Pico Explorer

Versión MicroPython del clásico juego de desactivación de bombas, para correr en
una **Pimoroni Pico Explorer Base** desde **Thonny**.

![board](https://shop.pimoroni.com/cdn/shop/products/pico-explorer-1_1024x1024.jpg)

## Hardware

- Raspberry Pi Pico (o Pico W) montada sobre la **Pico Explorer Base**
- Pantalla 1.54" 240x240 integrada
- Botones A / B / X / Y
- Buzzer piezo (GP0)
- (Opcional) 4 LEDs en la breadboard — GP6, GP7, GP8, GP9 con resistencia de 220Ω a GND

## Instalación

1. Flashea la Pico con el firmware **Pimoroni MicroPython** (incluye `picographics`):
   https://github.com/pimoroni/pimoroni-pico/releases — archivo `pimoroni-picow-*.uf2` o `pimoroni-pico-*.uf2`.
2. Abre **Thonny**, selecciona intérprete *MicroPython (Raspberry Pi Pico)*.
3. Copia `main.py` a la Pico (Archivo → Guardar como → Raspberry Pi Pico → `main.py`).
4. Pulsa **Run** o reinicia la Pico.

## Cómo se juega

- Tienes **5 minutos** y **3 fallos** para desactivar **5 módulos**.
- Pulsa **Y** para empezar y para cambiar de módulo.
- Cada módulo tiene reglas en `MANUAL.md` — imprime ese archivo y dáselo a un
  compañero (el *experto*) que NO debe mirar la pantalla.
- Tú (el *desactivador*) describes lo que ves; el experto te dice qué hacer.

## Controles globales

| Botón | Acción |
|------|--------|
| Y    | Siguiente módulo / iniciar |
| A/B/X/Y | Acciones específicas según módulo (ver MANUAL.md) |

## Módulos incluidos

1. **Cables** — corta el cable correcto según colores y serie.
2. **El Botón** — pulsar o mantener según color y palabra.
3. **Simon Dice** — repite la secuencia de colores.
4. **Memoria** — recuerda posiciones a través de 5 etapas.
5. **Contraseña** — encuentra la palabra válida cambiando letras.

## Pinout

```
A = GP12   B = GP13   X = GP14   Y = GP15
BUZZER = GP0
LEDs (opc.) = GP6 GP7 GP8 GP9
```
