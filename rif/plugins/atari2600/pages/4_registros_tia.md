# Registros TIA

El Television Interface Adapter es el centro del Atari 2600. Controla la senal
de television, los objetos graficos, audio, colisiones y varias entradas. Sus
registros estan mapeados como memoria; escribir o leer una direccion ejecuta una
accion de hardware.

## Sincronizacion y blanking

| Registro | Dir | Acceso | Bits | Funcion |
|---|---:|---|---|---|
| `VSYNC` | `0x00` | W | D1 | Inicia/detiene la sincronizacion vertical. Escribe `0x02` por 3 scanlines NTSC. |
| `VBLANK` | `0x01` | W | D1, D6, D7 | D1 blank vertical; D6 latches de `INPT4/5`; D7 descarga paddles. |
| `WSYNC` | `0x02` | W strobe | - | Detiene el CPU hasta el inicio del siguiente horizontal blank. |
| `RSYNC` | `0x03` | W strobe | - | Resetea contador horizontal. Principalmente para test de chip. |

`WSYNC` es la herramienta principal de temporizacion. Una escritura a `WSYNC`
congela el 6507 y lo libera cuando empieza el siguiente HBlank, alineando el
codigo con la scanline.

## Playfield y colores

| Registro | Dir | Acceso | Bits | Funcion |
|---|---:|---|---|---|
| `COLUP0` | `0x06` | W | D7-D1 | Color/luminancia de player 0 y missile 0. |
| `COLUP1` | `0x07` | W | D7-D1 | Color/luminancia de player 1 y missile 1. |
| `COLUPF` | `0x08` | W | D7-D1 | Color/luminancia de playfield y ball. |
| `COLUBK` | `0x09` | W | D7-D1 | Color/luminancia de fondo. |
| `CTRLPF` | `0x0A` | W | D0,D1,D2,D4,D5 | Reflejo, score mode, prioridad y tamano de ball. |
| `PF0` | `0x0D` | W | D7-D4 | Primeros 4 bits del playfield. |
| `PF1` | `0x0E` | W | D7-D0 | 8 bits centrales del playfield. |
| `PF2` | `0x0F` | W | D7-D0 | 8 bits finales del playfield. |

El playfield tiene 20 bits por media pantalla. En modo normal la derecha repite
la izquierda; con `CTRLPF` bit D0 se refleja. Cada bit de playfield ocupa 4
color clocks, asi que el playfield base cubre 160 color clocks visibles.

`CTRLPF`:

| Bit | Nombre | Efecto |
|---:|---|---|
| D0 | REF | Refleja la mitad derecha del playfield. |
| D1 | SCORE | Izquierda usa `COLUP0`, derecha usa `COLUP1`. |
| D2 | PFP | Playfield/ball tienen prioridad sobre players/missiles. |
| D4-D5 | Ball size | `00`=1, `01`=2, `10`=4, `11`=8 color clocks. |

## Players, missiles y ball

| Registro | Dir | Acceso | Bits | Funcion |
|---|---:|---|---|---|
| `NUSIZ0` | `0x04` | W | D5-D0 | Numero/tamano de copias de player 0 y missile 0. |
| `NUSIZ1` | `0x05` | W | D5-D0 | Numero/tamano de copias de player 1 y missile 1. |
| `REFP0` | `0x0B` | W | D3 | Refleja horizontalmente player 0. |
| `REFP1` | `0x0C` | W | D3 | Refleja horizontalmente player 1. |
| `GRP0` | `0x1B` | W | D7-D0 | Bitmap de 8 bits para player 0. |
| `GRP1` | `0x1C` | W | D7-D0 | Bitmap de 8 bits para player 1. |
| `ENAM0` | `0x1D` | W | D1 | Habilita missile 0. |
| `ENAM1` | `0x1E` | W | D1 | Habilita missile 1. |
| `ENABL` | `0x1F` | W | D1 | Habilita ball. |
| `VDELP0` | `0x25` | W | D0 | Retrasa player 0 una linea. |
| `VDELP1` | `0x26` | W | D0 | Retrasa player 1 una linea. |
| `VDELBL` | `0x27` | W | D0 | Retrasa ball una linea. |

