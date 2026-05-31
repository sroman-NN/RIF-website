

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import sys
import webbrowser
from pathlib import Path

from .errors import RIFError, PackError
from .linker import build_file, link_file
from .packer import pack_file
from .parser import Parser, parse_packer_config
from .compiler import Compiler


def main(argv: list[str] | None = None) -> int:
    """Punto de entrada principal para el parsing de argumentos y ejecución de comandos de la CLI.

    Soporta los subcomandos:
    - lex: Imprime la secuencia de tokens resultantes del análisis léxico.
    - parse: Muestra la información AST estructurada y las configuraciones del .pack.
    - pack: Empaqueta el archivo fuente de entrada en su formato temporal consolidado.
    - link: Enlaza los fragmentos locales a las secciones de ensamblador.
    - compile: Compila y emite el stream de bits para una única línea de instrucción de hardware.
    - build: Enlaza y genera un binario ejecutable estructurado.
    - help: Muestra la documentación local de RIF.

    Args:
        argv: Lista opcional de argumentos pasados por terminal.

    Returns:
        Código de estado de la aplicación (0 para éxito, 1 para error controlado, 2 para comando no reconocido).
    """
    raw_args = list(sys.argv[1:] if argv is None else argv)
    if raw_args and raw_args[0] in {"-pcli", "--plugin-cli"}:
        return _run_plugin_cli(raw_args[1:])

    from . import __version__
    parser = argparse.ArgumentParser(prog="rif", description="RIF lexer/parser/packer tools")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_lex = sub.add_parser("lex", help="lex a source file")
    p_lex.add_argument("source")

    p_parse = sub.add_parser("parse", help="parse a source file")
    p_parse.add_argument("source")

    p_pack = sub.add_parser("pack", help="create source.pack.temp")
    p_pack.add_argument("source")
    p_pack.add_argument("-o", "--output")

    p_link = sub.add_parser("link", help="link fragments and reparse the linked source")
    p_link.add_argument("source")
    p_link.add_argument("-o", "--output")

    p_compile = sub.add_parser("compile", help="compile one instruction or build generated tooling")
    p_compile.add_argument("source", nargs="?", help="RIF rule file, for example store.amd64.pack")
    p_compile.add_argument("instruction", nargs="*", help="instruction to compile, for example: copy rax = rbx")
    p_compile.add_argument("-vscode", "--vscode", nargs="*", metavar="PLUGIN", help="create an all-in-one VSIX from plugin vscode bundles")
    p_compile.add_argument("--p", dest="vscode_plugins", nargs="*", metavar="PLUGIN", help="plugins to include when building a VSIX with --vscode")
    p_compile.add_argument("--ext", "--extension", dest="extensions", action="append", help="source file extension for the generated VS Code language, for example .gbasm")
    p_compile.add_argument("-icon", "--icon", dest="icon", help="icon file for the generated VSIX package")
    p_compile.add_argument("-p", "--plugin", help="create a dedicated compiler for this plugin")
    p_compile.add_argument("--link", nargs="*", default=[], help="plugins to include in the dedicated compiler")
    p_compile.add_argument("--name", help="pack name inside the plugin")
    p_compile.add_argument("-o", "--output", help="output path for generated tooling")
    p_compile.add_argument("--no-exe", action="store_true", help="only generate the dedicated Python launcher")

    p_build = sub.add_parser("build", help="build a linked binary from a RIF file")
    p_build.add_argument("source", help="RIF rule/link file")
    p_build.add_argument("-o", "--output")
    p_build.add_argument("-s", "--source-text", default="", help="optional assembly source text")
    p_build.add_argument("--source-file", help="optional assembly source file")
    p_build.add_argument("-use", "--use", help="alternative path to packs or special flag")
    p_build.add_argument("--plugin", help="name of the plugin to use packs from")
    p_build.add_argument("--name", help="name of the pack inside the plugin")

    p_help = sub.add_parser("help", help="show local RIF help")
    p_help.add_argument("topic", nargs="?", help="markdown topic name")
    p_help.add_argument("--open", action="store_true", help="open help/index.html")

    p_install = sub.add_parser("install", help="install a RIF plugin package or VS Code extension")
    group_install = p_install.add_mutually_exclusive_group(required=True)
    group_install.add_argument("--package", help="GitHub URL or local plugin folder")
    group_install.add_argument("--vscode", help="Install a .vsix extension into VS Code")

    p_plugins = sub.add_parser("plugins", help="manage RIF plugins")
    p_plugins.add_argument("-list", action="store_true", dest="list_plugins", help="list installed plugins")
    p_plugins.add_argument("-delete", metavar="NAME", help="delete an installed plugin")
    p_plugins.add_argument("-doc", metavar="NAME", help="open plugin documentation")
    p_plugins.add_argument("-info", metavar="NAME", help="show plugin pack.json without purpose")
    p_plugins.add_argument("-openp", metavar="NAME", help="open plugin purpose in rif purpose.txt")
    
    p_plugins_sub = p_plugins.add_subparsers(dest="plugins_cmd")
    p_pl_load = p_plugins_sub.add_parser("load", help="load a local plugin folder")
    p_pl_load.add_argument("path", help="path to the local plugin folder")

    p_pl_init = p_plugins_sub.add_parser("init", help="initialize a new local plugin structure")
    p_pl_init.add_argument("name", help="name of the new plugin")

    p_pip = sub.add_parser("pip", help="run pip inside the current RIF Python environment")
    p_pip.add_argument("pip_args", nargs=argparse.REMAINDER)

    p_plug = sub.add_parser("plug", help="install a plugin folder into RIF")
    p_plug.add_argument("path", help="path to the plugin folder to install")

    p_list = sub.add_parser("list", help="list items")
    p_list.add_argument("item", choices=["plugins"], help="what to list")

    p_packs = sub.add_parser("packs", help="list available packs inside a plugin")
    p_packs.add_argument("--plugin", required=True, help="name of the plugin to query")

    p_clear = sub.add_parser("clear", help="clear items")
    p_clear.add_argument("item", choices=["cache", "table"], help="what to clear")
    p_clear.add_argument("subitem", nargs="?", help="optional sub-item to clear (e.g. hashing for table)")
    p_clear.add_argument("-p", "--plugin", help="plugin name to clear its specific cache")

    p_zip = sub.add_parser("zip", help="compress rif into a zip file ignoring __pycache__")
    p_zip.add_argument("-o", "--output", default="rif.zip", help="output zip file name")

    p_table = sub.add_parser("table", help="programmatically modify RIF tables")
    p_table.add_argument("--from", dest="from_path", help="path to pack file or directory")
    p_table.add_argument("-p", "--plugin", help="plugin name")
    p_table.add_argument("-use", "--use", help="pack name to use from plugin")
    p_table.add_argument("--file", help="specific file name inside the directory")
    p_table.add_argument("--section", help="target section (e.g. .regs)")
    p_table.add_argument("--dry-run", action="store_true", help="simulate changes without writing")
    p_table.add_argument("--no-backup", action="store_true", help="do not create a backup file")
    p_table.add_argument("--case-sensitive", action="store_true", help="enable case-sensitive matching")

    p_table_sub = p_table.add_subparsers(dest="table_cmd", required=True)

    p_t_modify = p_table_sub.add_parser("modify", help="modify a table row, column, cell or table")
    p_t_modify.add_argument("operation", help='operation string like "regs add row ax 000 16"')

    p_t_format = p_table_sub.add_parser("format", help="format tables in RIF pack files")
    p_t_format.add_argument("--table", help="restrict formatting to a specific table name")

    p_t_undo = p_table_sub.add_parser("undo", help="undo the last table modification")
    p_t_undo.add_argument("hash", nargs="?", help="optional hash to restore a specific state")

    p_t_redo = p_table_sub.add_parser("redo", help="redo the last undone table modification")
    p_t_redo.add_argument("hash", nargs="?", help="optional hash to redo a specific state")

    p_t_hashing = p_table_sub.add_parser("hashing-table", help="view history with hashes")
    p_t_hashing.add_argument("--open", action="store_true", help="open history log file")

    args = parser.parse_args(raw_args)

    try:
        if args.cmd == "help":
            return _run_help(args.topic, args.open)

        if args.cmd == "install":
            if args.vscode:
                import subprocess
                import shutil
                code_cmd = shutil.which("code")
                if not code_cmd:
                    raise RIFError("El ejecutable 'code' no se encuentra en el PATH. Instala VS Code y asegurate de que este en el PATH.")
                vsix_path = Path(args.vscode).resolve()
                if not vsix_path.exists():
                    raise RIFError(f"No se encontro el archivo VSIX: {vsix_path}")
                print(f"Instalando extension VS Code: {vsix_path.name}...")
                res = subprocess.run([code_cmd, "--install-extension", str(vsix_path)], check=False)
                if res.returncode != 0:
                    raise RIFError("Ocurrio un error al instalar la extension en VS Code.")
                print("Extension instalada exitosamente en Visual Studio Code.")
                return 0

            from .plugin_security import install_plugin_package
            dest = install_plugin_package(args.package, _rif_plugins_dir())
            print(f"plugin instalado: {dest}")
            return 0

        if args.cmd == "plugins":
            return _run_plugins_command(args)

        if args.cmd == "pip":
            if not args.pip_args:
                raise RIFError("usa: rif pip install package")
            import subprocess
            result = subprocess.run([sys.executable, "-m", "pip", *args.pip_args], check=False)
            return int(result.returncode)

        if args.cmd == "list":
            if args.item == "plugins":
                _print_plugins()
            return 0

        if args.cmd == "plug":
            from .plugin_security import install_plugin_folder
            dest = install_plugin_folder(Path(args.path), _rif_plugins_dir())
            print(f"plugin instalado: {dest}")
            return 0

        if args.cmd == "packs":
            import rif as _rif
            plugins_dir = Path(_rif.__file__).parent / "plugins"
            plugin_path = plugins_dir / args.plugin / "pack"
            if not plugin_path.exists():
                plugin_path = plugins_dir / args.plugin / "packs"
            if not plugin_path.exists() or not plugin_path.is_dir():
                print(f"Packs de plugin '{args.plugin}':")
                print("  (no hay packs disponibles o el plugin no existe)")
                return 0

            print(f"Packs disponibles para el plugin '{args.plugin}':")
            count = 0
            for item in sorted(plugin_path.iterdir()):
                if item.is_dir() and item.name != "__pycache__":
                    has_pack = any(path.suffix == ".pack" for path in item.glob("*.pack"))
                    if has_pack:
                        print(f"  - {item.name}")
                        count += 1
            if count == 0:
                print("  (no hay packs configurados en este plugin)")
            return 0

        if args.cmd == "clear":
            if args.item == "table":
                if args.subitem == "hashing":
                    from .table_modify import clear_table_hashing
                    clear_table_hashing()
                    return 0
                else:
                    print("Error: sub-item no soportado para clear table. Usa 'hashing'.", file=sys.stderr)
                    return 1

            if args.item == "cache":
                import shutil
                import rif as _rif
                rif_dir = Path(_rif.__file__).parent
                count = 0
                if getattr(args, "plugin", None):
                    plugin_dir = rif_dir / "plugins" / args.plugin
                    if not plugin_dir.exists():
                        print(f"Error: el plugin '{args.plugin}' no existe")
                        return 1
                    cache_dir = plugin_dir / ".cache"
                    if cache_dir.exists() and cache_dir.is_dir():
                        shutil.rmtree(cache_dir)
                        count += 1
                        print(f"Borrado directorio de cache .cache de {plugin_dir.name}")
                    for p in plugin_dir.rglob("__pycache__"):
                        if p.is_dir():
                            shutil.rmtree(p)
                            count += 1
                    if count == 0:
                        print(f"no habia cache para limpiar en el plugin '{args.plugin}'")
                    else:
                        print(f"limpieza del plugin '{args.plugin}' completada")
                else:
                    for p in rif_dir.rglob("__pycache__"):
                        if p.is_dir():
                            shutil.rmtree(p)
                            count += 1
                    print(f"Borrados {count} directorios __pycache__ de {rif_dir}")
            return 0

        if args.cmd == "zip":
            import zipfile
            import rif as _rif
            rif_dir = Path(_rif.__file__).parent
            output_zip = Path(args.output).resolve()

            count = 0
            with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
                for file_path in rif_dir.rglob("*"):
                    if "__pycache__" in file_path.parts:
                        continue
                    if file_path.is_file():

                        arcname = file_path.relative_to(rif_dir.parent)
                        zf.write(file_path, arcname)
                        count += 1
            print(f"Empaquetados {count} archivos en {output_zip}")
            return 0

        if args.cmd == "lex":
            text = Path(args.source).read_text(encoding="utf-8")
            p = Parser(text, args.source)
            cfg = p.lexer_config
            print(f"config.comment={cfg.comment!r}")
            print(f"config.separator={cfg.separator!r}")
            print(f"config.block={cfg.block!r}")
            print(f"config.encoding={cfg.encoding!r}")
            for line, indent, _, tokens in p.lexer.lex():
                values = " ".join(f"{t.kind}:{t.value}" for t in tokens)
                print(f"{line}:{indent}: {values}")
            return 0

        if args.cmd == "parse":
            text = Path(args.source).read_text(encoding="utf-8")
            program = Parser(text, args.source).parse()
            config = parse_packer_config(program)
            cfg = program.lexer_config
            print(f"comment={cfg.comment!r}")
            print(f"separator={cfg.separator!r}")
            print(f"block={cfg.block!r}")
            print(f"encoding={cfg.encoding!r}")
            print(f"sections={list(program.sections)}")
            print(f"world={program.world.values}")
            print(f"objects={list(program.objects)}")
            if program.regs.registers:
                print(f"regs.hiddesubs={program.regs.hiddesubs}")
                print(f"regs.order_column={program.regs.order_column}")
                print(f"regs.registers={[r.name for r in program.regs.registers]}")
                print(f"regs.aliases={program.regs.aliases}")
            if program.vars:
                print(f"vars={{{', '.join(f'{name}: {var.bits}' for name, var in program.vars.items())}}}")
            if program.type_defs.definitions:
                print(f"types={program.type_defs.order}")
                for name in program.type_defs.order:
                    type_def = program.type_defs.definitions[name]
                    print(f"type[{name}].size={type_def.size} values={type_def.values}")
            if program.data_definition.pattern:
                print(f"data_definition.pattern={program.data_definition.pattern}")
                print(f"data_definition.options={program.data_definition.options}")
            if program.memory.regions:
                print(f"memory={program.memory.order}")
                for name in program.memory.order:
                    region = program.memory.regions[name]
                    print(
                        f"memory[{name}].kind={region.kind} section={region.section} "
                        f"bytes={region.bytes} type={region.type_token} count={region.count}"
                    )
            if program.headers.blocks:
                print(f"headers={program.headers.order}")
                for name in program.headers.order:
                    header = program.headers.blocks[name]
                    table_rows = list(header.table.rows) if header.table else []
                    print(f"header[{name}].size={header.size} rows={table_rows}")
            for section, table in program.tables.items():
                print(f"table[{section}].fields={table.fields}")
                for name, row in table.rows.items():
                    print(f"table[{section}].{name}={row.values}")
            print(f"packer.enabled={config.enabled}")
            print(f"packer.fsystem={config.fsystem}")
            print(f"packer.ext={config.ext}")
            print(f"packer.sectpre={config.sectpre}")
            print(f"packer.subpre={config.subpre}")
            print(f"packer.definesec={sorted(config.defined_sections)}")
            print(f"packer.setpre={config.prefix_to_section}")
            print(f"packer.needsect={sorted(config.required_prefixes)}")
            print(f"packer.plugext={config.plugext}")
            print(f"packer.plugins={config.plugins}")
            print(f"packer.precompile={config.precompilers}")
            print(f"packer.types={config.types}")
            print(f"packer.output={config.output}")
            print(f"reader.sources={config.source_extensions}")
            return 0

        if args.cmd == "pack":
            result = pack_file(args.source, args.output)
            print(result.output_path)
            for fragment in result.fragments:
                print(f"+ {fragment}")
            return 0

        if args.cmd == "link":
            result = link_file(args.source, args.output)
            print(result.output_path)
            print(f"sections={list(result.program.sections)}")
            for fragment in result.fragments:
                print(f"+ {fragment}")
            return 0

        if args.cmd == "compile":
            if args.vscode is not None:
                vscode_plugins = [*(args.vscode or []), *(args.vscode_plugins or [])]
                if not vscode_plugins:
                    raise RIFError("usa: rif compile --vscode <plugin...> o rif compile --vscode --p <plugin...>")
                from .plugins.basics.cli.build_doc import build_vsix

                result = build_vsix(output=args.output, plugins=vscode_plugins, extensions=args.extensions, icon=args.icon)
                print("vscode_vsix=ok")
                print(f"vsix={result.output}")
                print(f"name={result.name}")
                print(f"version={result.version}")
                print("plugins=" + ",".join(result.plugins))
                print("extensions=" + ",".join(result.extensions))
                print(f"docs={result.docs}")
                print(f"syntax={result.syntax}")
                return 0

            if args.vscode_plugins:
                raise RIFError("usa --p junto con --vscode para construir una extension VSIX")

            if args.plugin:
                from .dedicated import create_dedicated_compiler

                result = create_dedicated_compiler(
                    args.plugin,
                    linked_plugins=args.link,
                    pack_name=args.name,
                    output=args.output,
                    make_exe=not args.no_exe,
                )
                print("dedicated_compiler=ok")
                print(f"plugin={result.plugin}")
                print("linked=" + ",".join(result.linked_plugins))
                print(f"root={result.root}")
                print(f"pack={result.pack_dir}")
                print(f"launcher={result.script_path}")
                if result.exe_path is not None:
                    print(f"exe={result.exe_path}")
                else:
                    print("exe=<no generado; instala PyInstaller o usa --no-exe>")
                return 0

            if not args.source or not args.instruction:
                raise RIFError(
                    "usa: rif compile <pack> <instruccion...>, "
                    "rif compile -p <plugin> [--link plugin ...] o "
                    "rif compile --vscode [--ext .rif] [--icon icon.png] --p <plugin...>"
                )
            instruction = " ".join(args.instruction)
            compiler = Compiler.from_file(args.source)
            result = compiler.compile_line(instruction)
            print(f"rule={result.rule_name}")
            print(f"bits={result.bits}")
            if result.hex is not None:
                print(f"hex={result.hex}")
            else:
                print("hex=<placeholder>")
                for resolved in result.resolved_placeholders:
                    placeholder = resolved.placeholder
                    print(f"resolved={placeholder.name}:{placeholder.kind}:{resolved.value}")
                for placeholder in result.placeholders:
                    print(f"placeholder={placeholder.name}:{placeholder.kind}:{placeholder.reason or ''}")
            return 0

        if args.cmd == "build":
            source_text = args.source_text
            if args.source_file:
                source_text = Path(args.source_file).read_text(encoding="utf-8")
            source_path = Path(args.source)
            if source_path.is_dir() and source_text:
                raise PackError("build de carpeta no acepta --source-text ni --source-file")

            use_packs_path = args.use
            if args.plugin and args.name:
                import rif as _rif
                plugin_pack_dir = Path(_rif.__file__).parent / "plugins" / args.plugin / "pack" / args.name
                if not plugin_pack_dir.exists():
                    plugin_pack_dir = Path(_rif.__file__).parent / "plugins" / args.plugin / "packs" / args.name
                if not plugin_pack_dir.exists() or not plugin_pack_dir.is_dir():
                    raise RIFError(f"el pack de plugin especificado no existe: {plugin_pack_dir}")
                use_packs_path = str(plugin_pack_dir)

            project_build = source_path.is_dir()
            result = build_file(args.source, args.output, source_text, write=project_build or args.output is not None, use_packs_path=use_packs_path)
            print(f"bytes={len(result.data)}")
            output = _build_output_path(args.source, args.output) if (project_build or args.output is not None) else None
            if output is not None:
                print(f"output={output}")
            if len(result.data) <= 256:
                print(f"hex={result.hex}")
            else:
                print(f"sha256={hashlib.sha256(result.data).hexdigest()}")
                print(f"hex.head={result.data[:32].hex()}")
                print(f"hex.tail={result.data[-32:].hex()}")
            for block in result.blocks:
                print(
                    f"block={block.name}:{block.kind}:off={block.physical_offset}:"
                    f"voff={block.virtual_offset}:size={block.physical_size}:vsize={block.virtual_size}"
                )
            for placeholder in result.placeholders:
                print(f"placeholder={placeholder.name}:{placeholder.kind}:{placeholder.reason or ''}")
            return 0

        if args.cmd == "table":
            from .table_modify import modify_table, format_tables, undo_table, redo_table, show_hashing_table

            backup = not args.no_backup

            if args.table_cmd == "modify":
                res = modify_table(
                    source=args.from_path,
                    plugin=args.plugin,
                    use=args.use,
                    file_name=args.file,
                    section=args.section,
                    operation_text=args.operation,
                    dry_run=args.dry_run,
                    backup=backup,
                    case_sensitive=args.case_sensitive,
                )
                print(res.summary)
                if res.preview:
                    print("Preview of changes:")
                    print(res.preview)
                return 0

            elif args.table_cmd == "format":
                results = format_tables(
                    source=args.from_path,
                    plugin=args.plugin,
                    use=args.use,
                    file_name=args.file,
                    table=args.table,
                    dry_run=args.dry_run,
                    backup=backup,
                    case_sensitive=args.case_sensitive,
                )
                for res in results:
                    print(res.summary)
                    if res.preview:
                        print(f"Format preview for {res.path}:")
                        print(res.preview)
                return 0

            elif args.table_cmd == "undo":
                res = undo_table(hash_str=args.hash)
                print(res.summary)
                if res.preview:
                    print("Restored state preview:")
                    print(res.preview)
                return 0

            elif args.table_cmd == "redo":
                res = redo_table(hash_str=args.hash)
                print(res.summary)
                if res.preview:
                    print("Reapplied state preview:")
                    print(res.preview)
                return 0

            elif args.table_cmd == "hashing-table":
                return show_hashing_table(open_file=args.open)

    except RIFError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    return 2


