from __future__ import annotations

from rif.plugins.gba.plugins.gba_common import ENTRY_OFFSET, GBA_ROM_BASE, arm_b, emit_bytes, u32


def main():
    return emit_bytes(u32(arm_b(GBA_ROM_BASE, GBA_ROM_BASE + ENTRY_OFFSET)))


def _start():
    return main()
