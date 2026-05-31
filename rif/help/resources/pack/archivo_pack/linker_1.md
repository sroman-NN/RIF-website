# Linker I: Archivos Fracturados

El bloque `linker:` te otorga un control granular sobre cómo el ensamblador agrupa e ingiere el código fuente distribuido en una jerarquía de archivos.

```rif
linker:
    filesystem 1 
    sectexec .rom 
    sectneed .header 
    sectneed .data 
    sectopt  .bss  
```

## Modo Fracturado (`filesystem 1`)

Cuando `filesystem` se declara en `1`, RIF deja de buscar un único archivo y comienza a buscar un ensamblado "fracturado" o esparcido a lo largo de varios documentos según las secciones estipuladas. Esto permite una programación más organizada (por ejemplo, separar el código de lectura de datos de la lógica del ROM principal).

### Regla de Construcción de Nombres

Las diferentes secciones exigen una nomenclatura de archivo **estricta** basada en lo configurado en la cabecera `packer:`.

La sintaxis del nombre de archivo a buscar por el compilador para cada sección fragmentada es: `{entryfilename}{seccion}{ext}`.
- Ejemplo para `.data`: `main.data.gbasm`
- Ejemplo para `.header`: `main.header.gbasm`

### Punto de Entrada Ejecutable (`sectexec`)
Declara la sección maestra ejecutable. Para esta sección, la regla de nombre se acorta y será el archivo base: `{entryfilename}{ext}`. 
- Ejemplo: `main.gbasm`. 
- Si un usuario compila el código, la directiva `.section` (en este caso `.rom`) será inyectada automáticamente y validada.

### Secciones Requeridas y Opcionales
- `sectneed`: Indica que RIF **debe obligatoriamente** encontrar y compilar un archivo para dicha sección (siguiendo la regla de nombre). Si el archivo no se encuentra, la compilación se abortará.
- `sectopt`: Informa al vinculador que busque un archivo con dicha sección, pero de no encontrarlo, omitirá el proceso y seguirá adelante de forma segura sin lanzar errores.

### Inyección de Contexto
Anotar una sección de fractura inyecta implícitamente un cambio a esa sección de la memoria en RIF. Es decir, tú como desarrollador ya no necesitas escribir la declaración `.seccion_x` al inicio del archivo fracturado; el propio Linker de RIF sabe a qué sección de la memoria pertenece ese código simplemente por su nombre de archivo, mitigando la duplicación en el código base.
