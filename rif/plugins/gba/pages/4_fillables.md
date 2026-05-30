# Fillables

El plugin `gba` expone fillables que generan datos de pantalla y bitmaps.
El linker los expande antes de compilar al encontrar `@nombre` en el fuente.

## @fill_screen

Genera un array con los pixels de toda la pantalla (240×160) rellenos de un color BGR555.

```rif
@fill_screen black screen_bg
@fill_screen green pantalla_verde
```

Argumentos:

| Posición | Tipo   | Default      | Descripción               |
|----------|--------|--------------|---------------------------|
| 1        | string | `"black"`    | Color: `black`, `white`, `green` |
| 2        | string | `"screen_data"` | Nombre del símbolo generado |

El fillable expande a:

```rif
screen_bg bitmap[76800] = 0x0000...
```

## @fill_screen_text

Genera un frame completo con texto centrado dibujado en fuente 5×7 (escala 3).

```rif
@fill_screen_text HELLO white green pantalla
```

Argumentos:

| Posición | Tipo   | Default           | Descripción               |
|----------|--------|-------------------|---------------------------|
| 1        | string | `"HELLO"`         | Texto a dibujar (ASCII)   |
| 2        | string | `"white"`         | Color de texto            |
| 3        | string | `"green"`         | Color de fondo            |
| 4        | string | `"screen_frame"`  | Nombre del símbolo        |

## @fill_bitmap_array_logo (del plugin fonts)

Genera una cadena de texto como bytes de bitmap 5×7:

```rif
@fill_bitmap_array_logo HOLA mi_logo
```

Para usar estos fillables, el pack debe declarar los plugins:

```pack
.pack
plugin "gba"
plugin "fonts"
```
