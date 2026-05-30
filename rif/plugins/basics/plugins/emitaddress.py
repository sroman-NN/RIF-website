"""Emite una dirección de memoria como placeholder reservando espacio físico.

Soporta la sintaxis:
    emitaddress target, [width]
donde target es la etiqueta o símbolo y width el tamaño en bits.
"""

from __future__ import annotations

from typing import Any

from rif import Err, Expr, Line


def _clean(value: Any) -> str:
    """Limpia y normaliza el valor de un operando."""
    if hasattr(value, "value"):
        value = value.value
    return str(value).strip()


def main():
    """Punto de entrada principal para el plugin de emisión de dirección."""
    Line.Advance()  # consumir "emitaddress"
    pack = [_clean(item) for item in Line.Unpack(",")]

    if len(pack) not in (1, 2) or not all(pack):
        return Err("emitaddress espera destino y tamano opcional")

    target = pack[0]
    width = pack[1] if len(pack) == 2 else None

    return Expr(["emit_address", target, width])


def _start():
    """Función de inicio del precompilador/emisor."""
    return main()
