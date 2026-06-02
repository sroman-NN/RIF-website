from __future__ import annotations
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from rif.compiler.compiler import Compiler

from rif.compiler.imports import *

from rif.compiler.end_instruction import _EndInstruction
from rif.compiler.runtime import _Runtime, _FIXED_EMIT_WIDTHS
from rif.compiler import conversors, resolvers


def emit_address(compiler: 'Compiler', value: Any, width: Any, runtime: _Runtime, rule_name: str) -> None:
    """Emite una dirección absoluta de memoria dentro de la instrucción empaquetada, reservando espacio físico y generando una relocación.

    Args:
        value: Nombre del símbolo, etiqueta u operando que representa la dirección.
        width: Ancho en bits de la dirección (ej. 16, 32, 64).
        runtime: Estado de compilación dinámico.
        rule_name: Nombre de la regla del ISA de origen.
    """
    width_int = 64
    if width not in (None, ""):
        evaluated_width = resolvers.eval_int(compiler, str(width), runtime, kind="number")
        if isinstance(evaluated_width, Placeholder):
            runtime.placeholders.append(evaluated_width)
            runtime.expressions.append(Expr(["placeholder", evaluated_width]))
            return
        width_int = evaluated_width

    if isinstance(value, Placeholder):
        target = value.target
        line = value.line
    else:
        target = str(value).strip()
        line = None

    operand = runtime.bindings.get(target)
    if operand is not None:
        target = str(operand.type.get("NAME", operand.name))
        if operand.placeholder is not None:
            target = operand.placeholder.target

    relocation_offset = runtime.base_offset_bits + len(runtime.bits)
    runtime.placeholders.append(
        Placeholder(
            target=target,
            kind="address",
            reason="dirección de memoria diferida",
            rule_name=rule_name,
            line=line,
            width=width_int,
        )
    )
    runtime.relocations.append(
        Relocation(
            kind="abs",
            target=target,
            offset_bits=relocation_offset,
            width=width_int,
            section=runtime.section,
            signed=False,
            byteorder=byteorder(compiler),
            rule_name=rule_name,
            source=runtime.source,
        )
    )
    runtime.bits.append_zeros(width_int)
    return

def reloc(compiler: 'Compiler', expr: Expr, runtime: _Runtime) -> None:
    if len(expr.elements) < 4:
        raise PackError("reloc espera tipo, destino y ancho")
    kind = str(expr.elements[1])
    target = relocation_target(compiler, str(expr.elements[2]), runtime)
    width = resolvers.eval_int(compiler, str(expr.elements[3]), runtime, kind="number")
    if isinstance(width, Placeholder):
        runtime.placeholders.append(width)
        runtime.expressions.append(Expr(["placeholder", width]))
        return
    addend = 0
    if len(expr.elements) > 4 and expr.elements[4] not in (None, ""):
        addend_value = resolvers.eval_int(compiler, str(expr.elements[4]), runtime, kind="number")
        if isinstance(addend_value, Placeholder):
            runtime.placeholders.append(addend_value)
            runtime.expressions.append(Expr(["placeholder", addend_value]))
            return
        addend = addend_value
    runtime.relocations.append(
        Relocation(
            kind=kind,
            target=target,
            offset_bits=runtime.base_offset_bits + len(runtime.bits),
            width=width,
            section=runtime.section,
            addend=addend,
            signed=kind in {"rel", "reldis", "relative"},
            byteorder=byteorder(compiler),
            rule_name=runtime.rule_name,
            source=runtime.source,
        )
    )
    runtime.bits.append_zeros(width)

