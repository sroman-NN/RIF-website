from __future__ import annotations

import ast
import json
import re
import shutil
import subprocess
import sys
import tempfile
import webbrowser
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .errors import PackError, RIFError


MANIFEST = "pack.json"
PURPOSE_MIN = 200
PURPOSE_MAX = 2000
REQUIRED_FIELDS = ("name", "version", "author", "purpose")
OPTIONAL_FIELDS = ("architecture", "license")
BLOCKED_IMPORTS = {
    "ctypes",
    "ftplib",
    "http",
    "os",
    "requests",
    "shutil",
    "socket",
    "subprocess",
    "urllib",
}
BLOCKED_CALLS = {
    "eval",
    "exec",
    "open",
    "__import__",
    "compile",
    "input",
}
BLOCKED_ATTR_CALLS = {
    "os.remove",
    "os.rmdir",
    "os.removedirs",
    "os.rename",
    "os.replace",
    "os.startfile",
    "os.system",
    "os.unlink",
    "Path.unlink",
    "Path.rmdir",
    "shutil.move",
    "shutil.rmtree",
    "subprocess.Popen",
    "subprocess.call",
    "subprocess.check_call",
    "subprocess.check_output",
    "subprocess.run",
}
BLOCKED_NAMES = {
    "Remove-Item",
    "rm",
    "rmdir",
}
BLOCKED_NAME_RE = re.compile(r"(?<![A-Za-z0-9_-])Remove-Item(?![A-Za-z0-9_-])|(?<![A-Za-z0-9_-])rm\s+-|(?<![A-Za-z0-9_-])rmdir\s+")
PLUGIN_NAME_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_-]*$")


@dataclass(frozen=True)
class PluginManifest:
    name: str
    version: str
    author: str
    purpose: str
    architecture: str = ""
    license: str = ""
    path: Path | None = None

    @property
    def public_info(self) -> dict[str, str]:
        out = {
            "name": self.name,
            "version": self.version,
            "author": self.author,
        }
        if self.architecture:
            out["architecture"] = self.architecture
        if self.license:
            out["license"] = self.license
        return out


def load_manifest(plugin_root: Path) -> PluginManifest:
    path = plugin_root / MANIFEST
    if not path.exists():
        raise PackError(f'plugin "{plugin_root.name}" no tiene {MANIFEST} obligatorio')
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise PackError(f"{path} no es JSON valido: {exc}") from exc
    if not isinstance(raw, dict):
        raise PackError(f"{path} debe contener un objeto JSON")

    for field in REQUIRED_FIELDS:
        value = raw.get(field)
        if not isinstance(value, str) or not value.strip():
            raise PackError(f'{path} requiere campo "{field}" no vacio')

    name = raw["name"].strip()
    if not PLUGIN_NAME_RE.match(name):
        raise PackError(f'{path} tiene name inseguro: "{name}"')
    if name != plugin_root.name:
        raise PackError(f'{path} name="{name}" no coincide con carpeta "{plugin_root.name}"')

    purpose = raw["purpose"].strip()
    if not PURPOSE_MIN <= len(purpose) <= PURPOSE_MAX:
        raise PackError(f'{path} requiere purpose entre {PURPOSE_MIN} y {PURPOSE_MAX} caracteres')

    return PluginManifest(
        name=name,
        version=raw["version"].strip(),
        author=raw["author"].strip(),
        purpose=purpose,
        architecture=str(raw.get("architecture") or "").strip(),
        license=str(raw.get("license") or "").strip(),
        path=path,
    )


def validate_plugin_root(plugin_root: Path, *, require_manifest: bool = True) -> PluginManifest | None:
    manifest = load_manifest(plugin_root) if require_manifest else None
    validate_plugin_sandbox(plugin_root)
    return manifest


def validate_plugin_sandbox(plugin_root: Path) -> None:
    for path in _sandboxed_python_files(plugin_root):
        _validate_python_file(path)


