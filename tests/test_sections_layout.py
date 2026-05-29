"""Tests para la compilación consciente de secciones (Fase 3)."""

import os
import tempfile
import unittest

from rif.compiler import Compiler
from rif.errors import PackError


PACK_LAYOUT = """
.pack
plugin "basics"

.rules
byte:
    need VALUE, imm
    emit imm.binary

rel8:
    reldis ., target, 8

relocabs:
    reloc abs, external, 8
"""

class TestSectionsLayout(unittest.TestCase):
    def _make_compiler(self, pack_source: str) -> Compiler:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".pack", delete=False, encoding="utf-8"
        ) as fobj:
            fobj.write(pack_source)
            tmp_path = fobj.name
        self.addCleanup(os.unlink, tmp_path)
        return Compiler.from_file(tmp_path)

    def test_prohibir_instrucciones_sin_seccion(self):
        """El compilador debe fallar si hay código/datos sin una sección explícita."""
        compiler = self._make_compiler(PACK_LAYOUT)
        source = "byte 0x01"
        with self.assertRaises(PackError) as ctx:
            compiler.compile_lines(source)
        self.assertIn("fuera de sección explícita", str(ctx.exception))

    def test_labels_guardan_seccion(self):
        """Las etiquetas deben registrar la sección en la que fueron declaradas."""
        compiler = self._make_compiler(PACK_LAYOUT)
        source = """
.text
target:
byte 0x01
"""
        compiler.compile_lines(source)
        self.assertIn("target", compiler.labels)
        self.assertEqual(compiler.labels["target"]["section"], ".text")
        self.assertEqual(compiler.labels["target"]["offset"], 0)

    def test_relocations_guardan_seccion(self):
        """Las relocations deben saber en qué sección se emitieron."""
        compiler = self._make_compiler(PACK_LAYOUT)
        source = """
.text
byte 0x01
relocabs
"""
        results = compiler.compile_lines(source)
        relocs = []
        for r in results:
            if r.relocations:
                relocs.extend(r.relocations)
        self.assertEqual(len(relocs), 1)
        self.assertEqual(relocs[0].section, ".text")
        self.assertEqual(relocs[0].offset_bits, 8)  # Después del byte 0x01

    def test_cruce_de_secciones_falla_reldis(self):
        """El cruce de secciones en un reldis estático debe fallar o diferirse."""
        compiler = self._make_compiler(PACK_LAYOUT)
        source = """
.text
rel8
.data
target:
byte 0x01
"""
        results = compiler.compile_lines(source)
        # reldis should be deferred because `target` is in a different section.
        placeholders = []
        for r in results:
            placeholders.extend(r.placeholders)
        # Verify it resulted in a placeholder because of section crossing
        self.assertTrue(any(p.target == "target" and p.kind == "reldis" for p in placeholders))

if __name__ == "__main__":
    unittest.main()
