# Keep Talking and Nobody Explodes – Pico Explorer

Versão física do jogo cooperativo com Raspberry Pi Pico e Pimoroni Pico Explorer.

## Como jogar

- O **desativador** vê o ecrã e descreve o que vê.
- O **especialista** tem o manual (`manual.md`) impresso e diz o que fazer.
- O especialista **não pode ver o ecrã**.
- 3 erros ou tempo esgotado = explosão. Resolver os 3 módulos = vitória.

---

## Hardware necessário

- Pimoroni Pico Explorer Base
- Raspberry Pi Pico ou Pico W (com firmware Pimoroni MicroPython)
- 5 cabos jumper de cores diferentes

---

## Ligação dos cabos

> **NÃO ligar nada ao GP0** — reservado para o buzzer interno.

| Pino | Cor do cabo | Outro extremo |
|------|-------------|---------------|
| GP1  | AZUL        | GND           |
| GP2  | CASTANHO    | GND           |
| GP3  | AMARELO     | GND           |
| GP4  | VERDE       | GND           |
| GP5  | VERMELHO    | GND           |

Cabo ligado (pino ao GND) = cabo intacto.
Puxar o cabo = cortá-lo no jogo.

---

## Instalação

1. Instalar [firmware Pimoroni MicroPython](https://github.com/pimoroni/pimoroni-pico/releases) no Pico
2. Abrir Thonny e ligar o Pico
3. Abrir `main.py` e guardar no Pico: `File > Save as > Raspberry Pi Pico`
4. Reiniciar o Pico — o jogo arranca automaticamente

---

## Módulos do jogo

| Módulo  | Descrição                                                       |
|---------|-----------------------------------------------------------------|
| CABOS   | Desativador descreve as cores, especialista diz qual cortar     |
| SIMON   | Memoriza e repete a sequência de cores com os botões            |
| SENHA   | Forma uma palavra válida navegando com os botões                |

---

## Controlos

| Botão | Função                          |
|-------|---------------------------------|
| A     | Subir / selecionar              |
| B     | Descer                          |
| X     | Próxima coluna                  |
| Y     | Confirmar / Começar / Reiniciar |

---

## Manual do especialista

Ver [`manual.md`](manual.md) — imprime antes de jogar.
