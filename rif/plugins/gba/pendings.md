# Pendings GBA ARM7TDMI

## Thumb

- `bkpt` no aplica a ARM7TDMI clasico de GBA y queda fuera salvo que se cree un modo ARMv5T.

## ARM

- Falta resolver pseudo-instrucciones ARM/Thumb que elijan automaticamente entre literal pool, `mov_imm`, `ldr_pc` o secuencias de varias instrucciones.
- Falta completar `msr` para CPSR/SPSR y validar campos de control/flags.
- Falta modelar coprocessor placeholders como unsupported explicito.

## GBA

- Falta una capa de macros de hardware para MMIO comun: video modes, DMA, IRQ, timers, input y audio.
- Falta validar alineacion por region de memoria en loads/stores segun ancho y destino.
- Falta soporte de secciones/literal pools para datos constantes cercanos al codigo Thumb.

## Resuelto

- Listas de registros con llaves en Thumb mediante `push_list`, `pop_list`, `ldmia_list` y `stmia_list`.
- Literales por etiqueta en Thumb mediante `ldr_pc_label` y `adr_label`.
- Set ARM base de 32 bits: branch, branch-link, BX, data processing sin shift, load/store inmediato, halfword/signed transfer, block transfer, multiply, MLA, SWI y MRS.
- ARM data processing con operand2 shift inmediato o por registro mediante `arm_dp_shift` y `arm_dp_shift_reg`.
- ARM multiply long mediante `arm_umull`, `arm_umlal`, `arm_smull` y `arm_smlal`.
- `FILLID` y `VFILLID` pueden resolver fills ya escritos en `fills.json` o fills creados en la misma expansion.
