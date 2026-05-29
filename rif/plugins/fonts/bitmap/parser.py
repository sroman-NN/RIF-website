from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import ast

from .lexer import FontLexerError, Token, lex_font


class FontParseError(ValueError):
    """Error sintactico o semantico en archivo .f SX7."""


@dataclass
class SX7Font:
    magic: str
    width: int
    height: int
    row_bytes: int
    align: str = "right"
    glyphs: dict[str, list[str]] = field(default_factory=dict)

    @property
    def bits_per_row(self) -> int:
        return self.row_bytes * 8

    def validate(self) -> None:
        validate_size(self.width, self.height, self.row_bytes, 0)

        if self.align not in {"right", "left"}:
            raise FontParseError("align debe ser right o left")

        for char, rows in self.glyphs.items():
            validate_glyph(char, rows, self.width, self.height)

    def get_bitmap(self, char: str, fallback: str | None = "?") -> list[str]:
        char = parse_char_label(char, 0)
        key = char

        if key not in self.glyphs and char.upper() in self.glyphs:
            key = char.upper()

        if key not in self.glyphs:
            if fallback is None:
                raise KeyError(f"Glyph no encontrado: {char!r}")

            fallback_key = parse_char_label(fallback, 0)
            if fallback_key not in self.glyphs:
                raise KeyError(f"Glyph no encontrado y fallback invalido: {fallback!r}")

            key = fallback_key

        return self.glyphs[key].copy()

    def pack_row(self, row: str) -> list[int]:
        if len(row) != self.width:
            raise FontParseError(
                f"Fila invalida: esperaba {self.width} bits, recibio {len(row)}"
            )

        if any(ch not in "01" for ch in row):
            raise FontParseError("Fila invalida: solo puede contener 0 y 1")

        if self.align == "right":
            packed_bits = row.rjust(self.bits_per_row, "0")
        elif self.align == "left":
            packed_bits = row.ljust(self.bits_per_row, "0")
        else:
            raise FontParseError(f"align invalido: {self.align!r}")

        return [
            int(packed_bits[i:i + 8], 2)
            for i in range(0, self.bits_per_row, 8)
        ]

    def unpack_row(self, row_bytes: list[int]) -> str:
        if len(row_bytes) != self.row_bytes:
            raise FontParseError(
                f"Se esperaban {self.row_bytes} byte(s), recibio {len(row_bytes)}"
            )

        for byte in row_bytes:
            if byte < 0 or byte > 255:
                raise FontParseError(f"Byte invalido: {byte}")

        bits = "".join(f"{byte:08b}" for byte in row_bytes)

        if self.align == "right":
            return bits[-self.width:]

        if self.align == "left":
            return bits[:self.width]

        raise FontParseError(f"align invalido: {self.align!r}")

    def get_row_bytes(self, char: str, fallback: str | None = "?") -> list[list[int]]:
        return [self.pack_row(row) for row in self.get_bitmap(char, fallback=fallback)]

    def get_flat_bytes(self, char: str, fallback: str | None = "?") -> list[int]:
        rows = self.get_row_bytes(char, fallback=fallback)
        return [byte for row in rows for byte in row]

    def get_ascii_entry(self, char: str, fallback: str | None = "?") -> list:
        if len(char) != 1:
            raise ValueError("Se esperaba exactamente un caracter")
        return [ord(char), self.get_flat_bytes(char, fallback=fallback)]

    def text_to_ascii_map(self, text: str, fallback: str | None = "?") -> list[list]:
        return [self.get_ascii_entry(ch, fallback=fallback) for ch in text]

    def set_glyph(self, char: str, rows: list[str]) -> None:
        key = parse_char_label(char, 0)
        validate_glyph(key, rows, self.width, self.height)
        self.glyphs[key] = rows.copy()

    def delete_glyph(self, char: str) -> None:
        key = parse_char_label(char, 0)
        if key not in self.glyphs:
            raise KeyError(f"Glyph no encontrado: {format_label(key)!r}")
        del self.glyphs[key]

    def to_text(self) -> str:
        lines: list[str] = [
            f"font {self.magic}",
            f"size {self.width}, {self.height}, {self.row_bytes}",
            f"align {self.align}",
            "",
        ]

        for char, rows in self.glyphs.items():
            lines.append(f"{format_label(char)}:")
            for row in rows:
                lines.append(f"   {row}")
            lines.append("")

        return "\n".join(lines).rstrip() + "\n"


