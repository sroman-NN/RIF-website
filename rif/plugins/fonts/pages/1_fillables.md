# Fillables

El plugin `fonts` expone fillables para el linker.

```rif
@fill_bitmap_array_logo
```

El linker busca funciones `fill_*` en los plugins declarados por el `.pack`, ejecuta la funcion y pega el texto retornado en el codigo fuente antes de compilar.

Esto permite crear tablas o datos repetitivos sin hardcodear macros dentro del core.

## Texto 5x7x1

La forma inversa de fillables permite poner primero el dato y despues la funcion:

```rif
@"ESTO ES UN TEXTO"@fonts_fill_5x7x1
```

`fonts_fill_5x7x1` genera una tabla `u8[]` con 7 bytes por glifo usando `font-5x7x1.f`, registra el resultado en `fills.json` y usa cache de proyecto para evitar recalcular el mismo texto.
