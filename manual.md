# MANUAL DEL EXPERTO

> Imprime esta pagina antes de jugar.
> NO puedes ver la pantalla del desactivador.
> El desactivador te describe lo que ve. Tu le dices que hacer.

---

## INFORMACION GENERAL

En la parte superior de la pantalla el desactivador siempre ve:

```
MM:SS  #XXXX  [errores]
```

- `MM:SS` — tiempo restante
- `#XXXX` — numero de serie (4 digitos)
- `X` / `XX` / `XXX` — errores (3 = pierde)

### Serial impar vs par

Suma los 4 digitos del serial.
- Suma impar → **serial impar**
- Suma par   → **serial par**

Ejemplos:
- `#3742` → 3+7+4+2 = 16 → **par**
- `#1531` → 1+5+3+1 = 10 → **par**
- `#2513` → 2+5+1+3 = 11 → **impar**

---

## MODULO: CABLES

El desactivador ve entre 3 y 5 cables de colores, numerados de arriba a abajo.
Te dice cuantos hay y de que colores, en orden.

### 3 cables

| Condicion                          | Cortar        |
|------------------------------------|---------------|
| No hay ningun ROJO                 | Cable 2       |
| El ultimo cable es VERDE           | Ultimo cable  |
| Hay mas de 1 AZUL                  | Ultimo AZUL   |
| (ninguna anterior)                 | Ultimo cable  |

### 4 cables

| Condicion                                    | Cortar        |
|----------------------------------------------|---------------|
| Mas de 1 ROJO **y** serial impar             | Ultimo ROJO   |
| Ultimo es AMARILLO **y** no hay ROJO         | Cable 1       |
| Exactamente 1 AZUL                           | Cable 1       |
| (ninguna anterior)                           | Cable 2       |

### 5 cables

| Condicion                                    | Cortar        |
|----------------------------------------------|---------------|
| Ultimo es MARRON **y** serial impar          | Cable 4       |
| Exactamente 1 ROJO **y** mas de 1 AMARILLO  | Cable 1       |
| No hay ningun MARRON                         | Cable 2       |
| (ninguna anterior)                           | Cable 1       |

---

## MODULO: SIMON

El desactivador ve 4 cuadros de colores que se iluminan en secuencia.
Debe repetir la secuencia pulsando los botones correctos.

**Los botones NO corresponden directamente a los colores.**
La correspondencia cambia segun el serial y los errores acumulados.

### Serial PAR

| Errores | ROJO | AZUL | VERDE | AMARILLO |
|---------|------|------|-------|----------|
| 0       | A    | B    | X     | Y        |
| 1       | B    | A    | Y     | X        |
| 2+      | X    | Y    | A     | B        |

### Serial IMPAR

| Errores | ROJO | AZUL | VERDE | AMARILLO |
|---------|------|------|-------|----------|
| 0       | B    | X    | Y     | A        |
| 1       | X    | Y    | A     | B        |
| 2+      | Y    | A    | B     | X        |

**Como usarlo:**
1. El desactivador dice el color que se ilumina.
2. Tu buscas en la tabla y le dices que boton pulsar.
3. Se repite para cada color de la secuencia.
4. La secuencia crece 1 color por ronda (hasta 4 rondas).

---

## MODULO: CONTRASENA

El desactivador ve 5 columnas de letras. Cada columna tiene una letra resaltada.
Debe formar una palabra valida de 5 letras.

### Controles del desactivador

| Boton | Accion                        |
|-------|-------------------------------|
| A     | Subir letra en columna actual |
| B     | Bajar letra en columna actual |
| X     | Pasar a la siguiente columna  |
| Y     | Confirmar la palabra          |

### Palabras validas

```
ABOUT   AFTER   COULD   EVERY   FIRST
GREAT   HOUSE   NEVER   OTHER   PLACE
RIGHT   SMALL   STILL   THEIR   THERE
THING   THINK   THREE   WATER   WHERE
WORLD
```

**Como ayudar:**
- El desactivador te dice que letras son posibles en cada posicion.
- Tu buscas en la lista cual de las palabras encaja.
- Le dices que letra poner en cada columna.
