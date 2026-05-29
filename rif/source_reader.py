from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .errors import PackError
from .lexer import Lexer
from .models import LexerConfig, PackerConfig, Program, Token


@dataclass(frozen=True)
class SourceEntry:
    kind: str
    text: str
    raw: str
    line: int
    section: str | None = None
    name: str | None = None
    tokens: tuple[str, ...] = ()


@dataclass(frozen=True)
class SourceReadResult:
    entries: tuple[SourceEntry, ...] = ()
    sections: tuple[str, ...] = ()

    @property
    def instructions(self) -> tuple[SourceEntry, ...]:
        return tuple(entry for entry in self.entries if entry.kind == "instruction")

    @property
    def labels(self) -> tuple[SourceEntry, ...]:
        return tuple(entry for entry in self.entries if entry.kind == "label")


class SourceReader:
    def __init__(self, program: Program, config: PackerConfig | None = None):
        self.program = program
        if config is None:
            from .parser import parse_packer_config
            config = parse_packer_config(program)
        self.config = config
        self.lexer_config = self._source_lexer_config()
        self.known_sections = self._known_sections()

    def read(self, source: str) -> SourceReadResult:
        entries: list[SourceEntry] = []
        sections: list[str] = []
        current_section: str | None = None

        for line_no, raw in enumerate(source.splitlines(), 1):
            text = self.strip_comment(raw).strip()
            if not text:
                continue

            tokens = self.lex_line(text, line_no)
            section = self.section_from_tokens(tokens)
            if section is not None:
                self._validate_section(section, line_no)
                current_section = section
                if section not in sections:
                    sections.append(section)
                entries.append(
                    SourceEntry(
                        kind="section",
                        text=text,
                        raw=raw,
                        line=line_no,
                        section=section,
                        name=section,
                        tokens=tuple(token.value for token in tokens),
                    )
                )
                continue

            label = self.label_from_tokens(tokens)
            if label is not None:
                if current_section is None:
                    raise PackError(f'etiqueta "{label}" sin sección explícita', line_no)
                entries.append(
                    SourceEntry(
                        kind="label",
                        text=text,
                        raw=raw,
                        line=line_no,
                        section=current_section,
                        name=label,
                        tokens=tuple(token.value for token in tokens),
                    )
                )
                continue

            if current_section is None:
                if self.config.source_require_section:
                    raise PackError(f'instrucción o dato fuera de sección explícita: "{text}"', line_no)
                current_section = self._default_section()

            entries.append(
                SourceEntry(
                    kind="instruction",
                    text=text,
                    raw=raw,
                    line=line_no,
                    section=current_section,
                    tokens=tuple(self.split_instruction(text)),
                )
            )

        return SourceReadResult(entries=tuple(entries), sections=tuple(sections))

    def read_path(self, path: str | Path) -> SourceReadResult:
        path = Path(path)
        if path.is_dir():
            return self.read(self.read_project_source(path))
        if path.is_file():
            return self.read(path.read_text(encoding=self.lexer_config.encoding))
        raise PackError(f"fuente de proyecto no existe: {path}")

    def read_project_source(self, root: str | Path) -> str:
        root = Path(root)
        files = self.project_files(root)
        chunks: list[str] = []
        for path in files:
            text = path.read_text(encoding=self.lexer_config.encoding)
            chunks.append(text.rstrip())
        return "\n".join(chunk for chunk in chunks if chunk) + ("\n" if chunks else "")

    def project_files(self, root: str | Path) -> tuple[Path, ...]:
        """Obtiene la lista ordenada de archivos de código fuente pertenecientes al proyecto."""
        root = Path(root)
        if not root.exists():
            raise PackError(f"carpeta de proyecto no existe: {root}")
        if not root.is_dir():
            raise PackError(f"la fuente de proyecto no es carpeta: {root}")

        code_dir = root / "code"
        search_root = code_dir if (code_dir.exists() and code_dir.is_dir()) else root

        extensions = {ext.lower() for ext in self.config.source_extensions}
        ignored = {self.config.ext.lower(), ".pack", ".temp"}
        files: list[Path] = []
        for path in sorted(search_root.rglob("*")):
            if not path.is_file():
                continue
            if any(part in {"plugins", "__pycache__"} for part in path.relative_to(search_root).parts):
                continue
            suffix = path.suffix.lower()
            if suffix in ignored:
                continue
            if suffix not in extensions:
                continue
            files.append(path)
        return tuple(files)

    def strip_comment(self, raw: str) -> str:
        comment = self.lexer_config.comment
        quote = False
        escaped = False
        out: list[str] = []
        for ch in raw:
            if escaped:
                out.append(ch)
                escaped = False
                continue
            if ch == "\\" and quote:
                out.append(ch)
                escaped = True
                continue
            if ch == '"':
                out.append(ch)
                quote = not quote
                continue
            if ch == comment and not quote:
                break
            out.append(ch)
        return "".join(out).rstrip()

    def lex_line(self, text: str, line: int) -> list[Token]:
        return Lexer("", self.lexer_config).lex_line(text, line)

    def section_from_tokens(self, tokens: list[Token]) -> str | None:
        if not tokens:
            return None

        if len(tokens) in (1, 2) and tokens[0].kind == "SECTION":
            if len(tokens) == 1 or tokens[1].kind == "BLOCK":
                return tokens[0].value

        if len(tokens) in (2, 3) and tokens[0].kind == "IDENT" and tokens[1].kind == "SECTION":
            if self.config.sectpre and tokens[0].value != self.config.sectpre:
                return None
            if len(tokens) == 2 or tokens[2].kind == "BLOCK":
                return tokens[1].value

        if len(tokens) in (2, 3) and tokens[0].value == self.config.source_section_directive and tokens[1].kind in {"IDENT", "SECTION"}:
            if len(tokens) == 2 or tokens[2].kind == "BLOCK":
                return self._normalize_section(tokens[1].value)

        return None

    def label_from_tokens(self, tokens: list[Token]) -> str | None:
        if len(tokens) == 2 and tokens[0].kind == "IDENT" and tokens[1].kind == "BLOCK":
            name = tokens[0].value
            if self._is_name(name):
                return name
        return None

    def split_instruction(self, source: str) -> list[str]:
        out: list[str] = []
        current: list[str] = []
        quote = False
        escaped = False

        def push() -> None:
            if current:
                out.append("".join(current))
                current.clear()

        for ch in source.strip():
            if escaped:
                current.append(ch)
                escaped = False
                continue
            if ch == "\\" and quote:
                escaped = True
                continue
            if ch == '"':
                quote = not quote
                continue
            if quote:
                current.append(ch)
                continue
            if ch.isspace():
                push()
                continue
            if ch in {",", "=", self.lexer_config.block}:
                push()
                out.append(ch)
                continue
            current.append(ch)
        push()
        return out

    def _known_sections(self) -> set[str]:
        table = self.program.tables.get(".sections")
        if table is None:
            return set()
        out: set[str] = set()
        for name in table.rows:
            out.add(name)
            out.add(self._normalize_section(name))
        return out

    def _validate_section(self, section: str, line: int) -> None:
        if self.config.source_validate_sections and self.known_sections and section not in self.known_sections:
            raise PackError(f'sección de fuente desconocida "{section}"', line)

    def _source_lexer_config(self) -> LexerConfig:
        return LexerConfig(
            comment=self.config.source_comment or self.program.lexer_config.comment,
            separator=self.config.source_separator or self.program.lexer_config.separator,
            block=self.config.source_block or self.program.lexer_config.block,
            encoding=self.program.lexer_config.encoding,
        )

    def _default_section(self) -> str:
        table = self.program.tables.get(".sections")
        if table is not None and table.rows:
            return self._normalize_section(next(iter(table.rows)))
        return ".text"

    def _normalize_section(self, value: str) -> str:
        text = str(value).strip()
        return text if text.startswith(".") else f".{text}"

    def _is_name(self, value: Any) -> bool:
        text = str(value)
        if not text:
            return False
        if not (text[0].isalpha() or text[0] == "_"):
            return False
        return all(ch.isalnum() or ch in "_-" for ch in text)
