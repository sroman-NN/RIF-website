from __future__ import annotations

from rif import Err, Expr, Line


def main():
    if Line.elements < 2:
        return Err("atari_vectors espera una etiqueta")
    Line.Advance()
    target = str(Line.Advance()).strip()
    Line.toks.clear()
    Line.expects(" ", "\n")
    if not target:
        return Err("atari_vectors espera una etiqueta")
    return [
        Expr(["reloc", "abs", target, "16", 0]),
        Expr(["reloc", "abs", target, "16", 0]),
        Expr(["reloc", "abs", target, "16", 0]),
    ]


def _start():
    return main()
