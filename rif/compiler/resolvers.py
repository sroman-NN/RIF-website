from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from rif.compiler.compiler import Compiler

from rif.compiler.imports import *

from rif.compiler.end_instruction import _EndInstruction
from rif.compiler.runtime import _Runtime
from rif.compiler import conversors, parser

def rule(compiler: 'Compiler', rule_name: str) -> Statement | None:
    """Busca y retorna la declaración de regla correspondiente en la sección `.rules`.

    Args:
        rule_name: Nombre de la regla del ISA.

    Returns:
        El nodo Statement de la regla, o None si no se encuentra.
    """
    rules = compiler.program.section(".rules")
    if rules is None:
        return None
    return next((stmt for stmt in rules.statements if stmt.name == rule_name), None)

def match_rule(compiler: 'Compiler', rule_name: str, tokens: list[str]) -> tuple[dict[str, OperandValue], int]:
    """Compara y mapea tokens de ensamblador con la plantilla de operandos exigida por una regla.

    Args:
        rule_name: Nombre de la regla a emparejar.
        tokens: Lista de tokens proporcionados en la instrucción del ensamblador.

    Returns:
        Una tupla con el diccionario de operandos enlazados (bindings) y la cantidad de tokens consumidos.
    """
    exprs = compiler.program.codegen.expressions_by_rule.get(rule_name, [])
    bindings: dict[str, OperandValue] = {}
    index = 0

    optional_separators = {",", "="}

    for expr in exprs:
        if not expr.elements:
            continue
        kind = expr.elements[0]

        if kind == "need_literal":
            if index >= len(tokens):
                raise PackError(f'se esperaba literal "{expr.elements[1]}"')
            expected = str(expr.elements[1])
            got = tokens[index]
            if got != expected:
                raise PackError(f'se esperaba literal "{expected}", se encontró "{got}"')
            index += 1
            continue

        if kind == "need":
            while index < len(tokens) and tokens[index] in optional_separators:
                index += 1
            if index >= len(tokens):
                raise PackError("faltan operandos para la regla")
            valid_types = list(expr.elements[1])
            target = str(expr.elements[2])
            bindings[target] = resolve_operand(compiler, tokens[index], valid_types, rule_name)
            index += 1
            continue

    while index < len(tokens) and tokens[index] in optional_separators:
        index += 1
    return bindings, index

def resolve_operand(compiler: 'Compiler', token: str, valid_types: list[Any], rule_name: str) -> OperandValue:
    """Resuelve semánticamente un token de operando detectando su tipo exacto.

    Detecta si el token es un registro, un tipo del ISA, un valor inmediato,
    una región de memoria, una etiqueta o un símbolo.

    Args:
        token: Cadena de texto del operando.
        valid_types: Tipos de operandos esperados/permitidos por la regla.
        rule_name: Nombre de la regla del ISA de origen.

    Returns:
        Un objeto OperandValue con los metadatos y estado del operando.
    """
    valid_names = {str(item) for item in valid_types}

    reg = find_register(compiler, token)
    if reg is not None:
        priv = "register" if reg.is_parent else "subregister"
        allowed = (priv == "register" and ".regs" in valid_names) or (priv == "subregister" and ".regs.subs" in valid_names)
        if allowed:
            info = TypeInfo(reg.values.copy())
            info.setdefault("NAME", reg.name)
            info["NAME"] = reg.name
            info["bits"] = reg.bits
            info["PRIVTYPE"] = priv
            return OperandValue(name=token, type=info, resolved=True)

    if "TYPE" in valid_names:
        type_operand = resolve_type_operand(compiler, token)
        if type_operand is not None:
            return type_operand

    if "VALUE" in valid_names:
        value_operand = resolve_value_operand(compiler, token)
        if value_operand is not None:
            return value_operand

    if {"STACK", "HEAP", "MEMORY"} & valid_names:
        memory_operand = resolve_memory_operand(compiler, token, valid_names, rule_name)
        if memory_operand is not None:
            return memory_operand

    if "SYMBOL" in valid_names:
        row = compiler.program.objects.get(token)
        if row is not None and (row.section == ".data" or row.values.get("PRIVTYPE") in {"stack", "heap"}):
            info = TypeInfo(row.values.copy())
            info.setdefault("NAME", row.name)
            info.setdefault("PRIVTYPE", "symbol" if row.section == ".data" else row.values.get("PRIVTYPE"))
            ph = Placeholder(target=token, kind="symbol", reason="símbolo diferido", rule_name=rule_name)
            return OperandValue(name=token, type=info, resolved=False, placeholder=ph)

        ph = Placeholder(target=token, kind="symbol", reason="símbolo no resuelto", rule_name=rule_name)
        info = TypeInfo({"NAME": token, "PRIVTYPE": "symbol", "bits": None})
        return OperandValue(name=token, type=info, resolved=False, placeholder=ph)

    if "LABEL" in valid_names:
        if token in compiler.labels:
            info = TypeInfo({"NAME": token, "PRIVTYPE": "label", "addrs": compiler.labels[token], "bits": None})
            return OperandValue(name=token, type=info, resolved=True)
        ph = Placeholder(target=token, kind="label", reason="etiqueta no resuelta", rule_name=rule_name)
        info = TypeInfo({"NAME": token, "PRIVTYPE": "label", "bits": None})
        return OperandValue(name=token, type=info, resolved=False, placeholder=ph)

    ph = Placeholder(target=token, kind="unknown", reason="operando no conocido", rule_name=rule_name)
    info = TypeInfo({"NAME": token, "PRIVTYPE": "unknown", "bits": None})
    return OperandValue(name=token, type=info, resolved=False, placeholder=ph)

