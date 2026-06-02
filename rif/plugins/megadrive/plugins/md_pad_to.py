from __future__ import annotations

from rif import Err, Expr, Line


def main():
    if Line.elements < 2:
        return Err("md_pad_to espera un offset")
    Line.Advance()
    value = " ".join(str(item).strip() for item in Line.toks).strip()
    Line.toks.clear()
    Line.expects(" ", "\n")
    if not value:
        return Err("md_pad_to espera un offset")
    return Expr(["pad_to", value])


def _start():
    return main()
