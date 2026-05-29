from pathlib import Path
from contextlib import redirect_stdout
from io import StringIO
import os
import sys
import tempfile
import unittest
from unittest.mock import patch

from rif.cli import main
from rif.linker import build_file, build_project


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "gba" / "pack" / "gba.pack"
SOURCE = ROOT / "gba" / "code" / "hello.rif"


class GbaExampleTests(unittest.TestCase):
    def test_gba_hello_world_green_rom(self):
        source = SOURCE.read_text(encoding="utf-8")
        result = build_file(PACK, source=source, write=False)

        self.assertEqual(len(result.data), 0x20000)
        self.assertEqual(result.data[0xA0:0xAC].rstrip(), b"HOLA MUNDO")
        self.assertEqual(result.data[0xBD], (-(sum(result.data[0xA0:0xBD]) + 0x19)) & 0xFF)
        self.assertEqual(result.data[0x100:0x102], (0x03E0).to_bytes(2, "little"))

    def test_gba_project_folder_builds_from_sources(self):
        result = build_project(ROOT / "gba", write=False)

        self.assertEqual(len(result.data), 0x20000)
        self.assertEqual(result.data[0x100:0x102], (0x03E0).to_bytes(2, "little"))

    def test_cli_build_project_writes_pack_output(self):
        output_path = ROOT / "gba" / "hello.gba"
        if output_path.exists():
            output_path.unlink()
        self.addCleanup(lambda: output_path.exists() and output_path.unlink())

        out = StringIO()
        with redirect_stdout(out):
            code = main(["build", str(ROOT / "gba")])

        self.assertEqual(code, 0)
        self.assertTrue(output_path.exists())
        self.assertIn("bytes=131072", out.getvalue())
        self.assertIn("output=", out.getvalue())
        self.assertIn("sha256=", out.getvalue())

    def test_gba_plugin_cli_dispatches(self):
        with tempfile.TemporaryDirectory() as home:
            for name in ("common", "rif.gba.cli.install", "rif.plugin_cli.gba"):
                sys.modules.pop(name, None)
            env = {"HOME": home, "USERPROFILE": home}
            out = StringIO()
            with patch.dict(os.environ, env, clear=False), redirect_stdout(out):
                code = main(["-pcli", "gba", "install", "mGBA", "--add-path"])

        self.assertEqual(code, 0)
        self.assertIn("mGBA registrado", out.getvalue())

    def test_gba_plugin_cli_run_no_duplicate_dry_run(self):
        out = StringIO()
        with redirect_stdout(out):
            code = main(["-pcli", "gba", "run", str(SOURCE), "-nd", "--dry-run"])

        self.assertEqual(code, 0)
        self.assertIn("no-duplicate", out.getvalue())


if __name__ == "__main__":
    unittest.main()
