from __future__ import annotations

import json
import re
import zipfile
from dataclasses import dataclass
from html import escape
from pathlib import Path
from typing import Any


DEFAULT_BUILD = {
    "name": "rif-docs",
    "displayName": "RIF Docs",
    "publisher": "rif",
    "version": "0.0.1",
    "description": "Documentacion generada por RIF",
    "author": {
        "name": "RIF Contributors",
        "url": "https://github.com",
    },
    "license": "MIT",
    "repository": "",
    "homepage": "",
    "bugs": "",
    "keywords": ["rif", "assembler", "retargetable"],
    "categories": ["Programming Languages", "Snippets", "Other"],
    "languageId": "rif",
    "extensions": [".rif"],
    "output": None,
}


@dataclass(frozen=True)
class VsixBuildResult:
    output: Path
    name: str
    version: str
    docs: int
    syntax: int
    plugins: tuple[str, ...]
    extensions: tuple[str, ...]


def main(args) -> int:
    result = build_vsix(
        project=getattr(args, "project", None),
        output=getattr(args, "output", None),
        plugins=getattr(args, "plugins", None),
        extensions=getattr(args, "extensions", None),
        icon=getattr(args, "icon", None),
    )
    _print_result(result)
    return 0


def build_vsix(
    *,
    project: str | Path | None = None,
    output: str | Path | None = None,
    plugins: list[str] | tuple[str, ...] | None = None,
    extensions: str | list[str] | tuple[str, ...] | None = None,
    icon: str | Path | None = None,
    build_overrides: dict[str, Any] | None = None,
) -> VsixBuildResult:
    project_path = _resolve_project(Path(project)) if project else None
    build = dict(DEFAULT_BUILD)
    if project_path is not None:
        build.update(_read_jsonc(project_path / "build.json", required=False))
    if build_overrides:
        build.update(build_overrides)

    doc: dict[str, Any] = {}
    syntax: dict[str, Any] = {}
    assets: dict[str, Path] = {}
    plugin_docs: dict[str, Path] = {}

    plugin_names = _plugin_names(plugins, build.get("plugins"))
    if project_path is None and not plugin_names:
        raise SystemExit("usa: rif compile -vscode <plugin...> o rif -pcli basics build-doc <proyecto>")

    _apply_plugin_bundle_defaults(build, plugin_names)
    _merge_plugin_vscode(plugin_names, doc, syntax, build, assets, plugin_docs)

    if project_path is not None:
        _merge_docs(doc, _read_jsonc(project_path / "doc.json", required=False))
        _merge_syntax(syntax, _read_jsonc(project_path / "syntaxs.json", required=False))

    _apply_explicit_extensions(build, extensions)
    _apply_explicit_icon(build, project_path or Path.cwd(), icon)
    _apply_minimal_defaults(project_path or Path.cwd(), doc, build, syntax)

    output_path = Path(output) if output else _output_path(project_path, build)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    files = _extension_files(project_path, doc, build, syntax, assets, plugin_docs)
    _write_vsix(output_path, files)

    return VsixBuildResult(
        output=output_path,
        name=str(build["name"]),
        version=str(build["version"]),
        docs=len(doc.get("words", {})),
        syntax=len(_syntax_words(doc, syntax)),
        plugins=tuple(plugin_names),
        extensions=tuple(_list_strings(build.get("extensions"))),
    )


def _print_result(result: VsixBuildResult) -> None:
    print(f"vsix={result.output}")
    print(f"name={result.name}")
    print(f"version={result.version}")
    if result.plugins:
        print("plugins=" + ",".join(result.plugins))
    if result.extensions:
        print("extensions=" + ",".join(result.extensions))
    print(f"docs={result.docs}")
    print(f"syntax={result.syntax}")


def _resolve_project(path: Path) -> Path:
    if path.exists():
        return path.resolve()

    fallback = Path.cwd() / path.name
    if fallback.exists():
        return fallback.resolve()

    raise SystemExit(f"project not found: {path}")


def _read_jsonc(path: Path, required: bool) -> dict[str, Any]:
    if not path.exists():
        if required:
            raise SystemExit(f"missing required file: {path}")
        return {}
    text = path.read_text(encoding="utf-8-sig")
    data = json.loads(_strip_json_comments(text))
    if not isinstance(data, dict):
        raise SystemExit(f"{path.name} must contain a JSON object")
    return data


def _merge_docs(base: dict[str, Any], override: dict[str, Any]) -> None:
    words_base = base.setdefault("words", {})
    words_override = override.get("words", {})
    if isinstance(words_base, dict) and isinstance(words_override, dict):
        words_base.update(words_override)


def _merge_syntax(base: dict[str, Any], override: dict[str, Any]) -> None:
    for list_key in ("directives", "registers", "keywords", "types", "builtins", "errors", "completions", "patterns", "instructions", "commands"):
        if list_key in override and isinstance(override[list_key], list):
            base_list = base.setdefault(list_key, [])
            if isinstance(base_list, list):
                for item in override[list_key]:
                    if item not in base_list:
                        base_list.append(item)


