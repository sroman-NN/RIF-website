# Plugin GBA

El plugin `gba` provee soporte para compilar ROMs de Game Boy Advance con RIF.

## Estructura

```
plugins/gba/
├── cli.py                    ← subcomandos rif -pcli gba
├── cli/
│   ├── install.py            ← instala mGBA
│   └── run.py                ← ejecuta el .gba en mGBA
├── fillables.py              ← @fill_screen / @fill_screen_text
├── packs/
│   └── example/
│       ├── gba.pack          ← pack raíz (fsystem 1)
│       ├── gba.regs.pack     ← registros ARM7TDMI
│       ├── gba.types.pack    ← tipos de dato
│       ├── gba.sections.pack ← layout de memoria
│       ├── gba.words.pack    ← instrucciones y macros
│       └── gba.rules.pack    ← reglas de compilación Thumb
└── plugins/
    ├── gba_common.py         ← utilidades y constantes
    ├── gba_headers.py        ← cabecera ROM (0x00-0xBF)
    ├── gba_logo.py           ← logo Nintendo (0x04-0x9F)
    ├── gba_checksum.py       ← checksum de cabecera
    ├── gba_entry.py          ← código de entrada ARM
    ├── gba_frame.py          ← framebuffer inicial
    └── gba_rompad.py         ← padding hasta 512 KB
```

## Mapa de memoria GBA

| Sección  | Dirección  | Tamaño | Descripción                  |
|----------|------------|--------|------------------------------|
| rom      | 0x08000000 | 32 MB  | Cartucho ROM (emitida al .gba)|
| ewram    | 0x02000000 | 256 KB | Work RAM externa (lenta)      |
| iwram    | 0x03000000 | 32 KB  | Work RAM interna (rápida)     |
| io       | 0x04000000 | 1 KB   | Registros de hardware MMIO    |
| palette  | 0x05000000 | 1 KB   | Paletas de color (BGR555)     |
| vram     | 0x06000000 | 96 KB  | Video RAM                     |
| oam      | 0x07000000 | 1 KB   | Atributos de sprites          |
| sram     | 0x0E000000 | 64 KB  | Save RAM del cartucho         |

## Arquitectura

El GBA corre un **ARM7TDMI** en modo **Thumb** (instrucciones de 16 bits, little endian).
El pack emite código Thumb directamente sin necesitar un ensamblador externo.
