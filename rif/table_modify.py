from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
import shutil
import time

from .errors import RIFError
from .lexer import Lexer
from .models import LexerConfig
from .parser import _plugin_roots


DELETE_WORDS = {"del", "delete", "remove", "rm", "drop"}
COLUMN_WORDS = {"column", "columns", "col", "cols", "field", "fields"}
ROW_WORDS = {"row", "rows"}
DATA_WORDS = {"data", "dato", "datos"}
TABLE_WORDS = {"table", "tables"}
MOVE_PLACES = {"before", "after", "to"}


@dataclass
class TableOperation:
    table: str
    kind: str
    args: list[str]
    value: str = ""


@dataclass
class TableBlock:
    path: Path
    start: int
    end: int
    separator: str
    indent: str
    table_name: str
    fields: list[str]
    rows: list[list[str]]
    dividers: list[tuple[int, list[str]]]
    section: str | None = None

    @property
    def row_names(self) -> list[str]:
        return [row[0] for row in self.rows]


@dataclass
class TableModifyResult:
    path: Path
    action: str
    summary: str
    backup_path: Path | None = None
    preview: str = ""
    dry_run: bool = False


def modify_table(
    *,
    source: str | None,
    plugin: str | None,
    use: str | None,
    file_name: str | None,
    section: str | None,
    operation_text: str,
    dry_run: bool = False,
    backup: bool = True,
    case_sensitive: bool = False,
) -> TableModifyResult:
    op = parse_operation(operation_text)
    files = _resolve_table_files(source, plugin, use, file_name)
    blocks = _load_blocks(files)
    if not blocks:
        searched = ", ".join(str(path) for path in files)
        raise RIFError(f"no se encontraron tablas editables en: {searched}")

    block = _select_block(blocks, op, section, case_sensitive)
    original_text = _read_text(block.path)
    lines = original_text.splitlines()

    action_summary = _apply_operation(block, op, case_sensitive)
    replacement = _format_table(block)
    new_lines = lines[:block.start] + replacement + lines[block.end:]
    new_text = "\n".join(new_lines)
    if original_text.endswith("\n"):
        new_text += "\n"

    _validate_table(block)
    preview = _preview_diff(lines[block.start:block.end], replacement)
    backup_path: Path | None = None

    if not dry_run:
        if backup:
            backup_path = _backup_path(block.path)
            shutil.copy2(block.path, backup_path)
        block.path.write_text(new_text, encoding="utf-8")
        _record_history(block.path, original_text, new_text, action_summary)

    return TableModifyResult(
        path=block.path,
        action=op.kind,
        summary=action_summary,
        backup_path=backup_path,
        preview=preview,
        dry_run=dry_run,
    )


def format_tables(
    *,
    source: str | None,
    plugin: str | None,
    use: str | None,
    file_name: str | None,
    table: str | None = None,
    dry_run: bool = False,
    backup: bool = True,
    case_sensitive: bool = False,
) -> list[TableModifyResult]:
    files = _resolve_table_files(source, plugin, use, file_name)
    blocks = _load_blocks(files)
    if table:
        blocks = [block for block in blocks if _same(block.table_name, table, case_sensitive)]
        if not blocks:
            raise RIFError(f"tabla no existe: {table}")
    if not blocks:
        raise RIFError("no se encontraron tablas editables para formatear")

    results: list[TableModifyResult] = []
    for path in sorted({block.path for block in blocks}):
        path_blocks = [block for block in blocks if block.path == path]
        original_text = _read_text(path)
        lines = original_text.splitlines()
        new_lines = list(lines)
        preview_parts: list[str] = []
        for block in sorted(path_blocks, key=lambda item: item.start, reverse=True):
            _validate_table(block)
            replacement = _format_table(block)
            preview_parts.append(_preview_diff(lines[block.start:block.end], replacement, limit=4))
            new_lines[block.start:block.end] = replacement
        new_text = "\n".join(new_lines)
        if original_text.endswith("\n"):
            new_text += "\n"

        backup_path: Path | None = None
        summary = f"formateada(s) {len(path_blocks)} tabla(s)"
        if not dry_run and new_text != original_text:
            if backup:
                backup_path = _backup_path(path)
                shutil.copy2(path, backup_path)
            path.write_text(new_text, encoding="utf-8")
            _record_history(path, original_text, new_text, summary)
        results.append(TableModifyResult(path, "format", summary, backup_path, "\n".join(preview_parts), dry_run))
    return results


