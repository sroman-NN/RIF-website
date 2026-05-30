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
    doc = _read_jsonc(project / "doc.json", required=False)
    build = {**DEFAULT_BUILD, **_read_jsonc(project / "build.json", required=False)}
    syntax = _read_jsonc(project / "syntaxs.json", required=False)
    _apply_minimal_defaults(project, doc, build, syntax)

    output = Path(args.output) if args.output else _output_path(project, build)
    output.parent.mkdir(parents=True, exist_ok=True)

    files = _extension_files(project, doc, build, syntax)
    _write_vsix(output, files)

    print(f"vsix={output}")
    print(f"name={build['name']}")
    print(f"version={build['version']}")
    print(f"docs={len(doc.get('words', {}))}")
    print(f"syntax={len(_syntax_words(doc, syntax))}")
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
        "extension/rif-completions.json": _json_bytes(_completions_json(doc, syntax)),
        "extension/rif-diagnostics.json": _json_bytes(_diagnostics_json(syntax)),
        "extension/extension.js": _extension_js().encode("utf-8"),
    }

    grammar = _grammar_json(build, doc, syntax)
    files["extension/syntaxes/rif.tmLanguage.json"] = _json_bytes(grammar)
    snippets = _snippets_json(doc)
    files["extension/snippets/rif.code-snippets"] = _json_bytes(snippets)

    for name, content in _word_docs(doc).items():
        files[f"extension/docs/{name}.md"] = content.encode("utf-8")

    for archive_name, path in _markdown_files(project, doc).items():
        files[f"extension/docs/project/{archive_name}"] = path.read_bytes()

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
        "activationEvents": [f"onLanguage:{language_id}"],
        "main": "./extension.js",
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
    ]

    if directives:
        patterns.append({"name": "entity.name.section.rif", "match": _word_pattern(directives, boundary=False)})
    if words:
        patterns.append({"name": "keyword.control.rif", "match": _word_pattern(words)})
    if builtins:
        patterns.append({"name": "support.function.rif", "match": _word_pattern(builtins)})
    if types:
        patterns.append({"name": "support.type.rif", "match": _word_pattern(types)})
    if registers:
        patterns.append({"name": "variable.language.register.rif", "match": _word_pattern(registers)})

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


def _snippets_json(doc: dict[str, Any]) -> dict[str, Any]:
    words = doc.get("words", {})
    snippets = {
        name: {
            "prefix": name,
            "body": [name],
            "description": _first_text(value) or f"RIF word {name}",
        }
        for name, value in words.items()
    } if isinstance(words, dict) else {}
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
            })

    for key in ("completions", "predictions", "prediction"):
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
  <Default Extension="js" ContentType="application/javascript" />
  <Default Extension="md" ContentType="text/markdown" />
  <Default Extension="txt" ContentType="text/plain" />
  <Default Extension="vsixmanifest" ContentType="text/xml" />
  <Default Extension="xml" ContentType="text/xml" />
</Types>
"""


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

function activate(context) {
  const pkg = require('./package.json');
  const language = (((pkg.contributes || {}).languages || [])[0] || {}).id || 'rif';
  const docs = loadJson(context, 'rif-docs.json', { words: {} });
  const completions = loadJson(context, 'rif-completions.json', []);
  const diagnostics = loadJson(context, 'rif-diagnostics.json', []);
  const collection = vscode.languages.createDiagnosticCollection('rif');
  context.subscriptions.push(collection);

  context.subscriptions.push(vscode.languages.registerCompletionItemProvider(language, {
    provideCompletionItems() {
      return completions.map(entry => {
        const item = new vscode.CompletionItem(entry.label, itemKind(entry.kind));
        item.insertText = entry.insertText || entry.label;
        item.detail = entry.detail || 'RIF';
        if (entry.documentation) item.documentation = new vscode.MarkdownString(entry.documentation);
        return item;
      });
    }
  }));

  context.subscriptions.push(vscode.languages.registerHoverProvider(language, {
    provideHover(document, position) {
      const range = document.getWordRangeAtPosition(position, /[A-Za-z_][A-Za-z0-9_-]*/);
      if (!range) return;
      const word = document.getText(range);
      const info = docs.words && docs.words[word];
      if (!info) return;
      const match = completions.find(entry => entry.label === word);
      const md = new vscode.MarkdownString(match && match.documentation ? match.documentation : word);
      md.isTrusted = true;
      return new vscode.Hover(md, range);
    }
  }));

  function refresh(document) {
    if (document.languageId !== language) return;
    const found = [];
    const text = document.getText();
    for (const rule of diagnostics) {
      try {
        const regex = new RegExp(rule.match, 'gm');
        let match;
        while ((match = regex.exec(text))) {
          const start = document.positionAt(match.index);
          const end = document.positionAt(match.index + Math.max(1, match[0].length));
          const severity = String(rule.severity || 'warning').toLowerCase() === 'error'
            ? vscode.DiagnosticSeverity.Error
            : vscode.DiagnosticSeverity.Warning;
          found.push(new vscode.Diagnostic(new vscode.Range(start, end), rule.message || 'RIF diagnostic', severity));
        }
      } catch (_) {}
    }
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
