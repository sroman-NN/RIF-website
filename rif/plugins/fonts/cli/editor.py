from __future__ import annotations


def render_rows(rows: list[list[str]]) -> None:
    width = len(rows[0]) if rows else 0

    print("\ncolumnas:")
    print("    " + " ".join(str(i % 10) for i in range(width)))
    print("   " + "--" * width)

    for y, row in enumerate(rows):
        bits = " ".join(row)
        preview = "".join("█" if bit == "1" else "·" for bit in row)
        print(f"{y:02d}| {bits}   {preview}")


def edit_bits(initial_rows: list[str], title: str) -> list[str] | None:
    """
    Editor terminal minimo.

    Solo permite alternar bits existentes:
        0 -> 1
        1 -> 0
    """

    rows = [list(row) for row in initial_rows]
    height = len(rows)
    width = len(rows[0]) if rows else 0

    while True:
        print("\n" + "=" * 60)
        print(title)
        print(f"size visual: {width}x{height}")
        render_rows(rows)
        print("\nComandos:")
        print("  x y       alterna el bit en columna x, fila y")
        print("  t x y     alterna el bit en columna x, fila y")
        print("  s         guardar")
        print("  q         cancelar")

        command = input("> ").strip().lower()

        if command in {"s", "save", "guardar"}:
            return ["".join(row) for row in rows]

        if command in {"q", "quit", "cancel", "cancelar"}:
            return None

        parts = command.split()

        if len(parts) == 3 and parts[0] in {"t", "toggle"}:
            parts = parts[1:]

        if len(parts) != 2:
            print("Comando invalido.")
            continue

        try:
            x = int(parts[0])
            y = int(parts[1])
        except ValueError:
            print("x/y deben ser enteros.")
            continue

        if x < 0 or x >= width or y < 0 or y >= height:
            print(f"Coordenada fuera de rango. x=0..{width - 1}, y=0..{height - 1}")
            continue

        rows[y][x] = "1" if rows[y][x] == "0" else "0"
