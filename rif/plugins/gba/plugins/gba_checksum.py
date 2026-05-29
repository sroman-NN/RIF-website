from __future__ import annotations

from rif.plugins.gba.plugins.gba_common import args, emit_bytes, make_checksum_block


def main():
    pack = args()
    text = pack[0] if pack else "Hola mundo"
    return emit_bytes(make_checksum_block(text))


def _start():
    return main()
