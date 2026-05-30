# Version actual

A 0.0.1 Beta

Esta version esta enfocada en cerrar el core retargetable:

- parser y AST
- collector de IR
- compiler runtime
- linker y placeholders
- plugins basicos
- lector de fuente configurable desde `.pack`
- build de proyectos por carpeta
- fillables `@...` provistos por plugins
- CLI por plugin con `rif -pcli`
- VSIX minimo desde `doc.json`, `syntaxs.json` y `build.json`
- plugin `fonts` con bitmap 5x7x1
- ejemplo GBA funcional por plugin
- CLI local
- help local con paginas de plugins

## Falta

- MIR estable para optimizadores.
- optimizadores de seleccion y reduccion de instrucciones.
- servidor de lenguaje completo para VS Code.
- diagnosticos semanticos profundos desde `.pack`.
- empaquetado final del compilador con CLI generada automaticamente.
- mas formatos de salida conectados por plugins.

La API todavia puede cambiar.
