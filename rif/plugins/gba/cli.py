from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
COMMANDS = ROOT / "cli"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="rif -pcli gba", description="GBA plugin tools")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_install = sub.add_parser("install", help="register an emulator")
    p_install.add_argument("emulator", help="emulator name, for example mGBA")
    p_install.add_argument("--add-path", nargs="?", const=True, default=False)

    p_run = sub.add_parser("run", help="run a GBA ROM")
    p_run.add_argument("rom")
    p_run.add_argument("-nd", "--no-duplicate", action="store_true")
    p_run.add_argument("--dry-run", action="store_true")

    args = parser.parse_args(argv)
    command = _load_command(args.cmd)
    return int(command.main(args) or 0)


def _load_command(name: str):
    path = COMMANDS / f"{name}.py"
    command_dir = str(COMMANDS)
    if command_dir not in sys.path:
        sys.path.insert(0, command_dir)
    spec = importlib.util.spec_from_file_location(f"rif.gba.cli.{name}", path)
    if spec is None or spec.loader is None:
        raise SystemExit(f"cannot load GBA command: {name}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


if __name__ == "__main__":
    raise SystemExit(main())
