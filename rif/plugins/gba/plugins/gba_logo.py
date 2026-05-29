from __future__ import annotations

from rif.plugins.gba.plugins.gba_common import NINTENDO_LOGO, emit_bytes


def main():
    return emit_bytes(NINTENDO_LOGO)


def _start():
    return main()