def _strip_json_comments(text: str) -> str:
    out: list[str] = []
    i = 0
    quote = False
    escaped = False
    while i < len(text):
        ch = text[i]
        nxt = text[i + 1] if i + 1 < len(text) else ""
        if escaped:
            out.append(ch)
            escaped = False
            i += 1
            continue
        if ch == "\\" and quote:
            out.append(ch)
            escaped = True
            i += 1
            continue
        if ch == '"':
            out.append(ch)
            quote = not quote
            i += 1
            continue
        if not quote and ch == "/" and nxt == "/":
            i += 2
            while i < len(text) and text[i] not in "\r\n":
                i += 1
            continue
        if not quote and ch == "/" and nxt == "*":
            i += 2
            while i + 1 < len(text) and not (text[i] == "*" and text[i + 1] == "/"):
                i += 1
            i += 2
            continue
        out.append(ch)
        i += 1
    return "".join(out)


def _output_path(project: Path | None, build: dict[str, Any]) -> Path:
    configured = build.get("output")
    if configured:
        output = Path(str(configured))
        base = project if project is not None else Path.cwd()
        return output if output.is_absolute() else base / output
    base = project if project is not None else Path.cwd() / "build" / "vscode"
    return base / f"{_slug(build['name'])}-{build['version']}.vsix"


def _plugin_names(
    explicit: list[str] | tuple[str, ...] | None,
    configured: Any,
) -> list[str]:
    out: list[str] = []
    for source in (explicit, configured):
        if isinstance(source, str):
            items = [source]
        elif isinstance(source, (list, tuple)):
            items = source
        else:
            items = []
        for item in items:
            name = str(item).strip()
            if name and name not in out:
                out.append(name)
    return out


def _merge_plugin_vscode(
    plugin_names: list[str],
    doc: dict[str, Any],
    syntax: dict[str, Any],
    build: dict[str, Any],
    assets: dict[str, Path],
    plugin_docs: dict[str, Path],
) -> None:
    plugins_dir = Path(__file__).resolve().parent.parent.parent
    for plugin_name in plugin_names:
        plugin_root = plugins_dir / plugin_name
        if not plugin_root.is_dir():
            raise SystemExit(f"plugin no encontrado: {plugin_name}")
        plugin_vscode = plugin_root / "vscode"
        if not plugin_vscode.is_dir():
            continue
        override_build = _read_jsonc(plugin_vscode / "build.json", required=False)
        _merge_build(build, override_build)
        
        # Auto-resolve icon source from plugin vscode folder
        if "icon" in override_build and "_iconSource" not in build:
            icon_rel = override_build["icon"]
            icon_src = plugin_vscode / icon_rel
            if icon_src.exists():
                build["_iconSource"] = str(icon_src)
        
        # Fallback to vscode/assets/icon.png etc.
        if "_iconSource" not in build and not build.get("icon"):
            for icon_name in ("icon.png", "icon.svg", "icon.jpg", "icon.jpeg"):
                candidate = plugin_vscode / "assets" / icon_name
                if candidate.exists():
                    build["_iconSource"] = str(candidate)
                    break

        _merge_docs(doc, _read_jsonc(plugin_vscode / "doc.json", required=False))
        _merge_syntax(syntax, _read_jsonc(plugin_vscode / "syntaxs.json", required=False))
        _collect_assets(plugin_name, plugin_vscode, assets)
        _collect_plugin_docs(plugin_name, plugin_root, plugin_docs)


def _merge_build(base: dict[str, Any], override: dict[str, Any]) -> None:
    for key, value in override.items():
        if key in {"extensions", "categories", "keywords", "badges"} and isinstance(value, list):
            base_list = base.setdefault(key, [])
            if not isinstance(base_list, list):
                base[key] = list(value)
                continue
            for item in value:
                if item not in base_list:
                    base_list.append(item)
        elif key in {"author", "repository", "bugs"} and isinstance(value, dict):
            current = base.setdefault(key, {})
            if isinstance(current, dict):
                current.update(value)
            else:
                base[key] = dict(value)
        elif key == "output":
            continue
        elif key not in {"name", "displayName", "description", "languageId"}:
            base[key] = value


def _apply_explicit_extensions(build: dict[str, Any], extensions: str | list[str] | tuple[str, ...] | None) -> None:
    normalized = _normalize_extensions(extensions)
    if normalized:
        build["extensions"] = normalized


def _normalize_extensions(value: str | list[str] | tuple[str, ...] | None) -> list[str]:
    if value is None:
        return []
    raw_items: list[str] = []
    if isinstance(value, str):
        raw_items = [value]
    elif isinstance(value, (list, tuple)):
        for item in value:
            raw_items.extend(str(item).split(","))
    else:
        raw_items = [str(value)]

    out: list[str] = []
    for item in raw_items:
        text = item.strip()
        if not text:
            continue
        if not text.startswith("."):
            text = f".{text}"
        if text not in out:
            out.append(text)
    return out


def _apply_explicit_icon(build: dict[str, Any], base: Path, icon: str | Path | None) -> None:
    if icon is None:
        return
    path = _resolve_asset_path(icon, base)
    if path is None or not path.is_file():
        raise SystemExit(f"icon not found: {icon}")
    if path.suffix.lower() not in {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}:
        raise SystemExit("VSIX icon must be png, jpg, jpeg, gif, webp or svg")
    build["_iconSource"] = str(path)


