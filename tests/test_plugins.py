"""Tests de carga y comportamiento de plugins en RIF.

Verifica que el sistema de plugins maneje correctamente tanto plugins
faltantes (error fatal descriptivo) como plugins válidos (carga exitosa).
"""

import unittest
from rif.errors import PackError
from rif.parser import Parser


class TestPlugins(unittest.TestCase):
    def test_plugin_faltante_falla_con_error_claro(self):
        """Verifica que un plugin declarado pero inexistente produce error fatal descriptivo."""
        source = '''
.pack
plugin "plugin_que_no_existe_abc123"

.rules
test:
    emit 00000000
'''
        with self.assertRaises(PackError) as ctx:
            Parser(source, None).parse()
        msg = str(ctx.exception).lower()
        self.assertTrue('plugin_que_no_existe_abc123' in msg or 'no encontrado' in msg)

    def test_plugin_basics_carga_correctamente(self):
        """Verifica que basics carga sin errores."""
        source = '''
.pack
plugin "basics"

.rules
test:
    emit 00000000
'''
        program = Parser(source, None).parse()
        self.assertIsNotNone(program)

if __name__ == '__main__':
    unittest.main()
