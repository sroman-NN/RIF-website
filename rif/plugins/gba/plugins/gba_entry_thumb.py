from __future__ import annotations

from rif.plugins.gba.plugins.gba_common import emit_bytes, make_entry_thumb_code


def main():
    return emit_bytes(make_entry_thumb_code())


def _start():
    return main()