def find_register(compiler: 'Compiler', token: str):
    """Busca un registro en el programa a través de su nombre o alias.

    Args:
        token: Nombre o alias del registro.

    Returns:
        El objeto registro correspondiente, o None si no se encuentra.
    """
    return next((r for r in compiler.program.regs.registers if r.name == token or r.alias == token), None)

def resolve_type_operand(compiler: 'Compiler', token: str) -> OperandValue | None:
    """Intenta resolver el token como un operando de definición de tipo.

    Args:
        token: Token a analizar.

    Returns:
        OperandValue si es un tipo válido, o None en caso contrario.
    """
    parsed = parser.parse_type_token(token, compiler.program)
    if parsed is None:
        return None
    definition, requested_size, dimensions = parsed
    info = TypeInfo(definition.values.copy())
    info["NAME"] = definition.name
    info["TYPE"] = "TYPE"
    info["PRIVTYPE"] = "type"
    info["raw"] = token
    info["SIZE"] = requested_size if requested_size is not None else definition.size
    info["size"] = requested_size if requested_size is not None else definition.size
    if requested_size is not None:
        info["bits"] = requested_size
    elif definition.bits is not None:
        info["bits"] = definition.bits
    if dimensions:
        info["dimensions"] = dimensions
    return OperandValue(name=token, type=info, resolved=True)

def resolve_value_operand(compiler: 'Compiler', token: str) -> OperandValue | None:
    """Intenta resolver el token como un operando de valor numérico inmediato.

    Args:
        token: Token a analizar.

    Returns:
        OperandValue si es un valor inmediato numérico válido, o None en caso contrario.
    """
    value = parser.parse_immediate_value(token, allow_string=False)
    if value is None:
        return None
    info = TypeInfo({
        "NAME": token,
        "TYPE": "VALUE",
        "PRIVTYPE": "value",
        "raw": value["raw"],
        "size": value["size"],
        "bits": value["size"],
        "binary": value["binary"],
        "value": value.get("value"),
    })
    return OperandValue(name=token, type=info, resolved=True)

def resolve_memory_operand(compiler: 'Compiler', token: str, valid_names: set[str], rule_name: str) -> OperandValue | None:
    """Intenta resolver el token como un operando de región de memoria del AST.

    Args:
        token: Token a analizar.
        valid_names: Conjunto de tipos esperados de operando.
        rule_name: Nombre de la regla origen.

    Returns:
        OperandValue si se trata de una región de memoria válida, o None.
    """
    region = compiler.program.memory.get(token)
    if region is None:
        return None
    if "MEMORY" not in valid_names:
        if region.kind == "stack" and "STACK" not in valid_names:
            return None
        if region.kind == "heap" and "HEAP" not in valid_names:
            return None

    info = TypeInfo(region.values.copy())
    info.setdefault("NAME", region.name)
    info.setdefault("PRIVTYPE", region.kind)
    ph = Placeholder(target=token, kind=region.kind, reason=f"{region.kind} diferido", rule_name=rule_name)
    return OperandValue(name=token, type=info, resolved=False, placeholder=ph)


