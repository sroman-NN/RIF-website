# Fillables

El plugin `fonts` expone fillables para el linker.

```rif
@fill_bitmap_array_logo
```

El linker busca funciones `fill_*` en los plugins declarados por el `.pack`, ejecuta la funcion y pega el texto retornado en el codigo fuente antes de compilar.

Esto permite crear tablas o datos repetitivos sin hardcodear macros dentro del core.