def _resolve_asset_path(value: str | Path, base: Path | None) -> Path | None:
    raw = Path(value)
    candidates: list[Path] = []
    if raw.is_absolute():
        candidates.append(raw)
    else:
        if base is not None:
            candidates.append(base / raw)
        candidates.append(Path.cwd() / raw)
        candidates.append(raw)
    for candidate in candidates:
        if candidate.exists():
            return candidate.resolve()
    return candidates[0].resolve() if candidates else None


def _collect_assets(plugin_name: str, plugin_vscode: Path, assets: dict[str, Path]) -> None:
    for folder_name in ("assets", "images", "media"):
        folder = plugin_vscode / folder_name
        if not folder.is_dir():
            continue
        for path in sorted(folder.rglob("*")):
            if path.is_file():
                rel = "/".join(path.relative_to(folder).parts)
                assets[f"{_slug(plugin_name)}/{rel}"] = path


def _collect_plugin_docs(plugin_name: str, plugin_root: Path, plugin_docs: dict[str, Path]) -> None:
    slug = _slug(plugin_name)
    for path in sorted(plugin_root.glob("*.md")):
        plugin_docs[f"{slug}/{path.name}"] = path
    pages = plugin_root / "pages"
    if pages.is_dir():
        for path in sorted(pages.rglob("*.md")):
            rel = "/".join(path.relative_to(pages).parts)
            plugin_docs[f"{slug}/pages/{rel}"] = path


def _apply_plugin_bundle_defaults(build: dict[str, Any], plugins: list[str]) -> None:
    if not plugins:
        return
    suffix = "-".join(_slug(name) for name in plugins)
    title = " ".join(name.upper() if len(name) <= 3 else name.title() for name in plugins)
    if not build.get("name") or build.get("name") == DEFAULT_BUILD["name"]:
        build["name"] = f"rif-{suffix}"
    if not build.get("displayName") or build.get("displayName") == DEFAULT_BUILD["displayName"]:
        build["displayName"] = f"RIF {title}"
    if not build.get("description") or build.get("description") == DEFAULT_BUILD["description"]:
        build["description"] = f"Soporte VS Code todo en uno para plugins RIF: {', '.join(plugins)}"
    if not build.get("languageId") or build.get("languageId") == DEFAULT_BUILD["languageId"]:
        build["languageId"] = f"rif-{suffix}"
    build["plugins"] = plugins


def _apply_minimal_defaults(project: Path, doc: dict[str, Any], build: dict[str, Any], syntax: dict[str, Any]) -> None:
    if not build.get("name") or build.get("name") == DEFAULT_BUILD["name"]:
        build["name"] = _slug(project.name or "rif-docs")
    if not build.get("displayName") or build.get("displayName") == DEFAULT_BUILD["displayName"]:
        build["displayName"] = f"RIF {project.name}".strip()
    if not build.get("description") or build.get("description") == DEFAULT_BUILD["description"]:
        build["description"] = f"Soporte VS Code generado para {project.name or 'RIF'}"

    words = doc.setdefault("words", {})
    if not isinstance(words, dict):
        doc["words"] = {}
        words = doc["words"]

    if not words and not syntax:
        for keyword in _minimal_keywords():
            words[keyword] = {
                "doc": [{
                    "type": "text",
                    "content": [f"Palabra basica de RIF: `{keyword}`."],
                }]
            }

    syntax.setdefault("keywords", [])
    if isinstance(syntax["keywords"], list):
        for keyword in _minimal_keywords():
            if keyword not in syntax["keywords"]:
                syntax["keywords"].append(keyword)
    syntax.setdefault("directives", [".pack", ".world", ".sections", ".rules", ".types", ".regs", ".DATA_DEFINITION"])


def _minimal_keywords() -> list[str]:
    return [
        "need", "emit", "call", "ON", "OFF", "switch", "case", "end_instruction",
        "align", "pad", "reloc", "reldis", "bitcat", "bitsize", "bitfit",
        "trunc", "zext", "sext", "lt", "lte", "gt", "gte",
    ]


def _extension_files(
    project: Path | None,
    doc: dict[str, Any],
    build: dict[str, Any],
    syntax: dict[str, Any],
    assets: dict[str, Path],
    plugin_docs: dict[str, Path],
) -> dict[str, bytes]:
    build_for_package = dict(build)
    icon_bundle = _icon_bundle(project, build_for_package)
    if icon_bundle:
        _icon_path, icon_archive_name = icon_bundle
        build_for_package["icon"] = icon_archive_name

    package = _package_json(build_for_package, syntax)
    readme = _readme(project, doc, build_for_package)
    manifest = _vsix_manifest(build_for_package)
    content_types = _content_types()

    files: dict[str, bytes] = {
        "[Content_Types].xml": content_types.encode("utf-8"),
        "extension.vsixmanifest": manifest.encode("utf-8"),
        "extension/package.json": _json_bytes(package),
        "extension/README.md": readme.encode("utf-8"),
        "extension/rif-docs.json": _json_bytes(doc),
        "extension/rif-completions.json": _json_bytes(_completions_json(doc, syntax)),
        "extension/rif-diagnostics.json": _json_bytes(_diagnostics_json(syntax)),
        "extension/extension.js": _extension_js().encode("utf-8"),
        "extension/language-configuration.json": _json_bytes(_language_configuration()),
    }

    grammar = _grammar_json(build, doc, syntax)
    files["extension/syntaxes/rif.tmLanguage.json"] = _json_bytes(grammar)
    snippets = _snippets_json(doc, syntax)
    files["extension/snippets/rif.code-snippets"] = _json_bytes(snippets)

    for name, content in _word_docs(doc).items():
        files[f"extension/docs/{name}.md"] = content.encode("utf-8")

    if project is not None:
        for archive_name, path in _markdown_files(project, doc).items():
            files[f"extension/docs/project/{archive_name}"] = path.read_bytes()

    for archive_name, path in sorted(assets.items()):
        files[f"extension/assets/{archive_name}"] = path.read_bytes()
    for archive_name, path in sorted(plugin_docs.items()):
        files[f"extension/docs/plugins/{archive_name}"] = path.read_bytes()
    if icon_bundle:
        icon_path, icon_archive_name = icon_bundle
        files[f"extension/{icon_archive_name}"] = icon_path.read_bytes()

    return files


