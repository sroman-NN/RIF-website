# Comando Table (CLI)

El comando `rif table` (o `rif -table`) permite modificar y formatear programáticamente las tablas `.pack` de RIF directamente desde la terminal. Esto es útil para automatizar la adición de instrucciones, registros, campos y formatear el código de tabla.

## Comandos Principales

- `rif table modify`: Modifica filas, columnas, tablas o valores.
- `rif table format`: Alinea y formatea las columnas de una tabla para que se lean correctamente.
- `rif table undo`: Deshace la última modificación de tabla.
- `rif table redo`: Rehace la modificación previamente deshecha.

> **Nota:** Todos los comandos de modificación y formateo crean automáticamente un archivo de copia de seguridad (`.bak`) de forma predeterminada.

## Especificando el Archivo o Pack

Puedes indicar el archivo o pack objetivo utilizando las siguientes opciones:

- `--from <archivo|carpeta>`: Ruta al archivo `.pack` o carpeta que los contiene.
- `-p <plugin> -use <pack>`: Modifica un pack alojado dentro de un plugin instalado.
- `--file <nombre>`: Cuando `--from` o `-p` apunta a una carpeta, especifica qué archivo modificar.
- `--section <seccion>`: Apunta a una sección específica (por ejemplo, `.regs` o `.data`).

> **Ejemplo:** `rif table modify --from my_pack/ --file cpu.pack "regs add column bits 32"`

## Operaciones de Modificación (`modify`)

El argumento final de `modify` es un string con la operación a ejecutar con la forma `"TABLA comando argumentos"`.

### Filas (Rows)
- **Añadir fila:** `add row <celda1> <celda2> ...`
  *(Ej: `"regs add row ax 000 16"`)*
- **Eliminar fila(s):** `del row <nombre1> <nombre2> ...`
- **Renombrar fila:** `rename row <viejo> <nuevo>`
- **Copiar fila:** `copy row <origen> <nuevo>`
- **Mover fila:** `move row <nombre> before|after|to <destino>`

### Columnas (Columns)
- **Añadir columna:** `add column <nombre> [valor_por_defecto]`
  *(Ej: `"regs add column type INT"`)*
- **Eliminar columna(s):** `del column <nombre1> <nombre2> ...`
- **Renombrar columna:** `rename column <viejo> <nuevo>`
- **Asignar valor a toda la columna:** `set column <columna> <valor1> <valor2> ...`
- **Mover columna:** `move column <nombre> before|after|to <destino>`

### Celdas (Cells)
- **Establecer valor:** `set <fila> <columna> <valor>`
  *(Ej: `"regs set ax bits 32"`)*
- **Operación rápida:** `<columna> <fila> <valor>`
  *(Ej: `"regs bits ax 32"`)*
- **Alternar valor booleano:** Usa `switch` como valor en celdas de tipo yes/no.
  *(Ej: `"rules set add hidden switch"`)*
- **Limpiar celda:** `clear <fila> <columna>`

### Tablas y Secciones
- **Eliminar tabla:** `del table`
- **Añadir sección/separador:** `addsect <texto>`

## Opciones Adicionales

- `--dry-run`: Simula los cambios y muestra las diferencias sin escribir el archivo.
- `--no-backup`: Evita crear el archivo `.bak` de seguridad.
- `--case-sensitive`: Las coincidencias en nombres de tablas, filas y columnas distinguen entre mayúsculas y minúsculas.
- `--table <nombre>`: Para `rif table format`, restringe el formateo a una tabla específica.