def _run_plugins_command(args: argparse.Namespace) -> int:
    if getattr(args, "plugins_cmd", None) == "load":
        src = Path(args.path)
        if not src.exists() or not src.is_dir():
            raise RIFError(f"ruta de plugin no valida o no es un directorio: {src}")
            
        from .plugin_security import load_manifest, validate_plugin_root, install_plugin_folder
        
                                        
        manifest = load_manifest(src)
        
                                                           
        validate_plugin_root(src)
        
                                             
        dest = _rif_plugins_dir() / manifest.name
        if dest.exists():
            ans = input(
                f"Este plugin ya existe, ¿Seguro que quieres reemplazar? "
                f"Reemplazarlo podría romper proyectos que usen este plugin. (s/n): "
            ).strip().lower()
            if ans not in {"s", "y", "si", "yes"}:
                print("Carga de plugin cancelada.")
                return 0
                                                                  
            import shutil
            shutil.rmtree(dest)
            
                                              
        install_plugin_folder(src, _rif_plugins_dir())
        print(f"plugin '{manifest.name}' cargado e instalado exitosamente en: {dest}")
        return 0

    if getattr(args, "plugins_cmd", None) == "init":
        import json
        name = args.name
        dest = Path.cwd() / name
        if dest.exists():
            raise RIFError(f"el directorio '{name}' ya existe en el directorio actual")
        dest.mkdir(parents=True)
        purpose = (
            "Este es un plugin generado por 'rif plugins init'. Se ha creado con el fin de proporcionar un "
            "punto de partida rapido para desarrollar nuevas funcionalidades, compiladores, componentes CLI y "
            "extensiones para el ecosistema Retargetable ISA Foundry (RIF). El proposito debe tener mas de doscientos "
            "caracteres para superar las validaciones de seguridad del entorno local y cumplir con las normas de sandboxing. "
            "¡Disfruta codificando!"
        )
        (dest / "pack.json").write_text(json.dumps({
            "name": name,
            "version": "0.1.0",
            "author": "Your Name",
            "purpose": purpose
        }, indent=4), encoding="utf-8")
        (dest / "fillables.py").write_text("# Registra tus fillables aqui\n", encoding="utf-8")
        (dest / "compiler.py").write_text("# Implementa logica del compilador aqui\n", encoding="utf-8")
        (dest / "cli.py").write_text("# Implementa comandos CLI aqui\n", encoding="utf-8")
        tests_dir = dest / "tests"
        tests_dir.mkdir()
        (tests_dir / f"test_{name}.py").write_text(f"def test_{name}():\n    assert True\n", encoding="utf-8")
        print(f"Estructura del plugin '{name}' creada exitosamente en: {dest}")
        return 0

    selected = [bool(args.list_plugins), args.delete is not None, args.doc is not None, args.info is not None, args.openp is not None]
    if sum(1 for item in selected if item) != 1:
        raise RIFError("usa una accion: rif plugins -list|-delete name|-doc name|-info name|-openp name")

    if args.list_plugins:
        _print_plugins()
        return 0

    if args.delete:
        import shutil
        root = _find_plugin_dir(args.delete)
        shutil.rmtree(root)
        print(f"plugin eliminado: {root}")
        return 0

    if args.doc:
        _find_plugin_dir(args.doc)
        return _run_help(f"plugin_{args.doc}", True)

    from .plugin_security import load_manifest, open_text_file, write_global_purpose

    name = args.info or args.openp
    root = _find_plugin_dir(name)
    manifest = load_manifest(root)

    if args.info:
        import json
        print(json.dumps(manifest.public_info, indent=2, ensure_ascii=False))
        print(f'purpose: usa "rif plugins -openp {manifest.name}" para abrirlo')
        return 0

    purpose_path = write_global_purpose(manifest)
    open_text_file(purpose_path)
    print(f"purpose escrito en: {purpose_path}")
    return 0


