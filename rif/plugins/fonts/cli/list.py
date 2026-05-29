from __future__ import annotations

from bitmap.parser import load_font
from common import iter_font_files


def main(args) -> int:
    return list_fonts()


def list_fonts() -> int:
    files = iter_font_files()

    if not files:
        print("No hay fuentes .f en fonts/bitmap/")
        return 0

    print(f"{'archivo':<24} {'formato':<12} {'align':<8} {'glyphs':<6} estado")
    print("-" * 64)

    for path in files:
        try:
            font = load_font(path)
            fmt = f"{font.width}x{font.height}x{font.row_bytes}"
            print(f"{path.name:<24} {fmt:<12} {font.align:<8} {len(font.glyphs):<6} ok")
        except Exception as exc:
            print(f"{path.name:<24} {'?':<12} {'?':<8} {'?':<6} invalida: {exc}")

    return 0
