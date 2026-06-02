# Linker

El linker construye bloques de salida desde `.sections`, resultados compilados, datos, memoria y headers.

Soporta:

- secciones con orden, permisos, alineacion y relleno
- secciones `nobits`
- headers declarativos
- placeholders
- relocaciones
- regiones `stack` y `heap`
- expresiones `link:*`
- fillables `@args@namefunc@namelabel` definidos por plugins

El linker no debe saber reglas de una arquitectura. Solo organiza bytes, offsets y referencias.

El codigo fuente se lee con el `reader` definido en `.pack`, no con reglas fijas del core.

Cuando `build` recibe una carpeta, el linker busca el `.pack`, carga los archivos definidos por `reader.sources` y escribe la salida usando `packer.output` o `packer.ext`.

Una linea fillable usa siempre esta forma:

```rif
@args@namefunc@namelabel
```

- `args` son los argumentos del fillable. Se parsean como shell, asi que puedes usar comillas: `@"assets/title.png" 128 false@image_bitmap@title_bitmap`.
- `namefunc` es la funcion declarada por el plugin, sin el prefijo interno `fill_` cuando exista alias.
- `namelabel` es el nombre exacto que se registra en `fills.json` y el simbolo que podras usar despues en el codigo.

El texto retornado por el fillable se pega en la fuente antes de compilar, por lo que labels y relocaciones posteriores usan offsets actualizados. Al final del link, `fills.json` queda resuelto con `virtual`/`addrs` y `physical`/`paddrs` cuando el dato fue emitido en una seccion enlazada.

Ejemplos:

```rif
@"Hola"@fonts_fill_5x7x1@hello_text
@"assets/title.png" 128 false@image_bitmap@title_bitmap
@bgm_sample 8192@gba_dsound_start@bgm_sample_player
```

Los helpers `fillid` y `vfillid` pueden leer esos datos de `fills.json`: `fillid` devuelve la direccion fisica y `vfillid` la direccion virtual.
