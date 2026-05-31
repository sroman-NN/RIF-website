from __future__ import annotations

CONTEXT = None
from rif.plugins.gba.plugins.gba_common import NINTENDO_LOGO, emit_bytes


def main():
    if getattr(globals().get("CONTEXT"), "phase", None) == "parse":
        return None
    return emit_bytes(NINTENDO_LOGO)


def _start():
    return main()
