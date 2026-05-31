# Conjunto de Instrucciones Thumb (GBA)

La consola GBA corre una CPU **ARM7TDMI** nativa. El framework de RIF compila sus instrucciones utilizando el modo **Thumb** (Instrucciones de 16-bits alineadas en formato *Little-Endian*), cumpliendo estrictamente con el manual de referencia técnica ARM (DDI 0029G).

> [!IMPORTANT]  
> En el estado Thumb de 16-bits, casi todas las instrucciones están limitadas a operar exclusivamente sobre los **registros bajos (R0-R7)** para ahorrar espacio en la codificación binaria.

---

## 🧮 Transferencia de Datos

Estas instrucciones permiten mover información entre los registros o cargar constantes.

| Instrucción RIF | Equivalencia ARM | Descripción |
| :--- | :--- | :--- |
| `store Rd = imm` | `MOV Rd, #imm8` | Carga un número inmediato (0-255) en un registro. |
| `move Rd, Rs` | `ADD Rd, Rs, #0` | Copia el contenido del registro origen `Rs` al destino `Rd`. |
| `lsl Rd, Rs, imm` | `LSL Rd, Rs, #imm5` | **L**ogical **S**hift **L**eft (Multiplica por 2^n). |
| `lsr Rd, Rs, imm` | `LSR Rd, Rs, #imm5` | **L**ogical **S**hift **R**ight (Divide sin signo). |
| `asr Rd, Rs, imm` | `ASR Rd, Rs, #imm5` | **A**rithmetic **S**hift **R**ight (Mantiene el signo). |

## ⚔️ Aritmética y Lógica

A diferencia de ARM, las instrucciones aritméticas de Thumb actualizan automáticamente las banderas (Flags) de condición en el registro CPSR (Condition Program Status Register).

| Instrucción RIF | Equivalencia ARM | Descripción |
| :--- | :--- | :--- |
| `add Rd, Rs, Rn` | `ADD Rd, Rs, Rn` | Suma aritmética (`Rd = Rs + Rn`). |
| `sub Rd, Rs, Rn` | `SUB Rd, Rs, Rn` | Resta aritmética (`Rd = Rs - Rn`). |
| `and Rd, Rs` | `AND Rd, Rs` | Y lógico bit a bit (`Rd &= Rs`). |
| `or Rd, Rs` | `ORR Rd, Rs` | O lógico bit a bit (`Rd \|= Rs`). |
| `xor Rd, Rs` | `EOR Rd, Rs` | O exclusivo lógico bit a bit (`Rd ^= Rs`). |
| `not Rd, Rs` | `MVN Rd, Rs` | Niega los bits (`Rd = ~Rs`). |
| `neg Rd, Rs` | `NEG Rd, Rs` | Niega el signo (Complemento a 2) (`Rd = 0 - Rs`). |
| `mul Rd, Rs` | `MUL Rd, Rs` | Multiplicación (`Rd *= Rs`). |
| `cmp Rd, Rs` | `CMP Rd, Rs` | Compara restando, actualizando flags pero sin guardar el resultado. |

## 💾 Acceso a Memoria (Load / Store)

El hardware de GBA requiere usar Load y Store para escribir en VRAM o leer el cartucho. La dirección efectiva de memoria siempre se calcula sumando el registro Base (`Rb`) y un registro de Desplazamiento (`Ro`).

| Instrucción RIF | Equivalencia ARM | Descripción |
| :--- | :--- | :--- |
| `ldr Rd, Rb, Ro` | `LDR Rd, [Rb, Ro]` | Lee **32-bits** de memoria (Word). |
| `ldrb Rd, Rb, Ro` | `LDRB Rd, [Rb, Ro]` | Lee **8-bits** sin signo (Byte). |
| `ldrh Rd, Rb, Ro` | `LDRH Rd, [Rb, Ro]` | Lee **16-bits** sin signo (Halfword). |
| `str Rd, Rb, Ro` | `STR Rd, [Rb, Ro]` | Escribe **32-bits** en memoria. |
| `strb Rd, Rb, Ro` | `STRB Rd, [Rb, Ro]` | Escribe **8-bits** en memoria. |
| `strh Rd, Rb, Ro` | `STRH Rd, [Rb, Ro]` | Escribe **16-bits** en memoria. |

> [!WARNING]  
> La VRAM del GBA (donde se dibujan los píxeles) **no** soporta escrituras de 8-bits (`strb`). Si intentas escribir un solo byte en la RAM de video, el hardware lo reflejará escribiendo el byte duplicado en los 16-bits de la dirección. Usa siempre `strh` para colores.

## 🔀 Control de Flujo (Saltos)

Las directivas de control de flujo son resueltas internamente por el motor de RIF. Él calculará automáticamente si el salto es hacia atrás o hacia adelante y generará los saltos relativos de 16-bits correctos.

| Instrucción RIF | Equivalencia ARM | Comportamiento |
| :--- | :--- | :--- |
| `jump label` | `B label` | Salto incondicional hacia `label`. |
| `call label` | `BL label` | Salta y guarda la dirección de retorno en el Link Register (`LR`). |
| `beq label` | `BEQ label` | Salta si es **igual** (Flag `Z=1`). |
| `bne label` | `BNE label` | Salta si es **diferente** (Flag `Z=0`). |
| `blt label` | `BLT label` | Salta si es **menor que** (Flags `N!=V`). |
| `bgt label` | `BGT label` | Salta si es **mayor que** (Flags `Z=0` y `N=V`). |
| `ble label` | `BLE label` | Salta si es **menor o igual** (Flags `Z=1` o `N!=V`). |
| `bge label` | `BGE label` | Salta si es **mayor o igual** (Flags `N=V`). |

## 🥞 Stack (Pila)

| Instrucción RIF | Equivalencia ARM | Descripción |
| :--- | :--- | :--- |
| `push Rd` | `PUSH {Rd}` | Empuja un registro a la pila de RAM (decrementa `SP`). |
| `pop Rd` | `POP {Rd}` | Extrae un registro de la pila hacia `Rd` (incrementa `SP`). |

## 📝 Declaración Directa de Datos

Si necesitas escribir bytes crudos intercalados en medio de tus rutinas (por ejemplo, para colores BGR555 o datos puros):

```rif
db 0xFF              ; Declara 1 Byte (8 bits)
dh 0x1234            ; Declara 1 Halfword (16 bits)
dw 0x12345678        ; Declara 1 Word (32 bits)

; También puedes usar las directivas externas de fuentes:
bitmap_text "RIF"    ; Emite bits del array de fuente de la consola
```
