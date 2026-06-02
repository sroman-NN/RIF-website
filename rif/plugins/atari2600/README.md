# Plugin: Atari 2600

Plugin oficial de RIF para ensamblar ROMs basicas de Atari 2600 / VCS con
MOS 6507, TIA y RIOT 6532. El objetivo del pack es producir binarios de 4 KiB
listos para Stella, con el mapa de memoria de cartucho en `0xF000`, registros
de hardware declarados y helpers para colocar los vectores finales del 6502.

## Inicio rapido

```bash
python -m rif build examples/atari2600 --plugin atari2600 --name example
python -m rif -pcli atari2600 install Stella --add-path
python -m rif -pcli atari2600 run examples/atari2600/atari2600.bin
```

## Que incluye

- Reglas para instrucciones documentadas del MOS 6502 compatibles con el 6507:
  cargas, stores, aritmetica, logica, shifts, branches, stack, saltos,
  subrutinas y banderas.
- Registros de TIA para video, audio, colisiones, entradas de paddle y boton.
- Registros de RIOT para joysticks, switches de consola, DDRs, RAM reflejada y
  temporizadores `TIM1T`, `TIM8T`, `TIM64T` y `TIM1024T`.
- Secciones `.rom`, `.ram` y `.zp` con offsets virtuales de Atari 2600.
- Macros `rompad_to_vectors` y `vectors label` para cerrar ROMs de 4 KiB.
- CLI de emulador para registrar y ejecutar Stella desde RIF.
- Documentacion interna por paginas y hovers de VS Code para instrucciones,
  registros y helpers del plugin.

## Estructura

```text
rif/plugins/atari2600/
  README.md
  cli.py
  cli/
    install.py
    run.py
  packs/example/
    atari2600.pack
    atari2600.regs.pack
    atari2600.rules.pack
    atari2600.sections.pack
    atari2600.types.pack
    atari2600.words.pack
  plugins/
    atari_pad_to.py
    atari_vectors.py
    mos6502_opcodes.json
  pages/
    0_uso.md
    1_cli.md
    2_arquitectura.md
    3_instrucciones_6502.md
    4_registros_tia.md
    5_riot_controles.md
    6_timing_video.md
    7_rom_minima.md
  vscode/
    build.json
    syntaxs.json
    doc.json
```

## Modelo de ROM

El pack de ejemplo asume una ROM NROM de 4 KiB. La seccion `.rom` emite desde
el offset fisico `0x0000`, pero usa `voffset 0xF000`, de modo que las
relocaciones absolutas generadas por `jmp_abs`, `jsr_abs`, `lda_abs` o
`sta_abs_addr` apuntan al espacio visible para el 6507.

El final de una ROM simple queda asi:

```rif
    rompad_to_vectors
    vectors start
```

`rompad_to_vectors` rellena hasta `0x0FFA`. `vectors start` escribe tres
direcciones de 16 bits: NMI, RESET e IRQ/BRK. En Atari 2600 normalmente solo
importa RESET, pero repetir el mismo label en los tres vectores hace que la ROM
sea tolerante a arranques y traps simples durante prototipos.

## Paginas de documentacion

1. `0_uso.md`: uso del pack, secciones y flujo de build.
2. `1_cli.md`: instalacion y ejecucion con Stella.
3. `2_arquitectura.md`: CPU 6507, bus, mapa de memoria y layout.
4. `3_instrucciones_6502.md`: familias de instrucciones y modos de direccionamiento.
5. `4_registros_tia.md`: referencia extensa de registros TIA.
6. `5_riot_controles.md`: RIOT, RAM, joysticks, switches y timers.
7. `6_timing_video.md`: frame, scanlines, VSYNC, VBLANK y kernel.
8. `7_rom_minima.md`: ejemplo comentado de ROM minima.
