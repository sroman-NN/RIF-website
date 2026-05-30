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
- fillables `@nombre` definidos por plugins

El linker no debe saber reglas de una arquitectura. Solo organiza bytes, offsets y referencias.

El codigo fuente se lee con el `reader` definido en `.pack`, no con reglas fijas del core.

Cuando `build` recibe una carpeta, el linker busca el `.pack`, carga los archivos definidos por `reader.sources` y escribe la salida usando `packer.output` o `packer.ext`.

Una linea `@fill_algo` se resuelve buscando una funcion `fill_algo` en los plugins declarados. El texto retornado se pega en la fuente antes de compilar, por lo que labels y relocaciones posteriores usan offsets actualizados.
