# Tablas y secciones

Una seccion empieza con `.nombre`.

Las tablas usan el separador configurado:

```rif
.regs
| NAME | binary | bits |
| a    | 000    | 8    |
```

Convenciones principales:

- `.pack`: plugins, packer y mapeos de tipos
- `.world`: datos globales del target
- `.sections`: secciones de salida
- `.regs`: registros
- `.vars`: variables de bits
- `.types`: tipos declarados
- `.DATA_DEFINITION`: patron de definicion de datos
- `.rules`: reglas de instrucciones
- `.stacks` y `.heaps`: regiones de memoria

Las tablas se convierten en objetos consultables por el compiler, linker y plugins.

> **Tip:** Puedes modificar y formatear tablas programáticamente usando la CLI `rif table` (por ejemplo, `rif table format --from archivo.pack` o `rif table modify --from archivo.pack "regs add row mi_reg 0x0"`). Para más detalles, consulta `rif help comando_table`.

El comportamiento del lector de fuente se define en `.pack`:

```rif
reader:
    comment "#"
    blocks ":"
    section ".section"
    sources ".rif"
```
