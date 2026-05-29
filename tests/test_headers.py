"""Tests para la definición y parseo de la sección .headers."""

import os
import tempfile
import unittest

from rif.parser import Parser

PACK_HEADERS = """
.pack
packer:
    definesec ".headers"

.headers
| NAME     | SIZE | HEX | FILL     |
| DOS_STUB | 64   |     | 00000000 |
| PE_SIG   | 4    | 50  |          |

DOS_STUB:
    | NAME     | OFFSET | SIZE | ENDIAN | VALUE |
    | e_magic  | 0      | 2    | raw    | 4d5a  |
"""

class TestHeaders(unittest.TestCase):
    def _parse(self, source: str):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".pack", delete=False, encoding="utf-8"
        ) as fobj:
            fobj.write(source)
            tmp_path = fobj.name
        self.addCleanup(os.unlink, tmp_path)
        return Parser(source, tmp_path).parse()

    def test_headers_parsed_from_headers_section(self):
        """Verifica que los headers se parseen correctamente desde .headers."""
        program = self._parse(PACK_HEADERS)
        
        self.assertTrue(program.headers.blocks, "No se encontraron bloques de headers")
        self.assertIn("DOS_STUB", program.headers.blocks)
        self.assertIn("PE_SIG", program.headers.blocks)

        dos_stub = program.headers.blocks["DOS_STUB"]
        self.assertEqual(dos_stub.size, 64)
        self.assertEqual(str(dos_stub.fill), "0")

        pe_sig = program.headers.blocks["PE_SIG"]
        self.assertEqual(pe_sig.size, 4)
        self.assertEqual(pe_sig.hex, "50")

        # Verificar que la tabla anidada de DOS_STUB se asignó correctamente
        self.assertIsNotNone(dos_stub.table)
        self.assertIn("e_magic", dos_stub.table.rows)

if __name__ == "__main__":
    unittest.main()
