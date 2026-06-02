from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from rif.compiler.compiler import Compiler


from rif.compiler import comparer, parser
from rif.compiler.imports import *
from rif.compiler.runtime import _Runtime
from rif.compiler.end_instruction import _EndInstruction
from rif.compiler import resolvers


def check_fits(compiler: 'Compiler', left: str, right: str, runtime: _Runtime) -> None:
    """Verifica que el tamaño en bits de dos operandos coincida perfectamente.

    Lanza PackError si hay incompatibilidad de tamaño una vez resueltos.

    Args:
        left: Nombre de la variable u operando izquierdo.
        right: Nombre de la variable u operando derecho.
        runtime: Estado de compilación dinámico.
    """
    left_op = runtime.bindings.get(left)
    right_op = runtime.bindings.get(right)
    if left_op is None or right_op is None:
        ph = Placeholder(target=f"{left},{right}", kind="fits", reason="operando no ligado", rule_name=runtime.rule_name)
        runtime.placeholders.append(ph)
        return

    bits_left = left_op.type.get("bits")
    bits_right = right_op.type.get("bits")
    if bits_left is None or bits_right is None:
        ph = Placeholder(target=f"{left}.bits,{right}.bits", kind="fits", reason="tamaño diferido", rule_name=runtime.rule_name)
        runtime.placeholders.append(ph)
        return

    if int(bits_left) != int(bits_right):
        raise PackError("El operador origen no cabe en el operador destino")

def check_exists(compiler: 'Compiler', target: Any, runtime: _Runtime, rule_name: str) -> None:
    """Verifica la existencia física de un registro o símbolo definido.

    Lanza PackError si se confirma que el registro especificado no existe en el hardware.

    Args:
        target: Identificador del operando o variable.
        runtime: Estado de compilación dinámico.
        rule_name: Nombre de la regla origen.
    """
    if isinstance(target, Placeholder):
        if target.target in runtime.bindings:
            check_exists(compiler, target.target, runtime, rule_name)
            return
        runtime.placeholders.append(target)
        return

    name = str(target)
    op = runtime.bindings.get(name)
    if op is None:
        runtime.placeholders.append(Placeholder(target=name, kind="unknown", reason="existencia diferida", rule_name=rule_name))
        return

    privtype = op.type.get("PRIVTYPE")
    if privtype == "symbol":
        runtime.placeholders.append(op.placeholder or Placeholder(target=op.name, kind="symbol", rule_name=rule_name))
        return

    if privtype in {"register", "subregister"}:
        if not REG.exists(op.type.get("NAME", op.name)):
            raise PackError("El registro no existe")
        return

    if not op.resolved:
        runtime.placeholders.append(op.placeholder or Placeholder(target=op.name, kind="unknown", rule_name=rule_name))

def check_bit_compare(compiler: 'Compiler', left: str, right: str, expect_equal: bool, runtime: _Runtime) -> None:
    """Compara la equivalencia o no-equivalencia de bits entre dos operandos.

    Args:
        left: Operando izquierdo.
        right: Operando derecho.
        expect_equal: Si es True, evalúa equivalencia (eq); si es False, evalúa desigualdad (neq).
        runtime: Estado de compilación dinámico.
    """
    left_bits = resolvers.resolve_bits_operand(compiler, left, runtime)
    right_bits = resolvers.resolve_bits_operand(compiler, right, runtime)

    if isinstance(left_bits, Placeholder):
        runtime.placeholders.append(left_bits)
        runtime.expressions.append(Expr(["placeholder", left_bits]))
        return
    if isinstance(right_bits, Placeholder):
        runtime.placeholders.append(right_bits)
        runtime.expressions.append(Expr(["placeholder", right_bits]))
        return

    if len(left_bits) != len(right_bits):
        raise PackError("eq/neq solo compara valores del mismo tamaño")

    equal = left_bits == right_bits
    if expect_equal and not equal:
        raise PackError("eq falló: los bits no son iguales")
    if not expect_equal and equal:
        raise PackError("neq falló: los bits son iguales")

def check_bit_predicate(compiler: 'Compiler', kind: str, value_ref: str, width: int, runtime: _Runtime) -> None:
    """Chequea predicados sobre el tamaño u holgura en bits de un operando (bitsize, bitfit).

    Lanza PackError si el predicado falla tras la resolución.

    Args:
        kind: Tipo de predicado ("bitsize" o "bitfit").
        value_ref: Nombre del operando o variable.
        width: Ancho esperado en bits.
        runtime: Estado de compilación dinámico.
    """
    if width < 0:
        raise PackError(f"{kind} no acepta tamanos negativos")

    bits = resolvers.resolve_bits_operand(compiler, value_ref, runtime)
    if isinstance(bits, Placeholder):
        if kind == "bitfit":
            numeric = resolvers.resolve_numeric_operand(compiler, value_ref, runtime)
            if not isinstance(numeric, Placeholder):
                fits = numeric == 0 if width == 0 else 0 <= numeric < (1 << width)
                if not fits:
                    raise PackError(f"bitfit fallo: {value_ref} no cabe en {width} bits")
                return
        runtime.placeholders.append(bits)
        runtime.expressions.append(Expr(["placeholder", bits]))
        return

    if kind == "bitsize":
        if len(bits) != width:
            raise PackError(f"bitsize fallo: {value_ref} tiene {len(bits)} bits, no {width}")
        return

    value = resolvers.resolve_bitfit_value(compiler, value_ref, bits, runtime)
    if isinstance(value, Placeholder):
        runtime.placeholders.append(value)
        runtime.expressions.append(Expr(["placeholder", value]))
        return
    fits = value == 0 if width == 0 else 0 <= value < (1 << width)
    if not fits:
        raise PackError(f"bitfit fallo: {value_ref} no cabe en {width} bits")

def check_numeric_compare(compiler: 'Compiler', kind: str, left: str, right: str, runtime: _Runtime) -> None:
    """Realiza comparaciones numéricas (lt, lte, gt, gte) entre dos operandos.

    Args:
        kind: Tipo de comparación lógica ("lt", "lte", "gt", "gte").
        left: Operando numérico izquierdo.
        right: Operando numérico derecho.
        runtime: Estado de compilación dinámico.
    """
    left_value = resolvers.resolve_numeric_operand(compiler, left, runtime)
    right_value = resolvers.resolve_numeric_operand(compiler, right, runtime)

    if isinstance(left_value, Placeholder):
        runtime.placeholders.append(left_value)
        runtime.expressions.append(Expr(["placeholder", left_value]))
        return
    if isinstance(right_value, Placeholder):
        runtime.placeholders.append(right_value)
        runtime.expressions.append(Expr(["placeholder", right_value]))
        return

    ok = {
        "lt": left_value < right_value,
        "lte": left_value <= right_value,
        "gt": left_value > right_value,
        "gte": left_value >= right_value,
    }[kind]
    if not ok:
        raise PackError(f"{kind} fallo: {left_value} y {right_value} no cumplen la comparacion")



def label_from_line(line: str) -> str | None:
    """Determina si la línea especificada corresponde a la definición de una etiqueta.

    Args:
        line: Línea de instrucción ensamblador.

    Returns:
        Nombre de la etiqueta si se matchea el patrón (e.g., 'label:'), o None.
    """
    tokens = parser.split_instruction(line)
    if len(tokens) == 2 and tokens[1] == ":" and comparer.is_label_name(tokens[0]):
        return tokens[0]
    return None

