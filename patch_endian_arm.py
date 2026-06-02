import pathlib
path = pathlib.Path(r"c:\Users\Kentucky\Desktop\AMST\Retargetable-ISA-Foundry-RIF-\rif\plugins\gba\plugins\arm_ins.py")
content = path.read_text(encoding="utf-8")

endian_func = """
def _get_endianness() -> str:
    ctx = globals().get("CONTEXT")
    if ctx is not None and getattr(ctx, "program", None) is not None and hasattr(ctx.program, "world"):
        raw = ctx.program.world.values.get("endianness", ctx.program.world.values.get("endianess", "little"))
        if isinstance(raw, int):
            return "big" if raw else "little"
        text = str(raw).strip().lower()
        if text in {"big", "be", "1"}:
            return "big"
    return "little"

def _emit32"""

content = content.replace("def _emit32", endian_func)
content = content.replace('.to_bytes(4, "little")', '.to_bytes(4, _get_endianness())')

path.write_text(content, encoding="utf-8")
print("Done patching arm_ins.")
