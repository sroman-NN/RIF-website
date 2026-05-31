from __future__ import annotations

from rif.fillables import record_fill
from rif.plugins.gba.plugins.gba_common import COLORS, NINTENDO_LOGO, SCREEN_H, SCREEN_W, make_checksum_block, make_entry_code, make_entry_thumb_code, make_frame


def _record(context, name: str, **info) -> None:
    record_fill(context, "gba", name, align=1, padding=0, **info)


def fill_headers(*_args, context=None) -> str:
    _record(context, "headers", size=4, bits=32, type="gba-header-branch")
    return "set_headers"


def fill_logo(*_args, context=None) -> str:
    _record(context, "logo", size=len(NINTENDO_LOGO), bits=len(NINTENDO_LOGO) * 8, type="gba-logo")
    return "set_logo"


def fill_checksum(title: str = "RIF GBA", *_args, context=None) -> str:
    data = make_checksum_block(title)
    _record(context, "checksum", size=len(data), bits=len(data) * 8, type="gba-checksum", title=title)
    return _bytes_to_db(data)


def fill_gba_header(title: str = "RIF GBA", *_args, context=None) -> str:
    data = make_checksum_block(title)
    size = 4 + len(NINTENDO_LOGO) + len(data)
    _record(context, "gba_header", size=size, bits=size * 8, type="gba-header", title=title)
    return "\n".join(("set_headers", "set_logo", _bytes_to_db(data)))


def fill_entry(*_args, context=None) -> str:
    data = make_entry_code()
    _record(context, "entry", size=len(data), bits=len(data) * 8, type="gba-entry-arm")
    return "set_entry"


def fill_entry_thumb(*_args, context=None) -> str:
    data = make_entry_thumb_code()
    _record(context, "entry_thumb", size=len(data), bits=len(data) * 8, type="gba-entry-thumb")
    return "set_entry_thumb"


def fill_frame(text: str = "HELLO", bg: str = "green", fg: str = "black", *_args, context=None) -> str:
    _record(context, "frame", size=SCREEN_W * SCREEN_H * 2, bits=SCREEN_W * SCREEN_H * 16, type="bgr555-frame", text=text, width=SCREEN_W, height=SCREEN_H, bg=bg, fg=fg)
    return "set_frame"


def fill_rompad(*_args, context=None) -> str:
    _record(context, "rompad", size=None, bits=None, type="gba-rompad", dynamic=True)
    return "set_rompad"


def fill_screen(color: str = "black", symbol: str = "screen_data", *_args, context=None) -> str:
    col_val = COLORS.get(color.lower(), 0x0000)
    data = bytearray()
    for _ in range(SCREEN_W * SCREEN_H):
        data.extend(col_val.to_bytes(2, "little"))
    _record(context, symbol, size=len(data), bits=len(data) * 8, type="bgr555-screen", color=color, width=SCREEN_W, height=SCREEN_H)
    return f"{symbol} u8[{len(data)}] = 0x{data.hex()}"


def fill_screen_text(text: str = "HELLO", fg: str = "white", bg: str = "green", symbol: str = "screen_frame", *_args, context=None) -> str:
    fg_val = COLORS.get(fg.lower(), 0x7FFF)
    bg_val = COLORS.get(bg.lower(), 0x03E0)
    data = make_frame(text, background=bg_val, foreground=fg_val)
    _record(context, symbol, size=len(data), bits=len(data) * 8, type="bgr555-frame", text=text, width=SCREEN_W, height=SCREEN_H, bg=bg, fg=fg)
    return f"{symbol} u8[{len(data)}] = 0x{data.hex()}"


def _bytes_to_db(data: bytes) -> str:
    return "\n".join(f"db 0x{byte:02X}" for byte in data)


def _start():
    return None