def _print_plugins() -> None:
    from .plugin_security import load_manifest

    print("Installed plugins:")
    count = 0
    for root in _plugin_dirs():
        try:
            manifest = load_manifest(root)
            print(f"  - {manifest.name} {manifest.version}")
        except RIFError as exc:
            print(f"  - {root.name} (invalido: {exc})")
        count += 1
    if count == 0:
        print("  (no plugins installed)")


def _plugin_dirs() -> list[Path]:
    from .parser import _plugin_roots

    out: list[Path] = []
    for root in _plugin_roots(Path.cwd()):
        if not root.exists():
            continue
        for item in sorted(root.iterdir()):
            if item.is_dir() and item.name != "__pycache__" and item not in out:
                out.append(item)
    return out


def _find_plugin_dir(name: str) -> Path:
    text = str(name).strip()
    if not text or any(sep in text for sep in ("/", "\\")) or text in {".", ".."}:
        raise RIFError(f"nombre de plugin inseguro: {name}")
    for root in _plugin_dirs():
        if root.name == text:
            return root
    raise RIFError(f"plugin no encontrado: {name}")


def _rif_plugins_dir() -> Path:
    import rif

    return Path(rif.__file__).parent / "plugins"


def _run_plugin_cli(args: list[str]) -> int:
    if not args:
        print("error: -pcli requiere nombre de plugin", file=sys.stderr)
        return 1

    plugin_name, plugin_args = args[0], args[1:]
    path = _find_plugin_cli(plugin_name)
    if path is None:
        print(f"error: plugin cli not found: {plugin_name}", file=sys.stderr)
        return 1

    module_name = f"rif.plugin_cli.{plugin_name}"
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        print(f"error: cannot load plugin cli: {path}", file=sys.stderr)
        return 1

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)

    entry = getattr(module, "main", None) or getattr(module, "run", None)
    if entry is None:
        print(f"error: plugin cli has no main(): {plugin_name}", file=sys.stderr)
        return 1

    result = entry(plugin_args)
    return int(result or 0)


