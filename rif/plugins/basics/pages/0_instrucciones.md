# 📖 Catálogo de Instrucciones - RIF Basics

Este catálogo detalla el funcionamiento de cada directiva provista por el plugin `basics`. Aprenderás qué hace, cómo se escribe en el archivo `.pack`, qué parámetros recibe y exactamente cómo se comunica con el compilador de RIF.

---

## 1. Directivas de Flujo y Captura

### 📋 `need`
Captura y valida operandos del código fuente de acuerdo a tipos definidos.
*   **Sintaxis en `.rules`:** `need <TIPO_1> [<TIPO_2> ...], <operador>`
*   **Parámetros:**
    *   `<TIPO>`: Tipos primitivos (`VALUE`, `SYMBOL`, `LABEL`, `STACK`, `HEAP`, `MEMORY`) o definidos en `.types` (ej: `REG`, `u8`).
    *   `<operador>`: Nombre de la variable donde se guardará el operando capturado.
*   **Comunicación con el Compilador:**
    *   El plugin consume tokens de la línea de ensamblado activa mediante `Line.Advance()`.
    *   Llama a `Operator.Save(target, RuleIndicator.current, valid_types)` para almacenar la ligadura (binding) del operando en el contexto del compilador.
    *   Retorna `Expr(["need", valids, target])`.
*   **Ejemplo:**
    ```rif
    ldx:
        need VALUE, imm
        need REG, rd
    ```

### 📤 `emit`
Serializa flujos de bits estáticos o dinámicos hacia la imagen física del binario.
*   **Sintaxis en `.rules`:** `emit [<ancho>] <bits_o_placeholder>`
*   **Parámetros:**
    *   `<ancho>`: Opcional. Fija la cantidad de bits a emitir (`cbit` = 8, `ccbit` = 16, `cdbit` = 32, `cebit` = 64).
    *   `<bits_o_placeholder>`: Cadena de `0` y `1` (ej. `10101001`), variable definida en `.vars`, o placeholder dinámico referenciado a un operador previo (ej. `rd.binary` o `imm.binary`).
*   **Comunicación con el Compilador:**
    *   Valida la existencia del operando consultando `Operator.Binding()`.
    *   Retorna `Expr(["emit_bits_exact", EmitInstruction])`, lo que añade un fragmento de bits (`EmitChunk`) a la secuencia física que el compilador empaquetará al final de la línea.
*   **Ejemplo:**
    ```rif
    lda:
        need VALUE, imm
        emit 10101001    ; Opcode de LDA (8 bits)
        emit imm.binary  ; Emite los bits del inmediato capturado
    ```

### 📞 `call`
Invoca y ejecuta una sub-regla o sub-rutina de compilación declarada.
*   **Sintaxis en `.rules`:** `call <nombre_regla>`
*   **Parámetros:**
    *   `<nombre_regla>`: El identificador de otra regla definida en la tabla `.rules`.
*   **Comunicación con el Compilador:**
    *   Llama al despachador interno del compilador para procesar de forma recursiva e inyectar las expresiones generadas por la regla destino.
    *   Retorna `Expr(["call", target])`.
*   **Ejemplo:**
    ```rif
    mi_regla_compleja:
        call otra_subregla
    ```

---

## 2. Operadores de Alineación y Layout

### 📏 `align`
Alinea el desplazamiento físico actual del bloque binario a un límite especificado.
*   **Sintaxis en `.rules`:** `align <limite_bytes> [<patron_relleno>]`
*   **Parámetros:**
    *   `<limite_bytes>`: Expresión o valor entero de potencia de 2 (ej: `4`, `16`).
    *   `<patron_relleno>`: Opcional. Bytes hexadecimales con los que se rellenará el hueco (por defecto `00`).
*   **Comunicación con el Compilador:**
    *   Retorna `Expr(["align", bytes, fill])`. El compilador calcula la diferencia hasta el siguiente múltiplo de `limite_bytes` en su offset de compilación actual e inserta los bytes de relleno correspondientes.
