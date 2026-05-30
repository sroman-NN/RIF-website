# Estructura de plugin

Estructura recomendada:

```text
plugins/NOMBRE/
    readme.md
    pages/
        0_intro.md
        1_detalle.md
    cli.py
    cli/
    plugins/
        instruccion.py
```

`readme.md` o cualquier `.md` en la raiz del plugin se usa como documentacion principal en `rif help`.

`pages/` permite subsecciones ordenadas. El nombre `0_intro.md` usa `0` para ordenar y `intro` como nombre visible.

Forma minima de instruccion:

```python
from rif import Expr, Line

def main():
    Line.Advance()
    return Expr(["op"])

def _start():
    return main()
```

APIs usuales:

- `Line`: tokens de la instruccion actual
- `RuleIndicator.current`: regla activa
- `Operators`: bindings declarados con `need`
- `PluginContext`: contexto de fase, programa y linea
- `Err`: error controlado
- `Expr`: IR para el compiler

El plugin debe evitar estado global propio salvo que pueda reiniciarse por contexto.