def reldis(compiler: 'Compiler', source: str, target: str, runtime: _Runtime, rule_name: str, width: Any = None) -> None:
    """Calcula y emite el desplazamiento de dirección relativo entre un origen y un destino.

    Args:
        source: Símbolo o posición de memoria origen.
        target: Símbolo o posición de memoria destino.
        runtime: Estado de compilación dinámico.
        rule_name: Nombre de la regla actual.
        width: Ancho en bits para empaquetar el desplazamiento (e.g., 8, 16, 32, 64).
    """
    if source != ".":
        source = relocation_target(compiler, source, runtime)
    target = relocation_target(compiler, target, runtime)

    width_int = None
    if width not in (None, ""):
        evaluated_width = resolvers.eval_int(compiler, str(width), runtime, kind="number")
        if isinstance(evaluated_width, Placeholder):
            runtime.placeholders.append(evaluated_width)
            runtime.expressions.append(Expr(["placeholder", evaluated_width]))
            return
        width_int = evaluated_width
    if width_int is not None and width_int not in (8, 16, 32, 64):
        raise PackError("reldis solo acepta tamaños 8, 16, 32 o 64")

    start = memory_point(compiler, source, runtime, rule_name)
    end = memory_point(compiler, target, runtime, rule_name)

    if isinstance(start, Placeholder):
        relocation_offset = runtime.base_offset_bits + len(runtime.bits)
        runtime.placeholders.append(
            Placeholder(
                target=start.target,
                kind=start.kind,
                field=start.field,
                reason=start.reason,
                rule_name=start.rule_name,
                line=start.line,
                width=width_int,
            )
        )
        runtime.expressions.append(Expr(["placeholder", start]))
        if width_int is not None:
            runtime.relocations.append(
                Relocation(
                    kind="reldis",
                    target=target,
                    relative_to=source,
                    offset_bits=relocation_offset,
                    width=width_int,
                    section=runtime.section,
                    signed=True,
                    byteorder=byteorder(compiler),
                    rule_name=rule_name,
                    source=runtime.source,
                )
            )
            runtime.bits.append_zeros(width_int)
        return
    if isinstance(end, Placeholder):
        relocation_offset = runtime.base_offset_bits + len(runtime.bits)
        runtime.placeholders.append(
            Placeholder(
                target=end.target,
                kind=end.kind,
                field=end.field,
                reason=end.reason,
                rule_name=end.rule_name,
                line=end.line,
                width=width_int,
            )
        )
        runtime.expressions.append(Expr(["placeholder", end]))
        if width_int is not None:
            runtime.relocations.append(
                Relocation(
                    kind="reldis",
                    target=end.target,
                    relative_to=source,
                    offset_bits=relocation_offset,
                    width=width_int,
                    section=runtime.section,
                    signed=True,
                    byteorder=byteorder(compiler),
                    rule_name=rule_name,
                    source=runtime.source,
                )
            )
            runtime.bits.append_zeros(width_int)
        return

    origin = start
    if width_int is not None:
        origin += width_int // 8
    distance = end - origin
    runtime.expressions.append(Expr(["reldis_value", source, target, distance, width_int]))
    if width_int is not None:
        runtime.bits.append_string(conversors.signed_int_to_bits(distance, width_int, byteorder(compiler)))

def byteorder(compiler: 'Compiler') -> Literal['big', 'little']:
    """Determina la ordenación de bytes (endianness) configurada en el diseño del ISA.

    Returns:
        La cadena "big" o "little".
    """
    raw = compiler.program.world.values.get("endianness", compiler.program.world.values.get("endianess", "little"))
    if isinstance(raw, int):
        return "big" if raw else "little"
    text = str(raw).strip().lower()
    if text in {"big", "be", "1"}:
        return "big"
    return "little"

def memory_point(compiler: 'Compiler', token: str, runtime: _Runtime, rule_name: str) -> int | Placeholder:
    """Calcula el offset numérico en bytes de un punto en memoria o etiqueta.

    Args:
        token: Símbolo o etiqueta a evaluar.
        runtime: Estado de compilación dinámico.
        rule_name: Nombre de la regla actual.

    Returns:
        El desplazamiento absoluto en bytes o un Placeholder si es diferido.
    """
    token = token.strip()
    if token == ".":
        current_bits = runtime.base_offset_bits + len(runtime.bits)
        if current_bits % 8 != 0:
            return Placeholder(target=".", kind="reldis", reason="posición actual no alineada a byte", rule_name=rule_name)
        return current_bits // 8

    if token in runtime.labels:
        if token in compiler.labels:
            target_sec = compiler.labels[token].get("section") or ".text"
            runtime_sec = runtime.section or ".text"
            if target_sec != runtime_sec:
                return Placeholder(target=token, kind="reldis", reason="cruce de secciones diferido", rule_name=rule_name)
        return runtime.labels[token]

    obj = compiler.program.objects.get(token)
    if obj is not None:
        value = obj.values.get("addrs")
        if value not in (None, ""):
            try:
                return int(value)
            except ValueError:
                return Placeholder(target=token, kind="reldis", reason="dirección inválida", rule_name=rule_name)

    operand = runtime.bindings.get(token)
    if operand is not None:
        value = operand.type.get("addrs")
        if value not in (None, ""):
            try:
                return int(value)
            except ValueError:
                return Placeholder(target=token, kind="reldis", reason="dirección inválida", rule_name=rule_name)
        if operand.placeholder is not None:
            return Placeholder(target=operand.placeholder.target, kind="reldis", reason="dirección diferida", rule_name=rule_name)

    return Placeholder(target=token, kind="reldis", reason="etiqueta o dirección no resuelta", rule_name=rule_name)

