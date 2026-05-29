from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from rif.plugins.gba.cli.common import find_emulator, load_config


def main(args) -> int:
    rom = Path(args.rom)
    if not rom.exists():
        print(f"ROM no encontrada: {rom}")
        return 1

    config = load_config()
    emulator = config.get("emulator", "mGBA")
    emulator_path = config.get("path") or find_emulator(emulator)
    command_path = emulator_path or emulator

    command = [command_path, str(rom)]
    if args.dry_run:
        if args.no_duplicate:
            print("no-duplicate " + " ".join(command))
            return 0
        print(" ".join(command))
        return 0

    if not emulator_path:
        print("mGBA no esta configurado; usa: rif -pcli gba install mGBA --add-path")
        return 1

    if args.no_duplicate and _is_mgba_running():
        if _open_in_existing_window(rom):
            print(f"reusando ventana mGBA: {rom}")
            return 0
        print("no se pudo reusar la ventana existente de mGBA")
        return 1

    subprocess.Popen(command)
    print(f"ejecutando {rom}")
    return 0


def _is_mgba_running() -> bool:
    if os.name == "nt":
        result = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq mGBA.exe", "/FO", "CSV", "/NH"],
            capture_output=True,
            text=True,
            check=False,
        )
        output = result.stdout.lower()
        if "mgba.exe" in output:
            return True
        result = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq mgba-qt.exe", "/FO", "CSV", "/NH"],
            capture_output=True,
            text=True,
            check=False,
        )
        return "mgba-qt.exe" in result.stdout.lower()

    result = subprocess.run(["pgrep", "-f", "mgba"], capture_output=True, text=True, check=False)
    return result.returncode == 0


def _open_in_existing_window(rom: Path) -> bool:
    if os.name != "nt":
        return False

    script = f"""
$ErrorActionPreference = 'Stop'
$rom = @'
{rom.resolve()}
'@
$shell = New-Object -ComObject WScript.Shell
if (-not $shell.AppActivate('mGBA')) {{ exit 2 }}
Add-Type -AssemblyName System.Windows.Forms
$old = [System.Windows.Forms.Clipboard]::GetText()
[System.Windows.Forms.Clipboard]::SetText($rom)
Start-Sleep -Milliseconds 120
$shell.SendKeys('^o')
Start-Sleep -Milliseconds 350
$shell.SendKeys('^v')
Start-Sleep -Milliseconds 80
$shell.SendKeys('{{ENTER}}')
Start-Sleep -Milliseconds 80
[System.Windows.Forms.Clipboard]::SetText($old)
"""
    powershell = "powershell.exe" if sys.platform == "win32" else "powershell"
    result = subprocess.run(
        [powershell, "-STA", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode == 0
