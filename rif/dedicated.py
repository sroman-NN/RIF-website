from __future__ import annotations

import json
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from .errors import RIFError


@dataclass(frozen=True)
class DedicatedCompilerResult:
    plugin: str
    linked_plugins: tuple[str, ...]
    root: Path
    pack_dir: Path
    script_path: Path
    exe_path: Path | None


def _get_plugin_extension(plugin_dir: Path) -> str | None:
    if not plugin_dir.exists() or not plugin_dir.is_dir():
        return None
    for item in sorted(plugin_dir.iterdir()):
        if item.is_file() and item.name.startswith("ext."):
            ext = item.name[4:]  # starts with "ext."
            if not ext.startswith("."):
                ext = "." + ext
            return ext
    return None


def create_dedicated_compiler(
    plugin: str,
    *,
    linked_plugins: list[str] | tuple[str, ...] = (),
    pack_name: str | None = None,
    output: str | Path | None = None,
    make_exe: bool = True,
    compiler_name: str | None = None,
    target_os: str | None = None,
    target_arch: str | None = None,
) -> DedicatedCompilerResult:
    plugin = _safe_name(plugin)
    links = tuple(dict.fromkeys(_safe_name(item) for item in linked_plugins if item))

    # 1. Download/Install dependencies from requirements.txt of plugin and linked_plugins
    import rif as _rif
    plugins_dir = Path(_rif.__file__).resolve().parent / "plugins"
    for p_name in (plugin, *links):
        req_file = plugins_dir / p_name / "requirements.txt"
        if req_file.exists():
            print(f"Instalando dependencias de '{p_name}' desde {req_file.name}...")
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(req_file)], check=False)

    pack_source = _plugin_pack_dir(plugin, pack_name)

    # 2. Determine target compiler name and detect extension from ext.* files
    target_name = compiler_name or f"rif-{plugin}-compiler"
    plugin_ext = _get_plugin_extension(plugins_dir / plugin)
    if not plugin_ext:
        for link in links:
            plugin_ext = _get_plugin_extension(plugins_dir / link)
            if plugin_ext:
                break

    # 3. Setup build root directory
    root = Path(output).resolve() if output is not None else (Path.cwd() / "build" / target_name).resolve()
    root.mkdir(parents=True, exist_ok=True)
    pack_dir = root / "dedicated_pack"
    if pack_dir.exists():
        _remove_generated_dir(root, pack_dir)
    shutil.copytree(pack_source, pack_dir)

    root_pack = _root_pack_file(pack_dir, plugin)
    _ensure_plugins(root_pack, plugin, links)

    # 4. Generate the launcher script
    script_path = root / f"{target_name}.py"
    script_path.write_text(_launcher_source(plugin, links, pack_dir, plugin_ext), encoding="utf-8")

    # 5. Copy the RIF source package next to the launcher to make the directory portable/self-contained
    rif_pkg_src = Path(_rif.__file__).resolve().parent
    rif_pkg_dest = root / "rif"
    if rif_pkg_dest.exists():
        shutil.rmtree(rif_pkg_dest)
    shutil.copytree(rif_pkg_src, rif_pkg_dest, ignore=shutil.ignore_patterns("__pycache__", ".git", "cache", ".cache"))

    metadata = {
        "plugin": plugin,
        "linked_plugins": list(links),
        "pack": str(pack_dir),
        "script": str(script_path),
        "target_os": target_os,
        "target_arch": target_arch,
        "extension": plugin_ext,
    }
    (root / "compiler.json").write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # 6. Generate cross-platform execution launchers
    # Generate bash script launcher (for macOS / Linux)
    sh_launcher = root / target_name
    sh_launcher.write_text(f'#!/bin/sh\nexec python3 "$(dirname "$0")/{target_name}.py" "$@"\n', encoding="utf-8")
    try:
        sh_launcher.chmod(sh_launcher.stat().st_mode | 0o755)
    except Exception:
        pass

    # Generate batch script launcher (for Windows)
    bat_launcher = root / f"{target_name}.bat"
    bat_launcher.write_text(f'@echo off\npython "%~dp0{target_name}.py" %*\n', encoding="utf-8")

    # 7. Zip the entire portable build folder as `{target_name}-{target_os}-{target_arch}.zip` if target is specified
    if target_os and target_arch:
        import zipfile
        archive_name = root.parent / f"{target_name}-{target_os}-{target_arch}.zip"
        print(f"Creando paquete portatil autocontenido para {target_os} {target_arch} en: {archive_name}")
        with zipfile.ZipFile(archive_name, 'w', zipfile.ZIP_DEFLATED) as zf:
            for file_path in root.rglob("*"):
                if "__pycache__" in file_path.parts:
                    continue
                if file_path.is_file():
                    zf.write(file_path, file_path.relative_to(root))
        print("Paquete portatil creado con exito!")

    # 8. Check if host matches target before trying PyInstaller (or if no target is requested, we assume host target)
    host_os = "windows" if sys.platform == "win32" else "linux" if sys.platform.startswith("linux") else "macos"
    if sys.platform == "darwin":
        host_os = "macos"

    is_same_os = True
    if target_os and target_os.lower() != host_os:
        is_same_os = False

    exe_path = None
    if make_exe and is_same_os:
        exe_path = _build_exe(root, script_path, plugin, pack_dir, target_name)
    else:
        if make_exe and not is_same_os:
            print(f"Nota: Se omite PyInstaller nativo porque el target '{target_os}' es diferente del host '{host_os}'. Usa el paquete portatil .zip generado.")

    return DedicatedCompilerResult(
        plugin=plugin,
        linked_plugins=links,
        root=root,
        pack_dir=pack_dir,
        script_path=script_path,
        exe_path=exe_path,
    )