def _find_plugin_cli(plugin_name: str) -> Path | None:
    roots = []
    cwd = Path.cwd().resolve()
    roots.extend(path / "plugins" for path in (cwd, *cwd.parents))
    roots.extend([
        Path(__file__).resolve().parents[1] / "plugins",
        Path(__file__).resolve().parent / "plugins",
    ])
    for root in roots:
        path = root / plugin_name / "cli.py"
        if path.exists():
            return path
    return None


def _build_output_path(source: str, output: str | None) -> Path | None:
    if output:
        return Path(output)

    source_path = Path(source)
    if not source_path.is_dir():
        return None

    from .linker import _find_project_pack
    try:
        pack = _find_project_pack(source_path)
    except Exception:
        return None

    program = Parser(pack.read_text(encoding="utf-8"), pack).parse()
    config = parse_packer_config(program)
    if config.output:
        output_path = Path(config.output)
        return output_path if output_path.is_absolute() else source_path / output_path
    return source_path / f"{pack.stem}{config.ext}"


def _help_root() -> Path:
    import rif
    return Path(rif.__file__).parent / "help"


def _help_topics() -> dict[str, Path]:
    root = _help_root()
    topics = {}
    if root.exists():
        topics.update({path.stem: path for path in sorted((root / "resources").rglob("*.md"))})

    from .parser import _plugin_roots
    plugin_roots = _plugin_roots(Path.cwd())
    for pr in plugin_roots:
        if not pr.exists(): continue
        for item in pr.iterdir():
            if item.is_dir() and item.name != "__pycache__":
                mds = list(item.glob("*.md"))
                if mds:

                    topics[f"plugin_{item.name}"] = mds[0]
                    topics[item.name] = mds[0] 
    return topics

