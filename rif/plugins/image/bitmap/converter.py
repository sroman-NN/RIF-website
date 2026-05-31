from pathlib import Path
import struct
import zlib

from rif.plugins.image.common.cache import get_cached_bytes, set_cached_bytes
from rif.plugin_security import assert_allowed_path


def image_to_bitmap_bytes(image_path: str, threshold: int = 128, invert: bool = False, *, context=None) -> bytes:
    params = {"threshold": threshold, "invert": invert, "format": "1bpp"}
    cached = get_cached_bytes(image_path, params, context=context)
    if cached is not None:
        return cached

    path_obj = assert_allowed_path(image_path, context=context)
    if not path_obj.exists():
        raise FileNotFoundError(f"Imagen no encontrada: {image_path}")

    bits = []
    for row in _load_luma_rows(path_obj):
        for pixel in row:
            bit = 1 if pixel >= threshold else 0
            if invert:
                bit = 1 - bit
            bits.append(bit)

    byte_array = bytearray()
    for i in range(0, len(bits), 8):
        chunk = bits[i:i + 8]
        val = 0
        for b_index, b in enumerate(chunk):
            val |= b << (7 - b_index)
        byte_array.append(val)

    result_bytes = bytes(byte_array)
    set_cached_bytes(image_path, params, result_bytes, context=context)
    return result_bytes


def _load_luma_rows(path: Path) -> list[list[int]]:
    try:
        from PIL import Image
    except ImportError:
        suffix = path.suffix.lower()
        if suffix == ".png":
            return _load_png_luma(path)
        if suffix == ".bmp":
            return _load_bmp_luma(path)
        if suffix == ".pbm":
            return _load_pbm_luma(path)
        raise RuntimeError("El plugin 'image' requiere Pillow para este formato. PNG, BMP y PBM funcionan sin dependencias.")

    with Image.open(path) as img:
        gray = img.convert("L")
        width, height = gray.size
        return [[int(gray.getpixel((x, y))) for x in range(width)] for y in range(height)]


def _load_png_luma(path: Path) -> list[list[int]]:
    raw = path.read_bytes()
    if not raw.startswith(b"\x89PNG\r\n\x1a\n"):
        raise ValueError("PNG invalido")

    pos = 8
    width = height = bit_depth = color_type = interlace = None
    payload = bytearray()
    while pos + 8 <= len(raw):
        length = struct.unpack(">I", raw[pos:pos + 4])[0]
        kind = raw[pos + 4:pos + 8]
        data = raw[pos + 8:pos + 8 + length]
        pos += 12 + length
        if kind == b"IHDR":
            width, height, bit_depth, color_type, compression, filter_method, interlace = struct.unpack(">IIBBBBB", data)
            if compression != 0 or filter_method != 0:
                raise ValueError("PNG con compresion o filtro no soportado")
        elif kind == b"IDAT":
            payload.extend(data)
        elif kind == b"IEND":
            break

    if width is None or height is None or bit_depth != 8 or interlace != 0:
        raise ValueError("PNG soportado: 8-bit sin interlace")

    channels_by_type = {0: 1, 2: 3, 4: 2, 6: 4}
    channels = channels_by_type.get(color_type)
    if channels is None:
        raise ValueError("PNG soportado: grayscale, RGB, grayscale-alpha o RGBA")

    inflated = zlib.decompress(bytes(payload))
    stride = width * channels
    rows: list[bytes] = []
    previous = bytes(stride)
    pos = 0
    for _ in range(height):
        filter_type = inflated[pos]
        scan = bytearray(inflated[pos + 1:pos + 1 + stride])
        pos += 1 + stride
        _unfilter_png_row(scan, previous, channels, filter_type)
        previous = bytes(scan)
        rows.append(previous)

    return [_png_row_to_luma(row, width, color_type, channels) for row in rows]


