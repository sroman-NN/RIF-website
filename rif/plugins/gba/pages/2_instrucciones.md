# Instrucciones ARM y Thumb

El pack GBA contiene reglas Thumb de 16 bits y reglas ARM de 32 bits. Thumb es
compacto y muy practico para ROM; ARM ofrece mas registros, inmediatos y
operaciones para rutinas generadas.

## Thumb: registros y limites

Muchas instrucciones Thumb simples solo aceptan registros bajos `R0-R7`.
`SP`, `LR` y `PC` son especiales. `R8-R12` existen, pero solo algunas formas
high-register pueden tocarlos directamente.

## Datos y constantes

| Regla | Equivalente | Uso |
|---|---|---|
| `store Rd = imm` | `MOVS Rd, #imm8` | Carga inmediato de 8 bits en registro bajo. |
| `movs Rd imm` | `MOVS Rd, #imm8` | Forma canonica Thumb. |
| `move Rd Rs` / `mov Rd Rs` | high register move | Copia registros, incluyendo formas altas si aplica. |
| `ldr_pc_label Rd label` | literal PC-relative | Carga datos cercanos a PC. |
| `adr_label Rd label` | ADR | Calcula direccion cercana a PC. |

## ALU Thumb

| Regla | Operacion |
|---|---|
| `adds Rd Rs Rn` / `add Rd Rs Rn` | `Rd = Rs + Rn`. |
| `subs Rd Rs Rn` / `sub Rd Rs Rn` | `Rd = Rs - Rn`. |
| `add_imm Rd imm` | Suma inmediato de 8 bits. |
| `sub_imm Rd imm` | Resta inmediato de 8 bits. |
| `cmp Rd Rs` | Compara registros. |
| `cmp_imm Rd imm` | Compara con inmediato. |
| `and`, `orr`, `eor`, `bic`, `mvn` | Logica bit a bit. |
| `lsl`, `lsr`, `asr`, `ror` | Shifts y rotaciones. |
| `mul` | Multiplicacion de registros bajos. |

## Load / Store Thumb

| Regla | Acceso |
|---|---|
| `ldr Rd Rb Ro` / `str Rd Rb Ro` | Word de 32 bits con offset de registro. |
| `ldrh Rd Rb Ro` / `strh Rd Rb Ro` | Halfword de 16 bits. |
| `ldrb Rd Rb Ro` / `strb Rd Rb Ro` | Byte de 8 bits. |
| `ldr_imm`, `str_imm` | Word con offset inmediato. |
| `ldrh_imm`, `strh_imm` | Halfword con offset inmediato. |
| `ldr_sp`, `str_sp` | Acceso relativo a `SP`. |

No uses `strb` en VRAM, OAM o Palette RAM. Esas memorias estan conectadas a un
bus de 16 bits y el hardware duplica el byte, corrompiendo pixeles o atributos.

## Control de flujo Thumb

| Regla | Condicion |
|---|---|
| `b` / `jump` | Salto incondicional. |
| `beq`, `bne` | Igual / diferente. |
| `bcs`, `bcc` | Carry set / clear. |
| `bmi`, `bpl` | Negativo / positivo. |
| `bvs`, `bvc` | Overflow set / clear. |
| `bhi`, `bls`, `bge`, `blt`, `bgt`, `ble` | Comparaciones ordenadas. |
| `call` / `bl` | Branch with link. |
| `bx` | Branch and exchange. |
| `swi` / `svc` | Llamada BIOS/software interrupt. |

## Stack Thumb

```rif
push {R0-R3,LR}
pop {R0-R3,PC}
```

Tambien existen formas de mascara (`push_mask`, `pop_mask`) para codigo
generado.

## ARM helpers

Las reglas ARM se usan en el ejemplo oficial y en fillables generados:

| Regla | Uso |
|---|---|
| `arm_mov_imm Rd imm` | Carga inmediato ARM. |
| `arm_add_imm Rd Rn imm` | Suma inmediato. |
| `arm_ldr_label Rd label` | Carga direccion de etiqueta via relocacion/literal. |
| `arm_ldrh Rd Rb off` / `arm_strh Rd Rb off` | Acceso halfword a MMIO/VRAM. |
| `arm_b label`, `arm_bcond cond label` | Saltos ARM. |
| `arm_bl label`, `arm_bx Rn` | Subrutinas y retorno/intercambio de estado. |
| `apply_reloc abs label bits` | Emite relocacion directa para datos puntero. |

## Datos crudos

```rif
db 0x12
dh 0x1234
dw 0x12345678
```
