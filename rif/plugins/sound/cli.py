import argparse
import sys
from rif.plugins.sound.cli.convert import register_convert_command, handle_convert_command
from rif.plugins.sound.cli.install import register_install_command, handle_install_command

def main(argv: list[str] | None = None) -> int:
    """Entry point for the RIF plugin CLI for sound."""
    parser = argparse.ArgumentParser(
        prog="rif -pcli sound",
        description="Sound plugin tools for RIF",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    register_convert_command(sub)
    register_install_command(sub)

    args = parser.parse_args(argv)
    
    if args.cmd == "convert":
        return handle_convert_command(args)
    elif args.cmd == "install":
        return handle_install_command(args)
        
    return 0
