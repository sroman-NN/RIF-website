# Macros de ROM

El plugin `gba` incluye macros que generan los datos requeridos por el hardware del GBA
en la cabecera de la ROM. Todas se declaran como words en el pack y se llaman desde `.rules`.

## set_headers

Genera los primeros 0xC0 bytes de la cabecera ROM:
- Entry point (instrucción `B entry`)
- Logo Nintendo (96 bytes, requerido por el BIOS)
- Título del juego (12 bytes, ASCII uppercase)
- Código del juego (4 bytes: `RIF0`)
- Código del fabricante (2 bytes: `00`)
- Byte de versión del BIOS GBA (`0x96`)
- Checksum de cabecera

```rif
.rom
set_headers
```

## set_logo

Emite solo el logo Nintendo (bytes 0x04–0x9F de la ROM).

## set_checksum

Escribe el bloque de checksum con el título del juego.

```rif
set_checksum "Mi Juego"
```

## set_entry

Genera el bloque de código de entrada ARM (desde 0xC0 a ~0x100):
- Inicializa el modo de video (BG Mode 3, 15bpp)
- Copia el framebuffer desde la ROM a VRAM (0x06000000)
- Queda en loop infinito

## set_frame

Genera el framebuffer inicial (240×160 pixels, 76800 bytes × 2 bytes/pixel BGR555).

```rif
set_frame "HELLO WORLD", white, green
```

Argumentos: texto a centrar, color del texto, color del fondo.

## set_rompad / rompad

Rellena la ROM hasta 512 KB con bytes `0xFF`, que es el valor de borrado de una Flash ROM.

```rif
set_rompad
```

## Ejemplo de ROM mínima

```rif
.rom
set_headers
set_frame "MI JUEGO", white, green
set_entry
set_rompad
```

Esta secuencia genera una ROM GBA válida que muestra texto centrado en pantalla.
