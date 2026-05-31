# Crear un Pack

Los archivos `.pack` son el corazón de la configuración de tu proyecto en RIF (Retargetable ISA Foundry). Actúan como el "manifiesto" de compilación que indica al ensamblador cómo interpretar el código fuente, qué reglas aplicar, qué plugins importar y cómo estructurar el empaquetado final.

## Estructura Básica

Un archivo `.pack` es un archivo de texto simple (con extensión `.pack`). Utiliza un lenguaje de configuración propietario, limpio y fácil de leer.

```rif
comment ;
blocks :
table-separator |
encoding utf-8

.pack

packer:
    entryfilename "main"
    ext ".gbasm"
```

## Secciones Principales
- **Cabecera global**: Configura la sintaxis general del propio lector (ej. cómo son los comentarios o bloques).
- **.pack**: El punto de entrada principal para cargar definiciones globales.
- **packer:**: Configura la recolección, nombre del archivo de origen y comportamiento de lectura.
- **linker:**: (Opcional) Configura el ensamblado de código fragmentado en diferentes archivos según sus secciones.

Para que RIF funcione, tu proyecto debe tener o heredar al menos una configuración de Pack válida.
