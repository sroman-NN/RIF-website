from __future__ import annotations

from rif import Err, Line

from rif.plugins.megadrive.plugins.md_common import emit_bytes, make_header


def main():
    Line.Advance()
    if Line.toks:
        return Err("md_header no acepta argumentos")
    Line.toks.clear()
    Line.expects(" ", "\n")
    return emit_bytes(make_header())


def _start():
    return main()
