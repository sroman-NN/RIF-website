# Plugin: Game Boy Advance

Plugin oficial de RIF para construir ROMs de Game Boy Advance con ARM7TDMI,
codigo ARM/Thumb, cabecera de cartucho, logo, checksum, recursos de imagen,
texto y audio, y CLI para ejecutar el resultado con mGBA.

## Inicio rapido

```bash
python -m rif build examples/gba --plugin gba --name example
python -m rif -pcli gba install mGBA --add-path
python -m rif -pcli gba run examples/gba/gba.gba -nd
```

## Que incluye

- Reglas Thumb de 16 bits para operaciones comunes: `store`, `movs`, `adds`,
  `subs`, shifts, ALU, load/store, branches, `push`, `pop`, `bl`, `swi`.
- Reglas ARM de 32 bits para arranque, rutinas de alto nivel y helpers:
  `arm_mov_imm`, `arm_ldr_label`, `arm_strh`, `arm_bcond`, `arm_bl`, etc.
- Tabla extensa de registros ARM7TDMI, aliases `SP/LR/PC`, MMIO de video,
  sonido, DMA, timers, serial, botones, interrupciones y regiones de memoria.
- Secciones de linker para cartucho y memoria: `.header`, `.rom`, `.rodata`,
  `.data` y `.bss`.
- Macros de ROM: `set_headers`, `set_logo`, `set_checksum`, `set_entry_thumb`,
  `set_rompad` y alias `rompad`.
- Fillables para cabecera, framebuffer, texto, imagenes, audio y fuentes cuando
  se usan los plugins `image`, `sound` y `fonts`.
- Metadata de VS Code con sintaxis, snippets, hovers y diagnosticos.

## Estructura

```text
rif/plugins/gba/
  README.md
  cli.py
  fillables.py
  packs/example/
    gba.pack
    gba.regs.pack
    gba.rules.pack
    gba.sections.pack
    gba.types.pack
    gba.words.pack
  pages/
    0_build_y_run.md
    1_overview.md
    2_instrucciones.md
    3_registros.md
    4_fillables.md
    5_macros_rom.md
    6_memoria_y_modos.md
    7_ejemplo_minimo.md
  plugins/
    arm_ins.py
    thumb_ins.py
    gba_headers.py
    gba_logo.py
    gba_checksum.py
    gba_entry.py
    gba_entry_thumb.py
    gba_rompad.py
  vscode/
    build.json
    syntaxs.json
    doc.json
```

## Modelo de secciones

| Seccion | VOffset | Emite | Uso |
|---|---:|---|---|
| `.header` | `0x08000000` | si | Primeros 192 bytes del cartucho. |
| `.rom` | `0x080000C0` | si | Codigo ARM/Thumb y datos colocados despues de la cabecera. |
| `.rodata` | continuo | si | Datos de solo lectura empaquetados en ROM. |
| `.data` | `0x02000000` | si | Datos inicializados para EWRAM. |
| `.bss` | `0x02030000` | no | Datos sin inicializar. |

Una ROM minima suele tener:

```rif
.header
    set_headers
    set_logo
    set_checksum "RIF GBA"
    set_entry_thumb

.rom
main:
    arm_b main

.rodata
    rompad
```

## Desarrollo con RIF

El ejemplo oficial usa ARM para mantener rutinas generadas y accesos MMIO
directos, pero el pack tambien expone instrucciones Thumb. La cabecera empieza
en ARM porque la BIOS de GBA arranca en estado ARM; `set_entry_thumb` emite el
puente para entrar a codigo Thumb cuando ese sea el flujo elegido.

## Documentacion

Abre el portal local con:

```bash
python -m rif help --open
```

Las paginas de este plugin cubren build/run, arquitectura, instrucciones,
registros, fillables, macros de ROM, memoria, modos de video y un ejemplo
minimo comentado.
