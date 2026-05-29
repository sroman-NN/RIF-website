from __future__ import annotations

from bitmap.parser import format_label, load_font, save_font
from common import parse_cli_char, resolve_font_path


def main(args) -> int:
    return delete_character(args.file, args.char)


def delete_character(file_name: str, char_arg: str) -> int:
    path = resolve_font_path(file_name)
    char = parse_cli_char(char_arg)
    font = load_font(path)

    if char not in font.glyphs:
        raise KeyError(f"La fuente no contiene el glyph {format_label(char)!r}")

    font.delete_glyph(char)
    save_font(path, font)
    print(f"Borrado {format_label(char)!r} de {path}")
    return 0
