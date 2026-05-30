from __future__ import annotations

from rif.plugins.gba.plugins.gba_common import SCREEN_W, SCREEN_H, COLORS, make_frame


def fill_screen(color: str = "black", symbol: str = "screen_data", *_args, context=None) -> str:
    """Genera un array con los pixels de la pantalla rellenos de un color BGR555."""
    col_val = COLORS.get(color.lower(), 0x0000)
    data = bytearray()
    for _ in range(SCREEN_W * SCREEN_H):
        data.extend(col_val.to_bytes(2, "little"))
    return f"{symbol} bitmap[{len(data)}] = 0x{data.hex()}"


def fill_screen_text(text: str = "HELLO", fg: str = "white", bg: str = "green",
                     symbol: str = "screen_frame", *_args, context=None) -> str:
    """Genera un frame de pantalla GBA con texto centrado dibujado en bitmap 5x7."""
    fg_val = COLORS.get(fg.lower(), 0x7FFF)
    bg_val = COLORS.get(bg.lower(), 0x03E0)
    data = make_frame(text, background=bg_val, foreground=fg_val)
    return f"{symbol} bitmap[{len(data)}] = 0x{data.hex()}"


def _start():
    return None
