

from __future__ import annotations

from typing import Any

from rif import Err, Expr, Line


def _clean(value: Any) -> str:
    """Limpia y normaliza el valor de un operando."""
    if hasattr(value, "value"):
        value = value.value
    return str(value).strip()


def main():
    """Punto de entrada principal para el alias heredado de emisión de dirección."""
    if Line.elements != 2:
        return Err("emitadress espera un operando")

    Line.Advance()  
    target = _clean(Line.Advance())
    Line.expects(" ", "\n")

    if not target:
        return Err("emitadress espera un operando")

    return Expr(["emit_address", target, None])


def _start():
    """Función de inicio del precompilador/emisor."""
    return main()