def eval_int(compiler: 'Compiler', expr: str, runtime: _Runtime, kind: str = "number") -> int | Placeholder:
    def resolve(name: str) -> Any:
        if name in runtime.bit_values:
            return int(runtime.bit_values[name] or "0", 2)
        if name in compiler.program.vars:
            return int(compiler.program.vars[name].bits, 2)
        if name in runtime.labels:
            return runtime.labels[name]
        if "." in name:
            target, field = name.split(".", 1)
            operand = runtime.bindings.get(target)
            if operand is not None:
                value = operand.type.get(field)
                if value not in (None, ""):
                    return value
            row = compiler.program.objects.get(target)
            if row is not None:
                value = row.values.get(field)
                if value not in (None, ""):
                    return value
        operand = runtime.bindings.get(name)
        if operand is not None:
            value = operand.type.get("value", operand.type.get("bits"))
            if value not in (None, ""):
                return value
        row = compiler.program.objects.get(name)
        if row is not None:
            value = row.values.get("addrs", row.values.get("VALUE"))
            if value not in (None, ""):
                return value
        raise UnresolvedExpression(name)

    try:
        return eval_int_expr(expr, resolve)
    except UnresolvedExpression as exc:
        return Placeholder(target=exc.name, kind=kind, reason="expresion diferida", rule_name=runtime.rule_name)
    except SyntaxError as exc:
        raise PackError(f'expresion numerica invalida "{expr}"') from exc
    except ValueError as exc:
        raise PackError(f'expresion numerica invalida "{expr}"') from exc

def resolve_numeric_operand(compiler: 'Compiler', name: str, runtime: _Runtime) -> int | Placeholder:
    """Resuelve un operando interpretándolo como un entero de 64 bits.

    Args:
        name: Nombre de la variable, campo o literal numérico.
        runtime: Estado de compilación dinámico.

    Returns:
        El valor numérico como int, o un objeto Placeholder si es diferido.
    """
    token = name.strip()
    if not token:
        return Placeholder(target=name, kind="number", reason="valor vacio", rule_name=runtime.rule_name)

    value = eval_int(compiler, token, runtime, kind="number")
    if not isinstance(value, Placeholder):
        return value
    if any(op in token for op in "+-*/%<>&|^~()"):
        return value

    if "." in token and token != ".":
        target, field = token.split(".", 1)
        operand = runtime.bindings.get(target)
        if operand is None:
            return Placeholder(target=target, field=field, kind="number", reason="operador no ligado", rule_name=runtime.rule_name)
        value = operand.type.get(field)
        if value in (None, ""):
            return Placeholder(target=target, field=field, kind=operand.type.get("PRIVTYPE", "unknown"), reason="campo diferido", rule_name=runtime.rule_name)
        try:
            if field == "binary":
                return int(str(value).replace("_", ""), 2)
            return int(str(value).replace("_", ""), 0)
        except ValueError:
            return int(conversors.value_to_bits(value), 2)

    bits = resolve_bits_operand(compiler, token, runtime)
    if isinstance(bits, Placeholder):
        return bits
    return int(bits or "0", 2)

def resolve_bitfit_value(compiler: 'Compiler', name: str, bits: str, runtime: _Runtime) -> int | Placeholder:
    """Obtiene el valor numérico absoluto correspondiente a un chequeo bitfit.

    Args:
        name: Identificador del operando.
        bits: Secuencia de bits pre-resuelta del operando.
        runtime: Estado de compilación dinámico.

    Returns:
        Valor numérico entero o un Placeholder.
    """
    try:
        token = name.strip()
        if all(ch in "01" for ch in token):
            return int(token, 2)
        return int(token.replace("_", ""), 0)
    except ValueError:
        pass

    return int(bits or "0", 2)

def resolve_bits_operand(compiler: 'Compiler', name: str, runtime: _Runtime) -> str | Placeholder:
    """Obtiene la secuencia de bits (cadena binaria de ceros y unos) de un operando.

    Args:
        name: Nombre del operando o variable.
        runtime: Estado de compilación dinámico.

    Returns:
        Cadena binaria o un Placeholder si los bits aún no están disponibles.
    """
    token = name.strip()
    if not token:
        return Placeholder(target=name, kind="bits", reason="valor vacío", rule_name=runtime.rule_name)

    if all(ch in "01" for ch in token):
        return token

    if runtime.bit_values and token in runtime.bit_values:
        return runtime.bit_values[token]

    if token in compiler.program.vars:
        return compiler.program.vars[token].bits

    if "." in token and token != ".":
        target, field = token.split(".", 1)
        operand = runtime.bindings.get(target)
        if operand is None:
            return Placeholder(target=target, field=field, kind="bits", reason="operador no ligado", rule_name=runtime.rule_name)
        value = operand.type.get(field)
        if value in (None, ""):
            return Placeholder(target=target, field=field, kind=operand.type.get("PRIVTYPE", "unknown"), reason="campo diferido", rule_name=runtime.rule_name)
        return conversors.value_to_bits(value)

    operand = runtime.bindings.get(token)
    if operand is not None:
        value = operand.type.get("binary")
        if value in (None, ""):
            if operand.placeholder is not None:
                return Placeholder(target=operand.placeholder.target, kind=operand.placeholder.kind, reason="bits diferidos", rule_name=runtime.rule_name)
            return Placeholder(target=token, kind=operand.type.get("PRIVTYPE", "unknown"), reason="bits diferidos", rule_name=runtime.rule_name)
        return conversors.value_to_bits(value)

    return Placeholder(target=token, kind="bits", reason="valor no resuelto", rule_name=runtime.rule_name)



