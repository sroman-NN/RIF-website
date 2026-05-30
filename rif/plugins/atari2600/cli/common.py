from __future__ import annotations

import json
import os
import shutil
from pathlib import Path


CONFIG_PATH = Path.home() / ".rif" / "plugins" / "atari2600" / "config.json"


def load_config() -> dict[str, str]:
    if not CONFIG_PATH.exists():
        return {}
    try:
        data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def save_config(data: dict[str, str]) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def find_emulator(name: str = "Stella") -> str | None:
    candidates = [name, "stella", "Stella", "Stella.exe", "stella.exe"]
    for candidate in dict.fromkeys(candidates):
        found = shutil.which(candidate)
        if found:
            return found

    if os.name == "nt":
        for base in (Path("C:/Program Files"), Path("C:/Program Files (x86)")):
            for exe in ("Stella.exe", "stella.exe"):
                found = base / "Stella" / exe
                if found.exists():
                    return str(found)

    path = Path(name)
    if path.exists():
        return str(path)
    return None


def add_to_user_path(directory: str) -> bool:
    if os.name != "nt":
        return False
    try:
        import ctypes
        import winreg

        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment", 0, winreg.KEY_ALL_ACCESS)
        current, _ = winreg.QueryValueEx(key, "Path")
        parts = [part.strip().rstrip("\\") for part in current.split(";") if part.strip()]
        clean = directory.strip().rstrip("\\")
        if clean in parts:
            return False
        updated = current + ";" + directory if current else directory
        winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, updated)
        ctypes.windll.user32.SendMessageTimeoutW(0xFFFF, 0x001A, 0, "Environment", 0x0002, 5000, None)
        return True
    except Exception:
        return False
