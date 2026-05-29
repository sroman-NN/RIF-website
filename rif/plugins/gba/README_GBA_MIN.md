# GBA minimo para RIF

Contenido:

- `gba/gba.pack`: pack GBA.
- `gba/hello.rif`: fuente de ejemplo.
- `plugins/gba/plugins/gba_*.py`: piezas que emiten header, logo, checksum, entrada ARM, framebuffer y padding.
- `plugins/gba/cli.py`: CLI del plugin.
- `plugins/gba/cli/`: comandos del plugin.

Uso desde la raiz del proyecto:

```bash
python -m rif build gba
python -m rif -pcli gba install mGBA --add-path
python -m rif -pcli gba run gba/hello.gba -nd
```

La regla disponible es:

```rif
headers
logo
checksum
entry
frame
rompad
```

Que hace:

- Genera un header GBA con logo Nintendo y checksum correcto.
- Entra a codigo ARM en `0x080000C0`.
- Activa modo grafico 3.
- Copia un framebuffer estatico a VRAM.
- Muestra `HOLA MUNDO` sobre pantalla verde.

Este no es un backend GBA completo. Es un ejemplo minimo para validar generacion de ROM por plugin.
