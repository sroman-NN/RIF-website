from __future__ import annotations

import unittest
from pathlib import Path

from rif.linker import build_project


class Atari2600PluginTests(unittest.TestCase):
    def test_example_builds_4k_rom_with_vectors(self):
        root = Path(__file__).resolve().parents[1] / "atari2600"
        result = build_project(root, write=False)

        self.assertEqual(len(result.data), 4096)
        self.assertEqual(result.data[:5], bytes.fromhex("78 d8 a2 ff 9a"))
        self.assertEqual(result.data[-6:], bytes.fromhex("00 f0 00 f0 00 f0"))
        rom = next(block for block in result.blocks if block.name == "rom")
        self.assertEqual(rom.virtual_offset, 0xF000)


if __name__ == "__main__":
    unittest.main()
