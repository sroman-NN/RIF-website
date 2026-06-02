from rif.plugins.image.bitmap.converter import image_to_bitmap_bytes
from rif.fillables import record_fill


def fill_image_bitmap(*args, context=None) -> str:
    if not args:
        return "; Error: @fill_image_bitmap requiere al menos la ruta a la imagen"

    image_path = str(args[0])
    label = context.get("fill_label") if isinstance(context, dict) else None
    symbol = str(label or (args[1] if len(args) > 1 else "image_data"))
    threshold = 128
    invert = False
    option_offset = 1 if label else 2

    if len(args) > option_offset:
        try:
            threshold = int(args[option_offset])
        except ValueError:
            pass

    if len(args) > option_offset + 1:
        invert = str(args[option_offset + 1]).strip().lower() in {"1", "true", "yes", "si", "sí", "on", "invert"}

    try:
        data = image_to_bitmap_bytes(image_path, threshold=threshold, invert=invert, context=context)
        record_fill(
            context,
            "image",
            symbol,
            size=len(data),
            bits=len(data) * 8,
            align=1,
            padding=0,
            type="u8",
            format="bitmap-1bpp",
            source=image_path,
            threshold=threshold,
            invert=invert,
        )
        return f"{symbol} u8[{len(data)}] = 0x{data.hex()}"
    except Exception as exc:
        return f"; Error al procesar imagen: {exc}"