def undo_table(hash_str: str | None = None) -> TableModifyResult:
    history = _load_history()
    index = int(history.get("index", 0))
    entries = list(history.get("entries", []))

    if hash_str is not None:
        found_idx = None
        for idx, entry in enumerate(entries):
            if entry.get("hash", "").startswith(hash_str):
                found_idx = idx
                break
        if found_idx is None:
            raise RIFError(f"no se encontro ningun cambio con el hash: {hash_str}")

        entry = entries[found_idx]
        path = Path(entry["path"])
        current = _read_text(path) if path.exists() else ""
        path.write_text(entry["before"], encoding="utf-8")

        history["index"] = found_idx
        _save_history(history)

        return TableModifyResult(
            path, 
            "undo", 
            f"undo (hash exacto {entry['hash']}): {entry['summary']}", 
            preview=_preview_text(current, entry["before"])
        )

    if index <= 0:
        raise RIFError("no hay cambios de tabla para deshacer")
    entry = entries[index - 1]
    path = Path(entry["path"])
    current = _read_text(path) if path.exists() else ""
    if current != entry["after"]:
        raise RIFError(f"no se puede deshacer: {path} cambio despues del historial")
    path.write_text(entry["before"], encoding="utf-8")
    history["index"] = index - 1
    _save_history(history)
    return TableModifyResult(path, "undo", f"undo: {entry['summary']}", preview=_preview_text(entry["after"], entry["before"]))


def redo_table(hash_str: str | None = None) -> TableModifyResult:
    history = _load_history()
    index = int(history.get("index", 0))
    entries = list(history.get("entries", []))

    if hash_str is not None:
        found_idx = None
        for idx, entry in enumerate(entries):
            if entry.get("hash", "").startswith(hash_str):
                found_idx = idx
                break
        if found_idx is None:
            raise RIFError(f"no se encontro ningun cambio con el hash: {hash_str}")

        entry = entries[found_idx]
        path = Path(entry["path"])
        current = _read_text(path) if path.exists() else ""
        path.write_text(entry["after"], encoding="utf-8")

        history["index"] = found_idx + 1
        _save_history(history)

        return TableModifyResult(
            path, 
            "redo", 
            f"redo (hash exacto {entry['hash']}): {entry['summary']}", 
            preview=_preview_text(current, entry["after"])
        )

    if index >= len(entries):
        raise RIFError("no hay cambios de tabla para rehacer")
    entry = entries[index]
    path = Path(entry["path"])
    current = _read_text(path) if path.exists() else ""
    if current != entry["before"]:
        raise RIFError(f"no se puede rehacer: {path} cambio despues del historial")
    path.write_text(entry["after"], encoding="utf-8")
    history["index"] = index + 1
    _save_history(history)
    return TableModifyResult(path, "redo", f"redo: {entry['summary']}", preview=_preview_text(entry["before"], entry["after"]))


