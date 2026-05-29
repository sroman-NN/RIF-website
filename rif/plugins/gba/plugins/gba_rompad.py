from __future__ import annotations

from rif.plugins.gba.plugins.gba_common import FRAME_OFFSET, ROM_SIZE, SCREEN_H, SCREEN_W, emit_bytes


def main():
    used = FRAME_OFFSET + SCREEN_W * SCREEN_H * 2
    return emit_bytes(b"\x00" * max(0, ROM_SIZE - used))


def _start():
    return main()