class FontParser:
    def __init__(self, tokens: list[Token], source_name: str = "<memory>") -> None:
        self.tokens = tokens
        self.source_name = source_name
        self.pos = 0

    def parse(self) -> SX7Font:
        magic = self._parse_font_header()
        width, height, row_bytes = self._parse_size()
        align = self._parse_optional_align()

        validate_size(width, height, row_bytes, self._current().line)

        glyphs: dict[str, list[str]] = {}

        while not self._match("EOF"):
            label_token = self._expect("LABEL")
            char = parse_char_label(str(label_token.value), label_token.line)

            if char in glyphs:
                raise self._error(label_token, f"Glyph duplicado: {format_label(char)!r}")

            rows: list[str] = []
            while self._match("BIT_ROW"):
                row_token = self._advance()
                row = str(row_token.value)

                if len(row) != width:
                    raise self._error(
                        row_token,
                        f"Ancho invalido. Esperaba {width} bits, recibio {len(row)}",
                    )

                rows.append(row)

                if len(rows) > height:
                    raise self._error(
                        row_token,
                        f"Glyph {format_label(char)!r} tiene demasiadas filas",
                    )

            validate_glyph(char, rows, width, height)
            glyphs[char] = rows

        if not glyphs:
            raise FontParseError(f"{self.source_name}: la fuente no contiene glyphs")

        font = SX7Font(
            magic=magic,
            width=width,
            height=height,
            row_bytes=row_bytes,
            align=align,
            glyphs=glyphs,
        )
        font.validate()
        return font

    def _parse_font_header(self) -> str:
        self._expect("FONT")
        token = self._expect("IDENT")
        magic = str(token.value)

        if magic != "SX7":
            raise self._error(token, "La cabecera debe ser exactamente: font SX7")

        return magic

    def _parse_size(self) -> tuple[int, int, int]:
        self._expect("SIZE")
        width = int(self._expect("INT").value)
        self._expect("COMMA")
        height = int(self._expect("INT").value)
        self._expect("COMMA")
        row_bytes = int(self._expect("INT").value)
        return width, height, row_bytes

    def _parse_optional_align(self) -> str:
        if not self._match("ALIGN"):
            return "right"

        self._advance()
        token = self._expect("IDENT")
        align = str(token.value).lower()

        if align not in {"right", "left"}:
            raise self._error(token, "align debe ser right o left")

        return align

    def _current(self) -> Token:
        return self.tokens[self.pos]

    def _advance(self) -> Token:
        token = self.tokens[self.pos]
        self.pos += 1
        return token

    def _match(self, kind: str) -> bool:
        return self._current().kind == kind

    def _expect(self, kind: str) -> Token:
        token = self._current()
        if token.kind != kind:
            raise self._error(token, f"Se esperaba {kind}, recibio {token.kind}")
        return self._advance()

    def _error(self, token: Token, message: str) -> FontParseError:
        return FontParseError(f"{self.source_name}:{token.line}:{token.column}: {message}")


def validate_size(width: int, height: int, row_bytes: int, line_number: int) -> None:
    if width <= 0:
        raise FontParseError(f"Linea {line_number}: width debe ser mayor que 0")
    if height <= 0:
        raise FontParseError(f"Linea {line_number}: height debe ser mayor que 0")
    if row_bytes <= 0:
        raise FontParseError(f"Linea {line_number}: row_bytes debe ser mayor que 0")
    if width > row_bytes * 8:
        raise FontParseError(
            f"Linea {line_number}: {width} bits no caben en {row_bytes} byte(s) por fila"
        )


def validate_glyph(char: str, rows: list[str], width: int, height: int) -> None:
    if len(rows) != height:
        raise FontParseError(
            f"Glyph {format_label(char)!r} invalido: esperaba {height} filas, recibio {len(rows)}"
        )

    for idx, row in enumerate(rows):
        if len(row) != width:
            raise FontParseError(
                f"Glyph {format_label(char)!r}, fila {idx}: esperaba {width} bits, recibio {len(row)}"
            )

        if any(ch not in "01" for ch in row):
            raise FontParseError(
                f"Glyph {format_label(char)!r}, fila {idx}: solo se permiten bits 0/1"
            )


def parse_char_label(raw: str, line_number: int = 0) -> str:
    if raw == " ":
        return " "

    raw = raw.strip()

    if raw == "space":
        return " "

    if raw.startswith("0x"):
        try:
            value = int(raw, 16)
            return chr(value)
        except ValueError as exc:
            raise FontParseError(f"Linea {line_number}: codigo hexadecimal invalido") from exc

    if raw.startswith(("'", '"')):
        try:
            value = ast.literal_eval(raw)
        except Exception as exc:
            raise FontParseError(f"Linea {line_number}: string invalido") from exc

        if not isinstance(value, str) or len(value) != 1:
            raise FontParseError(f"Linea {line_number}: se esperaba un solo caracter")

        return value

    if len(raw) != 1:
        raise FontParseError(
            f"Linea {line_number}: etiqueta invalida {raw!r}. Usa A, space, 0x20 o '@'"
        )

    return raw


def format_label(char: str) -> str:
    if char == " ":
        return "space"

    safe_single = char not in {":", "\n", "\r", "\t", ";"} and not char.isspace()
    if len(char) == 1 and safe_single:
        return char

    return f"0x{ord(char):02X}"


def parse_font(text: str, source_name: str = "<memory>") -> SX7Font:
    try:
        tokens = lex_font(text, source_name=source_name)
    except FontLexerError as exc:
        raise FontParseError(str(exc)) from exc

    return FontParser(tokens, source_name=source_name).parse()


def load_font(path: str | Path) -> SX7Font:
    path = Path(path)
    return parse_font(path.read_text(encoding="utf-8"), source_name=str(path))


def save_font(path: str | Path, font: SX7Font) -> None:
    path = Path(path)
    font.validate()
    path.write_text(font.to_text(), encoding="utf-8")
