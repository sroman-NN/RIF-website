from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from rif.compiler.compiler import Compiler


from rif.compiler.imports import *
from rif.compiler.runtime import _Runtime
from rif.compiler.end_instruction import _EndInstruction
from rif.compiler import checkers, comparer, conversors, executers, parser, resolvers
from rif.compiler import memory

def compile_line_at(compiler: 'Compiler', source: str, base_offset_bits: int, labels: dict[str, int], section: str | None = None) -> CompileResult:
    """Compila una instrucción en un desplazamiento de bits y contexto de etiquetas específico.

    Args:
        source: Línea de instrucción.
        base_offset_bits: Posición base en bits dentro de la sección actual.
        labels: Diccionario de etiquetas resueltas y sus desplazamientos en bytes.
        section: Sección activa para la instrucción.

    Returns:
        Resultado detallado de la compilación.
    """
    activate(compiler)
    tokens = parser.split_instruction(source)
    if not tokens:
        raise PackError("instrucción vacía")

    data_result = compile_data_definition(compiler, source, base_offset_bits)
    if data_result is not None:
        return data_result

    # Directivas internas para emision de direcciones fisicas y virtuales
    if tokens and tokens[0] in {"dw_phys", "dw_virt"}:
        if len(tokens) < 2:
            raise PackError(f"{tokens[0]} requiere un identificador de destino")
        target = tokens[1]
        kind = "physical" if tokens[0] == "dw_phys" else "abs"
        direct_value = parser.parse_direct_int(target)
        if direct_value is not None:
            encoded = direct_value.to_bytes(4, byteorder=memory.byteorder(compiler), signed=False)
            bits = "".join(format(byte, "08b") for byte in encoded)
            return CompileResult(
                rule_name=tokens[0],
                source=source,
                data=encoded,
                bits=bits,
                placeholders=[],
                expressions=[],
                resolved_placeholders=[],
                relocations=[],
            )
        runtime = _Runtime(
            rule_name=tokens[0],
            source=source,
            bindings={},
            base_offset_bits=base_offset_bits,
            labels=labels,
            section=section,
        )
        runtime.placeholders.append(
            Placeholder(
                target=target,
                kind="address" if kind == "abs" else "physical",
                reason=f"direccion {'fisica' if kind == 'physical' else 'virtual'} diferida",
                rule_name=tokens[0],
                line=0,
                width=32,
            )
        )
        runtime.relocations.append(
            Relocation(
                kind=kind,
                target=target,
                offset_bits=base_offset_bits,
                width=32,
                section=section,
                signed=False,
                byteorder=memory.byteorder(compiler),
                rule_name=tokens[0],
                source=source,
            )
        )
        runtime.bits.append_zeros(32)
        return CompileResult(
            rule_name=tokens[0],
            source=source,
            data=None,
            bits=runtime.bits.to_string(),
            placeholders=list(runtime.placeholders),
            expressions=list(runtime.expressions),
            resolved_placeholders=[],
            relocations=list(runtime.relocations),
        )

    rule_name = tokens[0]
    rule = resolvers.rule(compiler, rule_name)
    if rule is None:
        memory_result = compile_memory_definition(compiler, source)
        if memory_result is not None:
            return memory_result
        raise PackError(f'regla desconocida "{rule_name}"')

    bindings, consumed = resolvers.match_rule(compiler, rule_name, tokens[1:])
    if consumed != len(tokens) - 1:
        rest = " ".join(tokens[1 + consumed:])
        raise PackError(f'tokens sobrantes después de matchear {rule_name}: {rest}')

    runtime = _Runtime(
        rule_name=rule_name,
        source=source,
        bindings=bindings,
        base_offset_bits=base_offset_bits,
        labels=labels,
        section=section,
    )
    try:
        executers.execute_rule_body(compiler, rule_name, runtime)
    except _EndInstruction:
        pass
    resolution = PlaceholderResolver(compiler.program, labels).resolve_all(runtime.placeholders)
    runtime.placeholders = list(resolution.unresolved)

    data = None
    if not runtime.placeholders:
        if len(runtime.bits) % 8 == 0:
            data = runtime.bits.to_bytes()

    return CompileResult(
        rule_name=rule_name,
        source=source,
        data=data,
        bits=runtime.bits.to_string(),
        placeholders=list(runtime.placeholders),
        expressions=list(runtime.expressions),
        resolved_placeholders=list(resolution.resolved),
        relocations=list(runtime.relocations or []),
    )

