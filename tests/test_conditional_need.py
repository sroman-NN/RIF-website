"""Pruebas de regresión: `need` condicional no contamina la firma de la regla.

Verifica que los operandos declarados dentro de ramas ON/OFF o switch/case no
sean exigidos por `_match_rule` al compilar una instrucción, ya que dichas
ramas pueden no ejecutarse nunca.
"""

import os
import tempfile
import unittest

from rif.compiler import Compiler
from rif.errors import PackError


PACK_SIMPLE = """
.pack
plugin "basics"

.rules
foo:
    need VALUE, x
    emit x.binary
"""

PACK_WITH_SWITCH_NEED = """
.pack
plugin "basics"

.rules
bar:
    need VALUE, x
    switch x.size:
        case 8:
            need VALUE, y
            emit 00000000
        case 16:
            emit x.binary
"""

PACK_WITH_ON_NEED = """
.pack
plugin "basics"

.rules
baz:
    need VALUE, x
    ON x.size == 8:
        need VALUE, y
        emit 00000000
    OFF:
        emit x.binary
"""

class TestConditionalNeed(unittest.TestCase):
    def _make_compiler(self, pack_source: str) -> Compiler:
        """Crea un compilador temporal a partir de fuente pack en memoria."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".pack", delete=False, encoding="utf-8"
        ) as fobj:
            fobj.write(pack_source)
            tmp_path = fobj.name
        self.addCleanup(os.unlink, tmp_path)
        return Compiler.from_file(tmp_path)

    def test_regla_simple_acepta_un_operando(self):
        """Una regla con un `need` de nivel raíz exige exactamente ese operando."""
        compiler = self._make_compiler(PACK_SIMPLE)
        result = compiler.compile_line("foo 0xff")
        self.assertNotEqual(result.bits, "")

    def test_switch_need_no_exige_operandos_de_case(self):
        """Un `need` dentro de un case no debe ser exigido en la firma de la regla."""
        compiler = self._make_compiler(PACK_WITH_SWITCH_NEED)
        result = compiler.compile_line("bar 0xff")
        self.assertNotEqual(result.bits, "")

    def test_on_need_no_exige_operandos_de_rama(self):
        """Un `need` dentro de ON/OFF no debe ser exigido en la firma de la regla."""
        compiler = self._make_compiler(PACK_WITH_ON_NEED)
        result = compiler.compile_line("baz 0xff")
        self.assertNotEqual(result.bits, "")

if __name__ == '__main__':
    unittest.main()
