from __future__ import annotations

from rif import EmitChunk, EmitInstruction, Expr, Line, RuleIndicator


ROM_SIZE = 0x4000
STACK_TOP = 0x00FF0000


def emit_bytes(data: bytes):
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


def field(text: str, size: int) -> bytes:
    return text.encode("ascii", "ignore")[:size].ljust(size, b" ")


def u32(value: int) -> bytes:
    return int(value & 0xFFFFFFFF).to_bytes(4, "big")


def make_header(checksum: int = 0x8B7D) -> bytes:
    header = bytearray(b" " * 0x100)
    header[0x00:0x10] = field("SEGA MEGA DRIVE", 0x10)
    header[0x10:0x20] = field("(C)RIF 2026.JUN", 0x10)
    header[0x20:0x50] = field("RIF MEGA DRIVE EXAMPLE", 0x30)
    header[0x50:0x80] = field("RIF MEGA DRIVE EXAMPLE", 0x30)
    header[0x80:0x8E] = field("GM RIF00000000", 0x0E)
    header[0x8E:0x90] = int(checksum & 0xFFFF).to_bytes(2, "big")
    header[0x90:0xA0] = field("J", 0x10)
    header[0xA0:0xA4] = u32(0x00000000)
    header[0xA4:0xA8] = u32(ROM_SIZE - 1)
    header[0xA8:0xAC] = u32(0x00FF0000)
    header[0xAC:0xB0] = u32(0x00FFFFFF)
    header[0xB0:0xBC] = field("", 0x0C)
    header[0xBC:0xC8] = field("", 0x0C)
    header[0xC8:0xF0] = field("RIF GENERATED MEGA DRIVE ROM", 0x28)
    header[0xF0:0x100] = field("JUE", 0x10)
    return bytes(header)
