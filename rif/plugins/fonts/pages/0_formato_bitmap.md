# Formato Bitmap `.f`

Las fuentes bitmap usan archivos `.f` con formato `SX7`. El nombre historico se
mantiene por compatibilidad, pero el parser soporta diferentes anchos y altos.

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

## Cabecera

| Campo | Significado |
|---|---|
| `font SX7` | Identificador del formato. |
| `size w, h, row_bytes` | Ancho visible, alto y bytes fisicos por fila. |
| `align right/left` | Alineacion de bits dentro de cada fila fisica. |

`row_bytes` permite fuentes de hasta `row_bytes * 8` bits por fila. Por ejemplo,
una fuente de 6 pixeles de ancho puede usar `row_bytes = 1`; una de 12 pixeles
necesitaria `row_bytes = 2`.

## Glifos

Cada glifo usa una etiqueta seguida de exactamente `height` filas binarias:

```text
?:
   01110
   10001
   00001
   00010
   00100
   00000
   00100
```

Etiquetas permitidas:

| Forma | Ejemplo |
|---|---|
| Caracter directo | `A:` |
| Espacio | `space:` |
| Codigo hexadecimal | `0x3A:` |
| Literal de un caracter | `':':` |

## Fuentes incluidas

| Fuente | Tamano |
|---|---:|
| `font-3x5x1.f` | 3x5, 1 byte por fila |
| `font-4x6x1.f` | 4x6, 1 byte por fila |
| `font-5x7x1.f` | 5x7, 1 byte por fila |
| `font-6x8x1.f` | 6x8, 1 byte por fila |

Alias aceptados por la API: `3x5`, `4x6`, `5x7`, `6x8` y sus variantes `x1`.
