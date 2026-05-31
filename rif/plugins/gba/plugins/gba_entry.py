from __future__ import annotations

CONTEXT = None
from rif.plugins.gba.plugins.gba_common import emit_bytes, make_entry_code


def main():
    if getattr(globals().get("CONTEXT"), "phase", None) == "parse":
        return None
    return emit_bytes(make_entry_code())


def _start():
    return main()