def _inject_dynamic_help(index: Path, topics: dict[str, Path]) -> Path:
    import json
    import tempfile
    if not index.exists():
        return index
    html = index.read_text(encoding="utf-8")

    menu_html = '<div class="menu-group" data-category="paquetes">\n<div class="menu-category">Paquetes Instalados</div>\n<ul>\n'
    docs_json = []

    plugin_keys = [k for k in topics.keys() if k.startswith("plugin_")]
    if not plugin_keys:
        menu_html += '<li><span class="menu-link" style="opacity:0.5; cursor:default; padding-left:20px;">Ninguno</span></li>\n'
    else:
        for k in sorted(plugin_keys):
            name = k.replace("plugin_", "")
            path = topics[k]
            content = path.read_text(encoding="utf-8")
            menu_html += f'''<li>
              <a href="#" class="menu-link" data-key="{k}">
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"></path></svg>
                {name}
              </a>
            </li>\n'''
            docs_json.append(f'      "{k}": {json.dumps(content)}')

    menu_html += '</ul>\n</div>'

    import re
    html = re.sub(
        r'<!-- DYNAMIC_PLUGINS_MENU_START -->.*?<!-- DYNAMIC_PLUGINS_MENU_END -->',
        lambda m: f'<!-- DYNAMIC_PLUGINS_MENU_START -->\n{menu_html}\n<!-- DYNAMIC_PLUGINS_MENU_END -->',
        html, flags=re.DOTALL
    )

    docs_str = ",\n".join(docs_json)
    if docs_str:
        docs_str = ",\n" + docs_str

    html = re.sub(
        r'// DYNAMIC_PLUGINS_DOCS_START.*?// DYNAMIC_PLUGINS_DOCS_END',
        lambda m: f'// DYNAMIC_PLUGINS_DOCS_START\n{docs_str}\n// DYNAMIC_PLUGINS_DOCS_END',
        html, flags=re.DOTALL
    )

    try:
        index.write_text(html, encoding="utf-8")
        return index
    except (PermissionError, OSError):
        try:
            temp_dir = Path(tempfile.gettempdir())
            temp_index = temp_dir / "rif_help_index.html"
            temp_index.write_text(html, encoding="utf-8")
            print("Aviso: No se pudo escribir en el archivo de ayuda original por falta de permisos. Se usará una copia temporal.", file=sys.stderr)
            return temp_index
        except Exception:
            return index

