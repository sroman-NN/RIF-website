# Macros Estructurales de ROM

La BIOS de Game Boy Advance valida los primeros 192 bytes del cartucho antes de
ceder control al juego. El plugin `gba` ofrece macros que emiten esos bytes y el
puente de entrada.

## Secuencia recomendada

```rif
.header
    set_headers
    set_logo
    set_checksum "RIF GBA"
    set_entry_thumb

.rom
main:
    arm_b main

.rodata
    rompad
```

## Macros

| Macro | Funcion |
|---|---|
| `set_headers` | Emite la instruccion ARM inicial de salto de cabecera. |
| `set_logo` | Emite los 156 bytes del logo requerido por BIOS. |
| `set_checksum` | Calcula y emite metadatos/checksum de cabecera. |
| `set_entry` | Emite entrada ARM. |
| `set_entry_thumb` | Emite puente ARM -> Thumb. |
| `set_frame` | Emite un framebuffer Mode 3 solido; no dibuja texto ni fuentes. |
| `set_rompad` | Rellena la ROM a un tamano valido. |
| `rompad` | Alias de `set_rompad`. |

## Cabecera

La seccion `.header` tiene `voffset 0x08000000`. El bloque debe quedar al inicio
del archivo. Si omites `set_logo` o `set_checksum`, un emulador laxo podria
abrir la ROM, pero hardware real o emuladores estrictos pueden fallar.

## Entrada

La BIOS entra al cartucho en estado ARM. `set_entry_thumb` genera codigo ARM
para saltar al estado Thumb cuando el proyecto quiere ejecutar Thumb despues de
la cabecera. Si tu codigo inicial usa rutinas ARM, puedes usar `set_entry` o
mantener un puente ARM explicito.

## Padding

`rompad` debe ir al final de una seccion emitida, normalmente `.rodata` o al
final de `.rom`. Usa `0xFF` para dejar una imagen de cartucho alineada.

## Secciones y orden

El pack define:

| Seccion | Orden |
|---|---:|
| `.header` | 0 |
| `.rom` | 1 |
| `.rodata` | 2 |
| `.data` | 3 |
| `.bss` | 4 |

No coloques codigo antes de `.header` si estas construyendo una ROM completa.
