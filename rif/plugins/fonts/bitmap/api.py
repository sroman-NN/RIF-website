from __future__ import annotations

from pathlib import Path

from rif.plugins.cache_store import get_cached_bytes, set_cached_bytes
from rif.plugin_security import assert_allowed_path

from .parser import SX7Font, load_font


FONT_DIR = Path(__file__).resolve().parent
DEFAULT_FONT = "font-5x7x1.f"


def load_bitmap_font(name: str = DEFAULT_FONT, *, context=None) -> SX7Font:
    return load_font(resolve_font_path(name, context=context))


def resolve_font_path(name: str = DEFAULT_FONT, *, context=None) -> Path:
    path = Path(name)
    if not path.exists():
        path = FONT_DIR / name
    return assert_allowed_path(path, context=context)


def text_bitmap_bytes(text: str, font: str = DEFAULT_FONT, fallback: str | None = "?", *, context=None) -> bytes:
    loaded = load_bitmap_font(font, context=context)
    out = bytearray()
    for char in text:
        out.extend(loaded.get_flat_bytes(char, fallback=fallback))
    return bytes(out)


def cached_text_bitmap_bytes(text: str, font: str = DEFAULT_FONT, fallback: str | None = "?", *, context=None) -> bytes:
    font_path = resolve_font_path(font, context=context)
    stat = font_path.stat()
    params = {
        "text": text,
        "font": str(font_path),
        "mtime_ns": stat.st_mtime_ns,
        "size": stat.st_size,
        "fallback": fallback,
        "format": "bitmap-text",
    }
    cached = get_cached_bytes("fonts", "text", params, context=context)
    if cached is not None:
        return cached
    data = text_bitmap_bytes(text, font=str(font_path), fallback=fallback, context=context)
    set_cached_bytes("fonts", "text", params, data, context=context)
    return data


def text_bitmap_hex(text: str, font: str = DEFAULT_FONT, fallback: str | None = "?") -> str:
    return text_bitmap_bytes(text, font=font, fallback=fallback).hex()
