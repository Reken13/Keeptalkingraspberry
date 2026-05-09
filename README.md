# Keep Talking and Nobody Explodes – Pico Explorer

Version fisica del juego cooperativo con Raspberry Pi Pico y Pimoroni Pico Explorer.

## Como jugar

- El **desactivador** ve la pantalla y describe lo que ve.
- El **experto** tiene el manual (`manual.md`) impreso y dice que hacer.
- El experto NO puede ver la pantalla.
- 3 errores o tiempo agotado = explosion. Resolver los 3 modulos = victoria.

---

## Hardware necesario

- Pimoroni Pico Explorer Base
- Raspberry Pi Pico o Pico W (con firmware Pimoroni MicroPython)
- 5 cables jumper de colores

---

## Conexion de cables

> **NO conectar nada a GP0** — reservado para el buzzer interno.

| Pin  | Color cable | Otro extremo |
|------|-------------|--------------|
| GP1  | MARRON      | GND          |
| GP2  | VERDE       | GND          |
| GP3  | AMARILLO    | GND          |
| GP4  | ROJO        | GND          |
| GP5  | AZUL        | GND          |

Cable enchufado (pin conectado a GND) = cable intacto.
Jalar el cable fisicamente = cortarlo en el juego.

---

## Instalacion

1. Instalar [firmware Pimoroni MicroPython](https://github.com/pimoroni/pimoroni-pico/releases) en la Pico
2. Abrir Thonny y conectar la Pico
3. Abrir `main.py` y guardarlo en la Pico: `File > Save as > Raspberry Pi Pico`
4. Reiniciar la Pico — el juego arranca automaticamente

---

## Modulos del juego

| Modulo     | Descripcion                                                   |
|------------|---------------------------------------------------------------|
| CABLES     | Desactivador describe colores, experto dice cual cortar       |
| SIMON      | Memoriza y repite secuencia de colores con los botones        |
| CONTRASENA | Forma una palabra valida navegando con los botones            |

---

## Controles (botones del Pico Explorer)

| Boton | Uso general                        |
|-------|------------------------------------|
| A     | Subir / seleccionar                |
| B     | Bajar                              |
| X     | Siguiente columna                  |
| Y     | Confirmar / Empezar / Reiniciar    |

---

## Pantalla durante el juego

```
04:32  #7341  XX
─────────────────
```

- `04:32` — tiempo restante (verde → amarillo → rojo)
- `#7341` — numero de serie de la bomba (para las reglas)
- `XX`    — errores acumulados (3 = explosion)

---

## Manual del experto

Ver [`manual.md`](manual.md) — imprimelo antes de jugar.
