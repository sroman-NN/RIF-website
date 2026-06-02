from __future__ import annotations

from rif.plugins.fonts.bitmap.api import DEFAULT_FONT, cached_text_bitmap_bytes, load_bitmap_font, resolve_font_path
from rif.fillables import record_fill
import hashlib
import re


FONT_3X5 = "font-3x5x1.f"
FONT_4X6 = "font-4x6x1.f"
FONT_5X7 = "font-5x7x1.f"
FONT_6X8 = "font-6x8x1.f"


def fill_bitmap_array_logo(*args, context=None) -> str:
    return _fill_text(args, context=context, default_text="LOGO", default_symbol="bitmap_array_logo", storage="u8")


def fill_fonts_fill_text_u8(*args, context=None) -> str:
    return _fill_text(args, context=context, storage="u8")


def fill_fonts_fill_text_u16(*args, context=None) -> str:
    return _fill_text(args, context=context, storage="u16")


def fill_fonts_fill_text_u32(*args, context=None) -> str:
    return _fill_text(args, context=context, storage="u32")


def fill_fonts_fill_3x5x1(*args, context=None) -> str:
    return _fill_text(args, context=context, default_font=FONT_3X5, storage="u16")


def fill_fonts_fill_4x6x1(*args, context=None) -> str:
    return _fill_text(args, context=context, default_font=FONT_4X6, storage="u16")


def fill_fonts_fill_5x7x1(*args, context=None) -> str:
    return _fill_text(args, context=context, default_font=FONT_5X7, storage="u16")


def fill_fonts_fill_6x8x1(*args, context=None) -> str:
    return _fill_text(args, context=context, default_font=FONT_6X8, storage="u16")


def _fill_text(
    args,
    *,
    context=None,
    default_text: str = "",
    default_symbol: str | None = None,
    default_font: str = DEFAULT_FONT,
    storage: str = "u8",
) -> str:
    text = str(args[0]) if args else default_text
    label = context.get("fill_label") if isinstance(context, dict) else None
    symbol = str(label or (args[1] if len(args) > 1 else (default_symbol or _text_symbol(text))))
    font_index = 1 if label else 2
    font = str(args[font_index]) if len(args) > font_index else default_font
    data = cached_text_bitmap_bytes(text, font=font, context=context)
    loaded = load_bitmap_font(font, context=context)
    font_path = resolve_font_path(font, context=context)
    encoded, type_name, align, array_len, storage_name = _encode_storage(data, loaded.row_bytes, storage)
    record_fill(
        context,
        "fonts",
        symbol,
        size=len(encoded),
        bits=len(encoded) * 8,
        align=align,
        padding=0,
        type=type_name,
        format=f"font-{loaded.width}x{loaded.height}x{loaded.row_bytes}-text",
        text=text,
        font=str(font_path),
        glyphs=len(text),
        width=loaded.width,
        height=loaded.height,
        row_bytes=loaded.row_bytes,
        storage=storage_name,
        stride=loaded.height * align,
    )
    return f"{symbol} {type_name}[{array_len}] = 0x{encoded.hex()}"


def _encode_storage(data: bytes, row_bytes: int, storage: str) -> tuple[bytes, str, int, int, str]:
    if storage == "u8":
        return data, "u8", 1, len(data), "packed-row-bytes"

    if storage == "u16":
        if row_bytes > 2:
            raise ValueError("fonts_fill_text_u16 solo soporta fuentes de hasta 2 bytes por fila")
        encoded = bytearray()
        for start in range(0, len(data), row_bytes):
            row = data[start:start + row_bytes]
            encoded.extend(row.ljust(2, b"\x00"))
        return bytes(encoded), "u16", 2, len(encoded) // 2, "row-u16-little"

    if storage == "u32":
        if row_bytes > 4:
            raise ValueError("fonts_fill_text_u32 solo soporta fuentes de hasta 4 bytes por fila")
        encoded = bytearray()
        for start in range(0, len(data), row_bytes):
            row = data[start:start + row_bytes]
            encoded.extend(row.ljust(4, b"\x00"))
        return bytes(encoded), "u32", 4, len(encoded) // 4, "row-u32-little"

    raise ValueError(f"storage de fuente no soportado: {storage}")


def _text_symbol(text: str) -> str:
    head = re.sub(r"[^0-9A-Za-z_]+", "_", text.lower()).strip("_")[:24]
    digest = hashlib.sha1(text.encode("utf-8")).hexdigest()[:8]
    if not head or head[0].isdigit():
        head = "text"
    return f"{head}_{digest}"
