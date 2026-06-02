from typing import Literal

from rif.compiler.imports import *


def signed_int_to_bits(value: int, width: int, byteorder: Literal['little', 'big']) -> str:
    """Convierte un entero con signo a una cadena binaria de ancho fijo aplicando orden de bytes.

    Args:
        value: Entero a codificar.
        width: Cantidad de bits final (8, 16, 32, 64).
        byteorder: Orden de bytes ("big" o "little").

    Returns:
        Secuencia de bits.
    """
    minimum = -(1 << (width - 1))
    maximum = (1 << (width - 1)) - 1
    if value < minimum or value > maximum:
        raise PackError(f"reldis {value} no cabe en {width} bits")
    encoded = value.to_bytes(width // 8, byteorder=byteorder, signed=True)
    return "".join(format(byte, "08b") for byte in encoded)


def value_to_bits(value: Any) -> str:
    """Convierte un valor genérico o número no signado a su correspondiente representación de bits.

    Args:
        value: Valor de cualquier tipo.

    Returns:
        Cadena binaria.
    """
    if isinstance(value, int):
        if value < 0:
            raise PackError("no se pueden emitir enteros negativos como bits")
        width = max(1, value.bit_length())
        return format(value, f"0{width}b")

    text = str(value).strip()
    if not text:
        raise PackError("campo vacío no puede convertirse a bits")
    if all(ch in "01" for ch in text):
        return text
    if text.startswith(("0b", "0B")):
        body = text[2:]
        if body and all(ch in "01" for ch in body):
            return body
    if text.startswith(("0x", "0X")):
        value_int = int(text, 16)
        width = max(4, ((value_int.bit_length() + 3) // 4) * 4)
        return format(value_int, f"0{width}b")
    raise PackError(f'campo "{text}" no es binario')



def transform_bits(kind: str, bits: str, width: int) -> str:
    """Aplica una transformación específica de extensión o truncamiento sobre una cadena binaria.

    Args:
        kind: Tipo de transformación ("trunc", "zext", "sext").
        bits: Cadena binaria original.
        width: Ancho objetivo en bits.

    Returns:
        Cadena binaria transformada.
    """
    if width < 0:
        raise PackError(f"{kind} no acepta tamanos negativos")

    if kind == "trunc":
        if width == 0:
            return ""
        return bits[-width:]

    if len(bits) > width:
        raise PackError(f"{kind} no puede reducir de {len(bits)} a {width} bits")

    if kind == "zext":
        return bits.rjust(width, "0")

    if kind == "sext":
        sign = bits[0] if bits else "0"
        return bits.rjust(width, sign)

    raise PackError(f"transformacion de bits desconocida: {kind}")



def bits_to_bytes(bits: str) -> bytes:
    if len(bits) % 8 != 0:
        raise PackError(f"la emisión final no está alineada a byte: {len(bits)} bits")
    return bytes(int(bits[index:index + 8], 2) for index in range(0, len(bits), 8))
