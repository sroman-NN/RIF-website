from __future__ import annotations

from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
import tempfile
import unittest
import zipfile

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

            out = StringIO()
            with redirect_stdout(out):
                code = main(["-pcli", "basics", "build-doc", str(project)])

            vsix = project / "demo-rif.vsix"
            self.assertEqual(code, 0)
            self.assertTrue(vsix.exists())
            self.assertIn("vsix=", out.getvalue())

            with zipfile.ZipFile(vsix) as archive:
                names = set(archive.namelist())

            self.assertIn("extension/package.json", names)
            self.assertIn("extension/docs/headers.md", names)
            self.assertIn("extension/syntaxes/rif.tmLanguage.json", names)


if __name__ == "__main__":
    unittest.main()
