from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


def get_cached_bytes(plugin: str, kind: str, params: dict[str, Any], *, context: Any = None, program: Any = None) -> bytes | None:
    cache_file = _cache_file(plugin, kind, params, context=context, program=program)
    if cache_file.exists():
        return cache_file.read_bytes()
    return None


def set_cached_bytes(plugin: str, kind: str, params: dict[str, Any], data: bytes, *, context: Any = None, program: Any = None) -> Path:
    cache_file = _cache_file(plugin, kind, params, context=context, program=program)
    cache_file.parent.mkdir(parents=True, exist_ok=True)
    cache_file.write_bytes(data)
    return cache_file


def project_cache_root(*, context: Any = None, program: Any = None) -> Path:
    root = _project_root(context=context, program=program)
    cache = root / "cache"
    cache.mkdir(parents=True, exist_ok=True)
    marker = cache / ".id_del_cache"
    project_id = _project_id(root)
    current = _read_marker(marker)
    if current != project_id:
        marker.write_text(
            json.dumps({"project": str(root), "id": project_id}, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    return cache


def project_id(*, context: Any = None, program: Any = None) -> str:
    return _project_id(_project_root(context=context, program=program))


def _cache_file(plugin: str, kind: str, params: dict[str, Any], *, context: Any = None, program: Any = None) -> Path:
    root = project_cache_root(context=context, program=program)
    pid = project_id(context=context, program=program)
    key = _key({"project_id": pid, "plugin": plugin, "kind": kind, "params": params})
    return root / plugin / kind / f"{key}.bin"


def _key(payload: dict[str, Any]) -> str:
    raw = json.dumps(payload, sort_keys=True, default=str, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _project_root(*, context: Any = None, program: Any = None) -> Path:
    if isinstance(context, dict):
        value = context.get("project_path")
        if value:
            return Path(value).resolve()
        program = program or context.get("program")
    elif context is not None:
        value = getattr(context, "project_path", None)
        if value:
            return Path(value).resolve()
        program = program or getattr(context, "program", None)

    if program is not None:
        value = getattr(program, "project_path", None) or getattr(program, "cache_project_path", None)
        if value:
            return Path(value).resolve()
        source_path = getattr(program, "source_path", None)
        if source_path:
            return Path(source_path).resolve().parent

    return Path.cwd().resolve()


def _project_id(root: Path) -> str:
    return hashlib.sha256(str(root).encode("utf-8")).hexdigest()[:16]


def _read_marker(path: Path) -> str | None:
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    value = data.get("id")
    return str(value) if value else None
