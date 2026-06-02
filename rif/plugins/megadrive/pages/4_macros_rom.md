# Macros Estructurales de ROM (Mega Drive)

A diferencia de Game Boy Advance, donde se necesita un bloque de 192 bytes fijos y saltos opcodes incrustados en un logo, la Mega Drive tiene una tabla inicial de interrupciones definida por Motorola, seguida de una cabecera de 256 bytes donde se especifican los metadatos de hardware.

El plugin `megadrive` de RIF no usa directivas de un solo arroba `@` tradicionales (fillables abstractos), sino **instrucciones/macros directas** en tu ensamblador que se auto-generan.

## 🧱 Secuencia Funcional Mínima

Para que una ROM de Sega arranque, la estructura de tu archivo principal obligatoriamente debe ser:

```rif
.section .rom
    md_vectors start_label   ; Vector Table [0x000-0x0FF]
    md_header                ; Sega Header  [0x100-0x1FF]

start_label:                 ; Entrada del programa [0x200+]
    ; (Inicializar VDP, Z80 y limpiar RAM)
    
game_loop:
    bra game_loop

    md_rompad                ; Padding al final del código
```

## 🛠️ Detalles de las Macros

### `md_vectors <label>`
Construye automáticamente la Tabla de Vectores de Excepción del procesador M68k en la dirección `0x00000000`.
- Establece el **Puntero de Pila Inicial** estricto de Sega (`0x00FF0000`).
- Establece el vector de Reset para que apunte hacia el `label` que especifiques en el parámetro.
- Añade relleno en los vectores no capturados o no implementados y ocupa el espacio correcto desde `0x00000000` hasta `0x000000FF` (256 bytes).

### `md_header`
Inyecta 256 bytes (`0x100` a `0x1FF`) conteniendo la estructura obligatoria de Sega Mega Drive.
- Imprime `SEGA MEGA DRIVE`.
- Genera el Checksum binario oficial (`0x8B7D` interno del header, o validable).
- Informa a la consola sobre los periféricos soportados y punteros finales de RAM externa.

### `md_rompad`
Debe colocarse siempre como la **última instrucción de tu código principal**.
Las ROMs de Mega Drive generalmente deben tener tamaños exactos o múltiplos en potencia de 2 (`128 KB`, `256 KB`, `512 KB`...).
Esta macro detectará dinámicamente en tiempo de ensamblaje (build-time) cuántos bytes de código has escrito, y rellenará el resto con bytes en blanco (ceros en hardware original de SEGA en RIF usa NULL pad) hasta el siguiente salto lógico oficial, para que los emuladores o cartuchos flashcarts no reporten tamaños corruptos.
