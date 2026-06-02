# Conjunto de Instrucciones M68k (Mega Drive)

El framework RIF compila sus instrucciones utilizando el formato **Big-Endian** de la arquitectura **Motorola 68000**. El plugin incluye en su `megadrive.rules.pack` las instrucciones comunes necesarias para crear ROMs funcionales.

> [!NOTE]  
> A diferencia de la sintaxis estándar de Motorola (que usa `.b`, `.w`, `.l` como sufijos de punto), en RIF los tamaños suelen ser parte del propio mnemónico base usando guiones bajos (ej. `move_w` en lugar de `move.w`) para respetar la sintaxis estandarizada de RIF de no tener símbolos de puntuación en los identificadores de regla.

---

## 🧮 Transferencia de Datos

Estas instrucciones permiten mover información.

| Instrucción RIF | Equivalencia M68k | Descripción |
| :--- | :--- | :--- |
| `move_b_imm_d imm, Dn` | `MOVE.B #imm, Dn` | Mueve un byte inmediato a un registro de Datos. |
| `move_w_imm_d imm, Dn` | `MOVE.W #imm, Dn` | Mueve una palabra a un registro de Datos. |
| `move_l_imm_d imm, Dn` | `MOVE.L #imm, Dn` | Mueve un largo a un registro de Datos. |
| `move_w_d_d Dn, Dm`    | `MOVE.W Dn, Dm`   | Copia una palabra entre registros de Datos. |
| `move_w_d_mem Dn, addr`| `MOVE.W Dn, (abs).l`| Guarda registro de Datos a una dirección absoluta de RAM o VDP. |
| `move_w_mem_d addr, Dn`| `MOVE.W (abs).l, Dn`| Lee desde RAM/VDP hacia el registro de Datos. |
| `move_w_d_a Dn, An`    | `MOVE.W Dn, An`   | Mueve a registro de Direcciones. |
| `moveq imm, Dn`        | `MOVEQ #imm, Dn`  | Mueve rápido un número (-128 a 127) de 8 bits extendido a 32 bits a un registro. |

## ⚔️ Aritmética

| Instrucción RIF | Equivalencia M68k | Descripción |
| :--- | :--- | :--- |
| `add_w_imm_d imm, Dn`  | `ADD.W #imm, Dn`  | Suma aritmética. |
| `sub_w_imm_d imm, Dn`  | `SUB.W #imm, Dn`  | Resta aritmética. |
| `mulu_w_d_d Dn, Dm`    | `MULU.W Dn, Dm`   | Multiplicación sin signo (16x16 -> 32). |
| `divu_w_d_d Dn, Dm`    | `DIVU.W Dn, Dm`   | División sin signo. |
| `addq_w imm, Dn`       | `ADDQ.W #imm, Dn` | Suma rápida (1 a 8). |
| `neg_w Dn`             | `NEG.W Dn`        | Complemento a 2. |

## 🔀 Operadores Lógicos y Shifts

| Instrucción RIF | Equivalencia M68k | Descripción |
| :--- | :--- | :--- |
| `and_w_imm_d imm, Dn`  | `ANDI.W #imm, Dn` | Y lógico bit a bit con inmediato. |
| `or_w_imm_d imm, Dn`   | `ORI.W #imm, Dn`  | O lógico bit a bit con inmediato. |
| `eori_w imm, Dn`       | `EORI.W #imm, Dn` | O exclusivo lógico (XOR). |
| `lsl_w imm, Dn`        | `LSL.W #imm, Dn`  | Desplazamiento Lógico a la Izquierda. |
| `lsr_w imm, Dn`        | `LSR.W #imm, Dn`  | Desplazamiento Lógico a la Derecha. |

## 🕹️ Control de Flujo (Saltos)

| Instrucción RIF | Equivalencia M68k | Comportamiento |
| :--- | :--- | :--- |
| `bra label` | `BRA label` | Salto incondicional relativo corto. |
| `jmp label` | `JMP label` | Salto incondicional largo/absoluto. |
| `bsr label` | `BSR label` | Llama a subrutina (guarda retorno en stack). |
| `rts`       | `RTS`       | Retorno desde subrutina. |
| `beq label` | `BEQ label` | Salta si es **igual** (Flag `Z=1`). |
| `bne label` | `BNE label` | Salta si es **diferente** (Flag `Z=0`). |
| `cmp_w_imm_d imm, Dn`| `CMP.W #imm, Dn` | Compara inmediato contra un registro. |

## 🥞 Stack (Pila)

La Mega Drive no tiene instrucciones `PUSH`/`POP` directas nombradas así en la CPU; usa direccionamiento indirecto con predecremento y postincremento (`-(SP)` y `(SP)+`), pero el plugin expone:

| Instrucción RIF | Equivalencia M68k | Descripción |
| :--- | :--- | :--- |
| `move_l_d_sp_minus Dn` | `MOVE.L Dn, -(SP)`| Empuja `Dn` al Stack de sistema. |
| `move_l_sp_plus_d Dn`  | `MOVE.L (SP)+, Dn`| Extrae desde el Stack hacia `Dn`. |

## 📝 Declaración Cruda

Para emitir datos BCD (Binary Coded Decimal), colores, o tiles:

```rif
db 0xFF              ; Declara 1 Byte (8 bits)
dh 0x1234            ; Declara 1 Palabra (16 bits) - Orden Big-Endian
dw 0x12345678        ; Declara 1 Largo (32 bits) - Orden Big-Endian
```
