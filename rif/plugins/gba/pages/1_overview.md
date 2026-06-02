# Vision General

Game Boy Advance combina una CPU ARM7TDMI con memoria de cartucho, WRAM, VRAM,
OAM, Palette RAM, DMA, timers, sonido y botones mapeados en memoria. El plugin
`gba` modela esas piezas para que RIF pueda emitir una ROM lista para arranque.

## CPU ARM7TDMI

La CPU puede ejecutar dos estados:

| Estado | Tamano de instruccion | Uso tipico |
|---|---:|---|
| ARM | 32 bits | Arranque, rutinas rapidas, codigo con registros completos. |
| Thumb | 16 bits | Codigo compacto desde ROM, loops pequenos y rutinas generales. |

La BIOS arranca en ARM. Para entrar a Thumb se usa `BX` con el bit 0 del destino
en `1`; el plugin lo encapsula con `set_entry_thumb`.

## Mapa de memoria

| Region | Direccion | Tamano | Uso |
|---|---:|---:|---|
| BIOS | `0x00000000` | 16 KiB | Rutinas internas y arranque. |
| EWRAM | `0x02000000` | 256 KiB | RAM externa general. |
| IWRAM | `0x03000000` | 32 KiB | RAM interna rapida. |
| IOREG | `0x04000000` | 1 KiB visible aprox. | Registros de hardware. |
| PALRAM | `0x05000000` | 1 KiB | Paletas BGR555. |
| VRAM | `0x06000000` | 96 KiB | Tiles, mapas, bitmaps. |
| OAM | `0x07000000` | 1 KiB | Atributos de sprites. |
| ROM WS0 | `0x08000000` | hasta 32 MiB | Cartucho principal. |
| SRAM | `0x0E000000` | variable | Guardado externo. |

## Secciones del pack

| Seccion RIF | Direccion | Rol |
|---|---:|---|
| `.header` | `0x08000000` | Cabecera obligatoria de 192 bytes. |
| `.rom` | `0x080000C0` | Codigo principal despues de la cabecera. |
| `.rodata` | continuo | Tablas, sprites, texto, audio empaquetado. |
| `.data` | `0x02000000` | Datos inicializados para EWRAM. |
| `.bss` | `0x02030000` | Datos sin inicializar. |

## Estructura del plugin

```text
plugins/gba/
  cli.py
  fillables.py
  packs/example/
    gba.pack
    gba.regs.pack
    gba.rules.pack
  plugins/
    thumb_ins.py
    arm_ins.py
    gba_headers.py
    gba_logo.py
    gba_checksum.py
    gba_entry_thumb.py
```

## Relacion con otros plugins

El pack importa `image`, `fonts` y `sound` junto con `basics` y `gba`. Eso
permite usar fillables para convertir PNG/JPG/BMP, texto bitmap y audio PCM
dentro de la misma ROM.
