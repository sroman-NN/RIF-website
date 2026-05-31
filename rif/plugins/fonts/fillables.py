from __future__ import annotations

from rif.plugins.fonts.bitmap.api import DEFAULT_FONT, cached_text_bitmap_bytes, load_bitmap_font, resolve_font_path
from rif.fillables import record_fill
import hashlib
import re


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


def fill_fonts_fill_5x7x1(*args, context=None) -> str:
    text = str(args[0]) if args else ""
    symbol = str(args[1]) if len(args) > 1 else _text_symbol(text)
    font = str(args[2]) if len(args) > 2 else DEFAULT_FONT
    data = cached_text_bitmap_bytes(text, font=font, context=context)
    encoded = b"".join(bytes((byte, 0)) for byte in data)
    loaded = load_bitmap_font(font, context=context)
    font_path = resolve_font_path(font, context=context)
    record_fill(
        context,
        "fonts",
        symbol,
        size=len(encoded),
        bits=len(encoded) * 8,
        align=2,
        padding=0,
        type="u16",
        format="font-5x7x1-text",
        text=text,
        font=str(font_path),
        glyphs=len(text),
        width=loaded.width,
        height=loaded.height,
        row_bytes=loaded.row_bytes,
        storage="u16-row-low-byte",
        stride=loaded.height * 2,
    )
    return f"{symbol} u16[{len(data)}] = 0x{encoded.hex()}"


def _text_symbol(text: str) -> str:
    head = re.sub(r"[^0-9A-Za-z_]+", "_", text.lower()).strip("_")[:24]
    digest = hashlib.sha1(text.encode("utf-8")).hexdigest()[:8]
    if not head or head[0].isdigit():
        head = "text"
    return f"{head}_{digest}"
