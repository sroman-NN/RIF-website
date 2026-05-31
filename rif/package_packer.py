from __future__ import annotations

from pathlib import Path

from .errors import PackError, format_os_error
from .lexer import Lexer
from .models import PackedResult, PackerConfig, Program
from .parser import Parser, parse_packer_config


class PackagePacker:
    def __init__(self, source_path: str | Path):
        self.source_path = Path(source_path)

    def pack(self, output_path: str | Path | None = None, write: bool = True) -> PackedResult:
        if not self.source_path.exists():
            raise PackError(f"source file does not exist: {self.source_path}")

        source = self.source_path.read_text(encoding="utf-8")
        initial_program = Parser(source, self.source_path).parse()
        config = parse_packer_config(initial_program)
        output = Path(output_path) if output_path is not None else self.source_path.with_name(self.source_path.name + ".temp")

        fragments: list[Path] = []
        linked_source = source
        if config.enabled and config.fsystem != 0:
            fragments = self._find_fragments(config, initial_program)
            linked_source = self._merge(source, config, fragments)

        if write:
            try:
                output.write_text(linked_source, encoding="utf-8")
            except OSError as exc:
                raise PackError(
                    f"no se pudo escribir el archivo empaquetado en {output}: {format_os_error(exc)}. "
                    "Revisa que la ruta de salida sea valida, que su carpeta exista y que el archivo no este abierto o bloqueado."
                ) from exc

        linked_program = Parser(linked_source, output).parse()
        final_config = parse_packer_config(linked_program)
        return PackedResult(
            source_path=self.source_path,
            output_path=output,
            fragments=fragments,
            program=linked_program,
            config=final_config,
            linked_source=linked_source,
            initial_program=initial_program,
        )

    def _find_fragments(self, config: PackerConfig, program: Program) -> list[Path]:
        if config.fsystem != 1 or config.subpre is None:
            return []

        base = self.source_path.stem
        root = self.source_path.parent
        candidates = sorted(root.rglob(f"{base}.*.pack"))

        out: list[Path] = []
        for path in candidates:
            if path.resolve() == self.source_path.resolve():
                continue
            if path.name == self.source_path.name + ".temp":
                continue
            if path.suffix != ".pack":
                continue

            subprefix = self._subprefix(path, base)
            if subprefix is None:
                continue
            if config.subpre != "*" and subprefix != config.subpre:
                continue
            if subprefix not in config.prefix_to_section:
                continue

            target = config.prefix_to_section[subprefix]
            if config.defined_sections and target not in config.defined_sections:
                continue
            if subprefix in config.required_prefixes and not program.has_section(target):
                continue

            out.append(path)
        return out

    def _subprefix(self, path: Path, base: str) -> str | None:
        name = path.name
        prefix = f"{base}."
        ext = ".pack"
        if not name.startswith(prefix) or not name.endswith(ext):
            return None
        middle = name[len(prefix):-len(ext)]
        if not middle or "." in middle:
            return None
        return middle

    def _merge(self, source: str, config: PackerConfig, fragments: list[Path]) -> str:
        buckets: dict[str, list[str]] = {}
        base = self.source_path.stem

        for fragment in fragments:
            subprefix = self._subprefix(fragment, base)
            if subprefix is None:
                continue
            target = config.prefix_to_section.get(subprefix)
            if target is None:
                continue

            body = self._fragment_body(fragment, target)
            if body.strip():
                buckets.setdefault(target, []).append(body.rstrip())

        if not buckets:
            return source

        return self._append_to_sections(source, config, buckets)

    def _fragment_body(self, path: Path, target: str) -> str:
        text = path.read_text(encoding="utf-8")

        if not _contains_section_header(text):
            return text

        parsed = Parser(text, path).parse()
        section = parsed.section(target)
        if section is None:
            return ""
        return "\n".join(raw for _, raw in section.body_lines)

    def _append_to_sections(self, source: str, config: PackerConfig, buckets: dict[str, list[str]]) -> str:
        lines = source.splitlines()
        ranges = _section_ranges(lines)
        output_lines = list(lines)

        sort_key = lambda item: ranges.get(item[0], (10**12, 10**12))[1]
        for section, fragments in sorted(buckets.items(), key=sort_key, reverse=True):
            if section in ranges:
                _, end = ranges[section]
                output_lines[end:end] = [""] + _flat_fragments(fragments)
            else:
                header = _section_header(config, section)
                output_lines.extend(["", header])
                output_lines.extend(_flat_fragments(fragments))

        return "\n".join(output_lines).rstrip() + "\n"


def _contains_section_header(text: str) -> bool:
    for raw in text.splitlines():
        stripped = raw.strip()
        if stripped.startswith(".section ") or stripped == ".section":
            return True
        if _section_name_from_raw(raw) is not None:
            return True
    return False


def _section_ranges(lines: list[str]) -> dict[str, tuple[int, int]]:
    ranges: dict[str, tuple[int, int]] = {}
    current: str | None = None
    current_start = 0

    for index, raw in enumerate(lines):
        section = _section_name_from_raw(raw)
        if section is not None:
            if current is not None:
                ranges[current] = (current_start, index)
            current = section
            current_start = index

    if current is not None:
        ranges[current] = (current_start, len(lines))

    return ranges


def _section_name_from_raw(raw: str) -> str | None:
    try:
        tokens = Lexer(raw).lex_line(raw, 1)
    except Exception:
        return None
    if len(tokens) in (1, 2) and tokens[0].kind == "SECTION":
        if len(tokens) == 1 or tokens[1].kind == "BLOCK":
            return tokens[0].value
    if len(tokens) in (2, 3) and tokens[0].kind == "IDENT" and tokens[1].kind == "SECTION":
        if len(tokens) == 2 or tokens[2].kind == "BLOCK":
            return tokens[1].value
    return None


def _section_header(config: PackerConfig, section: str) -> str:
    if config.sectpre:
        return f"{config.sectpre} {section}"
    return section


def _flat_fragments(fragments: list[str]) -> list[str]:
    out: list[str] = []
    for fragment in fragments:
        out.extend(fragment.splitlines())
        out.append("")
    if out and out[-1] == "":
        out.pop()
    return out
