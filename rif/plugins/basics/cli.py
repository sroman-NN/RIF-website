from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
COMMANDS = ROOT / "cli"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="rif -pcli basics", description="Basics plugin tools")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_build_doc = sub.add_parser("build-doc", help="build a VSIX documentation bundle")
    p_build_doc.add_argument("project")
    p_build_doc.add_argument("-o", "--output")

    args = parser.parse_args(argv)
    command = _load_command(args.cmd.replace("-", "_"))
    return int(command.main(args) or 0)


def _load_command(name: str):
    path = COMMANDS / f"{name}.py"
    command_dir = str(COMMANDS)
    if command_dir not in sys.path:
        sys.path.insert(0, command_dir)
    spec = importlib.util.spec_from_file_location(f"rif.basics.cli.{name}", path)
    if spec is None or spec.loader is None:
        raise SystemExit(f"cannot load basics command: {name}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


if __name__ == "__main__":
    raise SystemExit(main())