*   **Ejemplo:**
    ```rif
    ; Alinea a palabra de 32 bits (4 bytes) usando ceros
    align 4
    ```

### ⚓ `pad`
Rellena el búfer de datos actual con un patrón hasta alcanzar una dirección u offset físico absoluto.
*   **Sintaxis en `.rules`:** `pad <offset_destino> [<patron_relleno>]`
*   **Parámetros:**
    *   `<offset_destino>`: Dirección física de destino (entero u offset).
    *   `<patron_relleno>`: Opcional. Patrón hexadecimal para rellenar el espacio.
*   **Comunicación con el Compilador:**
    *   Retorna `Expr(["pad", offset, fill])`. El compilador rellena la diferencia entre el tamaño acumulado del bloque y el `offset_destino`.
*   **Ejemplo:**
    ```rif
    ; Rellena la ROM de Atari hasta el inicio de los vectores (byte 4090) con ceros
    pad 4090 00
    ```

---

## 3. Manipulación y Conversión de Bits

### 🔗 `bitcat`
Concatena múltiples cadenas o referencias binarias en una sola variable lógica de bits.
*   **Sintaxis en `.rules`:** `bitcat <destino>, <origen_1>, <origen_2> [, ...]`
*   **Comunicación con el Compilador:**
    *   Une los fragmentos lógicos de bits y los almacena bajo una nueva variable temporal en `Operators.program.vars` o actualiza el binding en el contexto local.
*   **Ejemplo:**
    ```rif
    bitcat mi_resultado, R0.binary, 00001111
    ```

### ✂️ `trunc`
Trunca una secuencia binaria a un ancho de bits fijo, descartando los bits sobrantes de la izquierda.
*   **Sintaxis en `.rules`:** `trunc <destino>, <origen>, <ancho_bits>`
*   **Ejemplo:** `trunc imm_recortado, imm.binary, 8`

### ➕ `zext` y `sext`
Realizan extensión de cero (`zext`) o de signo (`sext`) sobre una cadena de bits hasta alcanzar un ancho objetivo.
*   **Sintaxis en `.rules`:** `zext <destino>, <origen>, <ancho_bits>` / `sext <destino>, <origen>, <ancho_bits>`
*   **Parámetros:**
    *   `<destino>`: Nombre de la variable resultante.
    *   `<origen>`: Cadena de bits original (ej. `imm.binary`).
    *   `<ancho_bits>`: Tamaño final deseado (ej. `16` o `32`).
*   **Comunicación con el Compilador:**
    *   `zext` rellena con ceros (`0`) a la izquierda.
    *   `sext` rellena con el bit de mayor peso del origen (bit de signo) a la izquierda.
    *   Almacenan el resultado en las variables locales del compilador (`Line.vars`).
*   **Ejemplo:**
    ```rif
    ; Convierte un inmediato de 8 bits a 16 bits preservando el signo para saltos
    sext imm16, offset8.binary, 16
    ```

### 🔍 `fits`, `bitfit` y `bitsize`
Validan rangos y anchos de bits.
*   **`fits <valor>, <ancho_bits>`**: Evalúa si un operando numérico cabe en una representación de `<ancho_bits>` con/sin signo. Si no cabe, arroja un error en tiempo de compilación.
*   **`bitfit <bits>, <ancho_esperado>`**: Lanza un error si la cadena de bits no mide exactamente `<ancho_esperado>`.
*   **`bitsize <destino>, <origen>`**: Cuenta la longitud de la cadena de bits y guarda el entero en la variable destino.

---

## 4. Relocación y Direcciones de Memoria

### 🔗 `reloc`
Inyecta una dirección absoluta de un símbolo y registra una relocación en la tabla del linker.
*   **Sintaxis en `.rules`:** `reloc <tipo_reloc>, <destino_label>, <ancho_bits>`
*   **Parámetros:**
    *   `<tipo_reloc>`: `abs` / `absolute` (dirección virtual absoluta) o `physical` (dirección física en disco/archivo).
    *   `<destino_label>`: El operando de tipo etiqueta (`LABEL` o `SYMBOL`) al que apunta.
    *   `<ancho_bits>`: Ancho físico del puntero en bits (típicamente `16` o `32`).
