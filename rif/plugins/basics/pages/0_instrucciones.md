# 📚 Catálogo Completo de Instrucciones - Plugin Basics

El plugin `basics` proporciona todas las directivas fundamentales para construir reglas de emisión en RIF. Cada instrucción es un componente reutilizable que se comunica con el compilador a través de la **Core API**.

---

## 🔍 Índice de Instrucciones

### Control de Compilación
- [`need`](#need) - Captura y valida operandos
- [`emit`](#emit) - Serializa fragmentos de bits
- [`call`](#call) - Reutiliza sub-reglas
- [`error` / `raise`](#error--raise) - Genera errores controlados

### Operaciones con Bits
- [`bitcat`](#bitcat) - Concatena fragmentos de bits
- [`bitsize`](#bitsize) - Obtiene el tamaño en bits
- [`bitfit`](#bitfit) - Valida si un valor cabe en N bits
- [`trunc`](#trunc) - Trunca un valor a N bits
- [`zext`](#zext) - Extensión cero (sin signo)
- [`sext`](#sext) - Extensión de signo

### Comparaciones y Validaciones
- [`eq` / `neq`](#eq--neq) - Igualdad y desigualdad
- [`lt`, `lte`, `gt`, `gte`](#comparadores-lt-lte-gt-gte) - Comparaciones numéricas
- [`fits`](#fits) - Valida si un valor cabe en un rango
- [`exists`](#exists) - Verifica si existe una etiqueta

### Memoria y Direcciones
- [`reloc`](#reloc) - Relocación de dirección absoluta
- [`reldis`](#reldis) - Distancia relativa al PC
- [`emitaddress`](#emitaddress) - Emite dirección de etiqueta
- [`fillid` / `vfillid`](#fillid--vfillid) - Resuelve IDs de fillables

### Alineación y Layout
- [`align`](#align) - Alinea a límite N bytes
- [`pad`](#pad) - Rellena con bytes específicos

---

## 📖 Documentación Detallada

### `need`

**Propósito:** Captura operandos desde la línea de código y los valida según tipos permitidos.

**Sintaxis:**
```rif
need <tipos...> <operador>
```

**Tipos Soportados:**
- `VALUE` - Valores numéricos (literales)
- `LABEL` - Etiquetas de código
- `SYMBOL` - Símbolos y constantes
- `REG` - Registros (si están definidos en `.regs`)
- `SREG` - Sub-registros especializados
- `TYPE` - Tipos de dato complejos
- `STACK`, `HEAP`, `MEMORY` - Regiones especiales

**Ejemplo:**
```rif
.rules
rule mov_reg:
    need REG, REG mov_target, mov_source
    emit 0001 mov_target.bits mov_source.bits
```

**Comportamiento:**
- Almacena el operador en un contexto disponible para otras instrucciones
- Valida que los operandos coincidan con los tipos declarados
- Genera error si los tipos no concuerdan o faltan operandos
- Múltiples tipos se escriben separados por comas

**Errores Comunes:**
```rif
need REG, REG  ; ❌ Falta operador al final
need REG invalid_name, ax  ; ❌ No identifica el nombre del operador
need VALUE, REG, VALUE result  ; ❌ Operador debe ir al final
```

**API Interna:**
- Llama a `Line.Unpack(",")` para separar componentes
- `Operator.Save(target, RuleIndicator.current, valid_types)` almacena la ligadura
- Retorna `Expr(["need", valids, target])`

---

### `emit`

**Propósito:** Serializa fragmentos de bits (estáticos o dinámicos) al stream binario de salida.

**Sintaxis:**
```rif
emit [modo] <fragmento1>, <fragmento2>, ...
```

**Modos Disponibles:**
- `bits` (default) - Emisión de bits individuales sin restricción
- `cbits` - Complementa automáticamente a byte (rellena con ceros si falta)
- `cbit` - Valida que sea exactamente 8 bits
- `cmbit` - Valida exactamente 4 bits
- `ccbit` - Valida exactamente 16 bits
- `cdbit` - Valida exactamente 32 bits
- `cebit` - Valida exactamente 64 bits

**Tipos de Fragmentos:**
- `01001010` - Bits literales en binario
- `operador.field` - Placeholder que se resuelve en compilación
- `variable_bits` - Referencia a variables de bits definidas

**Ejemplos:**
```rif
emit 11010101                    ; Emite 8 bits literales
emit cbits 1101, var_bits       ; Complementa a byte
emit bits operador.value        ; Emite placeholder
emit cbit 11111111              ; Asegura exacto 1 byte
```

**Comportamiento:**
- Valida que los bits sean válidos (`0` o `1`)
- Resuelve placeholders automáticamente en build-time
- Detecta campos faltantes en las tablas del pack
- Compacta bytes estáticos para optimización
- Permite múltiples fragmentos separados por comas

**Errores Comunes:**
```rif
emit 1010 1011 1100 1101  ; ❌ 16 bits sin modo compactado
emit operador.nonexistent ; ❌ Campo no existe
emit                      ; ❌ Fragmentos vacíos
```

**API Interna:**
- `_parse_chunk()` analiza cada fragmento
- `EmitChunk` estructura que representa cada componente
- Retorna `Expr(["emit_bits_exact", instruction])`

---

### `call`

**Propósito:** Reutiliza sub-reglas del compilador sin duplicar código.

**Sintaxis:**
```rif
call <nombre_regla>
```

**Ejemplo:**
```rif
.rules
rule helper:
    need VALUE value
    emit 1111 value.bits

rule main:
    need VALUE x
    call helper
```

**Comportamiento:**
- Busca la regla con el nombre exacto en el pack
- Ejecuta la sub-regla en el contexto actual
- Los operadores capturados en `main` se heredan a `helper`
- Las emisiones de `helper` se insertan inline en `main`
- Permite anidación de llamadas

**Errores Comunes:**
```rif
call unknown_rule        ; ❌ Regla no existe
call rule1 rule2         ; ❌ Solo acepta una regla
call                     ; ❌ Regla faltante
```

---

### `error` / `raise`

**Propósito:** Genera errores controlados durante la compilación.

**Sintaxis:**
```rif
error "Mensaje de error"
raise "Mensaje de error"
```

**Ejemplo:**
```rif
rule validate:
    need VALUE val
    fits val, 0, 255
    error "Valor fuera de rango"
```

**Comportamiento:**
- Detiene inmediatamente la compilación con un mensaje legible
- Útil para validaciones condicionales
- Aparece en el output de compilación
- El mensaje se propaga al usuario

**Diferencia:**
- `error` y `raise` se usan indistintamente
- Ambos generan un `PackError`

---

### `bitcat`

**Propósito:** Concatena múltiples fragmentos de bits en una secuencia única.

**Sintaxis:**
```rif
bitcat <fragmento1>, <fragmento2>, ..., <destino>
```

**Ejemplo:**
```rif
need REG r1, REG r2
bitcat r1.value, r2.value, result
emit cbits result.bits
```

**Comportamiento:**
- Ordena los fragmentos en el orden especificado (izquierda a derecha)
- Almacena el resultado concatenado en el operador destino
- Preserva la anchura de bits de cada componente
- El resultado es accesible para emisiones posteriores

---

### `bitsize`

**Propósito:** Obtiene la cantidad de bits de un valor.

**Sintaxis:**
```rif
bitsize <valor>, <destino>
```

**Ejemplo:**
```rif
need VALUE imm
bitsize imm, size
fits size, 1, 32
```

**Comportamiento:**
- Calcula los bits necesarios para representar el valor
- Almacena el resultado numérico en el operador destino
- Devuelve el mínimo de bits requeridos (sin padding)

---

### `bitfit`

**Propósito:** Valida si un fragmento de bits cabe exactamente en N bits.

**Sintaxis:**
```rif
bitfit <fragmento>, <n_bits>
```

**Ejemplo:**
```rif
need REG reg
bitfit reg.value, 4
emit reg.value  ; Solo si cabe en 4 bits
```

**Comportamiento:**
- Verifica que el fragmento tenga exactamente N bits
- Genera error si no coincide
- Complementario a `trunc` (validación vs. truncamiento)

---

### `trunc`

**Propósito:** Trunca un valor a N bits (descarta bits de orden superior).

**Sintaxis:**
```rif
trunc <valor>, <n_bits>, <destino>
```

**Ejemplo:**
```rif
need VALUE val
trunc val, 16, truncated
emit cbits truncated.bits
```

**Comportamiento:**
- Mantiene solo los primeros N bits
- Descarta el resto silenciosamente
- Almacena el resultado en el operador destino
- Perderá información si N es muy pequeño

---

### `zext`

**Propósito:** Extiende un valor con ceros (extensión sin signo) hasta M bits.

**Sintaxis:**
```rif
zext <valor>, <m_bits>, <destino>
```

**Ejemplo:**
```rif
need VALUE val
zext val, 32, extended
emit cdbit extended.bits
```

**Comportamiento:**
- Agrega ceros a la izquierda hasta alcanzar M bits
- Mantiene el valor numérico idéntico
- Útil para conversiones entre tipos sin signo
- Almacena en el operador destino

---

### `sext`

**Propósito:** Extiende un valor con signo hasta M bits.

**Sintaxis:**
```rif
sext <valor>, <m_bits>, <destino>
```

**Ejemplo:**
```rif
need VALUE val
sext val, 32, extended
```

**Comportamiento:**
- Detecta el bit de signo (MSB) del valor original
- Replica ese bit para llenar los bits faltantes
- Preserva el valor con signo en la representación extendida
- Crítico para operaciones con números negativos

---

### `eq` / `neq`

**Propósito:** Valida igualdad o desigualdad entre dos valores.

**Sintaxis:**
```rif
eq <valor1>, <valor2>
neq <valor1>, <valor2>
```

**Ejemplo:**
```rif
need REG r1, REG r2
eq r1, r2  ; Genera error si son diferentes
```

**Comportamiento:**
- `eq` genera error si los valores son diferentes
- `neq` genera error si los valores son iguales
- Se usan típicamente para validaciones

---

### Comparadores (`lt`, `lte`, `gt`, `gte`)

**Propósito:** Valida rangos numéricos.

**Sintaxis:**
```rif
lt <valor>, <límite>       ; valor < límite
lte <valor>, <límite>      ; valor <= límite
gt <valor>, <límite>       ; valor > límite
gte <valor>, <límite>      ; valor >= límite
```

**Ejemplo:**
```rif
need VALUE imm
gte imm, -128
lte imm, 127
emit cbits imm.bits
```

**Comportamiento:**
- Genera error si la condición falla
- Útil para validar rangos de operandos
- Soporta números negativos

---

### `fits`

**Propósito:** Valida si un valor cabe completamente en N bits (sin pérdida).

**Sintaxis:**
```rif
fits <valor>, <n_bits>
```

**Ejemplo:**
```rif
need VALUE imm
fits imm, 8
emit cbits imm.bits
```

**Comportamiento:**
- Verifica que el valor se represente en N bits sin desbordamiento
- Genera error si no cabe
- Trabajo complementario a `trunc` (validación vs. truncamiento)

---

### `exists`

**Propósito:** Verifica si una etiqueta está definida en el programa.

**Sintaxis:**
```rif
exists <etiqueta>
```

**Ejemplo:**
```rif
need LABEL lbl
exists lbl
reloc lbl, current_offset
```

**Comportamiento:**
- Busca la etiqueta en la tabla de símbolos del programa
- Genera error si no existe
- Comunica al linker que la etiqueta es requerida

---

### `reloc`

**Propósito:** Emite una dirección absoluta que será resuelta por el linker.

**Sintaxis:**
```rif
reloc <etiqueta>, <offset_actual>
```

**Ejemplo:**
```rif
need LABEL target
reloc target, 0x8000
```

**Comportamiento:**
- Genera un registro de relocación
- El linker resuelve la dirección final en la fase de enlace
- Se usa para referencias a símbolos externos o diferidos
- Inserta bytes placeholder en la imagen actual

---

### `reldis`

**Propósito:** Calcula la distancia relativa al PC (Program Counter).

**Sintaxis:**
```rif
reldis <etiqueta>, <destino>
```

**Ejemplo:**
```rif
need LABEL target
reldis target, offset
emit cbits offset.bits  ; Emite como branching offset
```

**Comportamiento:**
- Computa `target_address - current_pc`
- Almacena el desplazamiento en el operador destino
- Útil para instrucciones de salto relativo

---

### `emitaddress`

**Propósito:** Emite la dirección de una etiqueta.

**Sintaxis:**
```rif
emitaddress <etiqueta>
```

**Ejemplo:**
```rif
need LABEL start
emitaddress start  ; Emite los bytes de la dirección
```

**Comportamiento:**
- Resuelve la dirección de la etiqueta
- Emite los bytes correspondientes (tamaño depende de arquitectura)

---

### `fillid` / `vfillid`

**Propósito:** Resuelve IDs de objetos fillables (datos generados por plugins).

**Sintaxis:**
```rif
fillid <nombre>, <destino>
vfillid <nombre>, <destino>
```

**Ejemplo:**
```rif
fillid image_data, id
emit ccbit id.bits  ; Emite el ID del fillable
```

**Comportamiento:**
- Busca el fillable en `fills.json`
- `fillid` obtiene el ID numérico
- `vfillid` obtiene información adicional del fillable
- Los IDs se asignan durante la fase de build

---

### `align`

**Propósito:** Alinea la posición actual a un límite de N bytes.

**Sintaxis:**
```rif
align <n_bytes>
```

**Ejemplo:**
```rif
emit_code_section
align 4  ; Asegura alineación a 4 bytes
emit 11110000
```

**Comportamiento:**
- Si la posición actual no está alineada, inserta padding
- Completa hasta el siguiente múltiplo de N bytes
- Usa bytes `0x00` por defecto para rellenar

---

### `pad`

**Propósito:** Inserta exactamente N bytes de relleno.

**Sintaxis:**
```rif
pad <n_bytes>
```

**Ejemplo:**
```rif
emit_header
pad 16  ; Reserva 16 bytes
```

**Comportamiento:**
- Inserta bytes de relleno sin comprometer la estructura
- No modifica la posición lógica
- Útil para reservar espacio en ROMs

---

## 🔧 Patrones Comunes

### Patrón 1: Captura y Emisión Básica
```rif
rule op_add:
    need REG dest, REG src
    emit 00 dest.bits src.bits
```

### Patrón 2: Validación Condicional
```rif
rule imm_load:
    need REG dest, VALUE imm
    fits imm, 16
    emit 0001 dest.bits, imm.bits
```

### Patrón 3: Concatenación de Bits
```rif
rule multi_field:
    need REG r1, REG r2, VALUE flags
    bitcat r1.bits, r2.bits, flags.value, combined
    emit ccbit combined.bits
```

### Patrón 4: Rutinas Reutilizables
```rif
rule prologue:
    need VALUE stack_size
    emit ... ; código de prólogo

rule main_routine:
    need VALUE sz
    call prologue
    need VALUE body_size
    emit ... ; código del cuerpo
```

### Patrón 5: Direccionamiento Relativo
```rif
rule branch_forward:
    need LABEL target
    reldis target, distance
    fits distance, 12
    emit 111 distance.bits
```

---

## 🐛 Debugging y Tips

### Habilitar Logs Detallados
```bash
python -m rif compile pack.json instruction --verbose
```

### Verificar Tabla de Símbolos
```bash
python -m rif parse pack.json
```

### Análisis de Emisión
Usa `--debug` para ver cómo se procesan los placeholders:
```bash
python -m rif build proyecto --debug
```

---

## 📚 Referencia Rápida

| Instrucción | Entrada | Salida | Efecto |
|-------------|---------|--------|--------|
| `need` | Línea de tokens | Operador guardado | Captura |
| `emit` | Fragmentos | Bytes al stream | Serialización |
| `call` | Nombre de regla | Ejecución inline | Reutilización |
| `bitcat` | Múltiples fragmentos | Concatenación | Composición |
| `reloc` | Etiqueta | Registro al linker | Defer |
| `align` | N bytes | Padding | Alineación |
| `fits` | Valor, bits | Error o OK | Validación |
| `zext`/`sext` | Valor, bits | Extensión | Conversión |
| `reldis` | Etiqueta | Offset relativo | PC-rel |

---

## 🔗 Véase También

- [Estructura Interna del Plugin](estructura.md)
- [Mecanismos de Importación](importar.md)
- [Integración VS Code (VSIX)](1_vsix.md)
