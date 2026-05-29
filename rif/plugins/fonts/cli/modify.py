from __future__ import annotations

from bitmap.parser import format_label, load_font, save_font
from common import parse_cli_char, resolve_font_path
from editor import edit_bits


def main(args) -> int:
    return modify_character(args.file, args.char)


def modify_character(file_name: str, char_arg: str) -> int:
    path = resolve_font_path(file_name)
    char = parse_cli_char(char_arg)
    font = load_font(path)

    if char not in font.glyphs:
        raise KeyError(f"La fuente no contiene el glyph {format_label(char)!r}")

    edited = edit_bits(
        font.glyphs[char],
        title=f"Modificando {format_label(char)!r} en {path.name}",
    )

    if edited is None:
        print("Cancelado. No se modifico el archivo.")
        return 0

    font.set_glyph(char, edited)
    save_font(path, font)
    print(f"Guardado: {path}")
    return 0