def _icon_bundle(project: Path | None, build: dict[str, Any]) -> tuple[Path, str] | None:
    source = build.get("_iconSource")
    path: Path | None = Path(str(source)) if source else None
    if path is None:
        icon = build.get("icon")
        if isinstance(icon, str) and icon and "://" not in icon:
            path = _resolve_asset_path(icon, project or Path.cwd())
    if path is None or not path.exists() or not path.is_file():
        return None
    suffix = path.suffix.lower() or ".png"
    return path.resolve(), f"assets/icon{suffix}"


def _package_json(build: dict[str, Any], syntax: dict[str, Any]) -> dict[str, Any]:
    language_id = str(build.get("languageId") or build["name"])
    extensions = build.get("extensions") or [".rif"]
    if not isinstance(extensions, list):
        extensions = [str(extensions)]

    contributes: dict[str, Any] = {
        "languages": [{
            "id": language_id,
            "aliases": [str(build.get("displayName") or build["name"]), language_id],
            "extensions": extensions,
            "configuration": "./language-configuration.json",
        }],
        "grammars": [{
            "language": language_id,
            "scopeName": f"source.{language_id}",
            "path": "./syntaxes/rif.tmLanguage.json",
        }],
        "snippets": [{
            "language": language_id,
            "path": "./snippets/rif.code-snippets",
        }],
        "configuration": {
            "title": str(build.get("displayName") or build["name"]),
            "properties": {
                f"{language_id}.diagnostics.enabled": {
                    "type": "boolean",
                    "default": True,
                    "description": "Enable RIF diagnostics for this generated language bundle.",
                },
                f"{language_id}.completion.detail": {
                    "type": "boolean",
                    "default": True,
                    "description": "Show generated plugin documentation inside completion details.",
                },
            },
        },
        "semanticTokenTypes": [
            {"id": "register", "superType": "variable", "description": "CPU register"},
            {"id": "directive", "superType": "keyword", "description": "RIF or target directive"},
            {"id": "label", "superType": "class", "description": "Assembly label"},
            {"id": "fillable", "superType": "function", "description": "RIF fillable macro"},
        ],
    }

    default_command = {
        "command": f"{language_id}.openGeneratedDocs",
        "title": "RIF: Open Generated Docs",
        "category": "RIF",
    }
    commands = syntax.get("commands")
    contributes["commands"] = [default_command]
    if isinstance(commands, list):
        for command in commands:
            if command not in contributes["commands"]:
                contributes["commands"].append(command)
    contributes["menus"] = {
        "commandPalette": [
            {"command": default_command["command"], "when": f"editorLangId == {language_id}"}
        ]
    }

    package = {
        "name": _slug(str(build["name"])),
        "displayName": str(build.get("displayName") or build["name"]),
        "publisher": _slug(str(build.get("publisher") or "rif")),
        "version": str(build.get("version") or "0.0.1"),
        "description": str(build.get("description") or "Documentacion generada por RIF"),
        "author": build.get("author") or DEFAULT_BUILD["author"],
        "license": str(build.get("license") or DEFAULT_BUILD["license"]),
        "engines": {"vscode": str(build.get("vscodeEngine") or "^1.80.0")},
        "categories": build.get("categories") or DEFAULT_BUILD["categories"],
        "keywords": build.get("keywords") or DEFAULT_BUILD["keywords"],
        "activationEvents": [f"onLanguage:{language_id}"],
        "main": "./extension.js",
        "contributes": contributes,
    }
    for key in ("repository", "homepage", "bugs", "icon", "galleryBanner"):
        if build.get(key):
            package[key] = build[key]
    return package


