# Plugin: Fonts

Plugin oficial de RIF para fuentes bitmap retargetables. Convierte texto en
datos binarios durante el build, registra los assets en `fills.json` y deja que
cada plataforma decida como renderizarlos.

El plugin no sabe de GBA, Atari o Mega Drive. Solo produce filas de bits a partir
de fuentes `.f`; el proyecto o pack consumidor decide si las lee como bytes,
halfwords, words, tiles, sprites o framebuffer.

## Fuentes incluidas

| Archivo | Alias | Tamano | Uso recomendado |
|---|---|---:|---|
| `font-3x5x1.f` | `3x5`, `3x5x1` | 3x5 | HUD muy compacto. |
| `font-4x6x1.f` | `4x6`, `4x6x1` | 4x6 | Texto pequeno legible. |
| `font-5x7x1.f` | `5x7`, `5x7x1` | 5x7 | Fuente base, balanceada. |
| `font-6x8x1.f` | `6x8`, `6x8x1` | 6x8 | Titulos y texto mas abierto. |

Todas usan `row_bytes = 1`, es decir, cada fila se empaqueta en un byte.

## Fillables

Forma general:

```rif
@args@namefunc@namelabel
```

| Fillable | Salida | Descripcion |
|---|---|---|
| `fonts_fill_text_u8` | `u8[]` | Bytes crudos de filas empaquetadas. |
| `fonts_fill_text_u16` | `u16[]` | Una fila por halfword little-endian. Bueno para GBA. |
| `fonts_fill_text_u32` | `u32[]` | Una fila por word little-endian. Bueno para alineacion amplia. |
| `fonts_fill_3x5x1` | `u16[]` | Alias con fuente `font-3x5x1.f`. |
| `fonts_fill_4x6x1` | `u16[]` | Alias con fuente `font-4x6x1.f`. |
| `fonts_fill_5x7x1` | `u16[]` | Alias compatible con la fuente historica. |
| `fonts_fill_6x8x1` | `u16[]` | Alias con fuente `font-6x8x1.f`. |
| `bitmap_array_logo` | `u8[]` | Alias antiguo para texto/logo bitmap. |

Ejemplos:

```rif
@"PRESS START"@fonts_fill_5x7x1@press_start_text
@"HP 99" 3x5@fonts_fill_text_u8@hud_text
@"TITLE" font-6x8x1.f@fonts_fill_text_u16@title_text
```

## CLI

```bash
python -m rif -pcli fonts list
python -m rif -pcli fonts add font-5x7x1.f A
python -m rif -pcli fonts modify font-5x7x1.f A
python -m rif -pcli fonts delete font-5x7x1.f A
python -m rif -pcli fonts open font-5x7x1.f
```

## Formato `.f`

```text
font SX7
size 5, 7, 1
align right

A:
   01110
   10001
   10001
   11111
   10001
   10001
   10001
```

`size width, height, row_bytes` define cuantos bits visibles hay por fila,
cuantas filas tiene cada glifo y cuantos bytes fisicos ocupa cada fila. `align`
puede ser `right` o `left`.

## Integracion con plataformas

GBA, Atari 2600 o Mega Drive no deberian hardcodear glifos. Deben importar
`fonts` cuando necesiten texto, generar tablas con estos fillables y luego
renderizar esas filas segun su propio hardware.
