# Packer II y Errores

El empaquetador tiene otras declaraciones avanzadas, destinadas a la configuración de salida o de validación de sintaxis estricta de las secciones.

## Declarando el Entorno (`definesec`)

El compilador de RIF es altamente estricto. Por defecto, si el compilador está ejecutando tu código fuente y encuentra una llamada a un salto de sección (por ejemplo, escribir `.rom` como sección para el código), el sistema levantará un error que se ve así:

`[ CODE ] sección de fuente desconocida ".rom" en línea 1`

Esto ocurre porque RIF no tiene conocimiento nativo de cuáles son las secciones legales para tu ISA. Para prevenir esto, se deben usar variables `definesec`:

```rif
packer:
    definesec .rom
    definesec .data
```

> **Nota:** Al usar `linker: filesystem 1` con secciones declaradas explícitamente (`sectneed`, `sectopt`), RIF autorregistra las secciones, haciéndolas "conocidas" y anulando automáticamente este error sin necesidad de usar `definesec`.

## Salida y Compilados

Opcionalmente el empaquetador puede encargarse de definir el nombre explícito del archivo de volcado final, y su extensión para evitar choques con el código de entrada:

- `outext ".bin"`: La extensión final bajo la cual RIF escribirá los binarios por defecto.
- `output "juego.bin"`: Fuerza el guardado de la memoria hacia un nombre específico al compilar.