def _plugin_help_entries() -> dict[str, dict[str, object]]:
    import tempfile
    from .parser import _plugin_roots

    entries: dict[str, dict[str, object]] = {}
    for plugins_root in _plugin_roots(Path.cwd()):
        if not plugins_root.exists():
            continue
        for plugin_dir in sorted(path for path in plugins_root.iterdir() if path.is_dir() and path.name != "__pycache__"):
            root_doc = _plugin_root_doc(plugin_dir)
            pages = _plugin_pages(plugin_dir)
            if root_doc is None and not pages:
                continue

            combined_parts: list[str] = []
            if root_doc is not None:
                combined_parts.append(root_doc.read_text(encoding="utf-8"))
            else:
                combined_parts.append(f"# {plugin_dir.name}")

            for page in pages:
                combined_parts.append(f"\n\n## {page['title']}\n\n")
                combined_parts.append(page["path"].read_text(encoding="utf-8"))

            combined_path = Path(tempfile.gettempdir()) / f"rif_help_plugin_{plugin_dir.name}.md"
            combined_path.write_text("\n".join(part.rstrip() for part in combined_parts if part is not None).rstrip() + "\n", encoding="utf-8")
            entries[plugin_dir.name] = {
                "name": plugin_dir.name,
                "combined": combined_path,
                "root": root_doc,
                "pages": pages,
            }
    return entries


