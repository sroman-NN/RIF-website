# Instrucciones

Las instrucciones de `basics` son piezas comunes para paquetes retargetables.

```rif
byte:
    need VALUE, imm
    emit imm.binary
```

`need` captura operandos, `emit` materializa bits y `call` permite reutilizar reglas declaradas en `.rules`.

Las instrucciones condicionales `ON/OFF` y `switch/case` viven en el runtime del core, pero pueden ejecutar plugins dentro de cada rama.
