from __future__ import annotations

import json
import re
import zipfile
from html import escape
from pathlib import Path
from typing import Any


DEFAULT_BUILD = {
    "name": "rif-docs",
    "displayName": "RIF Docs",
    "publisher": "rif",
    "version": "0.0.1",
    "description": "Documentacion generada por RIF",
    "languageId": "rif",
    "extensions": [".rif"],
    "output": None,
}


def main(args) -> int:
    project = _resolve_project(Path(args.project))
    doc = _read_jsonc(project / "doc.json", required=True)
    build = {**DEFAULT_BUILD, **_read_jsonc(project / "build.json", required=False)}
    syntax = _read_jsonc(project / "syntaxs.json", required=False)

    output = Path(args.output) if args.output else _output_path(project, build)
    output.parent.mkdir(parents=True, exist_ok=True)

    files = _extension_files(project, doc, build, syntax)
    _write_vsix(output, files)

    print(f"vsix={output}")
    print(f"name={build['name']}")
    print(f"version={build['version']}")
    print(f"docs={len(doc.get('words', {}))}")
    return 0


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


def _output_path(project: Path, build: dict[str, Any]) -> Path:
    configured = build.get("output")
    if configured:
        output = Path(str(configured))
        return output if output.is_absolute() else project / output
    return project / f"{_slug(build['name'])}-{build['version']}.vsix"


def _extension_files(project: Path, doc: dict[str, Any], build: dict[str, Any], syntax: dict[str, Any]) -> dict[str, bytes]:
    package = _package_json(build, syntax)
    readme = _readme(project, doc, build)
    manifest = _vsix_manifest(build)
    content_types = _content_types()

    files: dict[str, bytes] = {
        "[Content_Types].xml": content_types.encode("utf-8"),
        "extension.vsixmanifest": manifest.encode("utf-8"),
        "extension/package.json": _json_bytes(package),
        "extension/README.md": readme.encode("utf-8"),
        "extension/rif-docs.json": _json_bytes(doc),
    }

    grammar = _grammar_json(build, doc, syntax)
    files["extension/syntaxes/rif.tmLanguage.json"] = _json_bytes(grammar)
    snippets = _snippets_json(doc)
    files["extension/snippets/rif.code-snippets"] = _json_bytes(snippets)

    for name, content in _word_docs(doc).items():
        files[f"extension/docs/{name}.md"] = content.encode("utf-8")

    return files


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
    }

    commands = syntax.get("commands")
    if isinstance(commands, list):
        contributes["commands"] = commands

    return {
        "name": _slug(str(build["name"])),
        "displayName": str(build.get("displayName") or build["name"]),
        "publisher": _slug(str(build.get("publisher") or "rif")),
        "version": str(build.get("version") or "0.0.1"),
        "description": str(build.get("description") or "Documentacion generada por RIF"),
        "engines": {"vscode": "^1.80.0"},
        "categories": ["Programming Languages", "Other"],
        "contributes": contributes,
    }


def _readme(project: Path, doc: dict[str, Any], build: dict[str, Any]) -> str:
    readme_ref = doc.get("readme")
    if isinstance(readme_ref, str):
        path = project / readme_ref
        if path.exists():
            return path.read_text(encoding="utf-8")

    lines = [f"# {build.get('displayName') or build['name']}", ""]
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
            if block.get("type") == "code":
                parts.append("```rif")
                parts.extend(str(item) for item in content)
                parts.append("```")
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
    words = list((doc.get("words") or {}).keys()) if isinstance(doc.get("words"), dict) else []
    keywords = syntax.get("keywords")
    if isinstance(keywords, list):
        words.extend(str(item) for item in keywords)
    pattern = r"\b(" + "|".join(re.escape(word) for word in sorted(set(words))) + r")\b" if words else r"\b\B"
    return {
        "scopeName": f"source.{language_id}",
        "patterns": [{"name": "keyword.control.rif", "match": pattern}],
    }


def _snippets_json(doc: dict[str, Any]) -> dict[str, Any]:
    words = doc.get("words", {})
    if not isinstance(words, dict):
        return {}
    return {
        name: {
            "prefix": name,
            "body": [name],
            "description": _first_text(value) or f"RIF word {name}",
        }
        for name, value in words.items()
    }


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
    <Tags>rif</Tags>
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
  <Default Extension="md" ContentType="text/markdown" />
  <Default Extension="txt" ContentType="text/plain" />
  <Default Extension="vsixmanifest" ContentType="text/xml" />
  <Default Extension="xml" ContentType="text/xml" />
</Types>
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
