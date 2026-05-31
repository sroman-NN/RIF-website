# Packer I: Configuración Principal

El bloque `packer:` es la sección responsable de informarle al compilador dónde buscar, bajo qué nombre, y con qué extensiones esperar el archivo de código fuente del proyecto.

```rif
packer:
    entryfilename "main"
    ext ".gbasm"
    filesystem 0
```

## Propiedades Fundamentales

### `entryfilename`
Especifica el nombre base del archivo principal del programa que el compilador debe ubicar. Por defecto, si esta instrucción se omite, RIF buscará el nombre `main`.

### `ext`
Obligatorio. Define la extensión del archivo fuente (por ejemplo, `".gbasm"`). Si el desarrollador olvida proporcionar la extensión, RIF podría fallar al intentar leer un archivo sin ninguna terminación de formato en el directorio.

### `filesystem`
Por defecto suele ser `0`, lo que le indica a RIF que toda la lógica de programación vive en un **solo archivo** ininterrumpido (por ejemplo: `main.gbasm`). Si se asigna el valor `1`, habilita el motor fragmentador para buscar archivos separados lógicamente por secciones.