def show_hashing_table(*, open_file: bool = False) -> int:
    history = _load_history()
    entries = history.get("entries", [])
    index = history.get("index", 0)

    if not entries:
        print("Historial de modificaciones de tabla vacío.")
        return 0

    import datetime
    import webbrowser

    lines = []
    lines.append("| State | Index | Hash | Action Summary | File | Date/Time |")
    lines.append("| :---: | :---: | :---: | :--- | :--- | :--- |")

    for i, entry in enumerate(entries):
        state = ""
        if i == index - 1:
            state = "⭐ [Last Done]"
        elif i == index:
            state = "➡️ [Next Redo]"

        t_str = datetime.datetime.fromtimestamp(entry.get("time", 0.0)).strftime("%Y-%m-%d %H:%M:%S")
        h = entry.get("hash", "n/a")
        summary = entry.get("summary", "")
        file_name = Path(entry.get("path", "")).name

        lines.append(f"| {state} | {i} | {h} | {summary} | {file_name} | {t_str} |")

    table_text = "\n".join(lines)

    if open_file:
        import tempfile
        temp_dir = Path(tempfile.gettempdir())
        temp_log = temp_dir / "rif_table_hashing.md"

        report = []
        report.append("# RIF Table Hashing & History Log\n")
        report.append(f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        report.append(f"Current History Index Pointer: **{index}** / {len(entries)}\n")
        report.append("## History Table\n")
        report.append(table_text)
        report.append("\n## Instructions\n")
        report.append("- Use `rif table undo <hash>` to restore a specific state before the given change.")
        report.append("- Use `rif table redo <hash>` to reapply a specific state after the given change.\n")

        temp_log.write_text("\n".join(report), encoding="utf-8")

        webbrowser.open(f"file:///{str(temp_log.resolve()).replace(chr(92), '/')}")
        print(f"Abriendo registro de historial de hashing en: {temp_log}")
    else:
        print("\n=== HISTORIAL DE CAMBIOS DE TABLA (HASHING) ===")
        print(f"{'STATE':<14} | {'INDEX':<5} | {'HASH':<8} | {'SUMMARY':<40} | {'FILE':<20} | {'DATE/TIME'}")
        print("-" * 115)
        for i, entry in enumerate(entries):
            state = ""
            if i == index - 1:
                state = "* Last Done"
            elif i == index:
                state = "> Next Redo"

            t_str = datetime.datetime.fromtimestamp(entry.get("time", 0.0)).strftime("%Y-%m-%d %H:%M:%S")
            h = entry.get("hash", "n/a")
            summary = entry.get("summary", "")
            if len(summary) > 40:
                summary = summary[:37] + "..."
            file_name = Path(entry.get("path", "")).name
            if len(file_name) > 20:
                file_name = file_name[:17] + "..."
            print(f"{state:<14} | {i:<5} | {h:<8} | {summary:<40} | {file_name:<20} | {t_str}")
        print(f"\nPuntero de Historial Actual: {index} / {len(entries)}")
        print("Usa 'rif table hashing-table --open' para ver en formato Markdown en tu navegador.")

    return 0


def clear_table_hashing() -> None:
    history = {"index": 0, "entries": []}
    _save_history(history)
    print("Historial de cambios de tabla y hashes limpiado exitosamente.")


def parse_operation(text: str) -> TableOperation:
    text = text.strip()
    if not text:
        raise RIFError("la operacion de tabla esta vacia")

    table, rest = _split_head(text)
    if not rest:
        raise RIFError('la operacion necesita formato: "TABLA comando args"')

    head, rest = _split_head(rest)
    action = head.lower()
    if action in DELETE_WORDS:
        kind_word, names_text = _split_head(rest)
        if not kind_word:
            raise RIFError("delete necesita: row|column|table <nombre>")
        kind = _target_kind(kind_word)
        if kind == "table":
            names = _names(names_text)
            if names:
                raise RIFError("del table no recibe nombres; usa --file o --section para escoger")
            return TableOperation(table, "delete_table", [])
        names = _names(names_text)
        if not names:
            raise RIFError(f"del {kind_word} necesita al menos un nombre")
        return TableOperation(table, f"delete_{kind}", names)

    if action == "add":
        kind_word, tail = _split_optional_kind(rest)
        if kind_word in COLUMN_WORDS:
            name, default = _split_column_add(tail)
            return TableOperation(table, "add_column", [name], default)
        if kind_word in ROW_WORDS:
            return TableOperation(table, "add_row", [tail.strip()])
        return TableOperation(table, "add_row", [rest])

    if action == "addsect":
        if not rest:
            raise RIFError("addsect necesita texto")
        return TableOperation(table, "add_section", [], rest)

    if action == "set":
        kind_word, tail = _split_optional_kind(rest)
        if kind_word in COLUMN_WORDS:
            parts = tail.split(None, 1)
            if len(parts) != 2:
                raise RIFError("set column necesita: set column <column> <valor|valores...>")
            return TableOperation(table, "set_column", [parts[0]], parts[1].strip())
        parts = rest.split(None, 2)
        if len(parts) != 3:
            raise RIFError("set necesita: set <row> <column> <valor>")
        return TableOperation(table, "set_cell", [parts[0], parts[1]], parts[2].strip())

    if action == "clear":
        parts = rest.split(None, 1)
        if len(parts) != 2:
            raise RIFError("clear necesita: clear <row> <column>")
        return TableOperation(table, "set_cell", [parts[0], parts[1]], "")

    if action == "rename":
        kind_word, tail = _split_required(rest, "rename necesita: row|column <viejo> <nuevo>")
        kind = _target_kind(kind_word)
        if kind == "table":
            raise RIFError("rename table no esta soportado")
        parts = tail.split(None, 1)
        if len(parts) != 2:
            raise RIFError(f"rename {kind_word} necesita nombre viejo y nuevo")
        return TableOperation(table, f"rename_{kind}", [parts[0], parts[1]])

    if action == "copy":
        kind_word, tail = _split_required(rest, "copy necesita: row <origen> <nuevo>")
        if kind_word.lower() not in ROW_WORDS:
            raise RIFError("copy solo soporta row")
        parts = tail.split(None, 1)
        if len(parts) != 2:
            raise RIFError("copy row necesita fila origen y fila nueva")
        return TableOperation(table, "copy_row", [parts[0], parts[1]])

    if action == "move":
        kind_word, tail = _split_required(rest, "move necesita: row|column <nombre> before|after|to <destino>")
        kind = _target_kind(kind_word)
        if kind == "table":
            raise RIFError("move table no esta soportado")
        parts = tail.split(None, 2)
        if len(parts) != 3 or parts[1].lower() not in MOVE_PLACES:
            raise RIFError(f"move {kind_word} necesita: <nombre> before|after|to <destino>")
        return TableOperation(table, f"move_{kind}", [parts[0], parts[1].lower(), parts[2]])

    quick = [head, *rest.split()]
    if len(quick) == 3:
        column, row, value = quick
        return TableOperation(table, "set_cell", [row, column], value)

    raise RIFError(f"operacion desconocida: {head!r}")


def _resolve_table_files(
    source: str | None,
    plugin: str | None,
    use: str | None,
    file_name: str | None,
) -> list[Path]:
    base: Path | None = None
    if plugin:
        if not use:
            raise RIFError("-p/--plugin necesita -use/--use para escoger la carpeta de packs")
        base = _plugin_pack_dir(plugin, use)

    if source:
        candidate = Path(source)
        if base and not candidate.exists():
            candidate = base / source
        if candidate.exists():
            base = candidate
        elif not plugin:
            raise RIFError(f"ruta no encontrada: {source}")

    if base is None:
        raise RIFError("usa --from <archivo|carpeta> o -p <plugin> -use <pack>")

    if base.is_file():
        files = [base]
    elif base.is_dir():
        files = sorted(path for path in base.glob("*.pack") if path.is_file())
    else:
        raise RIFError(f"origen invalido: {base}")

    if file_name:
        wanted = Path(file_name).name
        files = [path for path in files if path.name == wanted or path.stem == wanted]
        if not files:
            raise RIFError(f"no se encontro el archivo de tabla {file_name!r}")

    if not files:
        raise RIFError(f"no hay archivos .pack en {base}")
    return files


def _plugin_pack_dir(plugin: str, use: str) -> Path:
    for root in _plugin_roots(Path.cwd()):
        for packs_name in ("pack", "packs"):
            candidate = root / plugin / packs_name / use
            if candidate.exists() and candidate.is_dir():
                return candidate
    raise RIFError(f"pack de plugin no encontrado: plugin={plugin!r}, use={use!r}")


def _load_blocks(files: list[Path]) -> list[TableBlock]:
    blocks: list[TableBlock] = []
    for path in files:
        text = _read_text(path)
        cfg = Lexer.discover_config(text) if text.strip() else LexerConfig()
        blocks.extend(_find_table_blocks(path, text, cfg))
    return blocks


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8").lstrip("\ufeff")


def _find_table_blocks(path: Path, text: str, cfg: LexerConfig) -> list[TableBlock]:
    lexer = Lexer(text, cfg)
    lines = text.splitlines()
    blocks: list[TableBlock] = []
    i = 0
    current_section = _section_from_filename(path)

    while i < len(lines):
        code = lexer.strip_comment(lines[i]).strip()
        if code.startswith(cfg.separator):
            start = i
            raw_rows: list[tuple[str, list[str]]] = []
            indent = lines[i][: len(lines[i]) - len(lines[i].lstrip(" "))]
            while i < len(lines) and lexer.strip_comment(lines[i]).strip().startswith(cfg.separator):
                cells = _cells_from_line(lexer.strip_comment(lines[i]), cfg.separator)
                if _is_divider(cells):
                    raw_rows.append(("divider", cells))
                else:
                    raw_rows.append(("row", cells))
                i += 1
            if raw_rows and raw_rows[0][0] == "row" and raw_rows[0][1] and _same(raw_rows[0][1][0], "NAME", False):
                fields = raw_rows[0][1]
                rows: list[list[str]] = []
                dividers: list[tuple[int, list[str]]] = []
                for kind, cells in raw_rows[1:]:
                    if kind == "divider":
                        dividers.append((len(rows), cells))
                    else:
                        rows.append(_padded_row(cells, len(fields)))
                table_name = _table_name(current_section, path)
                blocks.append(TableBlock(path, start, i, cfg.separator, indent, table_name, fields, rows, dividers, current_section))
            continue

        maybe_section = _section_from_line(code)
        if maybe_section:
            current_section = maybe_section
        i += 1

    return blocks


def _cells_from_line(code: str, separator: str) -> list[str]:
    stripped = code.strip()
    parts = stripped.split(separator)
    if parts and parts[0].strip() == "":
        parts = parts[1:]
    if parts and parts[-1].strip() == "":
        parts = parts[:-1]
    return [part.strip() for part in parts]


def _is_divider(cells: list[str]) -> bool:
    return bool(cells) and cells[0].replace(" ", "") == "---"


def _select_block(
    blocks: list[TableBlock],
    op: TableOperation,
    section: str | None,
    case_sensitive: bool,
) -> TableBlock:
    wanted_table = op.table.strip()
    if not wanted_table:
        raise RIFError("el nombre de tabla no puede estar vacio")
    all_blocks = list(blocks)
    blocks = [block for block in blocks if _same(block.table_name, wanted_table, case_sensitive)]
    if not blocks:
        available = ", ".join(sorted({block.table_name for block in all_blocks}, key=str.lower))
        raise RIFError(f"tabla no existe: {wanted_table}. Tablas disponibles: {available or '(ninguna)'}")

    if section:
        wanted = _normalize_section(section)
        blocks = [block for block in blocks if block.section == wanted]
        if not blocks:
            raise RIFError(f"no existe tabla para la seccion {wanted}")

    matches = [block for block in blocks if _block_matches(block, op, case_sensitive)]
    if not matches:
        raise RIFError(_not_found_message(blocks, op, case_sensitive))
    if len(matches) > 1:
        places = ", ".join(f"{block.path.name}:{block.start + 1}" for block in matches)
        raise RIFError(f"operacion ambigua; coincide con varias tablas: {places}. Usa --file o --section")
    return matches[0]


def _block_matches(block: TableBlock, op: TableOperation, case_sensitive: bool) -> bool:
    if op.kind == "add_row":
        cells = _cells_from_operation(op.args[0])
        return bool(cells) and len(cells) <= len(block.fields) and _find_row_index(block, cells[0], case_sensitive) is None
    if op.kind in {"add_column", "delete_table", "add_section", "format"}:
        return True
    if op.kind == "delete_column":
        return all(_find_index(block.fields, name, case_sensitive) is not None for name in op.args)
    if op.kind == "rename_column":
        return _find_index(block.fields, op.args[0], case_sensitive) is not None
    if op.kind == "set_cell":
        return _find_row_index(block, op.args[0], case_sensitive) is not None and _find_index(block.fields, op.args[1], case_sensitive) is not None
    if op.kind == "set_column":
        return _find_index(block.fields, op.args[0], case_sensitive) is not None
    if op.kind == "delete_row":
        return all(_find_row_index(block, name, case_sensitive) is not None for name in op.args)
    if op.kind in {"rename_row", "copy_row"}:
        return _find_row_index(block, op.args[0], case_sensitive) is not None
    if op.kind == "move_column":
        return _find_index(block.fields, op.args[0], case_sensitive) is not None
    if op.kind == "move_row":
        return _find_row_index(block, op.args[0], case_sensitive) is not None
    return False


def _apply_operation(block: TableBlock, op: TableOperation, case_sensitive: bool) -> str:
    if op.kind == "delete_table":
        block.fields = []
        block.rows = []
        return f"tabla eliminada en {block.path.name}:{block.start + 1}"

    if op.kind == "delete_column":
        removed: list[str] = []
        for name in op.args:
            idx = _require_column(block, name, case_sensitive)
            if idx == 0:
                raise RIFError("no se puede borrar la columna NAME; usa del row")
            removed.append(block.fields[idx])
            del block.fields[idx]
            for row in block.rows:
                del row[idx]
        return f"columna(s) eliminada(s): {', '.join(removed)}"

    if op.kind == "delete_row":
        removed: list[str] = []
        for name in op.args:
            idx = _require_row(block, name, case_sensitive)
            removed.append(block.rows[idx][0])
            del block.rows[idx]
            _shift_dividers(block, idx, -1)
        return f"fila(s) eliminada(s): {', '.join(removed)}"

    if op.kind == "add_column":
        name = op.args[0].strip()
        if not name:
            raise RIFError("add column necesita nombre")
        if _find_index(block.fields, name, case_sensitive) is not None:
            raise RIFError(f"la columna ya existe: {name}")
        if op.value:
            for row in block.rows:
                _validate_value(op.value, row[0])
        block.fields.append(name)
        for row in block.rows:
            row.append(op.value)
        return f"columna agregada: {name}"

    if op.kind == "add_row":
        cells = _cells_from_operation(op.args[0])
        if not cells or not cells[0]:
            raise RIFError("add row necesita una celda NAME")
        if _find_row_index(block, cells[0], case_sensitive) is not None:
            raise RIFError(f"la fila ya existe: {cells[0]}")
        if len(cells) > len(block.fields):
            raise RIFError(f"la fila tiene {len(cells)} celdas, pero la tabla tiene {len(block.fields)} columnas")
        for value in cells[1:]:
            _validate_value(value, cells[0])
        block.rows.append(_padded_row(cells, len(block.fields)))
        return f"fila agregada: {cells[0]}"

    if op.kind == "set_cell":
        row_idx = _require_row(block, op.args[0], case_sensitive)
        col_idx = _require_column(block, op.args[1], case_sensitive)
        if col_idx == 0:
            raise RIFError("no se puede setear NAME; usa rename row")
        old = block.rows[row_idx][col_idx]
        value = _switch_value(old) if op.value.lower() == "switch" else op.value
        _validate_value(value, block.rows[row_idx][0])
        block.rows[row_idx][col_idx] = value
        return f"{block.rows[row_idx][0]}.{block.fields[col_idx]}: {old!r} -> {value!r}"

    if op.kind == "set_column":
        col_idx = _require_column(block, op.args[0], case_sensitive)
        if col_idx == 0:
            raise RIFError("no se puede setear NAME; usa rename row")
        values = _column_values(op.value)
        if len(values) != len(block.rows):
            raise RIFError(f"set column recibio {len(values)} valor(es), pero la tabla tiene {len(block.rows)} fila(s)")
        for row, value in zip(block.rows, values):
            _validate_value(value, row[0])
            row[col_idx] = value
        return f"columna seteada: {block.fields[col_idx]} ({len(values)} valor(es))"

    if op.kind == "add_section":
        block.dividers.append((len(block.rows), _section_divider_cells(block, op.value)))
        return f"seccion agregada en {block.table_name}: {op.value}"

    if op.kind == "rename_column":
        old, new = op.args
        idx = _require_column(block, old, case_sensitive)
        if idx == 0:
            raise RIFError("no se puede renombrar NAME")
        if _find_index(block.fields, new, case_sensitive) is not None:
            raise RIFError(f"la columna destino ya existe: {new}")
        block.fields[idx] = new
        return f"columna renombrada: {old} -> {new}"

    if op.kind == "rename_row":
        old, new = op.args
        idx = _require_row(block, old, case_sensitive)
        if _find_row_index(block, new, case_sensitive) is not None:
            raise RIFError(f"la fila destino ya existe: {new}")
        block.rows[idx][0] = new
        return f"fila renombrada: {old} -> {new}"

    if op.kind == "copy_row":
        old, new = op.args
        idx = _require_row(block, old, case_sensitive)
        if _find_row_index(block, new, case_sensitive) is not None:
            raise RIFError(f"la fila destino ya existe: {new}")
        copied = list(block.rows[idx])
        copied[0] = new
        block.rows.insert(idx + 1, copied)
        _shift_dividers(block, idx + 1, 1)
        return f"fila copiada: {old} -> {new}"

    if op.kind == "move_column":
        name, place, target = op.args
        src = _require_column(block, name, case_sensitive)
        if src == 0:
            raise RIFError("no se puede mover NAME")
        dst = _move_destination(block.fields, place, target, case_sensitive)
        if dst == 0:
            raise RIFError("no se puede mover una columna antes de NAME")
        _move_index(block.fields, src, dst)
        for row in block.rows:
            _move_index(row, src, dst)
        return f"columna movida: {name} {place} {target}"

    if op.kind == "move_row":
        name, place, target = op.args
        src = _require_row(block, name, case_sensitive)
        dst = _row_move_destination(block, place, target, case_sensitive)
        row = block.rows.pop(src)
        if src < dst:
            dst -= 1
        block.rows.insert(dst, row)
        return f"fila movida: {name} {place} {target}"

    raise RIFError(f"operacion no implementada: {op.kind}")


def _format_table(block: TableBlock) -> list[str]:
    if not block.fields:
        return []
    rendered_dividers = [cells for _, cells in block.dividers]
    rows = [block.fields] + block.rows + rendered_dividers
    widths = [0] * len(block.fields)
    for row in rows:
        for idx, cell in enumerate(_fit_row(row, len(block.fields))):
            widths[idx] = max(widths[idx], len(cell))

    out: list[str] = []
    out.append(_format_table_row(block, block.fields, widths))
    dividers_by_pos: dict[int, list[list[str]]] = {}
    for pos, cells in block.dividers:
        dividers_by_pos.setdefault(pos, []).append(cells)
    for idx, row in enumerate(block.rows):
        for divider in dividers_by_pos.get(idx, []):
            out.append(_format_table_row(block, _padded_row(divider, len(block.fields)), widths))
        out.append(_format_table_row(block, row, widths))
    for divider in dividers_by_pos.get(len(block.rows), []):
        out.append(_format_table_row(block, _padded_row(divider, len(block.fields)), widths))
    return out


def _format_table_row(block: TableBlock, row: list[str], widths: list[int]) -> str:
    cells = _fit_row(row, len(block.fields))
    body = " ".join(f"{block.separator} {cell.ljust(widths[idx])}" for idx, cell in enumerate(cells))
    return f"{block.indent}{body} {block.separator}"


def _format_plain_rows(block: TableBlock, rows: list[list[str]]) -> list[str]:
    if not rows:
        return []
    widths = [0] * len(rows[0])
    for row in rows:
        for idx, cell in enumerate(_padded_row(row, len(widths))):
            widths[idx] = max(widths[idx], len(cell))
    out: list[str] = []
    for row in rows:
        cells = _padded_row(row, len(block.fields))
        body = " ".join(f"{block.separator} {cell.ljust(widths[idx])}" for idx, cell in enumerate(cells))
        out.append(f"{block.indent}{body} {block.separator}")
    return out


def _validate_table(block: TableBlock) -> None:
    if not block.fields:
        return
    if not block.fields[0] or block.fields[0] != "NAME":
        raise RIFError("la primera columna debe ser NAME")
    duplicates = _duplicates(block.fields, case_sensitive=True)
    if duplicates:
        raise RIFError(f"columnas duplicadas: {', '.join(duplicates)}")
    row_names = [row[0] for row in block.rows]
    duplicates = _duplicates(row_names, case_sensitive=True)
    if duplicates:
        raise RIFError(f"filas duplicadas: {', '.join(duplicates)}")
    for row in block.rows:
        if len(row) != len(block.fields):
            raise RIFError(f"fila con tamano invalido: {row[0] if row else '<vacia>'}")
        if not row[0]:
            raise RIFError("fila sin NAME")


def _validate_value(value: str, row_name: str) -> None:
    value = str(value).strip()
    if value == "":
        return
    lowered = value.lower()
    if lowered in {"yes", "no"}:
        return
    compact = value.replace("_", "")
    if compact and all(ch in "01" for ch in compact):
        return
    if compact.startswith(("0x", "0X")):
        try:
            int(compact, 16)
            return
        except ValueError:
            pass
    if _same(value, row_name, False):
        return
    raise RIFError(f"valor invalido para {row_name}: {value!r}; usa binario, hex, yes/no o el propio nombre")


def _switch_value(value: str) -> str:
    lowered = value.strip().lower()
    if lowered == "yes":
        return "no"
    if lowered == "no":
        return "yes"
    raise RIFError("switch solo funciona sobre celdas yes/no")


def _column_values(text: str) -> list[str]:
    if "|" in text:
        return _cells_from_line(text, "|")
    return [part.strip() for part in text.split() if part.strip()]


def _section_divider_cells(block: TableBlock, text: str) -> list[str]:
    cells = ["---"] * max(1, len(block.fields))
    if len(cells) > 1:
        cells[1] = text.strip()
    elif cells:
        cells[0] = "---"
    return cells


def _shift_dividers(block: TableBlock, from_index: int, delta: int) -> None:
    shifted: list[tuple[int, list[str]]] = []
    for pos, cells in block.dividers:
        if pos > from_index or (delta > 0 and pos >= from_index):
            shifted.append((max(0, pos + delta), cells))
        else:
            shifted.append((pos, cells))
    block.dividers = shifted


def _move_destination(values: list[str], place: str, target: str, case_sensitive: bool) -> int:
    if place == "to":
        try:
            idx = int(target)
        except ValueError as exc:
            raise RIFError(f"destino numerico invalido: {target}") from exc
        return max(0, min(idx, len(values)))
    target_idx = _find_index(values, target, case_sensitive)
    if target_idx is None:
        raise RIFError(f"destino no existe: {target}")
    return target_idx if place == "before" else target_idx + 1


def _row_move_destination(block: TableBlock, place: str, target: str, case_sensitive: bool) -> int:
    if place == "to":
        try:
            idx = int(target)
        except ValueError as exc:
            raise RIFError(f"destino numerico invalido: {target}") from exc
        return max(0, min(idx, len(block.rows)))
    target_idx = _find_row_index(block, target, case_sensitive)
    if target_idx is None:
        raise RIFError(f"fila destino no existe: {target}")
    return target_idx if place == "before" else target_idx + 1


def _move_index(values: list[str], src: int, dst: int) -> None:
    item = values.pop(src)
    if src < dst:
        dst -= 1
    values.insert(max(0, min(dst, len(values))), item)


def _preview_diff(old: list[str], new: list[str], limit: int = 10) -> str:
    removed = [f"- {line}" for line in old[:limit]]
    added = [f"+ {line}" for line in new[:limit]]
    if len(old) > limit:
        removed.append(f"- ... {len(old) - limit} linea(s) mas")
    if len(new) > limit:
        added.append(f"+ ... {len(new) - limit} linea(s) mas")
    return "\n".join(removed + added)


def _preview_text(before: str, after: str) -> str:
    return _preview_diff(before.splitlines(), after.splitlines(), limit=8)


def _history_path() -> Path:
    override = os.environ.get("RIF_TABLE_HISTORY")
    if override:
        return Path(override)
    return Path.home() / ".rif" / "table_history.json"


def _load_history() -> dict[str, object]:
    path = _history_path()
    if not path.exists():
        return {"index": 0, "entries": []}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"index": 0, "entries": []}
    if not isinstance(data, dict):
        return {"index": 0, "entries": []}
    data.setdefault("index", 0)
    data.setdefault("entries", [])


    entries = data["entries"]
    updated = False
    for entry in entries:
        if "hash" not in entry:
            import hashlib
            h_in = f"{entry.get('path', '')}:{entry.get('time', 0.0)}:{entry.get('summary', '')}"
            entry["hash"] = hashlib.sha256(h_in.encode("utf-8")).hexdigest()[:8]
            updated = True
    if updated:
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        except Exception:
            pass

    return data


