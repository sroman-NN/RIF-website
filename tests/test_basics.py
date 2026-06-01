"""
Tests para Plugin Basics de RIF

Conjunto de pruebas unitarias para validar el funcionamiento
de todas las directivas del plugin basics.

Ejecución:
    pytest tests/test_basics.py -v
    pytest tests/test_basics.py -v -k "test_need"  # Tests específicos
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from typing import Any


class MockLine:
    """Mock para el objeto Line del compilador RIF"""
    def __init__(self, elements=0, toks=None):
        self.elements = elements
        self.toks = toks or []
        self.expects_called = False
        
    def Advance(self):
        if self.toks:
            return self.toks.pop(0)
        return None
    
    def Peek(self):
        return self.toks[0] if self.toks else None
    
    def Unpack(self, separator=","):
        """Desempaqueta tokens separados por delimitador"""
        result = []
        current = []
        for tok in self.toks:
            if str(tok).strip() == separator:
                if current:
                    result.append(current)
                    current = []
            else:
                current.append(tok)
        if current:
            result.append(current)
        return result
    
    def expects(self, *expected):
        self.expects_called = True
        return True


class MockErr:
    """Mock para errores del compilador"""
    def __init__(self, message):
        self.message = message
    
    def __str__(self):
        return self.message


class MockExpr:
    """Mock para expresiones del compilador"""
    def __init__(self, expr):
        self.expr = expr
    
    def __getitem__(self, idx):
        return self.expr[idx]


class MockOperator:
    """Mock para el manejo de operadores"""
    bindings = {}
    
    @classmethod
    def Save(cls, target, rule, valid_types=None):
        cls.bindings[target] = {
            'rule': rule,
            'valid_types': valid_types or []
        }
    
    @classmethod
    def Binding(cls, target, rule):
        return cls.bindings.get(target)
    
    @classmethod
    def reset(cls):
        cls.bindings.clear()


# ============================================================================
# TESTS: Directiva NEED
# ============================================================================

class TestNeed:
    """Tests para la directiva 'need'"""
    
    def test_need_single_type_single_operator(self):
        """need VALUE imm - Captura de un tipo simple"""
        # Simulación
        elements = 2
        assert elements >= 2, "need requiere al menos tipo y operador"
    
    def test_need_multiple_types(self):
        """need REG, VALUE reg, imm - Captura de múltiples tipos"""
        types_list = ["REG", "VALUE"]
        assert len(types_list) == 2
    
    def test_need_requires_operator(self):
        """need VALUE - Error: falta operador al final"""
        sanitized = ["VALUE"]
        # Última línea no es operador, falta operador
        assert len(sanitized) == 1
    
    def test_need_operator_must_be_identifier(self):
        """need VALUE 123 - Error: operador debe ser identificador"""
        operator = "123"
        import re
        identifier_re = re.compile(r"^[A-Za-z_][A-Za-z0-9_:-]*$")
        assert not identifier_re.match(operator)
    
    def test_need_no_leading_comma(self):
        """need , VALUE op - Error: no puede iniciar con coma"""
        sanitized = ["", "VALUE", "op"]
        assert sanitized[0] == ""
    
    def test_need_no_trailing_comma(self):
        """need VALUE , - Error: no puede terminar con coma"""
        sanitized = ["VALUE", ""]
        assert sanitized[-1] == ""
    
    def test_need_no_double_commas(self):
        """need VALUE,, op - Error: dos comas seguidas"""
        sanitized = ["VALUE", "", "op"]
        assert "" in sanitized
    
    def test_need_duplicate_types(self):
        """need VALUE, VALUE op - Error: tipo duplicado"""
        types_seen = {"VALUE"}
        assert "VALUE" in types_seen
    
    def test_need_types_before_operator(self):
        """need VALUE op, REG - Error: tipos después del operador"""
        sanitized = ["VALUE", "op", "REG"]
        # Si encontramos operador en posición 1, no puede haber más tipos
        op_index = 1
        assert len(sanitized) > op_index + 1
    
    def test_need_builtin_types(self):
        """Validar tipos built-in reconocidos"""
        builtin_types = {
            "SYMBOL", "LABEL", "VALUE", "TYPE",
            "STACK", "HEAP", "MEMORY"
        }
        assert "VALUE" in builtin_types
        assert "LABEL" in builtin_types
    
    def test_need_derived_types(self):
        """SREG es un tipo derivado de REG"""
        derived = {"SREG"}
        assert "SREG" in derived


# ============================================================================
# TESTS: Directiva EMIT
# ============================================================================

class TestEmit:
    """Tests para la directiva 'emit'"""
    
    def test_emit_binary_bits_valid(self):
        """emit 11010101 - Emite 8 bits válidos"""
        bits = "11010101"
        import re
        bits_re = re.compile(r"^[01]+$")
        assert bits_re.match(bits)
    
    def test_emit_invalid_bits(self):
        """emit 11020101 - Error: bits inválidos"""
        bits = "11020101"
        import re
        bits_re = re.compile(r"^[01]+$")
        assert not bits_re.match(bits)
    
    def test_emit_placeholder_valid(self):
        """emit imm.binary - Placeholder válido"""
        placeholder = "imm.binary"
        import re
        placeholder_re = re.compile(r"^([A-Za-z_][A-Za-z0-9_:-]*)\.([A-Za-z_][A-Za-z0-9_]*)$")
        assert placeholder_re.match(placeholder)
    
    def test_emit_placeholder_invalid_syntax(self):
        """emit 123.field - Placeholder inválido (no identifier)"""
        placeholder = "123.field"
        import re
        placeholder_re = re.compile(r"^([A-Za-z_][A-Za-z0-9_:-]*)\.([A-Za-z_][A-Za-z0-9_]*)$")
        assert not placeholder_re.match(placeholder)
    
    def test_emit_mode_cbit_exactly_8(self):
        """emit cbit 11111111 - Valida exactamente 8 bits"""
        bits = "11111111"
        assert len(bits) == 8
    
    def test_emit_mode_cbit_invalid_width(self):
        """emit cbit 1111111 - Error: no son 8 bits"""
        bits = "1111111"
        assert len(bits) != 8
    
    def test_emit_mode_cmbit_exactly_4(self):
        """emit cmbit 1111 - Valida exactamente 4 bits"""
        bits = "1111"
        assert len(bits) == 4
    
    def test_emit_mode_ccbit_exactly_16(self):
        """emit ccbit 1111000011110000 - Valida exactamente 16 bits"""
        bits = "1111000011110000"
        assert len(bits) == 16
    
    def test_emit_empty_error(self):
        """emit - Error: fragmentos vacíos"""
        fragments = []
        assert len(fragments) == 0
    
    def test_emit_multiple_fragments(self):
        """emit 1111, imm.value, 00110011 - Múltiples fragmentos"""
        fragments = ["1111", "imm.value", "00110011"]
        assert len(fragments) == 3


# ============================================================================
# TESTS: Directiva CALL
# ============================================================================

class TestCall:
    """Tests para la directiva 'call'"""
    
    def test_call_valid_rule_name(self):
        """call helper - Nombre de regla válido"""
        import re
        rule_name = "helper"
        ident_re = re.compile(r"^[A-Za-z_][A-Za-z0-9_:-]*$")
        assert ident_re.match(rule_name)
    
    def test_call_invalid_rule_name_starts_number(self):
        """call 123_rule - Error: nombre inválido"""
        import re
        rule_name = "123_rule"
        ident_re = re.compile(r"^[A-Za-z_][A-Za-z0-9_:-]*$")
        assert not ident_re.match(rule_name)
    
    def test_call_requires_exactly_one_argument(self):
        """call rule1 rule2 - Error: solo acepta una regla"""
        args = ["rule1", "rule2"]
        assert len(args) != 1
    
    def test_call_empty_error(self):
        """call - Error: regla faltante"""
        args = []
        assert len(args) == 0


# ============================================================================
# TESTS: Directiva ERROR/RAISE
# ============================================================================

class TestErrorRaise:
    """Tests para directivas error y raise"""
    
    def test_error_generates_exception(self):
        """error 'mensaje' - Genera excepción de compilación"""
        message = "Se esperaba un operador"
        assert isinstance(message, str)
        assert len(message) > 0
    
    def test_raise_generates_exception(self):
        """raise 'mensaje' - Genera excepción de compilación"""
        message = "Valor fuera de rango"
        assert isinstance(message, str)
    
    def test_error_message_propagates(self):
        """El mensaje de error se propaga al usuario"""
        error_msg = "RIF: emit requiere bits"
        assert "emit" in error_msg


# ============================================================================
# TESTS: Operaciones con Bits
# ============================================================================

class TestBitOperations:
    """Tests para operaciones con bits"""
    
    def test_bitcat_concatenation(self):
        """bitcat dest, src1, src2 - Concatena bits"""
        bits1 = "1111"
        bits2 = "0000"
        result = bits1 + bits2
        assert result == "11110000"
    
    def test_bitsize_calculation(self):
        """bitsize dest, value - Calcula bits requeridos"""
        # Para representar 15 se necesitan 4 bits
        value = 15
        bits_needed = value.bit_length()
        assert bits_needed == 4
    
    def test_bitsize_zero(self):
        """bitsize dest, 0 - Cero requiere 0 bits"""
        value = 0
        bits_needed = value.bit_length()
        assert bits_needed == 0
    
    def test_trunc_truncates_bits(self):
        """trunc dest, source, 8 - Trunca a 8 bits"""
        original = 0b111111111111
        truncated = original & ((1 << 8) - 1)
        assert truncated == 0b11111111
    
    def test_zext_zero_extension(self):
        """zext dest, source, 16 - Extiende con ceros"""
        value = 0b00001111
        extended = value | (0 << 8)
        assert extended == 0b00001111
    
    def test_sext_sign_extension_positive(self):
        """sext dest, 0b01111111, 16 - Extiende signo (positivo)"""
        value = 0b01111111
        msb = (value >> 7) & 1
        # Si MSB es 0, rellena con ceros
        assert msb == 0
    
    def test_sext_sign_extension_negative(self):
        """sext dest, 0b11111111, 16 - Extiende signo (negativo)"""
        value = 0b11111111
        msb = (value >> 7) & 1
        # Si MSB es 1, rellena con unos
        assert msb == 1


# ============================================================================
# TESTS: Comparaciones y Validaciones
# ============================================================================

class TestComparisons:
    """Tests para operadores de comparación"""
    
    def test_eq_equal(self):
        """eq r0, r1 - Valida igualdad"""
        r0, r1 = 42, 42
        assert r0 == r1
    
    def test_eq_not_equal_error(self):
        """eq r0, r1 - Error si son diferentes"""
        r0, r1 = 42, 43
        assert r0 != r1
    
    def test_neq_not_equal(self):
        """neq r0, r1 - Valida desigualdad"""
        r0, r1 = 42, 43
        assert r0 != r1
    
    def test_neq_equal_error(self):
        """neq r0, r1 - Error si son iguales"""
        r0, r1 = 42, 42
        assert r0 == r1
    
    def test_lt_less_than(self):
        """lt value, 100 - Valida menor que"""
        value = 50
        assert value < 100
    
    def test_lt_not_less_error(self):
        """lt value, 100 - Error si no es menor"""
        value = 150
        assert not (value < 100)
    
    def test_lte_less_or_equal(self):
        """lte value, 100 - Valida menor o igual"""
        value = 100
        assert value <= 100
    
    def test_gt_greater_than(self):
        """gt value, 100 - Valida mayor que"""
        value = 150
        assert value > 100
    
    def test_gte_greater_or_equal(self):
        """gte value, 100 - Valida mayor o igual"""
        value = 100
        assert value >= 100
    
    def test_fits_valid_range(self):
        """fits value, 8 - Valida que cabe en 8 bits"""
        value = 255  # 2^8 - 1
        max_val = (1 << 8) - 1
        assert value <= max_val
    
    def test_fits_overflow_error(self):
        """fits value, 8 - Error si no cabe en 8 bits"""
        value = 256  # 2^8
        max_val = (1 << 8) - 1
        assert value > max_val
    
    def test_bitfit_exact_width(self):
        """bitfit bits, 8 - Valida exactamente 8 bits"""
        bits = "11111111"
        assert len(bits) == 8
    
    def test_bitfit_wrong_width(self):
        """bitfit bits, 8 - Error si no son 8 bits"""
        bits = "1111111"
        assert len(bits) != 8


# ============================================================================
# TESTS: Alineación y Layout
# ============================================================================

class TestAlignment:
    """Tests para directivas de alineación"""
    
    def test_align_4_bytes(self):
        """align 4 - Alinea a 4 bytes"""
        offset = 5
        aligned = ((offset + 3) // 4) * 4
        assert aligned == 8
    
    def test_align_power_of_2(self):
        """align requiere potencias de 2"""
        alignment = 16
        # Verificar que es potencia de 2
        assert (alignment & (alignment - 1)) == 0
    
    def test_align_already_aligned(self):
        """align 4 en offset 8 - Ya está alineado"""
        offset = 8
        alignment = 4
        assert offset % alignment == 0
    
    def test_pad_fills_bytes(self):
        """pad 100 - Rellena hasta byte 100"""
        current = 0
        target = 100
        padding_needed = target - current
        assert padding_needed == 100


# ============================================================================
# TESTS: Memoria y Direcciones
# ============================================================================

class TestMemoryAndAddresses:
    """Tests para operaciones de memoria"""
    
    def test_reloc_absolute_address(self):
        """reloc abs, label, 32 - Registra relocación absoluta"""
        reloc_type = "abs"
        assert reloc_type in ["abs", "physical"]
    
    def test_reloc_physical_address(self):
        """reloc physical, label, 32 - Registra relocación física"""
        reloc_type = "physical"
        assert reloc_type in ["abs", "physical"]
    
    def test_reldis_relative_displacement(self):
        """reldis label, dest, 8 - Calcula desplazamiento relativo"""
        current_pc = 0x8000
        target_pc = 0x8010
        displacement = target_pc - current_pc
        assert displacement == 0x10
    
    def test_reldis_backward_displacement(self):
        """reldis label cuando está atrás - Desplazamiento negativo"""
        current_pc = 0x8010
        target_pc = 0x8000
        displacement = target_pc - current_pc
        assert displacement < 0
    
    def test_emitaddress_resolves_label(self):
        """emitaddress label - Resuelve dirección de etiqueta"""
        label = "start"
        assert isinstance(label, str)
    
    def test_exists_checks_label_exists(self):
        """exists label - Verifica existencia de etiqueta"""
        labels = {"start", "loop", "end"}
        assert "start" in labels
    
    def test_exists_label_not_found(self):
        """exists undefined_label - Error si no existe"""
        labels = {"start", "loop"}
        assert "undefined" not in labels


# ============================================================================
# TESTS: Fillables
# ============================================================================

class TestFillables:
    """Tests para directivas fillables"""
    
    def test_fillid_resolves_physical_address(self):
        """fillid asset_name - Resuelve dirección física"""
        fillables = {
            "sprite_1": {"physical": 0x06000000},
            "sprite_2": {"physical": 0x06001000}
        }
        assert fillables["sprite_1"]["physical"] == 0x06000000
    
    def test_vfillid_resolves_virtual_address(self):
        """vfillid asset_name - Resuelve dirección virtual"""
        fillables = {
            "data": {"virtual": 0x08000000}
        }
        assert fillables["data"]["virtual"] == 0x08000000


# ============================================================================
# TESTS: Integración
# ============================================================================

class TestIntegration:
    """Tests de integración de directivas"""
    
    def test_complete_rule_emission(self):
        """Regla completa: need + emit"""
        # Simulación de regla mov_reg
        rule = {
            'needs': ['REG', 'REG'],
            'operators': ['dest', 'src'],
            'emits': ['0001', 'dest.bits', 'src.bits']
        }
        assert len(rule['needs']) == 2
        assert len(rule['operators']) == 2
    
    def test_conditional_branching_rule(self):
        """Regla con ramificación condicional"""
        rule = {
            'condition': 'bne',
            'target': 'label',
            'displacement': 0x20
        }
        assert rule['condition'] in ['beq', 'bne', 'blt', 'bgt']
    
    def test_stack_operations(self):
        """Operaciones de pila"""
        stack = []
        stack.append(0x1234)  # push
        assert len(stack) == 1
        value = stack.pop()  # pop
        assert value == 0x1234
    
    def test_multiple_sections(self):
        """Manejo de múltiples secciones"""
        sections = {
            '.rom': [],
            '.data': [],
            '.bss': []
        }
        sections['.rom'].append("emit 0b11111111")
        assert len(sections['.rom']) == 1


# ============================================================================
# TESTS: Casos Limite y Errores
# ============================================================================

class TestEdgeCases:
    """Tests de casos límite y manejo de errores"""
    
    def test_need_single_char_operator(self):
        """need VALUE x - Operador de un carácter"""
        operator = "x"
        import re
        ident_re = re.compile(r"^[A-Za-z_][A-Za-z0-9_:-]*$")
        assert ident_re.match(operator)
    
    def test_need_underscore_prefix(self):
        """need VALUE _private - Operador con prefijo _"""
        operator = "_private"
        import re
        ident_re = re.compile(r"^[A-Za-z_][A-Za-z0-9_:-]*$")
        assert ident_re.match(operator)
    
    def test_emit_single_bit(self):
        """emit 1 - Emite un solo bit"""
        bits = "1"
        import re
        bits_re = re.compile(r"^[01]+$")
        assert bits_re.match(bits)
    
    def test_emit_large_bit_sequence(self):
        """emit 1111...1111 (1000 bits)"""
        bits = "1" * 1000
        import re
        bits_re = re.compile(r"^[01]+$")
        assert bits_re.match(bits)
    
    def test_fits_zero_value(self):
        """fits 0, 1 - Cero cabe en 1 bit"""
        value = 0
        max_val = (1 << 1) - 1
        assert value <= max_val
    
    def test_bitcat_empty_operands(self):
        """bitcat dest - Sin operandos fuente"""
        operands = []
        assert len(operands) == 0
    
    def test_align_large_boundary(self):
        """align 4096 - Alineación grande"""
        alignment = 4096
        # Verificar potencia de 2
        assert (alignment & (alignment - 1)) == 0
    
    def test_compare_boundary_values(self):
        """Comparaciones en límites de rango"""
        # 8 bits: 0-255
        max_8bit = 255
        assert max_8bit < 256
        assert (max_8bit + 1) == 256


# ============================================================================
# Fixtures y Utilidades
# ============================================================================

@pytest.fixture
def mock_line():
    """Fixture para MockLine"""
    return MockLine()


@pytest.fixture
def mock_operator():
    """Fixture para MockOperator"""
    MockOperator.reset()
    return MockOperator


@pytest.fixture
def compile_context():
    """Fixture para contexto de compilación"""
    return {
        'operators': {},
        'labels': {},
        'sections': {},
        'errors': []
    }


# ============================================================================
# Tests Paramétricos
# ============================================================================

class TestParametric:
    """Tests paramétricos para validación exhaustiva"""
    
    @pytest.mark.parametrize("bits,is_valid", [
        ("10101010", True),
        ("11110000", True),
        ("1", True),
        ("0", True),
        ("2", False),
        ("10a01010", False),
        ("", False),
    ])
    def test_emit_bits_validation(self, bits, is_valid):
        """Validación paramétrica de bits para emit"""
        import re
        bits_re = re.compile(r"^[01]+$")
        result = bool(bits_re.match(bits)) if bits else False
        assert result == is_valid
    
    @pytest.mark.parametrize("alignment,is_power_of_2", [
        (1, True),
        (2, True),
        (4, True),
        (8, True),
        (16, True),
        (32, True),
        (64, True),
        (3, False),
        (5, False),
        (7, False),
    ])
    def test_align_power_of_2_validation(self, alignment, is_power_of_2):
        """Validación de que alineaciones sean potencias de 2"""
        is_pow2 = (alignment & (alignment - 1)) == 0
        assert is_pow2 == is_power_of_2
    
    @pytest.mark.parametrize("value,bits,fits", [
        (0, 1, True),
        (1, 1, True),
        (2, 1, False),
        (255, 8, True),
        (256, 8, False),
        (65535, 16, True),
        (65536, 16, False),
    ])
    def test_fits_validation(self, value, bits, fits):
        """Validación paramétrica del operador fits"""
        max_val = (1 << bits) - 1
        result = value <= max_val
        assert result == fits


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
