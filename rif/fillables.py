from __future__ import annotations

import importlib.util
import inspect
import json
import re
import shlex
import sys
from dataclasses import dataclass
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

    fills = FillCollector(program, phase=phase)
    out: list[str] = []
    for raw in source.splitlines():
        stripped = raw.strip()
        if not stripped.startswith("@"):
            out.append(raw)
            continue
        expanded = expand_fillable_line(program, stripped, fillables, phase=phase, fills=fills)
        out.extend(expanded.splitlines())
    fills.write()
    return "\n".join(out) + ("\n" if source.endswith("\n") else "")


def expand_fillable_line(
    program: Program,
    stripped: str,
    fillables: dict[str, Any],
    *,
    phase: str,
    fills: "FillCollector | None" = None,
) -> str:
    call = _parse_fillable_call(stripped)
    if not call.name:
        raise PackError("fillable vacio despues de @")

    name, args = call.name, call.args
    func = fillables.get(name)
    if func is None:
        raise PackError(f'fillable no encontrado "@{name}"')

    plugin_name = getattr(func, "_rif_plugin_name", "unknown")
    context = {
        "program": program,
        "config": parse_packer_config(program),
        "source_path": program.source_path,
        "phase": phase,
        "project_path": getattr(program, "project_path", None) or getattr(program, "cache_project_path", None),
        "plugin_name": plugin_name,
        "fillable": name,
        "fill_label": call.label,
        "fills": fills,
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


@dataclass(frozen=True)
class FillableCall:
    name: str
    args: list[str]
    label: str


_FILL_LABEL_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_:-]*$")


def _parse_fillable_call(stripped: str) -> FillableCall:
    """Parsea la forma unica @args@namefunc@namelabel."""
    if not stripped.startswith("@"):
        raise PackError("fillable debe iniciar con @")

    separators = _fillable_separators(stripped)
    if len(separators) != 3 or separators[0] != 0:
        raise PackError("fillable debe usar la forma unica @args@namefunc@namelabel")

    arg_text = stripped[separators[0] + 1:separators[1]].strip()
    name_text = stripped[separators[1] + 1:separators[2]].strip()
    label = stripped[separators[2] + 1:].strip()
    name_parts = shlex.split(name_text, posix=True)
    if len(name_parts) != 1:
        raise PackError("fillable requiere exactamente una funcion entre el segundo y tercer @")
    if not label:
        raise PackError("fillable requiere namelabel despues del tercer @")
    if not _FILL_LABEL_RE.match(label):
        raise PackError(f'namelabel invalido "{label}"')
    return FillableCall(name_parts[0], shlex.split(arg_text, posix=True), label)


def _fillable_separators(text: str) -> list[int]:
    quote: str | None = None
    escape = False
    separators: list[int] = []
    for index, char in enumerate(text):
        if escape:
            escape = False
            continue
        if char == "\\":
            escape = True
            continue
        if quote is not None:
            if char == quote:
                quote = None
            continue
        if char in {"'", '"'}:
            quote = char
            continue
        if char == "@":
            separators.append(index)
    return separators


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
        from .plugin_security import validate_plugin_root
        validate_plugin_root(plugin_root)

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
                    setattr(func, "_rif_plugin_name", plugin_name)
                    out.setdefault(attr, func)
                    out.setdefault(attr[5:], func)
                    out.setdefault(attr.lower(), func)
                    out.setdefault(attr[5:].lower(), func)
    return out


class FillCollector:
    def __init__(self, program: Program | None = None, *, phase: str = "compile", project_path: str | Path | None = None):
        self.program = program
        self.phase = phase
        self.project_path = Path(project_path).resolve() if project_path else _project_root(program)
        self.records: dict[str, dict[str, dict[str, Any]]] = {}

    @property
    def path(self) -> Path:
        return self.project_path / "fills.json"

    def add(self, plugin: str, name: str, **info: Any) -> None:
        plugin_key = str(plugin or "unknown")
        fill_name = str(name or "fill")
        row = {"name": fill_name, **_jsonable(info)}
        self.records.setdefault(plugin_key, {})[fill_name] = row

    def payload(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "_meta": {
                "project": str(self.project_path),
                "phase": self.phase,
            }
        }
        for plugin, fills in sorted(self.records.items()):
            data[plugin] = dict(sorted(fills.items()))
        return data

    def write(self) -> None:
        if not self.records:
            return
        self.project_path.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.payload(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def record_fill(context: Any, plugin: str, name: str, **info: Any) -> None:
    if isinstance(context, dict) and context.get("fill_label"):
        name = str(context["fill_label"])
    collector = context.get("fills") if isinstance(context, dict) else None
    if isinstance(collector, FillCollector):
        collector.add(plugin, name, **info)
        return
    program = context.get("program") if isinstance(context, dict) else None
    project_path = context.get("project_path") if isinstance(context, dict) else None
    phase = str(context.get("phase", "compile")) if isinstance(context, dict) else "compile"
    direct = FillCollector(program, phase=phase, project_path=project_path)
    direct.add(plugin, name, **info)
    direct.write()


def _project_root(program: Program | None) -> Path:
    if program is not None:
        value = getattr(program, "project_path", None) or getattr(program, "cache_project_path", None)
        if value:
            return Path(value).resolve()
        source_path = getattr(program, "source_path", None)
        if source_path:
            return Path(source_path).resolve().parent
    return Path.cwd().resolve()


def _jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _jsonable(val) for key, val in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)