def resolve_chunk(compiler: 'Compiler', chunk: EmitChunk, runtime: _Runtime, instruction: EmitInstruction) -> str | Placeholder:
    """Resuelve un único fragmento (EmitChunk) de bits o valor del operando mapeado.

    Args:
        chunk: El fragmento a resolver.
        runtime: Estado de compilación dinámico.
        instruction: Instrucción de emisión origen.

    Returns:
        Secuencia binaria en cadena de texto o un Placeholder si es diferido.
    """
    if chunk.kind in {"bits", "byte"}:
        return chunk.value

    if chunk.kind == "bits_ref":
        resolved = resolve_bits_operand(compiler, chunk.value, runtime)
        if isinstance(resolved, Placeholder):
            return Placeholder(
                target=resolved.target,
                field=resolved.field,
                kind="emit",
                reason=resolved.reason,
                rule_name=runtime.rule_name,
                line=instruction.line,
            )
        return resolved

    if chunk.kind != "placeholder":
        return Placeholder(target=chunk.value, kind="emit", reason="chunk desconocido", rule_name=runtime.rule_name, line=instruction.line)

    target = chunk.target or ""
    field = chunk.field or ""
    operand = runtime.bindings.get(target)
    if operand is None:
        return Placeholder(target=target, field=field, kind="emit", reason="operador no ligado", rule_name=runtime.rule_name, line=instruction.line)

    value = operand.type.get(field)
    if value in (None, ""):
        return Placeholder(target=target, field=field, kind=operand.type.get("PRIVTYPE", "unknown"), reason="campo diferido", rule_name=runtime.rule_name, line=instruction.line)

    return conversors.value_to_bits(value)

def eval_value(compiler: 'Compiler', expr: str, runtime: _Runtime) -> Any:
    """Evalúa un identificador de operando, propiedad de registro o cadena RIF DSL.

    Args:
        expr: Operación o cadena del operando.
        runtime: Estado de compilación dinámico.

    Returns:
        El valor final evaluado o un Placeholder.
    """
    expr = expr.strip()
    if "." in expr:
        target, field = expr.split(".", 1)
        operand = runtime.bindings.get(target)
        if operand is None:
            return Placeholder(target=target, field=field, kind="eval", reason="operador no ligado", rule_name=runtime.rule_name)
        value = operand.type.get(field)
        if value is None and field == "TYPE":
            value = operand.type.get("PRIVTYPE")
            if value is not None:
                return str(value).upper()
        if value is None:
            return Placeholder(target=target, field=field, kind="eval", reason="campo no resuelto", rule_name=runtime.rule_name)
        return value
    if expr in runtime.bindings:
        return runtime.bindings[expr]
    return expr






def eval_condition(compiler: 'Compiler', stmt: Statement, runtime: _Runtime, rule_name: str) -> bool | Placeholder:
    tokens = condition_tokens(compiler, stmt)
    if not tokens:
        return True

    comparator_index = condition_comparator_index(compiler, tokens)
    if comparator_index is not None:
        op = tokens[comparator_index]
        left = " ".join(tokens[:comparator_index]).strip()
        right = " ".join(tokens[comparator_index + 1:]).strip()
        if not left or not right:
            raise PackError("ON tiene una comparacion incompleta", stmt.line)
        left_value = condition_value(compiler, left, runtime)
        right_value = condition_value(compiler, right, runtime)
        if isinstance(left_value, Placeholder):
            return left_value
        if isinstance(right_value, Placeholder):
            return right_value
        return compare_condition_values(compiler, left_value, op, right_value, stmt.line)

    expr = " ".join(tokens).strip()
    literal = condition_literal(compiler, expr)
    if literal is not None:
        return literal

    value = condition_value(compiler, expr, runtime, allow_bare_string=False)
    if isinstance(value, Placeholder):
        return value
    return truthy_condition(compiler, value)

