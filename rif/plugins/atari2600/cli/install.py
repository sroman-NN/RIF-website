from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

from rif.plugins.atari2600.cli.common import add_to_user_path, find_emulator, save_config


def main(args) -> int:
    emulator = str(args.emulator or "Stella")
    requested_path = args.add_path

    path = ""
    if isinstance(requested_path, str):
        candidate = Path(requested_path)
        path = str(candidate) if candidate.exists() else requested_path
    else:
        path = find_emulator(emulator) or ""

    if not path:
        path = _try_install_stella() or ""

    if not path:
        save_config({"emulator": emulator, "path": ""})
        print("Stella no fue encontrada. Instala Stella o repite con --add-path RUTA")
        return 1

    save_config({"emulator": emulator, "path": path})
    print(f"{emulator} registrado: {path}")
    if requested_path:
        directory = str(Path(path).parent)
        if add_to_user_path(directory):
            print(f"Directorio {directory} anadido al PATH del usuario.")
    return 0


def _try_install_stella() -> str | None:
    if sys.platform == "win32" and shutil.which("winget"):
        package_id = _winget_stella_id()
        if package_id:
            subprocess.run(["winget", "install", "-e", "--id", package_id], check=False)
            return find_emulator("Stella")
    if sys.platform == "darwin" and shutil.which("brew"):
        subprocess.run(["brew", "install", "--cask", "stella"], check=False)
        return find_emulator("Stella")
    return None


def _winget_stella_id() -> str | None:
    result = subprocess.run(
        ["winget", "search", "Stella", "--source", "winget"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    for line in result.stdout.splitlines():
        if "Stella" not in line:
            continue
        parts = [part for part in line.split() if part]
        for part in parts:
            if "." in part and "stella" in part.lower():
                return part
    return None
