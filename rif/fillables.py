from __future__ import annotations

import importlib.util
import inspect
import shlex
import sys
from pathlib import Path
from typing import Any

from .errors import PackError
from .models import Program
from .parser import _find_plugin_root, _plugin_roots, parse_packer_config


def expand_fillables(program: Program, source: str, *, phase: str = "compile") -> str:
    if "@" not in source:
        return source

    config = parse_packer_config(program)
    fillables = load_fillables(program, config)
    if not fillables:
        return source

    out: list[str] = []
    for raw in source.splitlines():
        stripped = raw.strip()
        if not stripped.startswith("@"):
            out.append(raw)
            continue
        expanded = expand_fillable_line(program, stripped, fillables, phase=phase)
        out.extend(expanded.splitlines())
    return "\n".join(out) + ("\n" if source.endswith("\n") else "")


def expand_fillable_line(
    program: Program,
    stripped: str,
    fillables: dict[str, Any],
    *,
    phase: str,
) -> str:
    parts = shlex.split(stripped[1:], posix=True)
    if not parts:
        raise PackError("fillable vacio despues de @")

    name, args = parts[0], parts[1:]
    func = fillables.get(name)
    if func is None:
        raise PackError(f'fillable no encontrado "@{name}"')

    context = {
        "program": program,
        "config": parse_packer_config(program),
        "source_path": program.source_path,
        "phase": phase,
    }
    try:
        signature = inspect.signature(func)
        if "context" in signature.parameters:
            result = func(*args, context=context)
        else:
            result = func(*args)
    except TypeError as exc:
        raise PackError(f'argumentos invalidos para "@{name}": {exc}') from exc

    if isinstance(result, (list, tuple)):
        return "\n".join(str(item) for item in result)
    return str(result)


def load_fillables(program: Program, config: Any | None = None) -> dict[str, Any]:
    if config is None:
        config = parse_packer_config(program)

    base_dir = Path.cwd()
    if program.source_path:
        base_dir = Path(program.source_path).parent

    out: dict[str, Any] = {}
    roots = _plugin_roots(base_dir)
    for plugin_name in config.plugins:
        plugin_root = _find_plugin_root(roots, plugin_name)
        if plugin_root is None:
            continue

        for extra in (plugin_root / "plugins", plugin_root):
            extra_str = str(extra)
            if extra.exists() and extra_str not in sys.path:
                sys.path.insert(0, extra_str)

        candidates = [plugin_root / "fillables.py", plugin_root / "__init__.py"]
        plugin_dir = plugin_root / "plugins"
        if plugin_dir.exists():
            candidates.extend(sorted(plugin_dir.glob("*.py")))

        for path in candidates:
            if not path.exists():
                continue
            module_name = f"rif.fillables.{plugin_name}.{path.stem}"
            spec = importlib.util.spec_from_file_location(module_name, path)
            if spec is None or spec.loader is None:
                continue
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            for attr in dir(module):
                func = getattr(module, attr)
                if attr.startswith("fill_") and callable(func):
                    out.setdefault(attr, func)
                    out.setdefault(attr[5:], func)
    return out