def _build_exe(root: Path, script_path: Path, plugin: str, pack_dir: Path, name: str) -> Path | None:
    import rif as _rif

    pyinstaller = shutil.which("pyinstaller")
    if pyinstaller is None:
        return None

    rif_parent = Path(_rif.__file__).resolve().parent.parent
    rif_plugins = Path(_rif.__file__).resolve().parent / "plugins"
    dist = root / "dist"
    work = root / "pyinstaller"
    add_data_sep = ";" if sys.platform == "win32" else ":"
    cmd = [
        pyinstaller,
        "--clean",
        "--noconfirm",
        "--onefile",
        "--paths",
        str(rif_parent),
        "--name",
        name,
        "--distpath",
        str(dist),
        "--workpath",
        str(work / "build"),
        "--specpath",
        str(work),
        "--collect-all",
        "rif",
        "--collect-submodules",
        "rif",
        "--hidden-import",
        "rif",
        "--hidden-import",
        "rif.errors",
        "--hidden-import",
        "rif.linker",
        "--hidden-import",
        "webbrowser",
        "--add-data",
        f"{rif_plugins}{add_data_sep}rif/plugins",
        "--add-data",
        f"{pack_dir}{add_data_sep}dedicated_pack",
        str(script_path),
    ]
    result = subprocess.run(cmd, cwd=Path.cwd(), text=True, capture_output=True, check=False)
    (root / "pyinstaller.stdout.log").write_text(result.stdout, encoding="utf-8")
    (root / "pyinstaller.stderr.log").write_text(result.stderr, encoding="utf-8")
    if result.returncode != 0:
        raise RIFError(
            f"no se pudo generar el .exe con PyInstaller; revisa {root / 'pyinstaller.stderr.log'}"
        )

    exe = dist / (name + (".exe" if sys.platform == "win32" else ""))
    return exe if exe.exists() else None


def _remove_generated_dir(root: Path, target: Path) -> None:
    root = root.resolve()
    target = target.resolve()
    try:
        target.relative_to(root)
    except ValueError as exc:
        raise RIFError(f"no se borrara una ruta fuera del compilador dedicado: {target}") from exc
    shutil.rmtree(target)


def _plugin_pack_dir(plugin: str, pack_name: str | None) -> Path:
    import rif as _rif

    plugin_root = Path(_rif.__file__).resolve().parent / "plugins" / plugin
    if not plugin_root.exists():
        raise RIFError(f"plugin no encontrado: {plugin}")

    candidates: list[Path] = []
    for base_name in ("packs", "pack"):
        if pack_name:
            candidates.append(plugin_root / base_name / pack_name)
        candidates.append(plugin_root / base_name / "example")
        candidates.append(plugin_root / base_name)

    for candidate in candidates:
        if candidate.exists() and candidate.is_dir() and any(candidate.glob("*.pack")):
            return candidate

    raise RIFError(f"no se encontro pack para plugin {plugin!r}")


