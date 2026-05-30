# Build y Run

El ejemplo GBA se construye desde una carpeta de proyecto:

```bash
python -m rif build gba
python -m rif -pcli gba run gba/hello.gba -nd
```

`-nd` intenta reutilizar una ventana abierta de mGBA para no duplicar instancias.

El pack GBA declara instrucciones pequenas para header, logo, checksum, entrada, framebuffer y padding.
