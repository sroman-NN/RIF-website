# Memoria y Modos de Video

GBA es little-endian. Los valores de 16 y 32 bits se guardan con el byte menos
significativo en la direccion mas baja.

## Alineacion

| Tamano | Directiva | Alineacion recomendada |
|---|---|---|
| 8 bits | `db`, `u8` | 1 byte |
| 16 bits | `dh`, `u16`, `bgr555` | direccion par |
| 32 bits | `dw`, `u32` | direccion divisible por 4 |

Lee y escribe halfwords con `ldrh`/`strh` o `arm_ldrh`/`arm_strh`. Para words
usa `ldr`/`str` o reglas ARM equivalentes.

## VRAM, OAM y Palette RAM

VRAM, OAM y Palette RAM estan conectadas a bus de 16 bits. Evita `strb` en esas
regiones: el hardware duplica el byte sobre el halfword. Para pixeles Mode 3 y
colores BGR555, usa `strh`.

## Regiones principales

| Region | Direccion | Notas |
|---|---:|---|
| `EWRAM` | `0x02000000` | 256 KiB, mas lenta que IWRAM. |
| `IWRAM` | `0x03000000` | 32 KiB, rapida para rutinas criticas. |
| `IOREG` | `0x04000000` | Registros MMIO. |
| `PALRAM` | `0x05000000` | Paletas, 16 bits. |
| `VRAM` | `0x06000000` | Video RAM. |
| `OAM` | `0x07000000` | Sprites/objetos. |
| `ROM_WS0` | `0x08000000` | Cartucho principal. |

## DISPCNT

`DISPCNT` (`0x04000000`) controla el modo de video y que capas estan activas.
Para Mode 3 con BG2:

```text
0x0403 = MODE 3 | BG2 enable
```

## Modos de video

| Modo | Tipo | Resolucion | Uso |
|---|---|---:|---|
| 0 | Tile | 240x160 | 4 fondos regulares. |
| 1 | Tile/affine | 240x160 | 2 fondos regulares + 1 affine. |
| 2 | Affine | 240x160 | 2 fondos affine. |
| 3 | Bitmap BGR555 | 240x160 | Framebuffer directo, 1 pagina. |
| 4 | Bitmap paletizado | 240x160 | 8 bits por pixel, doble buffer. |
| 5 | Bitmap BGR555 | 160x128 | Doble buffer, menor resolucion. |

Mode 3 es el mas simple para prototipos porque cada pixel es un halfword BGR555:

```text
addr = 0x06000000 + ((y * 240) + x) * 2
```

## BGR555

Cada color usa 15 bits:

| Bits | Canal |
|---|---|
| 0-4 | Rojo |
| 5-9 | Verde |
| 10-14 | Azul |

Ejemplos:

| Color | Valor |
|---|---:|
| Rojo | `0x001F` |
| Verde | `0x03E0` |
| Azul | `0x7C00` |
| Blanco | `0x7FFF` |

## VBlank

Para actualizar VRAM sin tearing en modos mas complejos, espera VBlank leyendo
`VCOUNT`:

```rif
wait_vblank:
    arm_ldrh R9, R3, 6
    arm_cmp_imm R9, 160
    arm_bcond ne, wait_vblank
```

Aqui `R3` contiene `0x04000000`, por lo que offset `6` lee `VCOUNT`.
