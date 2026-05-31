import argparse
from pathlib import Path
from rif.plugins.sound.GBA.converter import convert_to_gba_pcm

def register_convert_command(subparsers):
    """Registers the 'convert' command under RIF plugin CLI."""
    parser = subparsers.add_parser("convert", help="Convert WAV or MP3 to GBA signed 8-bit PCM")
    parser.add_argument("input", type=str, help="Input audio file (WAV, MP3, etc.)")
    parser.add_argument("output", type=str, help="Output file path (raw PCM bytes)")
    parser.add_argument("--rate", type=int, default=8192, help="Target sample rate in Hz (default: 8192)")
    parser.add_argument("--duration", type=float, help="Maximum duration to convert, in seconds")
    parser.add_argument("--start", type=float, default=0.0, help="Start offset in seconds")
    parser.add_argument("--volume", type=float, default=0.85, help="Linear volume multiplier")
    parser.add_argument("--fade-in", type=float, default=0.25, help="Fade-in duration in seconds")

def handle_convert_command(args) -> int:
    """Handles the execution of the conversion command."""
    input_path = Path(args.input)
    output_path = Path(args.output)
    
    if not input_path.exists():
        print(f"Error: input file does not exist: {input_path}")
        return 1
        
    print(f"Converting {input_path} to {output_path} at {args.rate}Hz...")
    try:
        data = convert_to_gba_pcm(
            input_path,
            sample_rate=args.rate,
            duration=args.duration,
            start=args.start,
            volume=args.volume,
            fade_in=args.fade_in,
        )
        # Write converted raw signed 8-bit PCM bytes to disk
        output_path.write_bytes(data)
        print(f"Success! Converted {len(data)} bytes.")
        return 0
    except Exception as exc:
        print(f"Error during sound conversion: {exc}")
        return 1
