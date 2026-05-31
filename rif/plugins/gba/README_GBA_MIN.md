# GBA para RIF

Este plugin contiene el pack GBA avanzado funcional usado por `examples/gba`.

Contenido principal:

- `packs/example/gba.pack`: pack raiz que enlaza registros, tipos, secciones, words y reglas.
- `packs/example/gba.rules.pack`: macros de ROM e instrucciones Thumb.
- `plugins/thumb_ins.py`: emisor Thumb de 16 bits little-endian.
- `plugins/gba_*.py`: cabecera, logo, checksum, entrada ARM, framebuffer y padding.
- `fillables.py`: generadores `@fill_screen` y `@fill_screen_text`.

Uso desde la raiz del proyecto:

```bash
python -m rif build examples/gba --plugin gba --name example
python -m rif -pcli gba run examples/gba/hello.gba -nd
```

Secuencia ROM avanzada usada por el ejemplo:

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

`set_rompad` rellena hasta el tamaño ROM configurado por el plugin usando la posicion real actual, por eso no duplica padding cuando se añade codigo despues del framebuffer.
