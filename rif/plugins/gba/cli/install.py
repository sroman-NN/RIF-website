from __future__ import annotations

from pathlib import Path

from rif.plugins.gba.cli.common import find_emulator, save_config, add_to_system_path


def main(args) -> int:
    emulator = str(args.emulator)
    requested_path = args.add_path
    path = ""

    if isinstance(requested_path, str):
        candidate = Path(requested_path)
        path = str(candidate) if candidate.exists() else requested_path
    elif requested_path:
        path = find_emulator(emulator) or ""

    save_config({"emulator": emulator, "path": path})

    if path:
        print(f"{emulator} registrado: {path}")
        if requested_path:
            dir_path = str(Path(path).parent)
            if add_to_system_path(dir_path):
                print(f"Directorio {dir_path} añadido al PATH correctamente.")
            else:
                print(f"Directorio {dir_path} ya estaba en el PATH o no se pudo añadir.")
    else:
        print(f"{emulator} registrado sin ruta; agrega el ejecutable al PATH o repite con --add-path RUTA")
    return 0
