# Ejemplo GBA RIF

Construccion desde la raiz del proyecto:

```bash
python -m rif build examples/gba --plugin gba --name example
```

Ejecucion con mGBA:

```bash
python -m rif -pcli gba run examples/gba/hello.gba -nd
```

Este ejemplo usa el pack avanzado real de `rif/plugins/gba/packs/example/gba.pack`.