Los players son registros de 8 bits. El TIA los serializa mientras el haz cruza
la pantalla. Para mostrar graficos verticales, el kernel cambia `GRP0`/`GRP1`
en lineas sucesivas.

## Posicion horizontal y movimiento

| Registro | Dir | Acceso | Funcion |
|---|---:|---|---|
| `RESP0` | `0x10` | W strobe | Resetea posicion horizontal de player 0. |
| `RESP1` | `0x11` | W strobe | Resetea posicion horizontal de player 1. |
| `RESM0` | `0x12` | W strobe | Resetea posicion horizontal de missile 0. |
| `RESM1` | `0x13` | W strobe | Resetea posicion horizontal de missile 1. |
| `RESBL` | `0x14` | W strobe | Resetea posicion horizontal de ball. |
| `HMP0` | `0x20` | W | Movimiento fino de player 0 en D7-D4. |
| `HMP1` | `0x21` | W | Movimiento fino de player 1 en D7-D4. |
| `HMM0` | `0x22` | W | Movimiento fino de missile 0 en D7-D4. |
| `HMM1` | `0x23` | W | Movimiento fino de missile 1 en D7-D4. |
| `HMBL` | `0x24` | W | Movimiento fino de ball en D7-D4. |
| `RESMP0` | `0x28` | W | Acopla missile 0 a player 0 si D1=1. |
| `RESMP1` | `0x29` | W | Acopla missile 1 a player 1 si D1=1. |
| `HMOVE` | `0x2A` | W strobe | Aplica todos los registros de movimiento horizontal. |
| `HMCLR` | `0x2B` | W strobe | Limpia `HMP0`, `HMP1`, `HMM0`, `HMM1`, `HMBL`. |

La posicion gruesa depende del ciclo exacto en que escribes `RESPx`. El ajuste
fino se carga en `HMPx` y se aplica con `HMOVE`, idealmente justo despues de
`WSYNC`.

## Audio

| Registro | Dir | Acceso | Bits | Funcion |
|---|---:|---|---|---|
| `AUDC0` | `0x15` | W | D3-D0 | Tipo de onda/ruido del canal 0. |
| `AUDC1` | `0x16` | W | D3-D0 | Tipo de onda/ruido del canal 1. |
| `AUDF0` | `0x17` | W | D4-D0 | Divisor de frecuencia del canal 0. |
| `AUDF1` | `0x18` | W | D4-D0 | Divisor de frecuencia del canal 1. |
| `AUDV0` | `0x19` | W | D3-D0 | Volumen del canal 0. |
| `AUDV1` | `0x1A` | W | D3-D0 | Volumen del canal 1. |

Cada canal tiene control, frecuencia y volumen independientes. `AUDVx = 0`
silencia el canal; valores `1-15` aumentan el nivel.

## Colisiones y entradas TIA

| Registro | Dir pack | Acceso | Bits | Lectura |
|---|---:|---|---|---|
| `CXM0P` | `0x30` | R | D7,D6 | M0/P1 y M0/P0. |
| `CXM1P` | `0x31` | R | D7,D6 | M1/P0 y M1/P1. |
| `CXP0FB` | `0x32` | R | D7,D6 | P0/PF y P0/BL. |
| `CXP1FB` | `0x33` | R | D7,D6 | P1/PF y P1/BL. |
| `CXM0FB` | `0x34` | R | D7,D6 | M0/PF y M0/BL. |
| `CXM1FB` | `0x35` | R | D7,D6 | M1/PF y M1/BL. |
| `CXBLPF` | `0x36` | R | D7 | BL/PF. |
| `CXPPMM` | `0x37` | R | D7,D6 | P0/P1 y M0/M1. |
| `INPT0`-`INPT3` | `0x38-0x3B` | R | D7 | Entradas de paddle. |
| `INPT4`-`INPT5` | `0x3C-0x3D` | R | D7 | Botones/latches. |
| `CXCLR` | `0x2C` | W strobe | - | Limpia todos los latches de colision. |

El pack usa direcciones "ghost" de lectura (`0x30-0x3D`) para poder nombrar
registros leidos sin chocar con nombres de escritura que comparten lineas bajas
del TIA.
