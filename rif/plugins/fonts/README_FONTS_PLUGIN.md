# SX7 Fonts Plugin

Plugin de fuentes bitmap retargetables para SX7/RIF.

Estructura principal:

```txt
fonts/
├── cli.py
├── cli/
│   ├── add.py
│   ├── common.py
│   ├── delete.py
│   ├── editor.py
│   ├── list.py
│   ├── modify.py
│   └── open.py
└── bitmap/
    ├── lexer.py
    ├── parser.py
    └── font-5x7x1.f
```

Formato `.f`:

```txt
font SX7
size 5, 7, 1 ; 5 bits, 7 filas, 1 byte por fila.
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

`size 5, 7, 1` significa:

- `5`: bits visuales por fila.
- `7`: filas por glyph.
- `1`: bytes fisicos por fila.

CLI:

```bash
python fonts/cli.py fonts
python fonts/cli.py list
python fonts/cli.py modify font-5x7x1.f A
python fonts/cli.py add font-5x7x1.f T
python fonts/cli.py delete font-5x7x1.f T
python fonts/cli.py open font-5x7x1.f
```

En RIF, la forma esperada seria equivalente a:

```bash
python -m rif -pcli fonts fonts
python -m rif -pcli fonts modify font-5x7x1.f A
```

API minima:

```python
from fonts.bitmap.parser import load_font

font = load_font("fonts/bitmap/font-5x7x1.f")
print(font.get_ascii_entry("A"))
# [65, [14, 17, 17, 31, 17, 17, 17]]
```
