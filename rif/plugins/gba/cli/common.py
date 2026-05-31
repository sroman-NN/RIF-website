from __future__ import annotations

import json
import shutil
from pathlib import Path


CONFIG_PATH = Path.home() / ".rif" / "plugins" / "gba" / "config.json"


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


def find_emulator(name: str) -> str | None:
    candidates = [name]
    if name.lower() == "mgba":
        candidates.extend(["mGBA", "mgba", "mgba-qt", "mGBA.exe", "mgba-qt.exe"])


    for candidate in dict.fromkeys(candidates):
        found = shutil.which(candidate)
        if found:
            return found


    if name.lower() == "mgba":
        program_files = [
            Path("C:/Program Files/mGBA"),
            Path("C:/Program Files (x86)/mGBA"),
            Path("C:/mGBA")
        ]
        for pf in program_files:
            for exe in ["mGBA.exe", "mgba-qt.exe", "mgba.exe"]:
                exe_path = pf / exe
                if exe_path.exists():
                    return str(exe_path)


    path = Path(name)
    if path.exists():
        return str(path)
    return None


def add_to_system_path(directory: str) -> bool:
    """Añade el directorio al PATH del usuario de Windows si no está presente."""
    import sys
    if sys.platform != "win32":
        return False

    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment", 0, winreg.KEY_ALL_ACCESS)
        path, _ = winreg.QueryValueEx(key, "Path")


        path_list = [p.strip().rstrip("\\") for p in path.split(";")]
        clean_dir = directory.strip().rstrip("\\")

        if clean_dir not in path_list:
            new_path = path + ";" + directory if path else directory
            winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, new_path)


            import ctypes
            HWND_BROADCAST = 0xFFFF
            WM_SETTINGCHANGE = 0x001A
            SMTO_ABORTIFHUNG = 0x0002
            ctypes.windll.user32.SendMessageTimeoutW(
                HWND_BROADCAST, WM_SETTINGCHANGE, 0, "Environment", SMTO_ABORTIFHUNG, 5000, None
            )
            return True
    except Exception as e:
        print(f"Advertencia: No se pudo modificar el PATH automáticamente ({e})")

    return False
