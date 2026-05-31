# Usar el Pack Propio

Para que RIF tome tu archivo `.pack` y reaccione a la configuración, debes colocarlo en la raíz de la carpeta de tu proyecto. 

## Estructura Recomendada

Una arquitectura de proyecto normal de RIF se ve así:

```text
mi_proyecto/
├── mi_proyecto.pack
└── code/
    └── main.gbasm
```

También es válido omitir la carpeta `code/` y poner todo al mismo nivel, aunque para proyectos grandes recomendamos tener los archivos fuente dentro de la carpeta `code`.

```text
mi_proyecto/
├── mi_proyecto.pack
└── main.gbasm
```

## Reconocimiento Automático

Al ejecutar el comando de compilación:
```bash
python -m rif.cli build mi_proyecto
```
El compilador RIF escaneará automáticamente el directorio raíz `mi_proyecto/` buscando cualquier archivo que termine en `.pack`. **Este archivo se convertirá en la configuración local absoluta** del compilador para dicho proyecto, dictando qué archivos leer y qué plugins usar.
