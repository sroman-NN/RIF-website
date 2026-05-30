# Basics

`basics` es el plugin base.

Incluye instrucciones comunes:

- `need`
- `emit`
- `call`
- `exists`
- `fits`
- `eq` y `neq`
- `bitcat`
- `bitsize`
- `bitfit`
- `trunc`
- `zext`
- `sext`
- `lt`, `lte`, `gt`, `gte`
- `align`
- `pad`
- `reldis`
- `reloc`
- `emitadress`
- `error` y `raise`
- `end_instruction`
- `emitaddress`

Tambien incluye CLI:

```bash
python -m rif -pcli basics build-doc carpeta
```

Ese comando genera un VSIX con resaltado, prediccion, snippets, hover Markdown y diagnosticos simples desde `doc.json`, `syntaxs.json`, `build.json` y archivos `.md`.

No define una arquitectura. Solo aporta piezas genericas para construir reglas.
