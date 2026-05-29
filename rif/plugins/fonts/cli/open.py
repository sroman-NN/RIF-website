from __future__ import annotations

import os
import platform
import subprocess

from common import resolve_font_path


def main(args) -> int:
    return open_font_file(args.file)


def open_font_file(file_name: str) -> int:
    path = resolve_font_path(file_name)
    system = platform.system().lower()

    if system == "windows":
        subprocess.Popen(["notepad.exe", str(path)])
        print(f"Abierto en Bloc de notas: {path}")
        return 0

    if system == "darwin":
        subprocess.Popen(["open", str(path)])
        print(f"Abierto: {path}")
        return 0

    editor = os.environ.get("EDITOR")
    if editor:
        subprocess.Popen([editor, str(path)])
        print(f"Abierto con {editor}: {path}")
        return 0

    subprocess.Popen(["xdg-open", str(path)])
    print(f"Abierto: {path}")
    return 0
