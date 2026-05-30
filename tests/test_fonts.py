from __future__ import annotations

import tempfile
from pathlib import Path
import unittest

from rif.compiler import Compiler
from rif.linker import BinaryLinker
from rif.parser import Parser
from rif.plugins.fonts.bitmap.api import text_bitmap_bytes
from rif.plugins.fonts.bitmap.parser import load_font


FONT_PATH = Path(__file__).resolve().parents[1] / "rif" / "plugins" / "fonts" / "bitmap" / "font-5x7x1.f"


class FontPluginTests(unittest.TestCase):
    def test_font_5x7x1_has_letters_and_digits(self):
        font = load_font(FONT_PATH)
        for char in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789":
            self.assertIn(char, font.glyphs)

        self.assertEqual(font.width, 5)
        self.assertEqual(font.height, 7)
        self.assertEqual(font.row_bytes, 1)
        self.assertEqual(font.get_flat_bytes("A"), [14, 17, 17, 31, 17, 17, 17])

    def test_bitmap_plugin_emits_text_bytes(self):
        pack = """
.pack
plugin "fonts"

.sections
| NAME | type | perms | align | fill | emit | order |
| text | code | rx    | 1     | 00   | yes  | 0     |

.rules
logo:
    bitmap "Aa0"
"""
        compiler = Compiler(Parser(pack, None).parse())
        result = compiler.compile_line("logo")

        self.assertEqual(result.data, text_bitmap_bytes("Aa0"))
        self.assertEqual(len(result.data), 21)

    def test_fillable_expansion_keeps_relocation_offsets(self):
        pack = """
.pack
plugin "basics"
plugin "fonts"

.world
endianness little

.sections
| NAME | type | perms | align | fill | emit | order |
| text | code | rx    | 1     | 00   | yes  | 0     |
| data | data | rw    | 1     | 00   | yes  | 1     |

.types
| NAME   | bits | array | sizeset | longset | arrautofill |
| bitmap | 8    | true  | false   | yes     | yes         |

.DATA_DEFINITION
\\
IDENT
TYPE
LITERAL "="
VALUE
\\
index true
arrautofill true

.rules
byte:
    need VALUE, imm
    emit imm.binary

relocabs:
    reloc abs, target, 16
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".pack", delete=False, encoding="utf-8") as fobj:
            fobj.write(pack)
            pack_path = Path(fobj.name)
        self.addCleanup(lambda: pack_path.exists() and pack_path.unlink())

        program = Parser(pack, pack_path).parse()
        linker = BinaryLinker(program)
        source = """
.text
byte 0x01
@fill_bitmap_array_logo
relocabs

.data
target:
byte 0x02
"""
        result = linker.build(source=source, write=False)

        self.assertEqual(result.data[0], 0x01)
        self.assertEqual(result.data[29:31], (31).to_bytes(2, "little"))
        self.assertEqual(result.data[31], 0x02)

    def test_fillable_expands_inside_compiler(self):
        pack = """
.pack
plugin "fonts"

.types
| NAME   | bits | array | sizeset | longset | arrautofill |
| bitmap | 8    | true  | false   | yes     | yes         |

.DATA_DEFINITION
\\
IDENT
TYPE
LITERAL "="
VALUE
\\
arrautofill true

.sections
| NAME | type | perms | align | fill | emit | order |
| data | data | rw    | 1     | 00   | yes  | 0     |
"""
        compiler = Compiler(Parser(pack, None).parse())
        results = compiler.compile_lines("""
.section data
@bitmap_array_logo
""")

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].rule_name, "data")
        self.assertEqual(len(results[0].data), 28)


if __name__ == "__main__":
    unittest.main()