def _readme(project: Path | None, doc: dict[str, Any], build: dict[str, Any]) -> str:
    readme_ref = doc.get("readme")
    if project is not None and isinstance(readme_ref, str):
        path = project / readme_ref
        if path.exists():
            return path.read_text(encoding="utf-8")

    lines = [f"# {build.get('displayName') or build['name']}", ""]
    lines.append(str(build.get("description") or "Documentacion generada por RIF"))
    lines.append("")
    author = build.get("author")
    if isinstance(author, dict) and author.get("name"):
        lines.append(f"Autor: {author['name']}")
    elif isinstance(author, str):
        lines.append(f"Autor: {author}")
    if build.get("version"):
        lines.append(f"Version: {build['version']}")
    if build.get("license"):
        lines.append(f"Licencia: {build['license']}")
    if len(lines) > 3:
        lines.append("")
    plugins = build.get("plugins")
    if isinstance(plugins, list) and plugins:
        lines.append("Plugins incluidos: " + ", ".join(str(item) for item in plugins))
        lines.append("")
        lines.append("## Plugin Docs")
        lines.append("")
        for plugin in plugins:
            slug = _slug(str(plugin))
            lines.append(f"- `{plugin}` docs are bundled under `docs/plugins/{slug}/`.")
        lines.append("")
    lines.extend([
        "## Features",
        "",
        "- Syntax highlighting generated from plugin vocabularies.",
        "- Hover documentation with examples and references.",
        "- Snippet completions for instructions, fillables and common blocks.",
        "- Regex diagnostics with optional quick fixes.",
        "- Document symbols for labels and sections.",
        "",
    ])
    words = doc.get("words", {})
    if isinstance(words, dict):
        for name, value in words.items():
            lines.append(f"## {name}")
            lines.append("")
            lines.append(_render_word(value))
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _word_docs(doc: dict[str, Any]) -> dict[str, str]:
    words = doc.get("words", {})
    if not isinstance(words, dict):
        return {}
    return {_slug(name): f"# {name}\n\n{_render_word(value)}\n" for name, value in words.items()}


def _markdown_files(project: Path, doc: dict[str, Any]) -> dict[str, Path]:
    out: dict[str, Path] = {}
    ignored = {".git", "__pycache__", ".rif-build"}
    for path in sorted(project.rglob("*.md")):
        if any(part in ignored for part in path.relative_to(project).parts):
            continue
        archive_name = "/".join(path.relative_to(project).parts)
        out[archive_name] = path

    readme_ref = doc.get("readme")
    if isinstance(readme_ref, str):
        path = project / readme_ref
        if path.exists() and path.suffix.lower() == ".md":
            out.setdefault(path.name, path)

    return out


def _render_word(value: Any) -> str:
    if not isinstance(value, dict):
        return str(value)

    parts: list[str] = []
    docs = value.get("doc", [])
    if isinstance(docs, list):
        for block in docs:
            if not isinstance(block, dict):
                continue
            content = block.get("content", [])
            if isinstance(content, str):
                content = [content]
            block_type = str(block.get("type") or "text")
            if block_type == "code":
                parts.append("```rif")
                parts.extend(str(item) for item in content)
                parts.append("```")
            elif block_type == "image":
                src = str(block.get("src") or (content[0] if content else ""))
                alt = str(block.get("alt") or block.get("title") or "image")
                if src:
                    parts.append(f"![{alt}]({src})")
                    caption = block.get("caption")
                    if caption:
                        parts.append(f"*{caption}*")
            elif block_type in {"note", "warning", "tip"}:
                title = block_type.upper()
                parts.append(f"> **{title}:** " + " ".join(str(item) for item in content))
            elif block_type == "list":
                parts.extend(f"- {item}" for item in content)
            else:
                parts.extend(str(item) for item in content)
            link = block.get("link")
            if link:
                parts.append(f"[link]({link})")
            parts.append("")

    links = value.get("links", [])
    if isinstance(links, list) and links:
        parts.append("## Links")
        parts.extend(f"- {link}" for link in links)

    return "\n".join(parts).strip()


