
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from rif.compiler.compiler import Compiler

from rif.compiler import memory
from rif.compiler import checkers, conversors, resolvers
from rif.compiler.imports import *
from rif.compiler.runtime import _Runtime
from rif.compiler.end_instruction import _EndInstruction


def execute_rule_body(compiler: 'Compiler', rule_name: str, runtime: _Runtime) -> None:
    """Ejecuta secuencialmente el cuerpo del bloque AST perteneciente a una regla.

    Args:
        rule_name: Nombre de la regla a ejecutar.
        runtime: Entorno de ejecución y estado de compilación dinámico.
    """
    if rule_name in runtime.stack:
        chain = " -> ".join(runtime.stack + [rule_name])
        raise PackError(f"call recursivo detectado: {chain}")
    rule = resolvers.rule(compiler, rule_name)
    if rule is None:
        raise PackError(f'regla desconocida "{rule_name}"')
    runtime.stack.append(rule_name)
    try:
        execute_statements(compiler, rule.children, runtime, rule_name)
    finally:
        runtime.stack.pop()

def execute_statements(compiler: 'Compiler', stmts: list[Statement], runtime: _Runtime, rule_name: str) -> None:
    """Evalúa una lista de sentencias/comandos DSL dentro de un contexto de ejecución.

    Args:
        stmts: Lista de sentencias AST a ejecutar.
        runtime: Entorno de ejecución dinámico.
        rule_name: Nombre de la regla origen en ejecución.
    """
    index = 0
    while index < len(stmts):
        stmt = stmts[index]

        if stmt.name == "need":
            index += 1
            continue

        if stmt.name == "end_instruction":
            runtime.expressions.append(Expr(["end_instruction"]))
            raise _EndInstruction()

        if stmt.name == "ON":
            index = execute_on_off(compiler, stmts, index, runtime, rule_name)
            continue

        if stmt.name == "OFF":
            index += 1
            continue

        if stmt.name == "switch":
            execute_switch(compiler, stmt, runtime, rule_name)
            index += 1
            continue

        if stmt.name == "case":
            raise PackError("case solo puede ejecutarse dentro de switch")

        if stmt.name in compiler.plugins:
            under_call = len(runtime.stack) > 1
            res = run_plugin(compiler, stmt, runtime, rule_name, under_call=under_call)
            execute_result(compiler, res, runtime, rule_name)
            index += 1
            continue

        ph = Placeholder(
            target=stmt.name,
            kind="instruction",
            reason="instrucción no conocida por el compiler",
            rule_name=rule_name,
            line=stmt.line,
        )
        runtime.placeholders.append(ph)
        runtime.expressions.append(Expr(["placeholder", ph]))
        index += 1

def execute_on_off(compiler: 'Compiler', stmts: list[Statement], index: int, runtime: _Runtime, rule_name: str) -> int:
    stmt = stmts[index]
    off_stmt = stmts[index + 1] if index + 1 < len(stmts) and stmts[index + 1].name == "OFF" else None
    next_index = index + 2 if off_stmt is not None else index + 1

    condition = resolvers.eval_condition(compiler, stmt, runtime, rule_name)
    if isinstance(condition, Placeholder):
        runtime.placeholders.append(condition)
        runtime.expressions.append(Expr(["placeholder", condition]))
        return next_index

    if condition:
        execute_statements(compiler, stmt.children, runtime, rule_name)
    elif off_stmt is not None:
        execute_statements(compiler, off_stmt.children, runtime, rule_name)
    return next_index


