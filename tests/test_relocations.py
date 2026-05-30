"""Tests para verificar la aplicación de relocations en la fase de link."""

import os
import tempfile
import unittest

from rif.linker import BinaryLinker
from rif.parser import Parser


PACK_RELOCATIONS = """
.pack
plugin "basics"
packer:
    definesec ".headers"

types:
    from .words as WORD

.sections
| NAME   | type   | perms | align | fill     | emit | order |
| text   | code   | rx    | 16    | 00000000 | yes  | 0     |
| data   | data   | rw    | 8     | 00000000 | yes  | 1     |

.words
| NAME | hex  |
| nop  | 90   |

.rules
byte:
    need VALUE, imm
    emit imm.binary

rel8:
    reldis ., target, 8

relocabs:
    reloc abs, target, 16

relocdata:
    reloc abs, target, 16

emit_addr:
    emitaddress target, 16
"""

class TestRelocations(unittest.TestCase):
    def _make_linker(self, pack_source: str) -> BinaryLinker:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".pack", delete=False, encoding="utf-8"
        ) as fobj:
            fobj.write(pack_source)
            tmp_path = fobj.name
        self.addCleanup(os.unlink, tmp_path)
        program = Parser(pack_source, tmp_path).parse()
        return BinaryLinker(program)

    def test_relocations_are_applied(self):
        """Verifica que las relocations se apliquen al ensamblar bytes finales."""
        linker = self._make_linker(PACK_RELOCATIONS)
        source = """
.text
start:
byte 0x90
rel8
relocabs
relocdata
emit_addr

.data
target:
byte 0x02
"""
        result = linker.build(source=source, write=False)
        data = result.data
        
        # .text -> 0: start. 1: rel8. 2,3: relocabs. 4,5: relocdata. 6,7: emit_addr
        # virtual_offsets:
        # start = 0
        # rel8 is at offset 1
        # relocabs is at offset 2
        # relocdata is at offset 4
        # emit_addr is at offset 6
        # target is at .data (offset 8 due to align 8 of .data and size 8 of .text)
        blocks_dict = {b.name: b for b in result.blocks}
        text_block = blocks_dict["text"]
        data_block = blocks_dict["data"]
        
        self.assertEqual(text_block.virtual_offset, 0)
        self.assertEqual(data_block.virtual_offset, 8)
        
        target_addr = data_block.virtual_offset
        msg_addr = target_addr
        
        # In `rel8`, origin is 1 (the `rel8` instruction). Target is `target_addr` (8).
        # Since `reldis` in RIF calculates relative to the next instruction (PC + instruction size),
        # the origin is 1 + 1 = 2. Distance = 8 - 2 = 6.
        self.assertEqual(data[0], 0x90) # nop
        self.assertEqual(data[1], 6)   # rel8
        
        # `relocabs` is `target_addr` (8) in 16 bits little endian: 08 00
        self.assertEqual(data[2], 0x08)
        self.assertEqual(data[3], 0x00)
        
        # `relocdata` is `msg_addr` (8) in 16 bits little endian: 08 00
        self.assertEqual(data[4], 0x08)
        self.assertEqual(data[5], 0x00)
        
        # `emit_addr` (emitaddress) is `target_addr` (8) in 16 bits little endian: 08 00
        self.assertEqual(data[6], 0x08)
        self.assertEqual(data[7], 0x00)
        
        # Check .data section at index 8
        self.assertEqual(data[8], 0x02)

if __name__ == "__main__":
    unittest.main()