def condition_tokens(compiler: 'Compiler', stmt: Statement) -> list[str]:
    tokens = [token.value for token in stmt.args if token.value != ","]
    normalized: list[str] = []
    index = 0
    while index < len(tokens):
        current = tokens[index]
        next_value = tokens[index + 1] if index + 1 < len(tokens) else None
        if current == "=" and next_value == "=":
            normalized.append("==")
            index += 2
            continue
        if current in {"<", ">", "!"} and next_value == "=":
            normalized.append(current + "=")
            index += 2
            continue
        normalized.append(current)
        index += 1
    return normalized

def condition_comparator_index(compiler: 'Compiler', tokens: list[str]) -> int | None:
    for index, token in enumerate(tokens):
        if token in {"==", "!=", "<", "<=", ">", ">="}:
            return index
    return None

def condition_value(compiler: 'Compiler', expr: str, runtime: _Runtime, allow_bare_string: bool = True) -> Any:
    expr = expr.strip()
    literal = condition_literal(compiler, expr)
    if literal is not None:
        return literal

    if expr in runtime.bindings or ("." in expr and expr != "."):
        value = eval_value(compiler, expr, runtime)
        if isinstance(value, Placeholder):
            return value
        if isinstance(value, OperandValue):
            return value.type.get("value", value.type.get("binary", value.name))
        return value

    if looks_numeric_condition(compiler, expr, runtime):
        value = eval_int(compiler, expr, runtime, kind="condition")
        if not isinstance(value, Placeholder):
            return value
        if not allow_bare_string:
            return value

    if allow_bare_string:
        return expr
    return Placeholder(target=expr, kind="condition", reason="condicion ON diferida", rule_name=runtime.rule_name)

def looks_numeric_condition(compiler: 'Compiler', expr: str, runtime: _Runtime) -> bool:
    compact = expr.strip().replace("_", "")
    if not compact:
        return False
    if compact.startswith(("0x", "0X", "0b", "0B")):
        return True
    if compact[0].isdigit():
        return True
    if any(op in expr for op in ("+", "-", "*", "/", "%", "<<", ">>", "&", "|", "^", "~", "(", ")")):
        return True
    return expr in runtime.bit_values or expr in runtime.labels or expr in compiler.program.vars or expr in compiler.program.objects

def condition_literal(compiler: 'Compiler', expr: str) -> bool | None:
    text = expr.strip().lower()
    if text in {"true", "yes", "on", "1", "enabled"}:
        return True
    if text in {"false", "no", "off", "0", "disabled", "impossible", "never", "none", "null"}:
        return False
    return None

def truthy_condition(compiler: 'Compiler', value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value != 0
    if isinstance(value, OperandValue):
        return True
    if isinstance(value, str):
        literal = condition_literal(compiler, value)
        if literal is not None:
            return literal
        try:
            return int(value.replace("_", ""), 0) != 0
        except ValueError:
            return bool(value)
    return bool(value)

def compare_condition_values(compiler: 'Compiler', left: Any, op: str, right: Any, line: int | None) -> bool:
    left_cmp, right_cmp = coerce_condition_pair(compiler, left, right)
    if op == "==":
        return left_cmp == right_cmp
    if op == "!=":
        return left_cmp != right_cmp
    if not isinstance(left_cmp, int) or not isinstance(right_cmp, int):
        raise PackError("ON solo permite < <= > >= con valores numericos", line)
    if op == "<":
        return left_cmp < right_cmp
    if op == "<=":
        return left_cmp <= right_cmp
    if op == ">":
        return left_cmp > right_cmp
    if op == ">=":
        return left_cmp >= right_cmp
    raise PackError(f"comparador ON no soportado: {op}", line)

def coerce_condition_pair(compiler: 'Compiler', left: Any, right: Any) -> tuple[Any, Any]:
    left_int = condition_int(compiler, left)
    right_int = condition_int(compiler, right)
    if left_int is not None and right_int is not None:
        return left_int, right_int
    return str(left), str(right)

def condition_int(compiler: 'Compiler', value: Any) -> int | None:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        text = value.strip().replace("_", "")
        try:
            return int(text, 0)
        except ValueError:
            if len(text) > 1 and all(ch in "01" for ch in text):
                return int(text, 2)
    return None