def run_plugin(compiler: 'Compiler', stmt: Statement, runtime: _Runtime, rule_name: str, under_call: bool = False) -> Any:
    """Invoca dinámicamente el plugin especificado por la sentencia.

    Controla si se realiza bajo el flujo de una llamada `call` de regla o la entrada
    principal a través de `_start` si estuviera definida.

    Args:
        stmt: Nodo AST que invoca el plugin.
        rule_name: Nombre de la regla actual.
        under_call: Indica si se ejecuta como resultado de un comando `call` DSL.

    Returns:
        El resultado retornado por la ejecución del plugin (generalmente objetos de tipo Expr).
    """
    mod = compiler.plugins[stmt.name]
    tokens = [stmt.name] + [plugin_arg_value(compiler, token.value, runtime) for token in stmt.args]
    Line.set_tokens(tokens)
    Line.line = stmt.line
    RuleIndicator.current = rule_name
    context = PluginContext(
        program=compiler.program,
        phase="compile",
        config=compiler.config,
        rule_name=rule_name,
        statement=stmt,
        compiler=compiler,
        line=stmt.line,
    )
    setattr(context, "runtime", runtime)
    try:
        if hasattr(mod, "set_context"):
            mod.set_context(context)
        setattr(mod, "CONTEXT", context)
        if under_call:
            res = mod.main()
        elif hasattr(mod, "_start"):
            res = mod._start()
        else:
            res = mod.main()
        if isinstance(res, Err):
            raise PackError(f"Plugin {stmt.name} error: {res.message}", stmt.line)
        return res
    finally:
        RuleIndicator.current = None
        Line.clear()



def execute_switch(compiler: 'Compiler', stmt: Statement, runtime: _Runtime, rule_name: str) -> None:
    """Ejecuta una sentencia condicional de tipo `switch` evaluando sus casos correspondientes.

    Args:
        stmt: Nodo AST del switch.
        runtime: Estado de compilación dinámico.
        rule_name: Nombre de la regla en ejecución.
    """
    expr = " ".join(token.value for token in stmt.args).strip()
    value = resolvers.eval_value(compiler, expr, runtime)
    if isinstance(value, Placeholder):
        runtime.placeholders.append(value)
        runtime.expressions.append(Expr(["placeholder", value]))
        return

    expected = str(value)
    for child in stmt.children:
        if child.name != "case":
            continue
        case_value = " ".join(token.value for token in child.args).strip()
        if case_value == expected:
            execute_statements(compiler, child.children, runtime, rule_name)
            return

    return



def plugin_arg_value(compiler: "Compiler", token: str, runtime: _Runtime) -> str:
    raw = str(token).strip()
    if raw in {",", ""}:
        return raw
    if raw in runtime.bindings or ("." in raw and raw != "."):
        value = resolvers.eval_value(compiler, raw, runtime)
        if isinstance(value, Placeholder):
            return raw
        if isinstance(value, OperandValue):
            return str(value.name)
        return str(value)
    return raw

def execute_result(compiler: "Compiler", result: Any, runtime: _Runtime, rule_name: str) -> None:
    """Procesa y ejecuta de manera recursiva el resultado producido por un plugin.

    Args:
        result: Objeto o colección retornado por el plugin (puede ser Expr, list, etc.).
        runtime: Entorno de ejecución de la compilación.
        rule_name: Nombre de la regla actual.
    """
    if result is None or result == 0:
        return
    if isinstance(result, list):
        for item in result:
            execute_result(compiler, item, runtime, rule_name)
        return
    if isinstance(result, Expr):
        runtime.expressions.append(result)
        execute_expr(compiler, result, runtime, rule_name)
        return
    if isinstance(result, FlowInstruction):
        for item in result.body:
            execute_result(compiler, item, runtime, rule_name)
        return

