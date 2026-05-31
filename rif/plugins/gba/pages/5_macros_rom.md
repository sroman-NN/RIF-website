# Macros de ROM

El plugin `gba` incluye macros para formar una ROM GBA valida.

## Secuencia minima funcional

```rif
.section .rom
set_headers
set_logo
set_checksum
set_entry
set_frame
set_rompad
```

## Secuencia avanzada del ejemplo

```rif
.section .rom
set_headers
set_logo
set_checksum
set_entry_thumb
set_frame
game_code
set_rompad
```

## Macros

- `set_headers`: emite la instruccion ARM inicial que salta a `0x080000C0`.
- `set_logo`: emite el logo Nintendo requerido por el BIOS.
- `set_checksum`: emite titulo, game code, maker code, version y checksum de cabecera.
- `set_entry`: emite entrada ARM que configura video mode 3, copia framebuffer a VRAM y queda en loop.
- `set_entry_thumb`: emite stub ARM que configura video mode 3 y salta al codigo Thumb ubicado despues del framebuffer.
- `set_frame`: emite un framebuffer 240x160 BGR555 con texto centrado.
- `game_code`: codigo Thumb de ejemplo para la ROM avanzada.
- `set_rompad` / `rompad`: rellena hasta el tamaño ROM configurado usando el offset actual real.
