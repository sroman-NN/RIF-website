# ROM Minima Comentada

Este ejemplo muestra una ROM NTSC minima: inicializa CPU, limpia RAM, genera
VSYNC, espera VBlank con el timer RIOT, consume 192 lineas visibles y hace
overscan. No dibuja sprites, pero produce una cadencia estable para empezar a
agregar kernel.

```rif
.section rom
start:
    sei
    cld
    txs

    lda_imm 0x00
    tax
    tay

clear_loop:
    sta_zpx 0 X
    inx
    bne clear_loop

    lda_imm 0x40
    sta_abs_addr COLUBK

main_loop:
    lda_imm 0x02
    sta_abs_addr VSYNC
    sta_abs_addr WSYNC
    sta_abs_addr WSYNC
    sta_abs_addr WSYNC
    lda_imm 0x00
    sta_abs_addr VSYNC

    lda_imm 43
    sta_abs_addr TIM64T
wait_vblank:
    lda_abs_addr INTIM
    bne wait_vblank

    lda_imm 0x00
    sta_abs_addr VBLANK

    ldx_imm 192
draw_loop:
    sta_abs_addr WSYNC
    dex
    bne draw_loop

    lda_imm 0x02
    sta_abs_addr VBLANK

    lda_imm 35
    sta_abs_addr TIM64T
wait_overscan:
    lda_abs_addr INTIM
    bne wait_overscan

    jmp_abs main_loop

    rompad_to_vectors
    vectors start
```

## Linea por linea

`sei`, `cld`, `txs` dejan la CPU en un estado predecible. `cld` es importante
porque el modo decimal del 6502 no aporta nada al kernel y puede sorprender en
operaciones `adc`/`sbc`.

El loop `clear_loop` usa `X` como contador de 8 bits. Al desbordar vuelve a cero
y `bne` termina. En hardware real hay espejos, por lo que este patron es comun
para limpiar RAM y registros bajos durante el arranque, aunque un juego final
puede limpiar zonas mas selectivas.

`COLUBK` define el color de fondo. Cambiar este registro dentro del kernel es
una de las formas mas baratas de crear bandas horizontales de color.

La fase `VSYNC` escribe `0x02`, espera tres lineas con `WSYNC` y vuelve a cero.

`TIM64T` se usa para esperar un bloque de VBlank u overscan. Mientras `INTIM` no
sea cero, el loop espera.

`VBLANK = 0` habilita la salida visible. El loop de 192 lineas solo hace
`WSYNC`; un juego real reemplaza o rodea esa espera con escrituras temporizadas a
TIA.

Al final, `rompad_to_vectors` y `vectors start` cierran la ROM para que el reset
del 6507 encuentre el punto de entrada correcto en `0xFFFC`.
