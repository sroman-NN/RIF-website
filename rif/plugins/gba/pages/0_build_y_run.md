# Build y Run

El ejemplo GBA funcional se construye desde la raiz del proyecto:

```bash
python -m rif build examples/gba --plugin gba --name example
```

Ejecutar con mGBA:

```bash
python -m rif -pcli gba run examples/gba/hello.gba -nd
```

`-nd` intenta reutilizar una ventana abierta de mGBA para no duplicar instancias.
