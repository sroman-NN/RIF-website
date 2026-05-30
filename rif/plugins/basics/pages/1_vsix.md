# VSIX

`rif -pcli basics build-doc carpeta` crea una extension VS Code.

Archivos soportados:

- `doc.json`: documentacion por palabra.
- `syntaxs.json`: resaltado, prediccion y diagnosticos.
- `build.json`: nombre, version, publisher, extensiones y salida.
- archivos `.md`: se empaquetan como documentacion adicional.

El VSIX generado incluye grammar TextMate, snippets, completions, hover Markdown y diagnosticos por expresion regular.
