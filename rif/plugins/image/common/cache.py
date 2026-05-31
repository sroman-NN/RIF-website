from __future__ import annotations

from pathlib import Path
from typing import Any

from rif.plugins.cache_store import get_cached_bytes as _get_cached_bytes
from rif.plugins.cache_store import set_cached_bytes as _set_cached_bytes
from rif.plugin_security import assert_allowed_path


def image_params(image_path: str, params: dict[str, Any], *, context: Any = None) -> dict[str, Any] | None:
    path = assert_allowed_path(image_path, context=context)
    if not path.exists():
        return None
    stat = path.stat()
    return {
        "path": str(path),
        "mtime_ns": stat.st_mtime_ns,
        "size": stat.st_size,
        "params": params,
    }


def get_cached_bytes(image_path: str, params: dict[str, Any], *, context: Any = None) -> bytes | None:
    payload = image_params(image_path, params, context=context)
    if payload is None:
        return None
    return _get_cached_bytes("image", "bitmap", payload, context=context)


def set_cached_bytes(image_path: str, params: dict[str, Any], data: bytes, *, context: Any = None) -> None:
    payload = image_params(image_path, params, context=context)
    if payload is None:
        return
    _set_cached_bytes("image", "bitmap", payload, data, context=context)