def _plugin_root_doc(plugin_dir: Path) -> Path | None:
    preferred = ["readme.md", "README.md", "Readme.md"]
    for name in preferred:
        candidate = plugin_dir / name
        if candidate.exists():
            return candidate
    docs = sorted(path for path in plugin_dir.glob("*.md") if path.is_file())
    return docs[0] if docs else None


def _plugin_pages(plugin_dir: Path) -> list[dict[str, object]]:
    pages_dir = plugin_dir / "pages"
    if not pages_dir.exists() or not pages_dir.is_dir():
        return []

    pages: list[dict[str, object]] = []
    for path in sorted(pages_dir.glob("*.md")):
        match = __import__("re").match(r"^(\d+)_(.+)\.md$", path.name)
        if not match:
            continue
        order = int(match.group(1))
        key = match.group(2)
        title = key.replace("_", " ").replace("-", " ").strip().title()
        pages.append({"order": order, "key": key, "title": title, "path": path})
    return sorted(pages, key=lambda item: (item["order"], item["key"]))


def _help_topics() -> dict[str, Path]:
    root = _help_root()
    topics: dict[str, Path] = {}
    if root.exists():
        topics.update({path.stem: path for path in sorted((root / "resources").rglob("*.md"))})

    for entry in _plugin_help_entries().values():
        name = str(entry["name"])
        topics[f"plugin_{name}"] = entry["combined"]
        topics[name] = entry["combined"]
        for page in entry["pages"]:
            topics[f"{name}/{page['key']}"] = page["path"]
            topics[f"plugin_{name}/{page['key']}"] = page["path"]
    return topics


