# Basics

`basics` es el plugin base de RIF. Aporta instrucciones comunes para validar operandos, emitir bits, hacer transformaciones binarias, crear relocaciones y generar documentacion VS Code.

## Incluye

- `need`, `emit`, `call`, `end_instruction`
- comparadores `eq`, `neq`, `lt`, `lte`, `gt`, `gte`
- bits `bitcat`, `bitsize`, `bitfit`, `trunc`, `zext`, `sext`
- layout `align`, `pad`
- simbolos `exists`, `emitaddress`, `reloc`, `reldis`
- CLI `rif -pcli basics build-doc`

## VS Code

El comando `build-doc` lee `doc.json`, `syntaxs.json` y `build.json`. Si no existen datos suficientes, genera un VSIX minimo con palabras RIF base para resaltado y prediccion.
