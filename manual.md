# MANUAL DO ESPECIALISTA

> Imprime esta página antes de jogar.
> **Não podes ver o ecrã do desativador.**
> O desativador descreve o que vê. Tu dizes o que fazer.

---

## INFORMAÇÃO GERAL

No topo do ecrã o desativador vê sempre:

```
MM:SS  #XXXX  [erros]
```

- `MM:SS` — tempo restante
- `#XXXX` — número de série (4 algarismos)
- `X` / `XX` / `XXX` — erros (3 = explosão)

### Serial ímpar vs par

Soma os 4 algarismos do número de série.
- Soma ímpar → **serial ímpar**
- Soma par   → **serial par**

Exemplos:
- `#3742` → 3+7+4+2 = 16 → **par**
- `#2513` → 2+5+1+3 = 11 → **ímpar**

---

## MÓDULO: CABOS

O desativador vê entre 3 e 5 cabos coloridos, numerados de cima para baixo.
Diz-te quantos são e as cores, por ordem.

### 3 cabos

| Condição                              | Cortar        |
|---------------------------------------|---------------|
| Não há nenhum VERMELHO                | Cabo 2        |
| O último cabo é VERDE                 | Último cabo   |
| Há mais de 1 AZUL                     | Último AZUL   |
| (nenhuma das anteriores)              | Último cabo   |

### 4 cabos

| Condição                                        | Cortar           |
|-------------------------------------------------|------------------|
| Mais de 1 VERMELHO **e** serial ímpar           | Último VERMELHO  |
| Último é AMARELO **e** não há VERMELHO          | Cabo 1           |
| Exatamente 1 AZUL                               | Cabo 1           |
| (nenhuma das anteriores)                        | Cabo 2           |

### 5 cabos

| Condição                                          | Cortar   |
|---------------------------------------------------|----------|
| Último é CASTANHO **e** serial ímpar              | Cabo 4   |
| Exatamente 1 VERMELHO **e** mais de 1 AMARELO    | Cabo 1   |
| Não há nenhum CASTANHO                            | Cabo 2   |
| (nenhuma das anteriores)                          | Cabo 1   |

---

## MÓDULO: SIMON

O desativador vê 4 quadrados coloridos (VERMELHO, AZUL, VERDE, AMARELO) que piscam em sequência.
Deve repetir a sequência carregando nos botões corretos.

**Os botões não correspondem diretamente às cores.**
A correspondência muda conforme o serial e os erros acumulados.

### Serial PAR

| Erros | VERMELHO | AZUL | VERDE | AMARELO |
|-------|----------|------|-------|---------|
| 0     | A        | B    | X     | Y       |
| 1     | B        | A    | Y     | X       |
| 2+    | X        | Y    | A     | B       |

### Serial ÍMPAR

| Erros | VERMELHO | AZUL | VERDE | AMARELO |
|-------|----------|------|-------|---------|
| 0     | B        | X    | Y     | A       |
| 1     | X        | Y    | A     | B       |
| 2+    | Y        | A    | B     | X       |

**Como usar:**
1. O desativador diz a cor que pisca.
2. Tu procuras na tabela e dizes que botão carregar.
3. Repete para cada cor da sequência.
4. A sequência cresce 1 cor por ronda (até 4 rondas).

---

## MÓDULO: SENHA

O desativador vê 5 colunas de letras, com uma letra destacada em cada coluna.
Tem de formar uma palavra válida de 5 letras.

### Controlos do desativador

| Botão | Ação                            |
|-------|---------------------------------|
| A     | Subir letra na coluna atual     |
| B     | Descer letra na coluna atual    |
| X     | Passar para a próxima coluna    |
| Y     | Confirmar a palavra             |

### Palavras válidas

```
ABOUT   AFTER   COULD   EVERY   FIRST
GREAT   HOUSE   NEVER   OTHER   PLACE
RIGHT   SMALL   STILL   THEIR   THERE
THING   THINK   THREE   WATER   WHERE
WORLD
```

**Como ajudar:**
- O desativador diz-te que letras aparecem em cada posição.
- Tu procuras qual das palavras encaixa.
- Dizes qual letra colocar em cada coluna.
