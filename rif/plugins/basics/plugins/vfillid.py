from __future__ import annotations
import json
from pathlib import Path
from rif.errors import PackError

def fill_VFILLID(*args, context=None) -> str:
    if not args:
        raise PackError("@VFILLID requiere un ID de fillable")

    id_name = str(args[0]).strip()
    if _exists_in_context(id_name, context):
        return f"dw_virt {id_name}"

    program = context.get("program") if isinstance(context, dict) else None
    proj_path = None
    if program is not None:
        proj_path = getattr(program, "project_path", None) or getattr(program, "cache_project_path", None)
        if not proj_path and program.source_path:
            proj_path = Path(program.source_path).resolve().parent
    else:
        proj_path = context.get("project_path") if isinstance(context, dict) else None

    if not proj_path:
        proj_path = Path.cwd()

    fills_file = Path(proj_path).resolve() / "fills.json"
    if not fills_file.exists():
        raise PackError(f"fills.json no encontrado en {proj_path}. Asegurate de compilar los fillables de origen primero.")

    try:
        data = json.loads(fills_file.read_text(encoding="utf-8"))
    except Exception as exc:
        raise PackError(f"Error al leer fills.json: {exc}")

    found_row = None
    for k, v in data.items():
        if k == "_meta":
            continue
        if isinstance(v, dict) and id_name in v:
            found_row = v[id_name]
            break

    if found_row is None:
        raise PackError(f"El ID '{id_name}' no existe en fills.json. Revisa tus definiciones de fillables.")

    virtual = _pick_address(found_row, "virtual", "addrs", "vaddr", "voffset")
    if virtual is not None:
        return f"dw_virt 0x{virtual:X}"

    return f"dw_virt {id_name}"


def _exists_in_context(id_name: str, context=None) -> bool:
    if not isinstance(context, dict):
        return False
    fills = context.get("fills")
    records = getattr(fills, "records", None)
    if not isinstance(records, dict):
        return False
    return any(isinstance(section, dict) and id_name in section for section in records.values())


def _pick_address(row, *keys: str) -> int | None:
    if not isinstance(row, dict):
        return None
    for key in keys:
        value = row.get(key)
        if value in (None, ""):
            continue
        try:
            return int(str(value).replace("_", ""), 0)
        except (TypeError, ValueError):
            continue
    return None
