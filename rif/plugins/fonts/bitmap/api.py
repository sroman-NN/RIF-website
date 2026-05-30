from __future__ import annotations

from pathlib import Path

from .parser import SX7Font, load_font


FONT_DIR = Path(__file__).resolve().parent
DEFAULT_FONT = "font-5x7x1.f"


def load_bitmap_font(name: str = DEFAULT_FONT) -> SX7Font:
    path = Path(name)
    if not path.exists():
        path = FONT_DIR / name
    return load_font(path)


def text_bitmap_bytes(text: str, font: str = DEFAULT_FONT, fallback: str | None = "?") -> bytes:
    loaded = load_bitmap_font(font)
    out = bytearray()
    for char in text:
        out.extend(loaded.get_flat_bytes(char, fallback=fallback))
    return bytes(out)


def text_bitmap_hex(text: str, font: str = DEFAULT_FONT, fallback: str | None = "?") -> str:
    return text_bitmap_bytes(text, font=font, fallback=fallback).hex()