def install_plugin_package(package: str, plugins_dir: Path) -> Path:
    src = _fetch_package(package)
    manifest = load_manifest(src)
    validate_plugin_root(src)
    plugins_dir.mkdir(parents=True, exist_ok=True)
    dest = plugins_dir / manifest.name
    if dest.exists():
        raise RIFError(f"plugin '{manifest.name}' ya existe en {dest}")
    shutil.copytree(src, dest, ignore=shutil.ignore_patterns("__pycache__", ".git", "cache", ".cache"))
    req = dest / "requirements.txt"
    if req.exists():
        print(f"Instalando dependencias de plugin '{manifest.name}' desde {req.name}...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(req)], check=False)
    return dest


def install_plugin_folder(src: Path, plugins_dir: Path) -> Path:
    if not src.exists() or not src.is_dir():
        raise RIFError(f"ruta de plugin no valida o no es un directorio: {src}")
    manifest = load_manifest(src)
    validate_plugin_root(src)
    plugins_dir.mkdir(parents=True, exist_ok=True)
    dest = plugins_dir / manifest.name
    if dest.exists():
        raise RIFError(f"plugin '{manifest.name}' ya existe en {dest}")
    shutil.copytree(src, dest, ignore=shutil.ignore_patterns("__pycache__", ".git", "cache", ".cache"))
    req = dest / "requirements.txt"
    if req.exists():
        print(f"Instalando dependencias de plugin '{manifest.name}' desde {req.name}...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(req)], check=False)
    return dest


def plugin_purpose_path() -> Path:
    import rif

    return Path(rif.__file__).parent / "purpose.txt"


def write_global_purpose(manifest: PluginManifest) -> Path:
    path = plugin_purpose_path()
    path.write_text(manifest.purpose.rstrip() + "\n", encoding="utf-8")
    return path


def open_path(path: Path) -> None:
    resolved = path.resolve()
    try:
        webbrowser.open(f"file:///{str(resolved).replace(chr(92), '/')}")
    except Exception:
        print(resolved)


def open_text_file(path: Path) -> None:
    resolved = path.resolve()
    if sys.platform == "win32":
        try:
            subprocess.Popen(["notepad.exe", str(resolved)])
            return
        except Exception:
            pass
    open_path(resolved)


def assert_allowed_path(path: str | Path, *, context: Any = None, program: Any = None) -> Path:
    raw = Path(path)
    project = _project_root(context=context, program=program)
    if not raw.is_absolute() and project is not None:
        candidate = (project / raw).resolve()
        if candidate.exists():
            resolved = candidate
        else:
            resolved = raw.resolve()
    else:
        resolved = raw.resolve()
    roots = allowed_roots(context=context, program=program)
    if any(_is_relative_to(resolved, root) for root in roots):
        return resolved
    formatted = ", ".join(str(root) for root in roots)
    raise PackError(f"ruta fuera del sandbox RIF: {resolved}. Permitidas: {formatted}")


def allowed_roots(*, context: Any = None, program: Any = None) -> tuple[Path, ...]:
    import rif

    roots: list[Path] = [Path.cwd().resolve(), Path(rif.__file__).resolve().parent]
    project = _project_root(context=context, program=program)
    if project is not None:
        roots.insert(0, project)
    out: list[Path] = []
    for root in roots:
        resolved = root.resolve()
        if resolved not in out:
            out.append(resolved)
    return tuple(out)


def _fetch_package(package: str) -> Path:
    value = str(package).strip()
    path = Path(value)
    if path.exists():
        return path.resolve()
    if not value.startswith(("https://github.com/", "http://github.com/", "git@github.com:")):
        raise RIFError("rif install --package solo acepta rutas locales o repositorios GitHub")

    target = Path(tempfile.mkdtemp(prefix="rif_plugin_")) / "package"
    result = subprocess.run(["git", "clone", "--depth", "1", value, str(target)], capture_output=True, text=True, check=False)
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "").strip()
        raise RIFError(f"no se pudo clonar el paquete: {detail}")
    return target


def _sandboxed_python_files(plugin_root: Path) -> list[Path]:
    out: list[Path] = []
    for name in ("fillables.py", "compiler.py", "__init__.py"):
        path = plugin_root / name
        if path.exists():
            out.append(path)
    plugin_dir = plugin_root / "plugins"
    if plugin_dir.exists():
        out.extend(path for path in plugin_dir.rglob("*.py") if "__pycache__" not in path.parts)
    return out


def _validate_python_file(path: Path) -> None:
    source = path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError as exc:
        raise PackError(f"plugin sandbox: {path} tiene sintaxis invalida: {exc}") from exc

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                _check_import(path, alias.name, node.lineno)
        elif isinstance(node, ast.ImportFrom):
            _check_import(path, node.module or "", node.lineno)
        elif isinstance(node, ast.Call):
            _check_call(path, node)
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            match = BLOCKED_NAME_RE.search(node.value)
            if match:
                raise PackError(f"plugin sandbox: {path}:{node.lineno} contiene comando bloqueado {match.group(0)!r}")


def _check_import(path: Path, module: str, line: int) -> None:
    root = module.split(".", 1)[0]
    if root in BLOCKED_IMPORTS:
        raise PackError(f"plugin sandbox: {path}:{line} import bloqueado: {module}")


def _check_call(path: Path, node: ast.Call) -> None:
    name = _call_name(node.func)
    if not name:
        return
    if isinstance(node.func, ast.Name) and name in BLOCKED_CALLS:
        raise PackError(f"plugin sandbox: {path}:{node.lineno} llamada bloqueada: {name}")
    if name in BLOCKED_ATTR_CALLS:
        raise PackError(f"plugin sandbox: {path}:{node.lineno} llamada bloqueada: {name}")


def _call_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        base = _call_name(node.value)
        if base:
            return f"{base}.{node.attr}"
        return node.attr
    return ""


def _project_root(*, context: Any = None, program: Any = None) -> Path | None:
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
    return None


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False
