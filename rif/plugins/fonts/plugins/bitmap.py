from __future__ import annotations

from rif import EmitChunk, EmitInstruction, Err, Expr, Line, RuleIndicator
from rif.plugins.fonts.bitmap.api import DEFAULT_FONT, cached_text_bitmap_bytes


CONTEXT = None


def _clean(value) -> str:
    if hasattr(value, "value"):
        value = value.value
    return str(value).strip()


def _args() -> tuple[str, str]:
    Line.Advance()
    pack = [_clean(item) for item in Line.Unpack(",")]
    pack = [item for item in pack if item]
    Line.toks.clear()
    Line.expects(" ", "\n")

    if not pack:
        return DEFAULT_FONT, "LOGO"
    if len(pack) == 1:
        return DEFAULT_FONT, pack[0]
    return pack[0], pack[1]


def _emit_bytes(data: bytes):
    chunks = tuple(
        EmitChunk(kind="byte", value=f"{byte:08b}", width=8, byte=byte)
        for byte in data
    )
    return Expr(["emit_bits_exact", EmitInstruction(
        mode="bits",
        chunks=chunks,
        rule_name=RuleIndicator.current,
        line=getattr(Line, "line", None),
        requires_byte=True,
    )])


def main():
    font, text = _args()
    try:
        return _emit_bytes(cached_text_bitmap_bytes(text, font=font, context=globals().get("CONTEXT")))
    except Exception as exc:
        return Err(str(exc))


def _start():
    return main()
