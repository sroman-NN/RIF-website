"""Pruebas unitarias para validar el soporte de arrays, sizeset, longset y arrautofill en RIF."""

import unittest
from pathlib import Path
from rif.compiler import Compiler
from rif.parser import Parser
from rif.errors import PackError

class TestArrays(unittest.TestCase):
    """Conjunto de pruebas para el soporte de arrays dinámicos en el compilador RIF."""

    def test_array_sizeset_and_longset_true(self):
        """Verifica un array con sizeset=True y longset=True (ej. array[8, 4])."""
        pack_source = """
.pack
plugin "basics"

.types
| NAME  | bits | longset | sizeset | array | arrautofill |
| myarr | 8    | yes     | yes     | yes   | yes         |

.DATA_DEFINITION
\\
IDENT
TYPE
LITERAL "="
VALUE
\\
index true
"""
        program = Parser(pack_source, None).parse()
        compiler = Compiler(program)
        
        result = compiler.compile_line("vals myarr[8, 4] = 0x11223344")
        self.assertEqual(result.hex, "11223344")
        
        self.assertIn("vals[0]", compiler.program.objects)
        self.assertIn("vals[3]", compiler.program.objects)

    def test_array_sizeset_false_and_longset_true(self):
        """Verifica un array con sizeset=False y longset=True (ej. char[4])."""
        pack_source = """
.pack
plugin "basics"

.types
| NAME | bits | longset | sizeset | array | arrautofill |
| char | 8    | yes     | no      | yes   | yes         |

.DATA_DEFINITION
\\
IDENT
TYPE
LITERAL "="
VALUE
\\
index true
"""
        program = Parser(pack_source, None).parse()
        compiler = Compiler(program)
        
        result = compiler.compile_line("msg char[4] = 0xAA")
        self.assertEqual(result.hex, "aa000000")

    def test_arrautofill_global_option(self):
        """Verifica que arrautofill funcione como instrucción en .DATA_DEFINITION."""
        pack_source = """
.pack
plugin "basics"

.types
| NAME | bits | longset | sizeset | array |
| char | 8    | yes     | no      | yes   |

.DATA_DEFINITION
\\
IDENT
TYPE
LITERAL "="
VALUE
\\
index true
arrautofill true
"""
        program = Parser(pack_source, None).parse()
        compiler = Compiler(program)
        
        result = compiler.compile_line("msg char[6] = 0xAABBCC")
        self.assertEqual(result.hex, "aabbcc000000")

    def test_array_longset_false_inferred_length(self):
        """Verifica un array con longset=False donde la longitud se infiere del valor."""
        pack_source = """
.pack
plugin "basics"

.types
| NAME | bits | longset | sizeset | array |
| char | 8    | no      | no      | yes   |

.DATA_DEFINITION
\\
IDENT
TYPE
LITERAL "="
VALUE
\\
index true
"""
        program = Parser(pack_source, None).parse()
        compiler = Compiler(program)
        
        result = compiler.compile_line("msg char[] = 0xAABBCC")
        self.assertEqual(result.hex, "aabbcc")
        self.assertIn("msg[0]", compiler.program.objects)
        self.assertIn("msg[2]", compiler.program.objects)
        self.assertNotIn("msg[3]", compiler.program.objects)

    def test_array_invalid_signature_raises_error(self):
        """Verifica que se lancen errores adecuados ante firmas de arrays inválidas."""
        pack_source = """
.pack
plugin "basics"

.types
| NAME  | bits | longset | sizeset | array |
| myarr | 8    | yes     | yes     | yes   |

.DATA_DEFINITION
\\
IDENT
TYPE
LITERAL "="
VALUE
\\
index true
"""
        program = Parser(pack_source, None).parse()
        compiler = Compiler(program)
        
        with self.assertRaises(PackError):
            compiler.compile_line("vals myarr[4] = 0xAA")
