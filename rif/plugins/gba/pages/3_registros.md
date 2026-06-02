# Registros de CPU y MMIO

La tabla `gba.regs.pack` contiene registros de CPU, aliases, registros
bancarizados, MMIO y regiones de memoria. Cada fila incluye metadatos para saber
si el simbolo sirve en ARM, Thumb, como registro bajo, como MMIO o como region.

## CPU

| Registro | Uso |
|---|---|
| `R0-R3` | Argumentos, temporales y retornos. |
| `R4-R7` | Registros generales bajos; utiles para variables locales. |
| `R8-R12` | Registros altos; mas comodos en ARM que en Thumb. |
| `SP` / `R13` | Stack pointer. |
| `LR` / `R14` | Link register, retorno de subrutinas. |
| `PC` / `R15` | Program counter. |
| `CPSR` | Estado actual: flags, modo CPU, bit Thumb. |
| `SPSR_*` | Estados guardados por modos privilegiados. |

## Video y LCD

| Registro | Direccion | Funcion |
|---|---:|---|
| `DISPCNT` | `0x04000000` | Modo de video, BGs, sprites y frame select. |
| `DISPSTAT` | `0x04000004` | Estado VBlank/HBlank/VCOUNT e IRQs. |
| `VCOUNT` | `0x04000006` | Linea actual de pantalla, 0-227. |
| `BG0CNT`-`BG3CNT` | `0x04000008` | Control de fondos. |
| `BGxHOFS/BGxVOFS` | `0x04000010` | Scroll de fondos. |
| `BG2PA`-`BG3Y` | `0x04000020` | Matrices y offsets affine. |
| `WIN*`, `MOSAIC`, `BLDCNT` | `0x04000040+` | Ventanas, mosaico y blending. |

## Sonido

| Registro | Direccion | Funcion |
|---|---:|---|
| `SOUND1CNT_*`-`SOUND4CNT_*` | `0x04000060+` | Canales PSG heredados. |
| `SOUNDCNT_L` | `0x04000080` | Mezcla PSG. |
| `SOUNDCNT_H` | `0x04000082` | Direct Sound A/B, volumen y DMA. |
| `SOUNDCNT_X` | `0x04000084` | Master enable y estado de canales. |
| `SOUNDBIAS` | `0x04000088` | Bias de salida. |
| `FIFO_A`, `FIFO_B` | `0x040000A0+` | FIFOs de Direct Sound. |

## DMA y timers

| Registro | Direccion | Funcion |
|---|---:|---|
| `DMA0SAD/DAD/CNT` | `0x040000B0` | DMA0. |
| `DMA1SAD/DAD/CNT` | `0x040000BC` | DMA1, comun para audio FIFO. |
| `DMA2SAD/DAD/CNT` | `0x040000C8` | DMA2. |
| `DMA3SAD/DAD/CNT` | `0x040000D4` | DMA3, transferencias grandes. |
| `TM0CNT`-`TM3CNT` | `0x04000100` | Timers. |

Los registros de 32 bits tambien tienen subpartes de 16 bits con sufijos `00`
y `01`, por ejemplo `DMA1CNT00` y `DMA1CNT01`.

## Entrada

| Registro | Direccion | Detalle |
|---|---:|---|
| `KEYINPUT` | `0x04000130` | Botones activos en bajo: `0` significa presionado. |
| `KEYCNT` | `0x04000132` | Control de IRQ de botones. |

Mascaras:

| Mascara | Valor |
|---|---:|
| `KEY_A` | `0x0001` |
| `KEY_B` | `0x0002` |
| `KEY_SELECT` | `0x0004` |
| `KEY_START` | `0x0008` |
| `KEY_RIGHT` | `0x0010` |
| `KEY_LEFT` | `0x0020` |
| `KEY_UP` | `0x0040` |
| `KEY_DOWN` | `0x0080` |
| `KEY_R` | `0x0100` |
| `KEY_L` | `0x0200` |

## Interrupciones y sistema

| Registro | Direccion | Uso |
|---|---:|---|
| `IE` | `0x04000200` | Interrupt enable. |
| `IF` | `0x04000202` | Interrupt flags; escribe 1 para limpiar bits. |
| `IME` | `0x04000208` | Master interrupt enable. |
| `WAITCNT` | `0x04000204` | Waitstates de cartucho y prefetch. |
| `POSTFLG` | `0x04000300` | Estado post-boot. |
| `HALTCNT` | `0x04000301` | Halt/stop. |

## Regiones

`BIOS`, `EWRAM`, `IWRAM`, `IOREG`, `PALRAM`, `VRAM`, `OAM`, `ROM_WS0`,
`ROM_WS1`, `ROM_WS2` y `SRAM` estan declaradas como regiones para documentar el
mapa y permitir referencias consistentes.
