from __future__ import annotations

from rif.plugins.fonts.bitmap.api import DEFAULT_FONT, cached_text_bitmap_bytes, load_bitmap_font, resolve_font_path
from rif.fillables import record_fill


def fill_bitmap_array_logo(*args, context=None) -> str:
    text = str(args[0]) if args else "LOGO"
    symbol = str(args[1]) if len(args) > 1 else "bitmap_array_logo"
    font = str(args[2]) if len(args) > 2 else DEFAULT_FONT
    data = cached_text_bitmap_bytes(text, font=font, context=context)
    loaded = load_bitmap_font(font, context=context)
    font_path = resolve_font_path(font, context=context)
    record_fill(
        context,
        "fonts",
        symbol,
        size=len(data),
        bits=len(data) * 8,
        align=loaded.row_bytes,
        padding=0,
        type="u8",
        format="bitmap-text",
        text=text,
        font=str(font_path),
        glyphs=len(text),
        width=loaded.width,
        height=loaded.height,
        row_bytes=loaded.row_bytes,
    )
    return f"{symbol} u8[{len(data)}] = 0x{data.hex()}"