def _save_history(history: dict[str, object]) -> None:
    path = _history_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(history, indent=2), encoding="utf-8")


def _record_history(path: Path, before: str, after: str, summary: str) -> None:
    if before == after:
        return
    history = _load_history()
    entries = list(history.get("entries", []))
    index = int(history.get("index", 0))
    entries = entries[:index]

    t = time.time()
    p_str = str(path.resolve())
    import hashlib
    h_in = f"{p_str}:{t}:{summary}"
    h = hashlib.sha256(h_in.encode("utf-8")).hexdigest()[:8]

    entries.append({
        "path": p_str,
        "before": before,
        "after": after,
        "summary": summary,
        "time": t,
        "hash": h,
    })
    history["entries"] = entries[-100:]
    history["index"] = len(history["entries"])
    _save_history(history)


def _backup_path(path: Path) -> Path:
    base = path.with_name(path.name + ".bak")
    if not base.exists():
        return base
    for index in range(1, 1000):
        candidate = path.with_name(f"{path.name}.bak{index}")
        if not candidate.exists():
            return candidate
    raise RIFError(f"no se pudo crear backup para {path}")


def _require_column(block: TableBlock, name: str, case_sensitive: bool) -> int:
    idx = _find_index(block.fields, name, case_sensitive)
    if idx is None:
        raise RIFError(f"columna no existe: {name}. Columnas: {', '.join(block.fields)}")
    return idx


