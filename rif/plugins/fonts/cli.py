from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
COMMANDS = ROOT / "cli"


ALIASES = {
    "fonts": "list",
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="rif -pcli fonts",
        description="SX7 bitmap font plugin tools",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("fonts", help="list available .f fonts")
    sub.add_parser("list", help="alias of fonts")

    p_modify = sub.add_parser("modify", help="modify bits of an existing glyph")
    p_modify.add_argument("file", help=".f file name or path")
    p_modify.add_argument("char", help="character, space, 0xNN or quoted literal")

    p_add = sub.add_parser("add", help="add a new glyph")
    p_add.add_argument("file", help=".f file name or path")
    p_add.add_argument("char", help="character, space, 0xNN or quoted literal")

    p_delete = sub.add_parser("delete", help="delete a glyph")
    p_delete.add_argument("file", help=".f file name or path")
    p_delete.add_argument("char", help="character, space, 0xNN or quoted literal")

    p_open = sub.add_parser("open", help="open a font in the system editor")
    p_open.add_argument("file", help=".f file name or path")

    args = parser.parse_args(argv)
    command_name = ALIASES.get(args.cmd, args.cmd)
    command = _load_command(command_name)
    return int(command.main(args) or 0)


def _load_command(name: str):
    path = COMMANDS / f"{name}.py"
    if not path.exists():
        raise SystemExit(f"cannot load fonts command: {name}")

    # Let command modules import sibling helpers as plain modules:
    #   import common
    #   import editor
    command_dir = str(COMMANDS)
    if command_dir not in sys.path:
        sys.path.insert(0, command_dir)

    # Let common.py import bitmap as a package:
    #   from bitmap.parser import ...
    root_dir = str(ROOT)
    if root_dir not in sys.path:
        sys.path.insert(0, root_dir)

    spec = importlib.util.spec_from_file_location(f"rif.fonts.cli.{name}", path)
    if spec is None or spec.loader is None:
        raise SystemExit(f"cannot load fonts command: {name}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


if __name__ == "__main__":
    raise SystemExit(main())
