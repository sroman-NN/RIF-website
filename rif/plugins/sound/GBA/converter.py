import subprocess
from pathlib import Path

def convert_to_gba_pcm(
    input_path: Path,
    sample_rate: int = 8192,
    *,
    duration: float | None = None,
    start: float = 0.0,
    volume: float = 0.85,
    fade_in: float = 0.25,
) -> bytes:
    """Converts any audio file (WAV, MP3, etc.) to GBA signed 8-bit mono PCM using FFmpeg.
    
    Streams the output from stdout directly into memory.
    """
    cmd = [
        "ffmpeg",
        "-y",
    ]
    if start > 0:
        cmd.extend(["-ss", str(start)])
    cmd.extend([
        "-i", str(input_path),
    ])
    if duration is not None and duration > 0:
        cmd.extend(["-t", str(duration)])
    filters: list[str] = []
    if volume > 0:
        filters.append(f"volume={volume}")
    if fade_in > 0:
        filters.append(f"afade=t=in:st=0:d={fade_in}")
    if filters:
        cmd.extend(["-filter:a", ",".join(filters)])
    cmd.extend([
        "-f", "s8",
        "-acodec", "pcm_s8",
        "-ac", "1",
        "-ar", str(sample_rate),
        "-"
    ])
    try:
        # Run ffmpeg as a subprocess, catching stdout and stderr
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return result.stdout
    except FileNotFoundError:
        raise Exception(
            "ffmpeg no se encuentra en el sistema. Por favor, asegúrate de tener instalado "
            "ffmpeg y que esté disponible en tu variable de entorno PATH."
        )
    except subprocess.CalledProcessError as exc:
        error_msg = exc.stderr.decode("utf-8", errors="ignore")
        raise Exception(f"FFmpeg falló al procesar el audio: {error_msg}")
