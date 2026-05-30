# Instrucciones

Las instrucciones viven en `.rules`.

Una regla usa `need` para capturar operandos y plugins para producir IR o bytes.

```rif
byte:
    need VALUE, imm
    emit imm.binary
```

Elementos comunes:

- `need`: captura operandos o literales
- `emit`: emite bits
- `call`: ejecuta otra regla
- `end_instruction`: termina la regla actual
- `ON/OFF`: flujo condicional
- `switch/case`: seleccion por valor

Las reglas deben mantenerse genericas. La semantica propia de una arquitectura debe estar en plugins.

El source de usuario se lee con el `reader` del `.pack`. Por eso una arquitectura puede definir comentario, separador, bloque de labels, directiva de seccion y extensiones de fuente sin hardcodear el core.

Tambien existen fillables:

```rif
@fill_bitmap_array_logo
```

Un fillable llama una funcion `fill_*` expuesta por un plugin declarado y pega el resultado antes de compilar.