def activate(compiler: Compiler) -> None:
    """Restaura y activa el estado de registro y bindings de operadores del programa.

    Esto garantiza que las expresiones de operadores se evalúen con el contexto correcto.
    """
    Operators.set_program(compiler.program)
    activate_type_map(compiler)
    Operators.saved_operators.clear()
    Operators.saved_operators.update({key: list(value) for key, value in compiler._saved_operators.items()})
    Operators.bindings.clear()
    Operators.bindings.update({key: dict(value) for key, value in compiler._operator_bindings.items()})

def activate_type_map(compiler: 'Compiler') -> None:
    TYPES_MAP.clear()
    TYPES_MAP.update(compiler._type_map)
    

def compile_lines_locked(compiler: 'Compiler', source: str) -> list[CompileResult]:
    """Compila un flujo de líneas estructurado en base a las secciones y etiquetas del SourceReader."""
    from rif.fillables import expand_fillables

    source = expand_fillables(compiler.program, source, phase="compile")
    read = compiler.source_reader.read(source)

    labels = {}
    section_offsets = {}

    for entry in read.entries:
        sec = entry.section or ".text"
        if sec not in section_offsets:
            section_offsets[sec] = 0

        if entry.kind == "label":
            offset_bits = section_offsets[sec]
            if offset_bits % 8 != 0:
                raise PackError(f'la etiqueta "{entry.name}" no cae en límite de byte')
            labels[entry.name] = offset_bits // 8
        elif entry.kind == "instruction":
            line = entry.text
            data_result = compile_data_definition(compiler, line, section_offsets[sec])
            if data_result is not None:
                section_offsets[sec] += len(data_result.bits)
                continue
            memory_result = compile_memory_definition(compiler, line)
            if memory_result is not None:
                continue
            result = compile_line_at(compiler, line, section_offsets[sec], labels, sec)
            section_offsets[sec] += len(result.bits)

    compiler.labels = {
        e.name: {"section": e.section or ".text", "offset": labels[e.name]}
        for e in read.entries if e.kind == "label"
    }

    out = []
    section_offsets = {}
    for entry in read.entries:
        sec = entry.section or ".text"
        if sec not in section_offsets:
            section_offsets[sec] = 0

        if entry.kind in ("label", "section"):
            continue

        line = entry.text
        data_result = compile_data_definition(compiler, line, section_offsets[sec])
        if data_result is not None:
            data_result.section = sec
            out.append(data_result)
            section_offsets[sec] += len(data_result.bits)
            continue

        memory_result = compile_memory_definition(compiler, line)
        if memory_result is not None:
            memory_result.section = sec
            out.append(memory_result)
            continue

        result = compile_line_at(compiler, line, section_offsets[sec], labels, sec)
        result.section = sec
        out.append(result)
        section_offsets[sec] += len(result.bits)

    return out


def compile_memory_definition(compiler: 'Compiler', source: str) -> CompileResult | None:
    """Procesa y compila definiciones de regiones de memoria como pila (stack) o montón (heap).

    Args:
        source: Línea de instrucción con la definición de memoria.

    Returns:
        CompileResult si se compiló con éxito, o None si no corresponde a una definición de memoria.
    """
    tokens = parser.split_instruction(source)
    if not tokens:
        return None
    kind = tokens[0].lower()
    if kind not in {"stack", "heap"}:
        return None
    if len(tokens) < 3:
        raise PackError(f"{kind} usa: {kind} NAME TYPE [COUNT] [SECTION] [ALIGN] [FILL]")

    name = tokens[1]
    if not comparer.is_label_name(name):
        raise PackError(f'nombre de {kind} invalido "{name}"')

    values: dict[str, Any] = {
        "NAME": name,
        "TYPE": tokens[2],
    }
    if len(tokens) > 3:
        values["COUNT"] = tokens[3]
    if len(tokens) > 4:
        values["SECTION"] = tokens[4]
    if len(tokens) > 5:
        values["ALIGN"] = tokens[5]
    if len(tokens) > 6:
        values["FILL"] = tokens[6]
    if len(tokens) > 7:
        raise PackError(f"{kind} tiene demasiados argumentos")

    region = memory_region_from_values(kind, name, values, 0, compiler.program)
    memory.register_memory_region(compiler, region)
    return CompileResult(kind, source, b"", "")

