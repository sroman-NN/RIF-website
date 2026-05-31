from __future__ import annotations

import sys
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
BITMAP_DIR = PLUGIN_ROOT / "bitmap"

if str(PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(PLUGIN_ROOT))

from bitmap.parser import FontParseError, parse_char_label  


def resolve_font_path(file_name: str) -> Path:
    path = Path(file_name)

    if path.exists():
        return path.resolve()

    candidate = BITMAP_DIR / file_name
    if candidate.exists():
        return candidate.resolve()

    raise FileNotFoundError(
        f"No existe {file_name!r}. Busca por ruta directa o dentro de {BITMAP_DIR}"
    )


def parse_cli_char(raw: str) -> str:
    try:
        return parse_char_label(raw, 0)
    except FontParseError as exc:
        raise ValueError(str(exc)) from exc


def iter_font_files() -> list[Path]:
    if not BITMAP_DIR.exists():
        return []
    return sorted(BITMAP_DIR.glob("*.f"))
