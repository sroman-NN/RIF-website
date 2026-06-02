from rif.compiler.imports import *

def parse_type_token(token: str, program: Program) -> tuple[TypeDefinition, int | None, list[int], int | None] | None:
    """Parseará el tipo de dato especificado en ensamblador, detectando dimensiones y tamaño total.

    Soporta la declaración dinámica de arrays basándose en las columnas de .types.
    """
    raw = token.strip()
    if not raw:
        return None

    name = raw
    dimensions: list[int] = []
    if "[" in raw and raw.endswith("]"):
        name, rest = raw.split("[", 1)
        rest = rest[:-1].strip()
        if rest:
            for item in rest.split(","):
                item = item.strip()
                if not item:
                    return None
                try:
                    dimensions.append(int(item.replace("_", ""), 0))
                except ValueError:
                    return None

    definition = program.type_defs.get(name)
    if definition is None:
        return None

    is_array = definition.get_bool("array")
    elem_size = definition.bits

    if is_array:
        longset = definition.get_bool("longset")
        sizeset = definition.get_bool("sizeset")

        if sizeset and longset:
            if len(dimensions) != 2:
                raise PackError(f"El tipo array {name} requiere especificar [SIZE, LONG]. Ejemplo: {name}[8, 10]")
            elem_size = dimensions[0]
            length = dimensions[1]
            requested_size = elem_size * length
            logical_dimensions = [length]
        elif sizeset and not longset:
            if len(dimensions) == 1:
                elem_size = dimensions[0]
                requested_size = None
                logical_dimensions = []
            elif len(dimensions) == 2:
                elem_size = dimensions[0]
                length = dimensions[1]
                requested_size = elem_size * length
                logical_dimensions = [length]
            else:
                raise PackError(f"El tipo array {name} requiere especificar [SIZE] o [SIZE, LONG]")
        elif not sizeset and longset:
            if len(dimensions) != 1:
                raise PackError(f"El tipo array {name} requiere especificar [LONG]. Ejemplo: {name}[10]")
            if elem_size is None:
                raise PackError(f"El tipo array {name} requiere un tamaño en bits (bits/SIZE) por defecto en .types")
            length = dimensions[0]
            requested_size = elem_size * length
            logical_dimensions = [length]
        else:
            if not dimensions:
                if elem_size is None:
                    raise PackError(f"El tipo array {name} requiere un tamaño en bits (bits/SIZE) por defecto en .types")
                requested_size = None
                logical_dimensions = []
            elif len(dimensions) == 1:
                if elem_size is None:
                    raise PackError(f"El tipo array {name} requiere un tamaño en bits (bits/SIZE) por defecto en .types")
                length = dimensions[0]
                requested_size = elem_size * length
                logical_dimensions = [length]
            elif len(dimensions) == 2:
                elem_size = dimensions[0]
                length = dimensions[1]
                requested_size = elem_size * length
                logical_dimensions = [length]
            else:
                raise PackError(f"El tipo array {name} no soporta mas de 2 dimensiones")
    else:
        requested_size = definition.bits
        if dimensions and definition.bits is not None:
            count = 1
            for item in dimensions:
                count *= item
            requested_size = definition.bits * count
        logical_dimensions = dimensions

    return definition, requested_size, logical_dimensions, elem_size


def parse_immediate_value(token: str, allow_string: bool = True) -> dict[str, Any] | None:
    """Parseará un valor numérico inmediato o literal (soporta decimal, binario 0b, hex 0x, strings).

    Args:
        token: Token del valor inmediato.
        allow_string: Indica si se permite decodificar como cadena binaria UTF-8 en caso de no ser numérico.

    Returns:
        Diccionario con la secuencia binaria calculada y metadatos, o None si es inválido.
    """
    raw = token.strip()
    if not raw:
        return None

    compact = raw.replace("_", "")
    try:
        value = int(compact, 0)
    except ValueError:
        if not allow_string:
            return None
        data = raw.encode("utf-8")
        bits = "".join(format(byte, "08b") for byte in data)
        return {"raw": raw, "value": raw, "size": len(bits), "binary": bits}

    if value < 0:
        return None

    if compact.startswith(("0b", "0B")):
        bits = compact[2:]
        if not bits or any(ch not in "01" for ch in bits):
            return None
        return {"raw": raw, "value": value, "size": len(bits), "binary": bits}

    if compact.startswith(("0x", "0X")):
        body = compact[2:]
        if not body or any(ch not in "0123456789abcdefABCDEF" for ch in body):
            return None
        width = len(body) * 4
        bits = format(value, f"0{width}b")
        return {"raw": raw, "value": value, "size": width, "binary": bits}

    width = max(1, value.bit_length())
    bits = format(value, f"0{width}b")
    return {"raw": raw, "value": value, "size": width, "binary": bits}


def parse_direct_int(token: str) -> int | None:
    text = str(token).strip().replace("_", "")
    if not text:
        return None
    try:
        value = int(text, 0)
    except ValueError:
        return None
    if value < 0:
        raise PackError("dw_virt/dw_phys no aceptan direcciones negativas")
    if value >= (1 << 32):
        raise PackError("dw_virt/dw_phys requieren una direccion de 32 bits")
    return value




def split_instruction(source: str) -> list[str]:
    """Divide una línea de instrucción en tokens léxicos respetando comillas, delimitadores y corchetes de arrays."""
    out: list[str] = []
    current: list[str] = []
    quote = False
    escaped = False
    bracket_level = 0
    brace_level = 0

    def push() -> None:
        if current:
            out.append("".join(current))
            current.clear()

    for ch in source.strip():
        if escaped:
            current.append(ch)
            escaped = False
            continue
        if ch == "\\" and quote:
            escaped = True
            continue
        if ch == '"':
            quote = not quote
            continue
        if quote:
            current.append(ch)
            continue
        if ch == "[":
            bracket_level += 1
            current.append(ch)
            continue
        if ch == "]":
            if bracket_level > 0:
                bracket_level -= 1
            current.append(ch)
            continue
        if ch == "{":
            brace_level += 1
            current.append(ch)
            continue
        if ch == "}":
            if brace_level > 0:
                brace_level -= 1
            current.append(ch)
            continue
        if ch.isspace():
            if bracket_level > 0 or brace_level > 0:
                current.append(ch)
            else:
                push()
            continue
        if ch in {",", "=", ":"}:
            if bracket_level > 0 or brace_level > 0:
                current.append(ch)
            else:
                push()
                out.append(ch)
            continue
        current.append(ch)
    push()
    return out


def strip_source_comment(raw: str) -> str:
    """Elimina los comentarios que comienzan con punto y coma (;) respetando cadenas con comillas.

    Args:
        raw: Línea de código fuente ensamblador.

    Returns:
        Línea limpia sin comentario.
    """
    quote = False
    escaped = False
    out: list[str] = []
    for ch in raw:
        if escaped:
            out.append(ch)
            escaped = False
            continue
        if ch == "\\" and quote:
            out.append(ch)
            escaped = True
            continue
        if ch == '"':
            out.append(ch)
            quote = not quote
            continue
        if ch == ";" and not quote:
            break
        out.append(ch)
    return "".join(out).rstrip()