def _require_row(block: TableBlock, name: str, case_sensitive: bool) -> int:
    idx = _find_row_index(block, name, case_sensitive)
    if idx is None:
        rows = ", ".join(block.row_names[:20])
        extra = "..." if len(block.row_names) > 20 else ""
        raise RIFError(f"fila no existe: {name}. Filas: {rows}{extra}")
    return idx


def _find_row_index(block: TableBlock, name: str, case_sensitive: bool) -> int | None:
    return _find_index(block.row_names, name, case_sensitive)


def _find_index(values: list[str], name: str, case_sensitive: bool) -> int | None:
    for idx, value in enumerate(values):
        if _same(value, name, case_sensitive):
            return idx
    return None


def _same(left: str, right: str, case_sensitive: bool) -> bool:
    if case_sensitive:
        return left == right
    return left.lower() == right.lower()


def _not_found_message(blocks: list[TableBlock], op: TableOperation, case_sensitive: bool) -> str:
    if op.kind in {"delete_column", "rename_column"}:
        columns = sorted({field for block in blocks for field in block.fields})
        return f"columna no existe: {op.args[0]}. Columnas disponibles: {', '.join(columns[:30])}"
    if op.kind == "set_cell":
        return f"fila o columna no existe: {op.args[0]} {op.args[1]}"
    if op.kind in {"delete_row", "rename_row", "copy_row"}:
        rows = sorted({row for block in blocks for row in block.row_names}, key=str.lower)
        return f"fila no existe: {op.args[0]}. Filas disponibles: {', '.join(rows[:30])}"
    return "no se encontro una tabla compatible con la operacion"


