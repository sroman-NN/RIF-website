from __future__ import annotations
import json
from pathlib import Path
from rif.errors import PackError

def fill_FILLID(*args, context=None) -> str:
    if not args:
        raise PackError("@FILLID requiere un ID de fillable")

    id_name = str(args[0]).strip()
    if _exists_in_context(id_name, context):
        return f"dw_phys {id_name}"

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

    found = False
    for k, v in data.items():
        if k == "_meta":
            continue
        if isinstance(v, dict) and id_name in v:
            found = True
            break

    if not found:
        raise PackError(f"El ID '{id_name}' no existe en fills.json. Revisa tus definiciones de fillables.")

    return f"dw_phys {id_name}"


def _exists_in_context(id_name: str, context=None) -> bool:
    if not isinstance(context, dict):
        return False
    fills = context.get("fills")
    records = getattr(fills, "records", None)
    if not isinstance(records, dict):
        return False
    return any(isinstance(section, dict) and id_name in section for section in records.values())
