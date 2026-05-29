import os
import tempfile
import textwrap
import unittest

from rif import SourceReader
from rif.compiler import Compiler
from rif.errors import PackError
from rif.parser import Parser


PACK_SOURCE = """
.pack
plugin "basics"

reader:
    comment "#"
    blocks "!"

.sections
| NAME | type | perms | align | fill | emit | order |
| text | code | rx    | 1     | 00   | yes  | 0     |
| data | data | rw    | 1     | 00   | yes  | 1     |

.rules
byte:
    need VALUE, imm
    emit imm.binary
"""


class SourceReaderTests(unittest.TestCase):
    def _make_compiler(self) -> Compiler:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".pack", delete=False, encoding="utf-8") as fobj:
            fobj.write(PACK_SOURCE)
            path = fobj.name
        self.addCleanup(os.unlink, path)
        return Compiler.from_file(path)

    def test_reader_usa_config_del_pack(self):
        compiler = self._make_compiler()
        source = textwrap.dedent(
            """
            .text!
            target!
            byte 0x01 # comentario
            """
        )

        read = compiler.source_reader.read(source)

        self.assertEqual(read.sections, (".text",))
        self.assertEqual(read.labels[0].name, "target")
        self.assertEqual(read.instructions[0].text, "byte 0x01")

    def test_compiler_usa_reader(self):
        compiler = self._make_compiler()
        source = textwrap.dedent(
            """
            .text!
            target!
            byte 0x01 # comentario
            """
        )

        results = compiler.compile_lines(source)

        self.assertEqual(results[0].hex, "01")
        self.assertEqual(compiler.labels["target"], {"section": ".text", "offset": 0})

    def test_seccion_desconocida_falla(self):
        compiler = self._make_compiler()

        with self.assertRaises(PackError) as ctx:
            compiler.compile_lines(".unknown!\nbyte 0x01\n")

        self.assertIn("sección de fuente desconocida", str(ctx.exception))

    def test_reader_directo(self):
        program = Parser(PACK_SOURCE, None).parse()
        reader = SourceReader(program)

        read = reader.read(".section text!\nbyte 0x02\n")

        self.assertEqual(read.sections, (".text",))
        self.assertEqual(read.instructions[0].tokens, ("byte", "0x02"))


if __name__ == "__main__":
    unittest.main()