def align(compiler: 'Compiler', n: int, runtime: _Runtime) -> None:
    """Alinea el desplazamiento de bits de la emisión a un múltiplo de 'n' bytes.

    Rellena con ceros hasta alcanzar la frontera de alineación.

    Args:
        n: Cantidad de bytes a la cual alinear.
        runtime: Estado de compilación dinámico.
    """
    if n <= 0:
        raise PackError("align espera un número mayor que cero")
    current_bits = runtime.base_offset_bits + len(runtime.bits)
    if current_bits % 8 != 0:
        raise PackError("align requiere que la posición actual esté en límite de byte")
    current_byte = current_bits // 8
    missing = (-current_byte) % n
    if missing:
        runtime.bits.append_zeros(missing * 8)

def pad(compiler: 'Compiler', n: int, runtime: _Runtime) -> None:
    """Introduce un relleno físico de 'n' bytes con ceros en la instrucción actual.

    Args:
        n: Número de bytes de relleno.
        runtime: Estado de compilación dinámico.
    """
    if n < 0:
        raise PackError("pad no acepta números negativos")
    if n:
        runtime.bits.append_zeros(n * 8)

def pad_to(compiler: 'Compiler', n: int, runtime: _Runtime) -> None:
    if n < 0:
        raise PackError("pad_to no acepta numeros negativos")
    current_bits = runtime.base_offset_bits + len(runtime.bits)
    if current_bits % 8 != 0:
        raise PackError("pad_to requiere que la posicion actual este en limite de byte")
    current_byte = current_bits // 8
    if n < current_byte:
        raise PackError(f"pad_to {n} queda antes de la posicion actual {current_byte}")
    pad(compiler, n - current_byte, runtime)

def relocation_target(compiler: 'Compiler', target: str, runtime: _Runtime) -> str:
    operand = runtime.bindings.get(target)
    if operand is None:
        return target
    if operand.placeholder is not None:
        return str(operand.placeholder.target)
    if operand.type.get("PRIVTYPE") == "label":
        value = operand.type.get("NAME")
        if value not in (None, ""):
            return str(value)
    for key in ("value", "addrs", "NAME"):
        value = operand.type.get(key)
        if value not in (None, ""):
            return str(value)
    return target

def emit(compiler: 'Compiler', instruction: EmitInstruction, runtime: _Runtime) -> None:
    """Concatena y añade los fragmentos (chunks) binarios de una directiva `emit` a los bits de salida.

    Args:
        instruction: Objeto EmitInstruction con los fragmentos a empaquetar.
        runtime: Estado de compilación dinámico.
    """
    bits = ""
    unresolved = False
    for chunk in instruction.chunks:
        resolved = resolvers.resolve_chunk(compiler, chunk, runtime, instruction)
        if isinstance(resolved, Placeholder):
            unresolved = True
            runtime.placeholders.append(resolved)
            runtime.expressions.append(Expr(["placeholder", resolved]))
            continue
        bits += resolved

    fixed_width = _FIXED_EMIT_WIDTHS.get(instruction.mode)
    if fixed_width is not None:
        if len(bits) > fixed_width:
            raise PackError(f"emit {instruction.mode} produjo {len(bits)} bits; se esperaban {fixed_width}")
        if unresolved:
            bits += "0" * (fixed_width - len(bits))
        elif len(bits) != fixed_width:
            raise PackError(f"emit {instruction.mode} produjo {len(bits)} bits; se esperaban {fixed_width}")
    elif instruction.mode == "cbits":
        padding = (-len(bits)) % 8
        if padding:
            bits += "0" * padding
    elif instruction.requires_byte and len(bits) % 8 != 0:
        raise PackError(f"emit produjo {len(bits)} bits; se esperaba múltiplo de 8")

    runtime.bits.append_string(bits)



def register_data_row(compiler: 'Compiler', name: str, values: dict[str, Any]) -> None:
    """Registra un nuevo símbolo de datos en la tabla global y sección `.data` del programa.

    Args:
        name: Nombre del símbolo.
        values: Atributos y metadatos del símbolo de datos.
    """
    row = TableRow(name=name, values=values, line=0, section=".data")
    compiler.program.objects[name] = row
    table = compiler.program.tables.get(".data")
    if table is not None:
        table.rows[name] = row

def register_memory_region(compiler: 'Compiler', region: MemoryRegion) -> None:
    """Registra una región de memoria (stack o heap) dentro del AST y su respectiva tabla global.

    Args:
        region: Objeto de tipo MemoryRegion que encapsula la definición.
    """
    section_name = f".{region.kind}s"
    table = compiler.program.tables.get(section_name)
    if table is None:
        fields = ["NAME", "TYPE", "COUNT", "SECTION", "ALIGN", "FILL"]
        table = Table(section=section_name, fields=fields)
        compiler.program.tables[section_name] = table

    row = TableRow(name=region.name, values=region.values, line=region.line or 0, section=section_name)
    table.rows[region.name] = row
    compiler.program.objects[region.name] = row
    compiler.program.memory.add(region)