def _split_head(text: str) -> tuple[str, str]:
    parts = text.split(None, 1)
    if len(parts) == 1:
        return parts[0], ""
    return parts[0], parts[1].strip()


def _split_required(text: str, message: str) -> tuple[str, str]:
    parts = text.strip().split(None, 1)
    if len(parts) != 2:
        raise RIFError(message)
    return parts[0].lower(), parts[1].strip()


def _split_optional_kind(text: str) -> tuple[str, str]:
    parts = text.strip().split(None, 1)
    if not parts:
        raise RIFError("add necesita datos")
    first = parts[0].lower()
    if first in ROW_WORDS or first in COLUMN_WORDS:
        return first, parts[1].strip() if len(parts) > 1 else ""
    return "", text.strip()


def _split_column_add(text: str) -> tuple[str, str]:
    parts = text.split(None, 1)
    if not parts:
        raise RIFError("add column necesita nombre")
    default = ""
    if len(parts) > 1:
        tail = parts[1].strip()
        default = tail[8:].strip() if tail.lower().startswith("default ") else tail
    return parts[0], default


def _target_kind(value: str) -> str:
    value = value.lower()
    if value in COLUMN_WORDS:
        return "column"
    if value in ROW_WORDS or value in DATA_WORDS:
        return "row"
    if value in TABLE_WORDS:
        return "table"
    raise RIFError(f"tipo de objetivo invalido: {value!r}; usa row, column o table")


