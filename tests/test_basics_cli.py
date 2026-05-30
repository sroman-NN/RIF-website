from __future__ import annotations

from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
import tempfile
import unittest
import zipfile
import json

from rif.cli import main


class BasicsCliTests(unittest.TestCase):
    def test_build_doc_generates_vsix_from_doc_and_build_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "demo"
            project.mkdir()
            (project / "doc.json").write_text(
                """
                {
                  "words": {
                    "headers": {
                      "doc": [
                        {"type": "text", "content": ["Documentacion"]},
                        {"type": "code", "content": ["headers"]}
                      ],
                      "links": ["github.com"]
                    }
                  }
                }
                """,
                encoding="utf-8",
            )
            (project / "build.json").write_text(
                """
                {
                  "name": "demo-rif",
                  "displayName": "Demo RIF",
                  "publisher": "rif",
                  "version": "0.0.1",
                  "output": "demo-rif.vsix"
                }
                """,
                encoding="utf-8",
            )
            (project / "syntaxs.json").write_text(
                """
                {
                  "keywords": ["entry"],
                  "types": ["bitmap"],
                  "registers": ["r0"],
                  "completions": [
                    {"label": "frame", "insertText": "frame", "documentation": "Frame doc"}
                  ],
                  "errors": [
                    {"match": "\\\\bBAD\\\\b", "message": "No uses BAD", "severity": "error"}
                  ]
                }
                """,
                encoding="utf-8",
            )

            out = StringIO()
            with redirect_stdout(out):
                code = main(["-pcli", "basics", "build-doc", str(project)])

            vsix = project / "demo-rif.vsix"
            self.assertEqual(code, 0)
            self.assertTrue(vsix.exists())
            self.assertIn("vsix=", out.getvalue())

            with zipfile.ZipFile(vsix) as archive:
                names = set(archive.namelist())
                package = json.loads(archive.read("extension/package.json"))
                completions = json.loads(archive.read("extension/rif-completions.json"))
                diagnostics = json.loads(archive.read("extension/rif-diagnostics.json"))

            self.assertIn("extension/package.json", names)
            self.assertIn("extension/docs/headers.md", names)
            self.assertIn("extension/syntaxes/rif.tmLanguage.json", names)
            self.assertIn("extension/extension.js", names)
            self.assertEqual(package["main"], "./extension.js")
            self.assertTrue(any(item["label"] == "frame" for item in completions))
            self.assertEqual(diagnostics[0]["message"], "No uses BAD")

    def test_build_doc_minimal_vsix_without_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "empty"
            project.mkdir()

            out = StringIO()
            with redirect_stdout(out):
                code = main(["-pcli", "basics", "build-doc", str(project)])

            vsix = project / "empty-0.0.1.vsix"
            self.assertEqual(code, 0)
            self.assertTrue(vsix.exists())

            with zipfile.ZipFile(vsix) as archive:
                names = set(archive.namelist())
                grammar = json.loads(archive.read("extension/syntaxes/rif.tmLanguage.json"))
                completions = json.loads(archive.read("extension/rif-completions.json"))

            self.assertIn("extension/package.json", names)
            self.assertTrue(grammar["patterns"])
            self.assertTrue(any(item["label"] == "emit" for item in completions))


if __name__ == "__main__":
    unittest.main()