*   **Comunicación con el Compilador:**
    *   Genera un objeto `Relocation` que se anexa a la lista global `bin_linker.relocations`.
    *   Deja un espacio vacío (de ceros) en la posición física actual que mide `<ancho_bits> // 8` bytes. Durante la fase de linkeo, una vez que el linker conoce las direcciones virtuales y físicas de todas las secciones, calcula el valor real y lo escribe encima de ese espacio vacío.
*   **Ejemplo:**
    ```rif
    mario_sprite_ptr:
        reloc abs, mario_sprite, 32  ; Escribe la dirección de 32 bits en el link final
    ```

### 📍 `reldis`
Calcula y escribe un desplazamiento (offset) relativo al PC de ejecución para saltos o direccionamiento relativo.
*   **Sintaxis en `.rules`:** `reldis <origen_offset>, <destino_label>, <ancho_bits>`
*   **Parámetros:**
    *   `<origen_offset>`: Generalmente `.` (que indica la posición de la instrucción actual).
    *   `<destino_label>`: Etiqueta destino del salto.
    *   `<ancho_bits>`: Tamaño en bits del campo del salto (ej. `8` para branches cortos o `12` para Thumb).
*   **Comunicación con el Compilador:**
    *   Crea una relocación del tipo `reldis` que se procesará en tiempo de enlace.
    *   El linker calculará la diferencia: `Dirección(destino) - (Dirección(origen) + offset_siguiente_instrucción)` y lo sobrescribirá en caliente con el signo adecuado.
*   **Ejemplo:**
    ```rif
    bne:
        need LABEL, target
        emit 11010000         ; Opcode de BNE
        reldis ., target, 8   ; Calcula el offset de salto relativo de 8 bits
    ```

### 🏷️ `emitaddress` (Alias: `emitadress`)
Emite la dirección física directa de un símbolo si ya está resuelta.
*   **Sintaxis:** `emitaddress <simbolo>, <ancho_bits>`
*   **Ejemplo:** `emitaddress mi_variable, 32`

### 📂 `fillid` y `vfillid`
Consultan de forma dinámica y no hardcodeada las direcciones físicas (`fillid`) o virtuales (`vfillid`) de estructuras registradas en el archivo `fills.json`.
*   **Sintaxis:** `fillid <id_estructura>` / `vfillid <id_estructura>`
*   **Parámetros:**
    *   `<id_estructura>`: El ID (ej: `"gba_header"`) registrado en `fills.json`.
*   **Comunicación con el Compilador:**
    *   Lee el archivo `fills.json` del proyecto activo.
    *   Recupera el campo `paddrs` (físico) o `addrs` (virtual) de la estructura y emite su valor como un entero de 32 bits alineado.
*   **Ejemplo:**
    ```rif
    set_entry:
        ; Emite la dirección virtual del header registrada de forma filleable
        vfillid gba_header
    ```

---

## 5. Aseveraciones y Control de Errores

### ⚖️ Operadores de Comparación (`eq`, `neq`, `lt`, `lte`, `gt`, `gte`)
Validan condiciones lógicas en tiempo de compilación. Si la condición no se cumple, abortan la compilación y muestran el error.
*   **Sintaxis:** `<operador_logico> <expresion_1>, <expresion_2> [, "mensaje_error"]`
*   **Ejemplo:**
    ```rif
    ; Asegura que el inmediato no sea mayor que 255
    lte imm, 255, "El valor inmediato supera el límite de 8 bits"
    ```

### 🛑 `error` y `raise`
Lanzan una excepción de compilación (`PackError`) inmediatamente con el mensaje especificado.
*   **Sintaxis:** `error "mensaje"` / `raise "mensaje"`
*   **Ejemplo:**
    ```rif
    error "La instrucción seleccionada no es compatible con el modo actual"
    ```
