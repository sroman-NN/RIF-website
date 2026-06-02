# Instrucciones 6502 / 6507

El pack `atari2600` cubre las instrucciones documentadas del MOS 6502 que usa el
6507. La nomenclatura del pack separa el mnemonico y el modo de direccionamiento
para que RIF pueda validar tamanos y relocaciones de manera directa.

## Registros de CPU

| Registro | Tamano | Uso |
|---|---:|---|
| `A` | 8 bits | Acumulador. Operaciones aritmeticas, logicas y transferencias principales. |
| `X` | 8 bits | Indice, contador, offset zero-page y ayuda para limpiar RAM. |
| `Y` | 8 bits | Indice alterno, contador y offset en modos indexados. |
| `SP` | 8 bits | Puntero de stack. El stack vive logicamente en pagina `0x0100`. |

## Modos de direccionamiento en el pack

| Sufijo | Ejemplo | Significado |
|---|---|---|
| `_imm` | `lda_imm 0x02` | Inmediato de 8 bits. |
| `_zp` | `sta_zp 0x80` | Direccion zero-page de 8 bits. |
| `_zpx` | `lda_zpx 0x80` | Zero-page indexado por `X`. |
| `_zpy` | `ldx_zpy 0x80` | Zero-page indexado por `Y`. |
| `_abs` | `jmp_abs loop` | Etiqueta con relocacion absoluta de 16 bits. |
| `_abs_addr` | `sta_abs_addr VSYNC` | Direccion/simbolo absoluto de 16 bits. |
| `_absx` | `lda_absx table` | Etiqueta absoluta indexada por `X`. |
| `_absy` | `lda_absy table` | Etiqueta absoluta indexada por `Y`. |
| `_indx` | `lda_indx ptr` | Indirecto indexado: `(zp,X)`. |
| `_indy` | `lda_indy ptr` | Indirecto indexado: `(zp),Y`. |
| `_rel` | `bne_rel loop` | Branch relativo. Alias de las formas `bne`, `beq`, etc. |

## Carga, store y transferencia

| Familia | Reglas comunes | Uso |
|---|---|---|
| Load | `lda_*`, `ldx_*`, `ldy_*` | Cargar `A`, `X` o `Y` desde inmediato, RAM, ROM o MMIO. |
| Store | `sta_*`, `stx_*`, `sty_*` | Escribir registros a RAM o registros TIA/RIOT. |
| Transfer | `tax`, `tay`, `tsx`, `txa`, `txs`, `tya` | Copiar entre registros internos. |

Ejemplo:

```rif
    lda_imm 0x02
    sta_abs_addr VSYNC
    lda_imm 0x00
    sta_abs_addr COLUBK
```

## Aritmetica y comparacion

| Familia | Reglas | Notas |
|---|---|---|
| Suma | `adc_*` | Suma con carry. Limpia o prepara `C` con `clc`/`sec`. |
| Resta | `sbc_*` | Resta con borrow invertido del 6502. |
| Comparacion | `cmp_*`, `cpx_*`, `cpy_*` | Actualiza flags sin modificar registros. |
| Inc/Dec | `inc_*`, `dec_*`, `inx`, `iny`, `dex`, `dey` | Muy usado para loops por scanline. |

## Logica y shifts

| Familia | Reglas | Uso |
|---|---|---|
| AND | `and_*` | Enmascarar bits de entradas o flags. |
| OR | `ora_*` | Componer valores para TIA. |
| XOR | `eor_*` | Alternar bits, patrones o colores. |
| BIT | `bit_zp`, `bit_abs`, `bit_abs_addr` | Probar bits contra `A`. |
| Shifts | `asl_*`, `lsr_*`, `rol_*`, `ror_*` | Mover bits y preparar graficos. |

`asl`, `lsr`, `rol` y `ror` sin sufijo operan sobre `A`; las formas `_zp`,
`_zpx`, `_abs` y `_absx` operan sobre memoria.

## Control de flujo

| Regla | Condicion |
|---|---|
| `bcc` | Carry clear. |
| `bcs` | Carry set. |
| `beq` | Zero set. |
| `bne` | Zero clear. |
| `bmi` | Negative set. |
| `bpl` | Negative clear. |
| `bvc` | Overflow clear. |
| `bvs` | Overflow set. |
| `jmp_abs` | Salto absoluto. |
| `jsr_abs` | Subrutina. |
| `rts` | Retorno de subrutina. |
| `rti` | Retorno de interrupcion. |

Los branches usan desplazamientos relativos de 8 bits. Si el destino queda muy
lejos, usa `jmp_abs` o reestructura el loop.

## Stack y estado

| Regla | Uso |
|---|---|
| `pha`, `pla` | Guardar/restaurar acumulador. |
| `php`, `plp` | Guardar/restaurar flags. |
| `sei`, `cli` | Deshabilitar/habilitar interrupciones maskables. |
| `cld`, `sed` | Modo decimal desactivado/activado. En 2600 normalmente se usa `cld`. |
| `clc`, `sec` | Carry clear/set para `adc` y `sbc`. |
| `clv` | Limpia overflow. |

## Helpers propios del pack

| Helper | Sintaxis | Funcion |
|---|---|---|
| `rompad_to_vectors` | `rompad_to_vectors` | Rellena hasta el offset fisico `0x0FFA`. |
| `vectors` | `vectors start` | Emite NMI, RESET e IRQ/BRK hacia la etiqueta dada. |