def _root_pack_file(pack_dir: Path, plugin: str) -> Path:
    preferred = pack_dir / f"{plugin}.pack"
    if preferred.exists():
        return preferred
    packs = sorted(path for path in pack_dir.glob("*.pack") if path.is_file())
    if not packs:
        raise RIFError(f"pack dedicado sin archivos .pack: {pack_dir}")
    return packs[0]


def _ensure_plugins(pack_path: Path, plugin: str, links: tuple[str, ...]) -> None:
    text = pack_path.read_text(encoding="utf-8")
    wanted = tuple(dict.fromkeys((plugin, *links)))
    existing = set()
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("plugin "):
            value = stripped[len("plugin "):].strip().strip("\"'")
            if value:
                existing.add(value)

    missing = [name for name in wanted if name not in existing]
    if not missing:
        return

    lines = text.splitlines()
    insert_at = next((i for i, line in enumerate(lines) if line.strip().startswith("pluginsymbolorder")), None)
    if insert_at is None:
        insert_at = next((i + 1 for i, line in enumerate(lines) if line.strip() == ".pack"), len(lines))
    plugin_lines = [f'plugin "{name}"' for name in missing]
    lines[insert_at:insert_at] = plugin_lines
    pack_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _launcher_source(plugin: str, links: tuple[str, ...], pack_dir: Path, extension: str | None) -> str:
    import rif as _rif

    rif_parent = Path(_rif.__file__).resolve().parent.parent
    return f'''from __future__ import annotations

import argparse
import hashlib
import os
import sys
from pathlib import Path

PLUGIN = {plugin!r}
LINKED_PLUGINS = {list(links)!r}
FALLBACK_PACK_DIR = Path({str(pack_dir)!r})
FALLBACK_RIF_PARENT = Path({str(rif_parent)!r})
EXTENSION = {extension!r}


def _pack_dir() -> Path:
    bundled = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent)) / "dedicated_pack"
    if bundled.exists():
        return bundled
    return FALLBACK_PACK_DIR


def main(argv=None) -> int:
    try:
        if not getattr(sys, "frozen", False) and FALLBACK_RIF_PARENT.exists() and str(FALLBACK_RIF_PARENT) not in sys.path:
            sys.path.insert(0, str(FALLBACK_RIF_PARENT))

        from rif.errors import RIFError
        from rif.linker import Linker, build_project

        parser = argparse.ArgumentParser(prog=f"rif-{{PLUGIN}}-compiler")
        parser.add_argument("source", help="archivo de codigo, archivo .pack o carpeta de proyecto")
        parser.add_argument("-o", "--output", help="ruta de salida")
        parser.add_argument("--pack", help="pack dedicado alternativo")
        parser.add_argument("--info", action="store_true", help="muestra plugins enlazados y pack usado")
        args = parser.parse_args(argv)

        pack = Path(args.pack).resolve() if args.pack else _pack_dir()
        if args.info:
            print(f"plugin={{PLUGIN}}")
            print("linked=" + ",".join(LINKED_PLUGINS))
            print(f"pack={{pack}}")
            if EXTENSION:
                print(f"extension={{EXTENSION}}")

        source = Path(args.source)
        output = Path(args.output) if args.output else None
        if source.is_dir():
            result = build_project(source, output, write=True, use_packs_path=pack)
        elif source.suffix == ".pack":
            result = Linker(source).build_binary("", output, write=output is not None)
        else:
            text = source.read_text(encoding="utf-8")
            result = Linker(pack).build_binary(text, output, write=output is not None)

        print(f"bytes={{len(result.data)}}")
        if output is not None:
            print(f"output={{output}}")
        if len(result.data) <= 256:
            print(f"hex={{result.hex}}")
        else:
            print(f"sha256={{hashlib.sha256(result.data).hexdigest()}}")
            print(f"hex.head={{result.data[:32].hex()}}")
            print(f"hex.tail={{result.data[-32:].hex()}}")
        return 0
    except Exception as exc:
        if os.environ.get("RIF_DEBUG"):
            raise
        try:
            RIFError
        except NameError:
            is_rif_error = False
        else:
            is_rif_error = isinstance(exc, RIFError)
        prefix = "error" if is_rif_error else f"error inesperado ({{type(exc).__name__}})"
        print(f"{{prefix}}: {{exc}}", file=sys.stderr)
        print("usa RIF_DEBUG=1 para ver el traceback completo", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
'''


def _safe_name(value: str) -> str:
    name = str(value).strip()
    if not name or any(part in name for part in ("/", "\\", "..")):
        raise RIFError(f"nombre inseguro: {value!r}")
    return name
