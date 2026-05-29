"""Pruebas unitarias para validar la UX de compilación (build) estructurada y la gestión de packs en RIF."""

import os
import shutil
import tempfile
import unittest
from pathlib import Path
from rif.linker import build_project, _find_project_pack
from rif.errors import PackError
from rif.parser import Parser
from rif.compiler import Compiler

class TestBuildUX(unittest.TestCase):
    """Conjunto de pruebas para la UX de compilación mejorada y packs de plugins."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.temp_dir)
        self.project_path = Path(self.temp_dir) / "my_gba_project"
        self.project_path.mkdir()

    def test_structured_project_layout_parsing(self):
        """Verifica que se detecten correctamente los packs en 'pack/' y fuentes en 'code/'."""
        pack_dir = self.project_path / "pack"
        code_dir = self.project_path / "code"
        pack_dir.mkdir()
        code_dir.mkdir()

        pack_file = pack_dir / "my_gba_project.pack"
        pack_file.write_text(
            """
.pack
plugin "basics"

.sections
| NAME | type | perms | align | fill | emit | order |
| text | code | rx    | 1     | 00   | yes  | 0     |

.rules
byte:
    need VALUE, imm
    emit imm.binary
""",
            encoding="utf-8",
        )

        source_file = code_dir / "main.rif"
        source_file.write_text(
            """
.section text
start:
byte 0xFA
""",
            encoding="utf-8",
        )

        resolved_pack = _find_project_pack(self.project_path)
        self.assertEqual(resolved_pack, pack_file)

        result = build_project(self.project_path, write=False)
        self.assertEqual(result.hex, "fa")

    def test_find_project_pack_with_use_path(self):
        """Verifica que se soporte una ruta alternativa de packs con use_packs_path."""
        external_packs_dir = Path(self.temp_dir) / "external_packs"
        external_packs_dir.mkdir()

        pack_file = external_packs_dir / "my_gba_project.pack"
        pack_file.write_text(
            """
.pack
plugin "basics"

.rules
byte:
    need VALUE, imm
    emit imm.binary
""",
            encoding="utf-8",
        )

        resolved_pack = _find_project_pack(self.project_path, use_packs_path=external_packs_dir)
        self.assertEqual(resolved_pack, pack_file)
