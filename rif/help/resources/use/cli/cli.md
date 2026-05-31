# CLI

Comandos principales:

```bash
python -m rif lex archivo.pack
python -m rif parse archivo.pack
python -m rif pack archivo.pack
python -m rif link archivo.pack
python -m rif compile archivo.pack instruccion
python -m rif build archivo.pack
python -m rif build archivo.pack --source-file programa.rif
python -m rif build carpeta_proyecto
python -m rif table modify --from archivo.pack "regs set ax bits 32"
python -m rif table format --from archivo.pack
python -m rif table undo
python -m rif -pcli plugin comando
python -m rif -pcli basics build-doc carpeta_proyecto
python -m rif help
```

`rif help` lista temas locales.

`rif help --open` abre `help/index.html`.

`rif help tema` imprime un documento Markdown.

`rif build carpeta_proyecto` busca el `.pack` dentro de la carpeta y lee los fuentes indicados por el `reader` del paquete.

`rif -pcli nombre ...` delega comandos a la CLI propia de un plugin.

`rif -pcli basics build-doc carpeta` lee `doc.json`, `syntaxs.json` y `build.json`; con `doc.json` y `build.json` ya puede generar un VSIX.

`rif help plugin` muestra la documentacion del plugin. Si el plugin tiene `pages/0_nombre.md`, tambien puedes abrir subsecciones con `rif help plugin/nombre`.