def _grammar_json(build: dict[str, Any], doc: dict[str, Any], syntax: dict[str, Any]) -> dict[str, Any]:
    language_id = str(build.get("languageId") or build["name"])
    words = _syntax_words(doc, syntax)
    directives = _list_strings(syntax.get("directives"))
    types = _list_strings(syntax.get("types"))
    registers = _list_strings(syntax.get("registers"))
    builtins = _list_strings(syntax.get("builtins"))

    patterns: list[dict[str, Any]] = [
        {"name": "comment.line.semicolon.rif", "match": r";.*$"},
        {"name": "comment.line.number-sign.rif", "match": r"#.*$"},
        {"name": "string.quoted.double.rif", "begin": '"', "end": '"', "patterns": [{"name": "constant.character.escape.rif", "match": r"\\."}]},
        {"name": "constant.numeric.rif", "match": r"\b(0x[0-9A-Fa-f_]+|0b[01_]+|[0-9][0-9_]*)\b"},
        {"name": "keyword.operator.rif", "match": r"[=\+\-\*\/&\|<>!~,:]"},
        {"name": "entity.name.function.label.rif", "match": r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*(:)", "captures": {"1": {"name": "entity.name.function.label.rif"}, "2": {"name": "keyword.operator.rif"}}},
        {"name": "support.function.fillable.rif", "match": r"@[A-Za-z_][A-Za-z0-9_]*"},
        {"name": "support.function.fillable.reverse.rif", "match": r"@(?:[^@\"']|\"(?:\\.|[^\"])*\"|'(?:\\.|[^'])*')+@[A-Za-z_][A-Za-z0-9_]*"},
        {"name": "variable.other.symbol.rif", "match": r"\b[A-Za-z_][A-Za-z0-9_]*(?=\s+(?:u8|u16|u32|s8|b8|b16|b32)\[)"},
    ]

    if directives:
        patterns.append({"name": "keyword.control.directive.rif", "match": _word_pattern(directives, boundary=False)})
    if words:
        patterns.append({"name": "keyword.control.rif", "match": _word_pattern(words)})
    if builtins:
        patterns.append({"name": "support.function.builtin.rif", "match": _word_pattern(builtins)})
    if types:
        patterns.append({"name": "storage.type.rif", "match": _word_pattern(types)})
    if registers:
        patterns.append({"name": "constant.language.register.rif", "match": _word_pattern(registers)})

    custom_patterns = syntax.get("patterns")
    if isinstance(custom_patterns, list):
        for pattern in custom_patterns:
            if isinstance(pattern, dict) and isinstance(pattern.get("match"), str):
                patterns.append({
                    "name": str(pattern.get("name") or "meta.rif"),
                    "match": pattern["match"],
                })

    return {
        "scopeName": f"source.{language_id}",
        "patterns": patterns,
    }


def _snippets_json(doc: dict[str, Any], syntax: dict[str, Any]) -> dict[str, Any]:
    words = doc.get("words", {})
    snippets = {
        name: {
            "prefix": name,
            "body": [name],
            "description": _first_text(value) or f"RIF word {name}",
        }
        for name, value in words.items()
    } if isinstance(words, dict) else {}
    for key in ("snippets", "completions", "predictions"):
        items = syntax.get(key)
        if not isinstance(items, list):
            continue
        for item in items:
            completion = _completion_item(item)
            if not completion:
                continue
            label = completion["label"]
            body = str(completion["insertText"]).splitlines() or [label]
            snippets.setdefault(label, {
                "prefix": label,
                "body": body,
                "description": completion.get("documentation") or completion.get("detail") or f"RIF snippet {label}",
            })
    return snippets


def _completions_json(doc: dict[str, Any], syntax: dict[str, Any]) -> list[dict[str, Any]]:
    completions: list[dict[str, Any]] = []
    seen: set[str] = set()

    words = doc.get("words", {})
    if isinstance(words, dict):
        for label, value in words.items():
            seen.add(str(label))
            completions.append({
                "label": str(label),
                "insertText": str(label),
                "detail": "RIF",
                "documentation": _render_word(value),
                "kind": "Keyword",
                "source": "doc",
            })

    for key in ("completions", "predictions", "prediction", "snippets"):
        items = syntax.get(key)
        if isinstance(items, list):
            for item in items:
                completion = _completion_item(item)
                if completion and completion["label"] not in seen:
                    seen.add(completion["label"])
                    completions.append(completion)

    for label in _syntax_words(doc, syntax):
        if label not in seen:
            seen.add(label)
            completions.append({
                "label": label,
                "insertText": label,
                "detail": "RIF",
                "documentation": "",
                "kind": "Keyword",
                "source": "syntax",
            })

    return completions


def _completion_item(item: Any) -> dict[str, Any] | None:
    if isinstance(item, str):
        return {"label": item, "insertText": item, "detail": "RIF", "documentation": "", "kind": "Keyword"}
    if not isinstance(item, dict):
        return None
    label = item.get("label") or item.get("name") or item.get("prefix")
    if not label:
        return None
    return {
        "label": str(label),
        "insertText": str(item.get("insertText") or item.get("body") or label),
        "detail": str(item.get("detail") or item.get("type") or "RIF"),
        "documentation": str(item.get("documentation") or item.get("doc") or item.get("description") or ""),
        "kind": str(item.get("kind") or "Keyword"),
        "filterText": str(item.get("filterText") or label),
        "sortText": str(item.get("sortText") or item.get("priority") or label),
        "source": str(item.get("source") or ""),
    }


def _diagnostics_json(syntax: dict[str, Any]) -> list[dict[str, Any]]:
    errors = syntax.get("errors")
    if not isinstance(errors, list):
        return []
    out: list[dict[str, Any]] = []
    for item in errors:
        if isinstance(item, dict) and isinstance(item.get("match"), str):
            out.append({
                "match": item["match"],
                "message": str(item.get("message") or item.get("name") or "RIF diagnostic"),
                "severity": str(item.get("severity") or "warning"),
                "code": str(item.get("code") or item.get("name") or ""),
                "source": str(item.get("source") or "RIF"),
                "suggest": item.get("suggest") if isinstance(item.get("suggest"), str) else "",
            })
    return out


def _first_text(value: Any) -> str:
    if not isinstance(value, dict):
        return ""
    docs = value.get("doc", [])
    if not isinstance(docs, list):
        return ""
    for block in docs:
        if isinstance(block, dict) and block.get("type") == "text":
            content = block.get("content", [])
            if isinstance(content, list) and content:
                return str(content[0])
            if isinstance(content, str):
                return content
    return ""


def _syntax_words(doc: dict[str, Any], syntax: dict[str, Any]) -> list[str]:
    words: list[str] = []
    doc_words = doc.get("words")
    if isinstance(doc_words, dict):
        words.extend(str(item) for item in doc_words.keys())
    for key in ("keywords", "words", "instructions"):
        words.extend(_list_strings(syntax.get(key)))
    return sorted(set(words))


def _list_strings(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        return [str(item) for item in value.keys()]
    if isinstance(value, list):
        out: list[str] = []
        for item in value:
            if isinstance(item, str):
                out.append(item)
            elif isinstance(item, dict):
                label = item.get("label") or item.get("name") or item.get("prefix")
                if label:
                    out.append(str(label))
        return out
    return []


def _word_pattern(words: list[str], boundary: bool = True) -> str:
    escaped = "|".join(re.escape(word) for word in sorted(set(words), key=len, reverse=True))
    if not escaped:
        return r"\b\B"
    if boundary:
        return rf"\b({escaped})\b"
    return rf"({escaped})"


def _vsix_manifest(build: dict[str, Any]) -> str:
    identity = escape(_slug(str(build["name"])))
    publisher = escape(_slug(str(build.get("publisher") or "rif")))
    version = escape(str(build.get("version") or "0.0.1"))
    display = escape(str(build.get("displayName") or build["name"]))
    description = escape(str(build.get("description") or "Documentacion generada por RIF"))
    return f"""<?xml version="1.0" encoding="utf-8"?>
<PackageManifest Version="2.0.0" xmlns="http://schemas.microsoft.com/developer/vsx-schema/2011">
  <Metadata>
    <Identity Id="{identity}" Version="{version}" Language="en-US" Publisher="{publisher}" />
    <DisplayName>{display}</DisplayName>
    <Description>{description}</Description>
    <Tags>{escape(','.join(_list_strings(build.get('keywords')) or ['rif']))}</Tags>
    <Categories>Visual Studio Code</Categories>
    <GalleryFlags>Public</GalleryFlags>
    <Properties>
      <Property Id="Microsoft.VisualStudio.Code.Engine" Value="^1.80.0" />
    </Properties>
  </Metadata>
  <Installation>
    <InstallationTarget Id="Microsoft.VisualStudio.Code" />
  </Installation>
  <Dependencies />
  <Assets>
    <Asset Type="Microsoft.VisualStudio.Code.Manifest" Path="extension/package.json" Addressable="true" />
  </Assets>
</PackageManifest>
"""


def _content_types() -> str:
    return """<?xml version="1.0" encoding="utf-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="json" ContentType="application/json" />
  <Default Extension="js" ContentType="application/javascript" />
  <Default Extension="md" ContentType="text/markdown" />
  <Default Extension="png" ContentType="image/png" />
  <Default Extension="jpg" ContentType="image/jpeg" />
  <Default Extension="jpeg" ContentType="image/jpeg" />
  <Default Extension="gif" ContentType="image/gif" />
  <Default Extension="svg" ContentType="image/svg+xml" />
  <Default Extension="webp" ContentType="image/webp" />
  <Default Extension="txt" ContentType="text/plain" />
  <Default Extension="vsixmanifest" ContentType="text/xml" />
  <Default Extension="xml" ContentType="text/xml" />
</Types>
"""


def _language_configuration() -> dict[str, Any]:
    return {
        "comments": {
            "lineComment": ";",
        },
        "brackets": [["[", "]"], ["(", ")"], ["{", "}"]],
        "autoClosingPairs": [
            {"open": '"', "close": '"'},
            {"open": "[", "close": "]"},
            {"open": "(", "close": ")"},
            {"open": "{", "close": "}"},
        ],
        "surroundingPairs": [
            {"open": '"', "close": '"'},
            {"open": "[", "close": "]"},
            {"open": "(", "close": ")"},
        ],
        "folding": {
            "markers": {
                "start": "^\\s*;\\s*#region\\b",
                "end": "^\\s*;\\s*#endregion\\b",
            }
        },
        "wordPattern": r"(@?[A-Za-z_][A-Za-z0-9_-]*|0x[0-9A-Fa-f_]+|0b[01_]+)",
    }


def _extension_js() -> str:
    return r"""const vscode = require('vscode');

function loadJson(context, name, fallback) {
  try {
    const uri = vscode.Uri.joinPath(context.extensionUri, name);
    const bytes = require('fs').readFileSync(uri.fsPath, 'utf8');
    return JSON.parse(bytes);
  } catch (_) {
    return fallback;
  }
}

function itemKind(name) {
  const value = String(name || '').toLowerCase();
  return vscode.CompletionItemKind[value[0].toUpperCase() + value.slice(1)] || vscode.CompletionItemKind.Keyword;
}

function markdown(context, text) {
  const rendered = String(text || '').replace(/\]\((assets\/[^)]+)\)/g, (_match, assetPath) => {
    return `](${vscode.Uri.joinPath(context.extensionUri, assetPath).toString()})`;
  });
  const md = new vscode.MarkdownString(rendered);
  md.isTrusted = true;
  md.supportHtml = true;
  return md;
}

function activate(context) {
  const pkg = require('./package.json');
  const language = (((pkg.contributes || {}).languages || [])[0] || {}).id || 'rif';
  const openDocsCommand = `${language}.openGeneratedDocs`;
  const docs = loadJson(context, 'rif-docs.json', { words: {} });
  const completions = loadJson(context, 'rif-completions.json', []);
  const diagnostics = loadJson(context, 'rif-diagnostics.json', []);
  const collection = vscode.languages.createDiagnosticCollection('rif');
  const diagnosticRules = new Map();
  context.subscriptions.push(collection);

  context.subscriptions.push(vscode.commands.registerCommand(openDocsCommand, async () => {
    const uri = vscode.Uri.joinPath(context.extensionUri, 'README.md');
    const document = await vscode.workspace.openTextDocument(uri);
    await vscode.window.showTextDocument(document, { preview: true });
  }));

  context.subscriptions.push(vscode.languages.registerCompletionItemProvider(language, {
    provideCompletionItems() {
      return completions.map(entry => {
        const item = new vscode.CompletionItem(entry.label, itemKind(entry.kind));
        const insertText = entry.insertText || entry.label;
        item.insertText = String(insertText).includes('$')
          ? new vscode.SnippetString(insertText)
          : insertText;
        item.detail = entry.detail || 'RIF';
        if (entry.documentation) item.documentation = markdown(context, entry.documentation);
        item.filterText = entry.filterText || entry.label;
        item.sortText = entry.sortText || entry.label;
        return item;
      });
    }
  }, '@', '.', '_', ':'));

  context.subscriptions.push(vscode.languages.registerHoverProvider(language, {
    provideHover(document, position) {
      const range = document.getWordRangeAtPosition(position, /@?[A-Za-z_][A-Za-z0-9_-]*/);
      if (!range) return;
      const word = document.getText(range);
      const info = docs.words && (docs.words[word] || docs.words[word.replace(/^@/, '')]);
      if (!info) return;
      const match = completions.find(entry => entry.label === word || entry.label === word.replace(/^@/, ''));
      return new vscode.Hover(markdown(context, match && match.documentation ? match.documentation : word), range);
    }
  }));

  context.subscriptions.push(vscode.languages.registerDocumentSymbolProvider(language, {
    provideDocumentSymbols(document) {
      const symbols = [];
      for (let line = 0; line < document.lineCount; line++) {
        const text = document.lineAt(line).text;
        const section = text.match(/^\s*(\.[A-Za-z_][A-Za-z0-9_.-]*)\s*$/);
        const label = text.match(/^\s*([A-Za-z_][A-Za-z0-9_]*)\s*:/);
        if (section) {
          symbols.push(new vscode.DocumentSymbol(section[1], 'RIF section', vscode.SymbolKind.Namespace, document.lineAt(line).range, document.lineAt(line).range));
        } else if (label) {
          symbols.push(new vscode.DocumentSymbol(label[1], 'label', vscode.SymbolKind.Function, document.lineAt(line).range, document.lineAt(line).range));
        }
      }
      return symbols;
    }
  }));

  context.subscriptions.push(vscode.languages.registerCodeActionsProvider(language, {
    provideCodeActions(document, range, context) {
      const actions = [];
      for (const diagnostic of context.diagnostics) {
        const rule = diagnosticRules.get(diagnostic.code);
        if (!rule || !rule.suggest) continue;
        const fix = new vscode.CodeAction(rule.suggest, vscode.CodeActionKind.QuickFix);
        fix.diagnostics = [diagnostic];
        fix.isPreferred = true;
        actions.push(fix);
      }
      return actions;
    }
  }, { providedCodeActionKinds: [vscode.CodeActionKind.QuickFix] }));

  function refresh(document) {
    if (document.languageId !== language) return;
    const enabled = vscode.workspace.getConfiguration(language).get('diagnostics.enabled', true);
    if (!enabled) {
      collection.delete(document.uri);
      return;
    }
    const found = [];
    const text = document.getText();
    diagnostics.forEach((rule, index) => {
      try {
        const regex = new RegExp(rule.match, 'gm');
        let match;
        while ((match = regex.exec(text))) {
          const start = document.positionAt(match.index);
          const end = document.positionAt(match.index + Math.max(1, match[0].length));
          const level = String(rule.severity || 'warning').toLowerCase();
          const severity = level === 'error'
            ? vscode.DiagnosticSeverity.Error
            : level === 'info'
              ? vscode.DiagnosticSeverity.Information
              : level === 'hint'
                ? vscode.DiagnosticSeverity.Hint
                : vscode.DiagnosticSeverity.Warning;
          const diagnostic = new vscode.Diagnostic(new vscode.Range(start, end), rule.message || 'RIF diagnostic', severity);
          diagnostic.source = rule.source || 'RIF';
          diagnostic.code = rule.code || `rif-${index}`;
          diagnosticRules.set(diagnostic.code, rule);
          found.push(diagnostic);
        }
      } catch (_) {}
    });
    collection.set(document.uri, found);
  }

  vscode.workspace.textDocuments.forEach(refresh);
  context.subscriptions.push(vscode.workspace.onDidOpenTextDocument(refresh));
  context.subscriptions.push(vscode.workspace.onDidChangeTextDocument(event => refresh(event.document)));
  context.subscriptions.push(vscode.workspace.onDidCloseTextDocument(document => collection.delete(document.uri)));
}

function deactivate() {}

module.exports = { activate, deactivate };
"""


def _write_vsix(output: Path, files: dict[str, bytes]) -> None:
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, data in sorted(files.items()):
            archive.writestr(name, data)


def _json_bytes(data: Any) -> bytes:
    return (json.dumps(data, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def _slug(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9_-]+", "-", value.strip().lower()).strip("-")
    return slug or "rif"