def _inject_dynamic_help(index: Path, topics: dict[str, Path]) -> Path:
    import json
    import re
    import tempfile

    if not index.exists():
        return index
    html = index.read_text(encoding="utf-8")

    menu_html = '<div class="menu-group" data-category="paquetes">\n<div class="menu-category">Paquetes Instalados</div>\n<ul>\n'
    docs_json: list[str] = []

    plugin_entries = _plugin_help_entries()
    if not plugin_entries:
        menu_html += '<li><span class="menu-link" style="opacity:0.5; cursor:default; padding-left:20px;">Ninguno</span></li>\n'
    else:
        for entry in plugin_entries.values():
            name = str(entry["name"])
            key = f"plugin_{name}"
            content = entry["combined"].read_text(encoding="utf-8")
            menu_html += f'''<li>
              <a href="#" class="menu-link" data-key="{key}">
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"></path></svg>
                {name}
              </a>
            </li>\n'''
            docs_json.append(f'      "{key}": {json.dumps(content)}')
            for page in entry["pages"]:
                page_key = f"plugin_{name}/{page['key']}"
                page_content = page["path"].read_text(encoding="utf-8")
                menu_html += f'''<li>
              <a href="#" class="menu-link" data-key="{page_key}" style="padding-left:34px;">
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5l5 5v11a2 2 0 01-2 2z"></path></svg>
                {page['title']}
              </a>
            </li>\n'''
                docs_json.append(f'      "{page_key}": {json.dumps(page_content)}')

    menu_html += '</ul>\n</div>'

    html = re.sub(
        r'<!-- DYNAMIC_PLUGINS_MENU_START -->.*?<!-- DYNAMIC_PLUGINS_MENU_END -->',
        lambda m: f'<!-- DYNAMIC_PLUGINS_MENU_START -->\n{menu_html}\n<!-- DYNAMIC_PLUGINS_MENU_END -->',
        html,
        flags=re.DOTALL,
    )

    docs_str = ",\n".join(docs_json)
    if docs_str:
        docs_str = ",\n" + docs_str

    html = re.sub(
        r'// DYNAMIC_PLUGINS_DOCS_START.*?// DYNAMIC_PLUGINS_DOCS_END',
        lambda m: f'// DYNAMIC_PLUGINS_DOCS_START\n{docs_str}\n// DYNAMIC_PLUGINS_DOCS_END',
        html,
        flags=re.DOTALL,
    )

    try:
        index.write_text(html, encoding="utf-8")
        return index
    except (PermissionError, OSError):
        try:
            temp_index = Path(tempfile.gettempdir()) / "rif_help_index.html"
            temp_index.write_text(html, encoding="utf-8")
            print("Aviso: No se pudo escribir en el archivo de ayuda original por falta de permisos. Se usara una copia temporal.", file=sys.stderr)
            return temp_index
        except Exception:
            return index


def _run_help(topic: str | None, open_index: bool) -> int:
    root = _help_root()
    index = root / "index.html"
    topics = _help_topics()

    resolved_index = _inject_dynamic_help(index, topics)


    if open_index or not topic:
        import webbrowser

        path_str = str(resolved_index.resolve())
        webbrowser.open(f"file:///{path_str.replace(chr(92), '/')}")
        print(f"Abriendo documentación en: {resolved_index}")
        if topic:  
            return 0

        _print_help_topics(topics)
        return 0

    if topic:
        path = topics.get(topic) or topics.get(f"plugin_{topic}")
        if path is None:
            print(f"help topic not found: {topic}", file=sys.stderr)
            _print_help_topics(topics)
            return 1
        print(path.read_text(encoding="utf-8"))
        return 0

    return 0


def _print_help_topics(topics: dict[str, Path]) -> None:
    for name in sorted(topics):
        print(name)


def run() -> None:
    """Punto de entrada de bootstrap de la CLI de RIF.

    Lanza SystemExit con el código de retorno devuelto por main().
    """
    raise SystemExit(main())


if __name__ == "__main__":
    run()