def compile_data_definition(compiler: 'Compiler', source: str, base_offset_bits: int) -> CompileResult | None:
    """Compila una declaración de inicialización de datos estáticos en memoria (e.g., 'var_name type = valor').

    Args:
        source: Línea con la declaración de datos.
        base_offset_bits: Desplazamiento base acumulado en bits.

    Returns:
        CompileResult de la definición de datos si matchea el formato, o None en caso contrario.
    """
    if not compiler.program.data_definition.pattern and not compiler.program.data_definition.options:
        return None

    tokens = parser.split_instruction(source)
    if len(tokens) < 4:
        return None

    name, type_token, literal = tokens[0], tokens[1], tokens[2]
    if literal != "=":
        return None
    if not comparer.is_label_name(name):
        return None

    parsed_type = parser.parse_type_token(type_token, compiler.program)
    if parsed_type is None:
        return None
    type_def, requested_size, dimensions, elem_size = parsed_type

    value_token = " ".join(tokens[3:]).strip()
    allow_string = comparer.type_allows_string(type_def, compiler.program)
    immediate = parser.parse_immediate_value(value_token, allow_string=allow_string)
    if immediate is None:
        raise PackError(f'data definition "{source}" necesita VALUE valido')

    value_bits = str(immediate["binary"])
    value_size = int(immediate["size"])

    is_array = type_def.get_bool("array")
    if is_array and requested_size is None:
        elem_bits = elem_size if elem_size is not None else (type_def.bits or 8)
        length = (value_size + elem_bits - 1) // elem_bits
        if length == 0:
            length = 1
        requested_size = elem_bits * length
        dimensions = [length]

    type_size = requested_size if requested_size is not None else type_def.bits

    if type_size is not None:
        strict = comparer.truthy(type_def.values.get("strictsize"))
        if value_size > type_size:
            raise PackError(f'VALUE de {value_size} bits no cabe en TYPE {type_def.name} de {type_size} bits')
        if strict and value_size != type_size:
            raise PackError(f'TYPE {type_def.name} exige {type_size} bits exactos; VALUE tiene {value_size}')

        arrautofill_opt = compiler.program.data_definition.options.get("arrautofill")
        arrautofill_global = arrautofill_opt is not None and (not arrautofill_opt or comparer.truthy(arrautofill_opt[0]))
        arrautofill_type = type_def.get_bool("arrautofill")
        arrautofill = arrautofill_global or arrautofill_type

        if arrautofill:
            if is_array:
                value_bits = value_bits.ljust(type_size, "0")
            else:
                value_bits = value_bits.rjust(type_size, "0")
        else:
            value_bits = value_bits.rjust(type_size, "0")

    if len(value_bits) % 8 != 0:
        raise PackError("data definition debe emitir un numero completo de bytes")

    offset = base_offset_bits // 8
    data = bytes(int(value_bits[i:i + 8], 2) for i in range(0, len(value_bits), 8))
    row_values = {
        "NAME": name,
        "TYPE": type_def.name,
        "TYPE_RAW": type_token,
        "PRIVTYPE": "symbol",
        "raw": immediate["raw"],
        "size": len(value_bits),
        "bits": len(value_bits),
        "binary": value_bits,
        "addrs": offset,
        "VALUE": immediate.get("value"),
        "SOURCE_DATA": True,
        "SECTION_OFFSET": offset,
    }
    if dimensions:
        row_values["dimensions"] = dimensions
    memory.register_data_row(compiler, name, row_values)
    index_option = compiler.program.data_definition.options.get("index") or ["false"]
    if dimensions and comparer.truthy(index_option[0]):
        count = 1
        for item in dimensions:
            count *= item
        element_bits = elem_size if elem_size is not None else type_def.bits
        if element_bits is None and count and len(value_bits) % count == 0:
            element_bits = len(value_bits) // count
        if element_bits is not None and element_bits % 8 == 0:
            for index in range(count):
                start = index * element_bits
                end = start + element_bits
                child_name = f"{name}[{index}]"
                child_values = dict(row_values)
                child_values["NAME"] = child_name
                child_values["parent"] = name
                child_values["index"] = index
                child_values["size"] = element_bits
                child_values["bits"] = element_bits
                child_values["binary"] = value_bits[start:end]
                child_values["addrs"] = offset + (start // 8)
                child_values["SECTION_OFFSET"] = offset + (start // 8)
                memory.register_data_row(compiler, child_name, child_values)

    return CompileResult("data", source, data, value_bits)
