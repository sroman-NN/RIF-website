from __future__ import annotations

CONTEXT = None
from rif.plugins.gba.plugins.gba_common import BLACK, GREEN, args, color, emit_bytes, make_frame


def main():
    if getattr(globals().get("CONTEXT"), "phase", None) == "parse":
        return None
    pack = args()
    text = pack[0] if pack else "Hola mundo"
    background = color(pack[1], GREEN) if len(pack) > 1 else GREEN
    foreground = color(pack[2], BLACK) if len(pack) > 2 else BLACK
    return emit_bytes(make_frame(text, background=background, foreground=foreground))


def _start():
    return main()
