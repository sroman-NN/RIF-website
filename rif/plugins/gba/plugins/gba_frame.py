from __future__ import annotations

CONTEXT = None
from rif.plugins.gba.plugins.gba_common import GREEN, args, color, emit_bytes, make_frame


def main():
    if getattr(globals().get("CONTEXT"), "phase", None) == "parse":
        return None
    pack = args()
    color_arg = pack[1] if len(pack) > 1 else (pack[0] if pack else "green")
    background = color(color_arg, GREEN)
    return emit_bytes(make_frame(background=background))


def _start():
    return main()
