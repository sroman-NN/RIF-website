# Version actual

### RIF 0.0.3 Semi Stable

Esta version consolida el core retargetable y deja el flujo de trabajo de editor en un punto util para proyectos reales.

## Soportado

- Parser y AST para archivos `.pack`.
- Compiler runtime con reglas, operandos, placeholders y etiquetas.
- Linker con secciones, headers, memoria, padding y relocaciones.
- Lector de fuente configurable desde `.pack`.
- Build de proyectos por carpeta.
- Fillables `@...` provistos por plugins.
- CLI por plugin con `rif -pcli`.
- Sistema de plugins locales e instalables.
- Plugin `fonts` con bitmap 5x7x1.
- Ejemplo GBA funcional por plugin.
- Help local con paginas de core y plugins.
- Constructor VS Code/VSIX con `rif compile --vscode`.
- Instalador VSIX con `rif install --vscode`.

## Estado de estabilidad

`Semi Stable` significa que el flujo normal de packs, plugins, build, help y VSIX ya es usable, pero algunas APIs internas todavia pueden ajustarse mientras se cierran MIR, optimizadores y empaquetado de compiladores dedicados.

## Aun falta

- MIR estable para optimizadores.
- Optimizadores de seleccion y reduccion de instrucciones.
- Diagnosticos semanticos profundos desde `.pack`.
- Empaquetado final del compilador con CLI generada automaticamente.
- Mas formatos de salida conectados por plugins.
