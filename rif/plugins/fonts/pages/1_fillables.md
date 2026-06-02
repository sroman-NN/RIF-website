# Fillables de Fonts

Los fillables convierten texto en datos durante el link. Todos usan la forma:

```rif
@args@namefunc@namelabel
```

`namelabel` es el simbolo generado y tambien la clave registrada en `fills.json`.

## Salida generica

### `fonts_fill_text_u8`

Genera filas empaquetadas como bytes crudos.

```rif
@"SCORE" 3x5@fonts_fill_text_u8@score_text
```

### `fonts_fill_text_u16`

Genera una fila por halfword little-endian. Si la fuente usa un byte por fila,
ese byte queda en la parte baja del halfword. Es el formato mas comodo para GBA.

```rif
@"PRESS START" 5x7@fonts_fill_text_u16@press_start_text
```

### `fonts_fill_text_u32`

Genera una fila por word little-endian. Es util cuando un renderer quiere leer
palabras alineadas.

```rif
@"TITLE" 6x8@fonts_fill_text_u32@title_text
```

## Aliases por tamano

Estos aliases emiten `u16[]`:

```rif
@"HP"@fonts_fill_3x5x1@hud_hp
@"MENU"@fonts_fill_4x6x1@menu_text
@"RIF"@fonts_fill_5x7x1@rif_text
@"START"@fonts_fill_6x8x1@start_text
```

## Alias antiguo

`bitmap_array_logo` conserva compatibilidad y emite `u8[]`:

```rif
@"RIF"@bitmap_array_logo@logo_bitmap
```

## Argumentos

Con `namelabel`, el primer argumento es texto y el segundo, opcional, es fuente:

```rif
@"Texto" font-6x8x1.f@fonts_fill_text_u16@texto_6x8
@"Texto" 6x8@fonts_fill_text_u16@texto_6x8_alias
```

Sin fuente explicita se usa `font-5x7x1.f`.

## Metadatos en `fills.json`

Cada fillable registra:

- `format`: `font-WxHxB-text`.
- `text`: texto original.
- `font`: ruta resuelta de la fuente.
- `glyphs`: cantidad de caracteres.
- `width`, `height`, `row_bytes`.
- `storage`: `packed-row-bytes`, `row-u16-little` o `row-u32-little`.
- `stride`: bytes por glifo.
