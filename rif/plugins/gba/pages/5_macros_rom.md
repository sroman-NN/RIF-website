# Macros Estructurales de ROM (GBA)

Para que el hardware real de Game Boy Advance (o un emulador estricto) inicie un cartucho, los primeros 192 bytes de la memoria flash (`.rom` desde la dirección `0x08000000`) deben contener una cabecera extremadamente precisa.

El plugin `gba` proporciona macros que resuelven todas las exigencias binarias automáticamente.

## 🧱 Secuencia Funcional Mínima

El orden de los siguientes componentes es fundamental. RIF emitirá bloques binarios del tamaño exacto en el orden en que pongas estas macros:

```rif
.section .rom
set_headers        ; [0x00-0x03] Salto de la BIOS a tu código
set_logo           ; [0x04-0x9F] Logo nativo de Nintendo (Comprimido)
set_checksum       ; [0xA0-0xBF] Título, Códigos y Checksums cruzados
set_entry_thumb    ; [0xC0-...]  Punto de entrada ARM -> Salta a Thumb
```

> [!CAUTION]  
> Si omites la macro `set_logo`, la BIOS del GBA asumirá que el cartucho es pirata y se negará a bootear.
> De igual forma, si alteras `set_checksum`, el cálculo matemático que valida los bytes del título fallará y la consola bloqueará la ejecución con una pantalla en blanco.

## 🛠️ Detalles de las Macros

### `set_headers`
Crea el vector de salto original en ARM (32 bits). Generalmente emite `B 0x080000C0`, instruyendo a la BIOS que el código del juego comienza justo después del bloque de la cabecera.

### `set_logo`
Inyecta 156 bytes exactos equivalentes al logo vectorizado de Nintendo. La BIOS lee y compara estos bits a mano.

### `set_checksum`
Inyecta metadatos del juego (Game Title, Maker Code, Version) y calcula un checksum complementario (Complemento a 2 negado) del header completo. RIF calcula esto automáticamente por ti.

### `set_entry_thumb`
Al finalizar el booteo, la consola está en modo ARM nativo. Esta macro inyecta el estado (Stubs) y ejecuta un `BX` (Branch and Exchange) para forzar a la CPU a cambiar al modo **Thumb** (16-bits). Después de esta línea, todo el código que escribas debajo será código Thumb real validado por RIF.

### `set_rompad`
Si un cartucho se construye muy corto (por ejemplo, 137 KB), los emuladores podrían tener problemas de paginación o alineación de caché. Esta macro se debe colocar al final de tu documento `.gbasm` y rellenará inteligentemente con `0xFF` el archivo hasta alcanzar los bloques oficiales (alineados a potencias de 2 KB, 32 KB, etc.) calculando en caliente cuánto código ya ha sido emitido.