def _unfilter_png_row(row: bytearray, previous: bytes, bpp: int, filter_type: int) -> None:
    if filter_type == 0:
        return
    for i in range(len(row)):
        left = row[i - bpp] if i >= bpp else 0
        up = previous[i] if i < len(previous) else 0
        up_left = previous[i - bpp] if i >= bpp and i - bpp < len(previous) else 0
        if filter_type == 1:
            row[i] = (row[i] + left) & 0xFF
        elif filter_type == 2:
            row[i] = (row[i] + up) & 0xFF
        elif filter_type == 3:
            row[i] = (row[i] + ((left + up) // 2)) & 0xFF
        elif filter_type == 4:
            row[i] = (row[i] + _paeth(left, up, up_left)) & 0xFF
        else:
            raise ValueError(f"Filtro PNG no soportado: {filter_type}")


def _paeth(a: int, b: int, c: int) -> int:
    p = a + b - c
    pa = abs(p - a)
    pb = abs(p - b)
    pc = abs(p - c)
    if pa <= pb and pa <= pc:
        return a
    if pb <= pc:
        return b
    return c


def _png_row_to_luma(row: bytes, width: int, color_type: int, channels: int) -> list[int]:
    out: list[int] = []
    for x in range(width):
        i = x * channels
        if color_type == 0:
            out.append(row[i])
        elif color_type == 2:
            out.append(_rgb_luma(row[i], row[i + 1], row[i + 2]))
        elif color_type == 4:
            gray, alpha = row[i], row[i + 1]
            out.append((gray * alpha + 255 * (255 - alpha)) // 255)
        else:
            luma = _rgb_luma(row[i], row[i + 1], row[i + 2])
            alpha = row[i + 3]
            out.append((luma * alpha + 255 * (255 - alpha)) // 255)
    return out


def _load_bmp_luma(path: Path) -> list[list[int]]:
    raw = path.read_bytes()
    if raw[:2] != b"BM":
        raise ValueError("BMP invalido")
    offset = struct.unpack("<I", raw[10:14])[0]
    dib_size = struct.unpack("<I", raw[14:18])[0]
    if dib_size < 40:
        raise ValueError("BMP DIB no soportado")
    width, height, planes, bpp, compression = struct.unpack("<iiHHI", raw[18:34])
    if planes != 1 or compression != 0 or bpp not in {24, 32}:
        raise ValueError("BMP soportado: 24/32-bit sin compresion")
    abs_height = abs(height)
    row_stride = ((width * bpp + 31) // 32) * 4
    rows: list[list[int]] = []
    for y in range(abs_height):
        source_y = abs_height - 1 - y if height > 0 else y
        start = offset + source_y * row_stride
        row: list[int] = []
        for x in range(width):
            i = start + x * (bpp // 8)
            b, g, r = raw[i], raw[i + 1], raw[i + 2]
            row.append(_rgb_luma(r, g, b))
        rows.append(row)
    return rows


def _load_pbm_luma(path: Path) -> list[list[int]]:
    raw = path.read_bytes()
    tokens = list(_pbm_tokens(raw))
    if len(tokens) < 3 or tokens[0] not in {b"P1", b"P4"}:
        raise ValueError("PBM soportado: P1 o P4")
    width = int(tokens[1])
    height = int(tokens[2])
    rows: list[list[int]] = []
    if tokens[0] == b"P1":
        values = tokens[3:]
        if len(values) < width * height:
            raise ValueError("PBM P1 incompleto")
        for y in range(height):
            row: list[int] = []
            for x in range(width):
                bit = values[y * width + x]
                row.append(0 if bit == b"1" else 255)
            rows.append(row)
        return rows

    header_end = _pbm_binary_data_offset(raw)
    data = raw[header_end:]
    stride = (width + 7) // 8
    if len(data) < stride * height:
        raise ValueError("PBM P4 incompleto")
    for y in range(height):
        row = []
        chunk = data[y * stride:(y + 1) * stride]
        for x in range(width):
            byte = chunk[x // 8]
            bit = (byte >> (7 - (x % 8))) & 1
            row.append(0 if bit else 255)
        rows.append(row)
    return rows


def _pbm_tokens(raw: bytes):
    token = bytearray()
    comment = False
    for byte in raw:
        ch = chr(byte)
        if comment:
            if ch in "\r\n":
                comment = False
            continue
        if ch == "#":
            comment = True
            continue
        if ch.isspace():
            if token:
                yield bytes(token)
                token.clear()
            continue
        token.append(byte)
    if token:
        yield bytes(token)


def _pbm_binary_data_offset(raw: bytes) -> int:
    count = 0
    comment = False
    in_token = False
    for index, byte in enumerate(raw):
        ch = chr(byte)
        if comment:
            if ch in "\r\n":
                comment = False
            continue
        if ch == "#":
            comment = True
            continue
        if ch.isspace():
            if in_token:
                count += 1
                in_token = False
                if count == 3:
                    return index + 1
            continue
        in_token = True
    raise ValueError("PBM P4 sin datos")


def _rgb_luma(r: int, g: int, b: int) -> int:
    return (299 * r + 587 * g + 114 * b) // 1000