def _names(text: str) -> list[str]:
    return [part.strip() for part in text.replace(",", " ").split() if part.strip()]


def _cells_from_operation(text: str) -> list[str]:
    if "|" in text:
        return _cells_from_line(text, "|")
    return text.split()


def _padded_row(row: list[str], width: int) -> list[str]:
    if len(row) > width:
        return list(row)
    return list(row) + [""] * (width - len(row))


def _fit_row(row: list[str], width: int) -> list[str]:
    return (list(row) + [""] * width)[:width]


def _duplicates(values: list[str], case_sensitive: bool) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for value in values:
        key = value if case_sensitive else value.lower()
        if key in seen and value not in out:
            out.append(value)
        seen.add(key)
    return out


def _normalize_section(value: str) -> str:
    value = value.strip()
    return value if value.startswith(".") else f".{value}"


def _table_name(section: str | None, path: Path) -> str:
    if section:
        return section[1:] if section.startswith(".") else section
    return path.stem


def _section_from_filename(path: Path) -> str | None:
    parts = path.name.split(".")
    if len(parts) >= 3 and parts[-1] == "pack":
        return _normalize_section(parts[-2])
    return None


def _section_from_line(code: str) -> str | None:
    if not code:
        return None
    first = code.split(None, 1)[0].rstrip(":")
    if first.startswith(".") and len(first) > 1:
        return first
    parts = code.split(None, 2)
    if len(parts) >= 2 and parts[1].startswith("."):
        return parts[1].rstrip(":")
    return None
