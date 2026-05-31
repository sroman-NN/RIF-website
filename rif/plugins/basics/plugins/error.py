

from __future__ import annotations

from typing import Any

from rif import Line, Err, Errors


def _clean(value: Any) -> str:
    if hasattr(value, "value"):
        value = value.value
    return str(value).strip()


def main():
    if Line.elements != 2:
        return Err("La instrucción error espera un string")

    Line.Advance()  
    message = _clean(Line.Advance())
    Line.expects(" ", "\n")

    a = "----- |      ERROR       | -----"
    b = message
    c = "----- |      -----       | -----"
    Errors.add([a, b, c])

    return 0


def _start():
    return main()
