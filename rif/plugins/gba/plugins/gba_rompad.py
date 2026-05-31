from __future__ import annotations

from rif.plugins.gba.plugins.gba_common import emit_bytes

CONTEXT = None

MIN_ROM_SIZE = 0x00020000       
MAX_ROM_SIZE = 0x02000000       


def _current_byte() -> int:
    ctx = globals().get("CONTEXT")
    rt = getattr(ctx, "runtime", None)
    if rt is None:
        return 0
    current_bits = int(getattr(rt, "base_offset_bits", 0)) + len(getattr(rt, "bits", ""))
    if current_bits % 8:
        raise ValueError("gba_rompad requiere posicion alineada a byte")
    return current_bits // 8


def _next_rom_size(used: int) -> int:
    """Devuelve el tamano de ROM GBA donde cabe `used`.

    GBA no esta limitada a 128 KiB. 128 KiB es solo un minimo util para ROMs
    pequenas; si el ejemplo incluye framebuffers, tiles, musica o mas codigo,
    el padding debe subir al siguiente tamano potencia de dos.
    """
    size = MIN_ROM_SIZE
    while size < used:
        size <<= 1
    return size


def main():
    if getattr(globals().get("CONTEXT"), "phase", None) == "parse":
        return None

    used = _current_byte()
    target = _next_rom_size(used)

    if target > MAX_ROM_SIZE:
        from rif import Err
        return Err(
            f"ROM GBA excede el limite de {MAX_ROM_SIZE} bytes antes de rompad: {used}"
        )

    return emit_bytes(b"\x00" * (target - used))


def _start():
    return main()
