

from __future__ import annotations

import re
from typing import Any

from rif import (
    EmitChunk,
    EmitInstruction,
    Err,
    Expr,
    Line,
    Operator,
    Operators,
    RuleIndicator,
    TYPES_MAP,
)

_BITS_RE = re.compile(r"^[01]+$")
_IDENT_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_:-]*$")
_PLACEHOLDER_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_:-]*)\.([A-Za-z_][A-Za-z0-9_]*)$")
_FIXED_WIDTHS = {
    "cmbit": 4,
    "cbit": 8,
    "ccbit": 16,
    "cdbit": 32,
    "cebit": 64,
}
_MODES = {"bits", "cbits", *_FIXED_WIDTHS}


def _clean(value: Any) -> str:
    if hasattr(value, "value"):
        value = value.value
    return str(value).strip()


def _section_for_type(type_ref: Any) -> str | None:
    """Convierte una referencia de tipo en sección verificable, si aplica."""
    name = _clean(type_ref)


    if name == "SYMBOL":
        return None


    if name == ".regs.subs":
        return ".regs"

    if name.startswith("."):
        return name

    mapped = TYPES_MAP.get(name)
    if mapped is None:
        return None

    mapped_name = _clean(mapped)
    if mapped_name == ".regs.subs":
        return ".regs"
    if mapped_name.startswith("."):
        return mapped_name
    return None


def _validate_placeholder(target: str, field: str) -> Err | None:
    binding = Operator.Binding(target, RuleIndicator.current)
    if binding is None:
        return Err(f'Placeholder desconocido "{target}.{field}". "{target}" no fue capturado por need')

    program = Operators.program
    if program is None:
        return None

    checked_sections: set[str] = set()
    missing: list[str] = []

    for type_ref in binding.valid_types:
        section_name = _section_for_type(type_ref)
        if not section_name or section_name in checked_sections:
            continue
        checked_sections.add(section_name)

        table = program.tables.get(section_name)
        if table is None:

            continue
        if field not in table.fields:
            missing.append(section_name)

    if missing:
        sections = ", ".join(sorted(missing))
        return Err(f'El placeholder "{target}.{field}" requiere el campo "{field}" en: {sections}')

    return None


def _parse_chunk(token: str) -> EmitChunk | Err:
    if _BITS_RE.match(token):
        return EmitChunk(kind="bits", value=token, width=len(token))

    program = Operators.program
    if program is not None and token in getattr(program, "vars", {}):
        bit_var = program.vars[token]
        return EmitChunk(kind="bits", value=bit_var.bits, width=bit_var.width)

    match = _PLACEHOLDER_RE.match(token)
    if match:
        target, field = match.groups()
        error = _validate_placeholder(target, field)
        if error is not None:
            return error
        return EmitChunk(
            kind="placeholder",
            value=token,
            target=target,
            field=field,
            width=None,
        )

    if _IDENT_RE.match(token):
        return EmitChunk(kind="bits_ref", value=token, width=None)

    return Err(f'Fragmento inválido para emit: "{token}"')


def _compact_static_byte(chunks: list[EmitChunk]) -> list[EmitChunk]:
    if any(chunk.kind != "bits" for chunk in chunks):
        return chunks

    bits = "".join(chunk.value for chunk in chunks)
    if len(bits) != 8:
        return chunks

    return [EmitChunk(kind="byte", value=bits, width=8, byte=int(bits, 2))]


def main():
    if Line.elements <= 1:
        return Err("Se esperaba al menos un fragmento de bits")

    Line.Advance()  

    mode = "bits"
    first = Line.Peek()
    if first in _MODES:
        mode = _clean(Line.Advance())

    raw_chunks = [_clean(item) for item in Line.toks if _clean(item) != ","]
    Line.toks.clear()
    Line.expects(" ", "\n")

    if not raw_chunks:
        return Err("Se esperaba al menos un fragmento de bits")

    chunks: list[EmitChunk] = []
    known_width = 0
    has_dynamic = False

    for token in raw_chunks:
        if not token:
            return Err("emit no permite fragmentos vacíos")

        chunk = _parse_chunk(token)
        if isinstance(chunk, Err):
            return chunk

        chunks.append(chunk)
        if chunk.kind == "bits":
            known_width += chunk.width or 0
        else:
            has_dynamic = True

    fixed_width = _FIXED_WIDTHS.get(mode)

    if fixed_width is not None and not has_dynamic and known_width != fixed_width:
        return Err(f"emit {mode} requiere exactamente {fixed_width} bits; recibió {known_width}")

    if fixed_width == 8:
        chunks = _compact_static_byte(chunks)

    instruction = EmitInstruction(
        mode=mode,
        chunks=tuple(chunks),
        rule_name=RuleIndicator.current,
        line=getattr(Line, "line", None),
        requires_byte=False,
    )

    return Expr(["emit_bits_exact", instruction])


def _start():
    return main()
