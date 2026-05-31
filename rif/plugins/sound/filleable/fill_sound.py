from rif.plugins.sound.GBA.converter import convert_to_gba_pcm
from rif.fillables import record_fill
from rif.errors import PackError
from pathlib import Path
import re


def _number(value, default, cast):
    try:
        return cast(value)
    except (TypeError, ValueError):
        return default


def _symbol(value: str) -> str:
    out = re.sub(r"[^0-9A-Za-z_]+", "_", str(value)).strip("_")
    if not out or out[0].isdigit():
        out = f"sound_{out}"
    return out

def fill_sound_wav(*args, context=None) -> str:
    """Invoked via @fill_sound_wav or @sound_wav in RIF source files.
    
    Converts a WAV sound file to s8 PCM and registers it as a RIF fillable.
    """
    if not args:
        return "; Error: @fill_sound_wav requiere al menos la ruta al archivo de sonido"
        
    sound_path = str(args[0])
    symbol = str(args[1]) if len(args) > 1 else "sound_data"
    sample_rate = _number(args[2], 8192, int) if len(args) > 2 else 8192
    duration = _number(args[3], 6.0, float) if len(args) > 3 else 6.0
    start = _number(args[4], 0.0, float) if len(args) > 4 else 0.0
    volume = _number(args[5], 0.85, float) if len(args) > 5 else 0.85
    fade_in = _number(args[6], 0.25, float) if len(args) > 6 else 0.25
            
    # Resolve relative paths relative to project_path or source_path
    proj_path = context.get("project_path") if context else None
    input_file = Path(sound_path)
    if proj_path and not input_file.is_absolute():
        input_file = Path(proj_path) / sound_path
        
    if not input_file.exists():
        # Let's try relative to source file parent directory
        src_path = context.get("source_path") if context else None
        if src_path:
            alt_path = Path(src_path).parent / sound_path
            if alt_path.exists():
                input_file = alt_path

    if not input_file.exists():
        raise PackError(f"archivo de sonido no encontrado: {sound_path}")
        
    try:
        # Perform conversion to GBA signed 8-bit PCM
        data = convert_to_gba_pcm(input_file, sample_rate=sample_rate, duration=duration, start=start, volume=volume, fade_in=fade_in)
        
        # Record this fill in fills.json
        record_fill(
            context,
            "sound",
            symbol,
            size=len(data),
            bits=len(data) * 8,
            align=4,
            padding=0,
            type="s8",
            format="pcm-s8",
            source=str(sound_path),
            sample_rate=sample_rate,
            duration=duration,
            start=start,
            volume=volume,
            fade_in=fade_in,
        )
        # Return assembly-compilable definition
        return f"{symbol} s8[{len(data)}] = 0x{data.hex()}"
    except Exception as exc:
        raise PackError(f"error al procesar audio {sound_path}: {exc}") from exc

def fill_sound_mp3(*args, context=None) -> str:
    """Invoked via @fill_sound_mp3 or @sound_mp3 in RIF source files.
    
    Converts an MP3 sound file to s8 PCM and registers it as a RIF fillable.
    """
    # Both WAV and MP3 are converted using ffmpeg, so we can reuse the same handler
    return fill_sound_wav(*args, context=context)


def fill_gba_dsound_start(symbol: str = "sound_data", sample_rate: str = "8192", *_args, context=None) -> str:
    """Emits generic GBA Direct Sound A startup code for a PCM symbol."""
    rate = _number(sample_rate, 8192, int)
    if rate <= 0:
        raise PackError("gba_dsound_start requiere sample_rate mayor que cero")
    reload_value = 65536 - int(16777216 / rate)
    if not 0 <= reload_value <= 0xFFFF:
        raise PackError(f"sample_rate invalido para timer GBA: {rate}")

    safe = _symbol(symbol)
    prefix = f"__gba_dsound_{safe}"
    record_fill(
        context,
        "sound",
        f"{safe}_player",
        type="gba-direct-sound-a",
        symbol=symbol,
        sample_rate=rate,
        timer_reload=reload_value,
        channel="A",
        dma_channel=1,
        fifo="FIFO_A",
        dma_count=4,
        fifo_prefill_bytes=16,
    )
    return f"""
    arm_mov_imm R0, 0x04000000
    arm_add_imm R0, R0, 0xC4
    arm_mov_imm R1, 0
    arm_strh R1, R0, 2

    arm_mov_imm R0, 0x04000000
    arm_add_imm R0, R0, 0x100
    arm_mov_imm R1, 0
    arm_strh R1, R0, 2

    arm_mov_imm R0, 0x04000000
    arm_add_imm R0, R0, 0x80
    arm_mov_imm R1, 0
    arm_strh R1, R0, 0
    arm_ldr_label R1, {prefix}_soundcnt_h
    arm_strh R1, R0, 2
    arm_mov_imm R1, 0x80
    arm_strh R1, R0, 4
    arm_mov_imm R1, 0x0200
    arm_strh R1, R0, 8

    arm_mov_imm R0, 0x04000000
    arm_add_imm R0, R0, 0xBC
    arm_ldr_label R2, {prefix}_sample_ptr
    arm_str R2, R0, 0
    arm_mov R3, R2
    arm_mov_imm R2, 0x04000000
    arm_add_imm R2, R2, 0xA0
    arm_str R2, R0, 4
    arm_ldr R4, R3, 0
    arm_str R4, R2, 0
    arm_ldr R4, R3, 4
    arm_str R4, R2, 0
    arm_ldr R4, R3, 8
    arm_str R4, R2, 0
    arm_ldr R4, R3, 12
    arm_str R4, R2, 0
    arm_mov_imm R2, 4
    arm_strh R2, R0, 8
    arm_ldr_label R2, {prefix}_dma_control
    arm_strh R2, R0, 10

    arm_mov_imm R0, 0x04000000
    arm_add_imm R0, R0, 0x100
    arm_ldr_label R1, {prefix}_timer_reload
    arm_strh R1, R0, 0
    arm_mov_imm R1, 0x80
    arm_strh R1, R0, 2
    arm_b {prefix}_after_literals
{prefix}_soundcnt_h:
    dw 0x00000B0F
{prefix}_dma_control:
    dw 0x0000B640
{prefix}_timer_reload:
    dw 0x{reload_value:04X}
{prefix}_sample_ptr:
    apply_reloc abs, {symbol}, 32
{prefix}_after_literals:
""".strip()
