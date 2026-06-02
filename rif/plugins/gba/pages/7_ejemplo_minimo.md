# Ejemplo Minimo

Este ejemplo configura Mode 3, pinta la pantalla de rojo y entra en un bucle
infinito. Usa reglas ARM porque permiten cargar direcciones MMIO grandes de
forma directa dentro del pack actual.

```rif
.header
    set_headers
    set_logo
    set_checksum "RIF GBA"
    set_entry

.rom
main:
    ; DISPCNT = 0x0403 (Mode 3 | BG2 enable)
    arm_mov_imm R0, 0x04000000
    arm_mov_imm R1, 0x0400
    arm_add_imm R1, R1, 0x03
    arm_strh R1, R0, 0

    ; R2 = VRAM start
    ; R3 = VRAM end for 240 * 160 pixels * 2 bytes
    arm_mov_imm R2, 0x06000000
    arm_mov_imm R3, 0x06000000
    arm_add_imm R3, R3, 0x12C00

    ; BGR555 red = 0x001F
    arm_mov_imm R4, 0x001F

fill_loop:
    arm_strh R4, R2, 0
    arm_add_imm R2, R2, 2
    arm_cmp R2, R3
    arm_bcond ne, fill_loop

forever:
    arm_b forever

.rodata
    rompad
```

## Compilar

```bash
python -m rif build my_game --plugin gba --name example
```

Si guardas el archivo en una carpeta de proyecto llamada `my_game`, la salida
normal sera `my_game/my_game.gba`.

## Ejecutar

```bash
python -m rif -pcli gba run my_game/my_game.gba -nd
```

## Variante Thumb

Para codigo Thumb, usa `set_entry_thumb` y construye direcciones grandes con
composicion de shifts o labels/literal pools. El pack expone `store`, `movs`,
`adds`, `strh`, `b`, `beq`, `bne`, `push`, `pop` y mas reglas Thumb para ese
flujo.