def execute_expr(compiler: "Compiler", expr: Expr, runtime: _Runtime, rule_name: str) -> None:
    """Interpreta y ejecuta una expresión semántica DSL de RIF.

    Procesa mandatos DSL fundamentales como `fits`, `exists`, `emit`, `call`,
    comparaciones de bits, predicados de tamaño, extensiones y desplazamientos relativos.

    Args:
        expr: Objeto Expr que contiene la operación y sus argumentos.
        runtime: Estado de compilación dinámico.
        rule_name: Nombre de la regla actual.
    """
    if not expr.elements:
        return
    kind = expr.elements[0]

    if kind in {"need", "need_literal"}:
        return

    if kind == "fits":
        checkers.check_fits(compiler, str(expr.elements[1]), str(expr.elements[2]), runtime)
        return

    if kind == "exists":
        target = expr.elements[1]
        checkers.check_exists(compiler, target, runtime, rule_name)
        return

    if kind in {"emit", "emit_bits_exact"}:
        instruction = expr.elements[1]
        if isinstance(instruction, EmitInstruction):
            memory.emit(compiler, instruction, runtime)
        return

    if kind == "call":
        target_rule = str(expr.elements[1])
        execute_rule_body(compiler, target_rule, runtime)
        return

    if kind in {"eq", "neq"}:
        checkers.check_bit_compare(compiler, str(expr.elements[1]), str(expr.elements[2]), kind == "eq", runtime)
        return

    if kind in {"bitsize", "bitfit"}:
        width = resolvers.eval_int(compiler, str(expr.elements[2]), runtime, kind="number")
        if isinstance(width, Placeholder):
            runtime.placeholders.append(width)
            runtime.expressions.append(Expr(["placeholder", width]))
            return
        checkers.check_bit_predicate(compiler, kind, str(expr.elements[1]), width, runtime)
        return

    if kind in {"lt", "lte", "gt", "gte"}:
        checkers.check_numeric_compare(compiler, kind, str(expr.elements[1]), str(expr.elements[2]), runtime)
        return

    if kind in {"bitcat", "trunc", "zext", "sext"}:
        execute_bit_transform(compiler, expr, runtime)
        return

    if kind == "emit_address":
        width = expr.elements[2] if len(expr.elements) > 2 else 64
        memory.emit_address(compiler, expr.elements[1], width, runtime, rule_name)
        return

    if kind == "reldis":
        width = expr.elements[3] if len(expr.elements) > 3 else None
        memory.reldis(compiler, str(expr.elements[1]), str(expr.elements[2]), runtime, rule_name, width)
        return

    if kind == "align":
        n = resolvers.eval_int(compiler, str(expr.elements[1]), runtime, kind="number")
        if isinstance(n, Placeholder):
            runtime.placeholders.append(n)
            runtime.expressions.append(Expr(["placeholder", n]))
            return
        memory.align(compiler, n, runtime)
        return

    if kind == "pad":
        n = resolvers.eval_int(compiler, str(expr.elements[1]), runtime, kind="number")
        if isinstance(n, Placeholder):
            runtime.placeholders.append(n)
            runtime.expressions.append(Expr(["placeholder", n]))
            return
        memory.pad(compiler, n, runtime)
        return

    if kind == "pad_to":
        n = resolvers.eval_int(compiler, str(expr.elements[1]), runtime, kind="number")
        if isinstance(n, Placeholder):
            runtime.placeholders.append(n)
            runtime.expressions.append(Expr(["placeholder", n]))
            return
        memory.pad_to(compiler, n, runtime)
        return

    if kind == "placeholder":
        ph = expr.elements[1]
        if isinstance(ph, Placeholder):
            runtime.placeholders.append(ph)
        return

    if kind == "reloc":
        memory.reloc(compiler, expr, runtime)
        return

def execute_bit_transform(compiler: 'Compiler', expr: Expr, runtime: _Runtime) -> None:
    """Ejecuta transformaciones a nivel de bit como bitcat, trunc, zext o sext.

    Args:
        expr: Expresión AST que describe la transformación.
        runtime: Estado de compilación dinámico.
    """
    kind = str(expr.elements[0])
    target = expr.elements[1]
    args = [str(item) for item in expr.elements[2:]]

    if kind == "bitcat":
        pieces: list[str] = []
        for arg in args:
            bits = resolvers.resolve_bits_operand(compiler, arg, runtime)
            if isinstance(bits, Placeholder):
                runtime.placeholders.append(bits)
                runtime.expressions.append(Expr(["placeholder", bits]))
                return
            pieces.append(bits)
        result = "".join(pieces)
    else:
        value_ref = args[0]
        width = resolvers.eval_int(compiler, args[1], runtime, kind="number")
        if isinstance(width, Placeholder):
            runtime.placeholders.append(width)
            runtime.expressions.append(Expr(["placeholder", width]))
            return
        bits = resolvers.resolve_bits_operand(compiler, value_ref, runtime)
        if isinstance(bits, Placeholder):
            runtime.placeholders.append(bits)
            runtime.expressions.append(Expr(["placeholder", bits]))
            return
        result = conversors.transform_bits(kind, bits, width)

    if target is not None:
        runtime.bit_values[str(target)] = result
    runtime.expressions.append(Expr([f"{kind}_value", target, result]))

