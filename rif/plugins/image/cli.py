import argparse

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="rif -pcli image",
        description="Image plugin tools for RIF",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("info", help="show information about the image plugin")

    args = parser.parse_args(argv)
    if args.cmd == "info":
        print("Image Plugin para RIF.")
        print("Provee utilidades para convertir imagenes a bitmap y optimizar la compilacion.")
    return 0
