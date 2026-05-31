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
python -m rif compile --vscode --ext .gbasm --p gba sound fonts basics
python -m rif install --vscode build/vscode/extension.vsix
python -m rif help
```

`rif help` lista temas locales.

`rif help --open` abre el portal local `help/index.html`.

`rif help tema` imprime un documento Markdown.

`rif build carpeta_proyecto` busca el `.pack` dentro de la carpeta y lee los fuentes indicados por el `reader` del paquete.

`rif -pcli nombre ...` delega comandos a la CLI propia de un plugin.

`rif -pcli basics build-doc carpeta` lee `doc.json`, `syntaxs.json` y `build.json` de un proyecto y genera un VSIX desde esa carpeta.

`rif compile --vscode --ext .gbasm --p gba sound fonts basics` arma una extension VS Code desde los bundles `vscode/` de los plugins indicados.

`rif install --package <url/carpeta>` instala un plugin desde una ruta local o URL de GitHub.

`rif install --vscode <archivo.vsix>` instala una extension VSIX empaquetada en Visual Studio Code usando el comando `code`.

`rif help plugin` muestra la documentacion del plugin. Si el plugin tiene `pages/0_nombre.md`, tambien puedes abrir subsecciones con `rif help plugin/nombre`.

Para el flujo completo de VS Code consulta `rif help vscode`.
