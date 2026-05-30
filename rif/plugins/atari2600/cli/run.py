from __future__ import annotations

import subprocess
from pathlib import Path

from rif.plugins.atari2600.cli.common import find_emulator, load_config


def main(args) -> int:
    rom = Path(args.rom)
    if not rom.exists():
        print(f"ROM no encontrada: {rom}")
        return 1

    config = load_config()
    emulator = config.get("emulator", "Stella")
    emulator_path = config.get("path") or find_emulator(emulator)
    command_path = emulator_path or emulator
    command = [command_path, str(rom)]

    if args.dry_run:
        print(" ".join(command))
        return 0

    if not emulator_path:
        print("Stella no esta configurado; usa: rif -pcli atari2600 install Stella --add-path")
        return 1

    subprocess.Popen(command)
    print(f"ejecutando {rom}")
    return 0
