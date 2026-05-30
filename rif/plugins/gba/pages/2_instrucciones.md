# Instrucciones Thumb

El pack GBA compila instrucciones Thumb de 16 bits en little endian,
según el manual ARM7TDMI-S (DDI 0029G).

## Transferencia de datos

| Instrucción         | ARM equiv.       | Descripción                      |
|---------------------|------------------|----------------------------------|
| `store Rd = imm`    | MOV Rd, #imm8    | Carga inmediato 8-bit en Rd      |
| `move Rd, Rs`       | ADD Rd, Rs, #0   | Copia Rs → Rd                    |
| `lsl Rd, Rs, imm`   | LSL Rd, Rs, #imm5| Desplazamiento lógico izquierda  |
| `lsr Rd, Rs, imm`   | LSR Rd, Rs, #imm5| Desplazamiento lógico derecha    |
| `asr Rd, Rs, imm`   | ASR Rd, Rs, #imm5| Desplazamiento aritmético derecha|

Solo R0-R7 son accesibles en Thumb (registros bajos de 3 bits).

## Aritmética y lógica

| Instrucción    | ARM equiv.   | Descripción                    |
|----------------|--------------|--------------------------------|
| `add Rd, Rs, Rn` | ADD Rd, Rs, Rn | Rd = Rs + Rn                |
| `sub Rd, Rs, Rn` | SUB Rd, Rs, Rn | Rd = Rs - Rn                |
| `and Rd, Rs`   | AND Rd, Rs   | Rd &= Rs                       |
| `or  Rd, Rs`   | ORR Rd, Rs   | Rd \|= Rs                      |
| `xor Rd, Rs`   | EOR Rd, Rs   | Rd ^= Rs                       |
| `not Rd, Rs`   | MVN Rd, Rs   | Rd = ~Rs                       |
| `neg Rd, Rs`   | NEG Rd, Rs   | Rd = 0 - Rs                    |
| `mul Rd, Rs`   | MUL Rd, Rs   | Rd *= Rs                       |
| `cmp Rd, Rs`   | CMP Rd, Rs   | Rd - Rs (solo actualiza flags) |

## Acceso a memoria

| Instrucción          | ARM equiv.           | Descripción                |
|----------------------|----------------------|----------------------------|
| `ldr  Rd, Rb, Ro`   | LDR  Rd, [Rb, Ro]   | Carga 32 bits              |
| `ldrb Rd, Rb, Ro`   | LDRB Rd, [Rb, Ro]   | Carga 8 bits (sin signo)   |
| `ldrh Rd, Rb, Ro`   | LDRH Rd, [Rb, Ro]   | Carga 16 bits (sin signo)  |
| `str  Rd, Rb, Ro`   | STR  Rd, [Rb, Ro]   | Guarda 32 bits             |
| `strb Rd, Rb, Ro`   | STRB Rd, [Rb, Ro]   | Guarda 8 bits              |
| `strh Rd, Rb, Ro`   | STRH Rd, [Rb, Ro]   | Guarda 16 bits             |

`Rb` = base, `Ro` = offset register. Dirección efectiva = `Rb + Ro`.

## Control de flujo

| Instrucción   | ARM equiv. | Descripción                         |
|---------------|------------|-------------------------------------|
| `jump label`  | B label    | Salto incondicional (±1 KB)         |
| `call label`  | BL label   | Salto con retorno (guarda PC en LR) |
| `beq label`   | BEQ label  | Salta si Z=1 (igual)                |
| `bne label`   | BNE label  | Salta si Z=0 (distinto)             |
| `blt label`   | BLT label  | Salta si N≠V (menor)                |
| `bgt label`   | BGT label  | Salta si Z=0 y N=V (mayor)          |
| `ble label`   | BLE label  | Salta si Z=1 o N≠V (menor/igual)    |
| `bge label`   | BGE label  | Salta si N=V (mayor/igual)          |

## Stack

| Instrucción | ARM equiv.   | Descripción                           |
|-------------|--------------|---------------------------------------|
| `push Rd`   | PUSH {Rd}    | Guarda registro en stack (SP -= 4)    |
| `pop  Rd`   | POP  {Rd}    | Recupera registro del stack (SP += 4) |

## Datos directos

```rif
db 0xFF          ; emite un byte
dh 0x1234        ; emite un halfword (2 bytes, LE)
dw 0x12345678    ; emite un word (4 bytes, LE)
bitmap_text "HELLO"  ; emite bytes del bitmap 5x7
```

## Ejemplo completo

```rif
.rom
store R0 = 0x80    ; R0 = 0x80
store R1 = 0x03    ; R1 = 0x03 → R0:R1 = DISPCNT address base
lsl   R2, R0, 3   ; R2 = R0 << 3
add   R3, R0, R1  ; R3 = R0 + R1
cmp   R3, R2      ; compara
bne   loop_end    ; salta si distinto

loop_end:
    jump loop_end ; loop infinito
```
