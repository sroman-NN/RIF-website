from __future__ import annotations

from bitmap.api import DEFAULT_FONT, text_bitmap_bytes


def fill_bitmap_array_logo(*args, context=None) -> str:
    text = str(args[0]) if args else "LOGO"
    symbol = str(args[1]) if len(args) > 1 else "bitmap_array_logo"
    font = str(args[2]) if len(args) > 2 else DEFAULT_FONT
    data = text_bitmap_bytes(text, font=font)
    return f"{symbol} bitmap[{len(data)}] = 0x{data.hex()}"
