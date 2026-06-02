from __future__ import annotations

from rif import Err, Expr, Line

from rif.plugins.megadrive.plugins.md_common import STACK_TOP, emit_bytes


def main():
    if Line.elements < 2:
        return Err("md_vectors espera una etiqueta de reset")
    Line.Advance()
    target = str(Line.Advance()).strip()
    Line.toks.clear()
    Line.expects(" ", "\n")
    if not target:
        return Err("md_vectors espera una etiqueta de reset")
    return [
        emit_bytes(STACK_TOP.to_bytes(4, "big")),
        Expr(["reloc", "abs", target, "32", 0]),
        Expr(["pad", 0x100 - 8]),
    ]


def _start():
    return main()
