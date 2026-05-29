from __future__ import annotations

from dataclasses import dataclass


class FontLexerError(SyntaxError):
    """Error lexico en archivo .f de SX7."""


@dataclass(frozen=True)
class Token:
    kind: str
    value: object
    line: int
    column: int
    raw: str = ""

    def describe(self) -> str:
        return f"{self.kind}({self.value!r}) at {self.line}:{self.column}"


class FontLexer:
    """
    Lexer para fuentes bitmap SX7.

    Formato soportado:
        font SX7
        size 5, 7, 1 ; width bits, height rows, row bytes
        align right

        A:
           01110
           10001
    """

    def __init__(self, text: str, source_name: str = "<memory>") -> None:
        self.text = text
        self.source_name = source_name

    def tokenize(self) -> list[Token]:
        tokens: list[Token] = []
        lines = self.text.splitlines()

        for line_no, original in enumerate(lines, start=1):
            uncommented = self._strip_comment(original)
            stripped = uncommented.strip()

            if not stripped:
                continue

            column = self._first_non_space_column(uncommented)
            lower = stripped.lower()

            if lower.startswith("font"):
                tokens.extend(self._lex_font(stripped, line_no, column))
                continue

            if lower.startswith("size"):
                tokens.extend(self._lex_size(stripped, line_no, column))
                continue

            if lower.startswith("align"):
                tokens.extend(self._lex_align(stripped, line_no, column))
                continue

            if stripped.endswith(":"):
                label = stripped[:-1].strip()
                if not label:
                    raise self._error(line_no, column, "Etiqueta vacia")
                tokens.append(Token("LABEL", label, line_no, column, stripped))
                continue

            row = self._normalize_bit_row(stripped)
            if row is not None:
                tokens.append(Token("BIT_ROW", row, line_no, column, stripped))
                continue

            raise self._error(line_no, column, f"Linea invalida: {stripped!r}")

        tokens.append(Token("EOF", None, len(lines) + 1, 1, ""))
        return tokens

    def _lex_font(self, stripped: str, line_no: int, column: int) -> list[Token]:
        parts = stripped.split()
        if len(parts) != 2 or parts[0].lower() != "font":
            raise self._error(line_no, column, "Declaracion font invalida. Usa: font SX7")

        return [
            Token("FONT", "font", line_no, column, stripped),
            Token("IDENT", parts[1], line_no, column + stripped.find(parts[1]), stripped),
        ]

    def _lex_align(self, stripped: str, line_no: int, column: int) -> list[Token]:
        parts = stripped.split()
        if len(parts) != 2 or parts[0].lower() != "align":
            raise self._error(line_no, column, "Declaracion align invalida. Usa: align right")

        return [
            Token("ALIGN", "align", line_no, column, stripped),
            Token("IDENT", parts[1], line_no, column + stripped.find(parts[1]), stripped),
        ]

    def _lex_size(self, stripped: str, line_no: int, column: int) -> list[Token]:
        rest = stripped[4:].strip()
        if not rest or stripped[:4].lower() != "size":
            raise self._error(line_no, column, "size requiere ancho, alto y bytes por fila")

        tokens = [Token("SIZE", "size", line_no, column, stripped)]
        i = 0

        while i < len(rest):
            ch = rest[i]

            if ch.isspace():
                i += 1
                continue

            absolute_column = column + 5 + i

            if ch == ",":
                tokens.append(Token("COMMA", ",", line_no, absolute_column, stripped))
                i += 1
                continue

            if ch.isdigit():
                start = i
                while i < len(rest) and rest[i].isdigit():
                    i += 1
                raw_int = rest[start:i]
                tokens.append(Token("INT", int(raw_int), line_no, absolute_column, stripped))
                continue

            raise self._error(line_no, absolute_column, f"Caracter invalido en size: {ch!r}")

        return tokens

    def _normalize_bit_row(self, stripped: str) -> str | None:
        row = stripped.replace(" ", "").replace("_", "").replace("\t", "")
        if not row:
            return None
        return row if all(ch in "01" for ch in row) else None

    def _strip_comment(self, line: str) -> str:
        index = line.find(";")
        return line.rstrip() if index == -1 else line[:index].rstrip()

    def _first_non_space_column(self, line: str) -> int:
        for idx, ch in enumerate(line):
            if not ch.isspace():
                return idx + 1
        return 1

    def _error(self, line: int, column: int, message: str) -> FontLexerError:
        return FontLexerError(f"{self.source_name}:{line}:{column}: {message}")


def lex_font(text: str, source_name: str = "<memory>") -> list[Token]:
    return FontLexer(text, source_name=source_name).tokenize()
