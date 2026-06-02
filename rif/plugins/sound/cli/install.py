import argparse
import sys
import os
import zipfile
import urllib.request
import urllib.error
import shutil
from pathlib import Path

FFMPEG_WIN_URL = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"

def get_rif_tools_dir() -> Path:
    """Devuelve el directorio base de herramientas RIF."""
    return Path.home() / ".rif" / "tools"

def register_install_command(subparsers):
    """Registers the 'install' command under RIF plugin CLI."""
    parser = subparsers.add_parser("install", help="Instala herramientas de audio locales (ej. ffmpeg)")
    parser.add_argument("tool", type=str, choices=["ffmpeg"], help="Nombre de la herramienta a instalar")

def handle_install_command(args) -> int:
    """Handles the execution of the install command."""
    if args.tool != "ffmpeg":
        print(f"Error: herramienta '{args.tool}' no soportada por el instalador nativo.")
        return 1

    if sys.platform != "win32":
        print("El autoinstalador nativo de ffmpeg de RIF actualmente solo soporta Windows.")
        print("Para Linux o macOS, instala ffmpeg usando tu gestor de paquetes (ej. 'sudo apt install ffmpeg' o 'brew install ffmpeg').")
        return 1

    tools_dir = get_rif_tools_dir()
    ffmpeg_dir = tools_dir / "ffmpeg"
    ffmpeg_bin = ffmpeg_dir / "bin" / "ffmpeg.exe"
    
    if ffmpeg_bin.exists():
        print(f"ffmpeg ya esta instalado localmente en: {ffmpeg_bin}")
        return 0

    print("Descargando FFmpeg (Windows 64-bit GPL Build)...")
    print(f"URL: {FFMPEG_WIN_URL}")
    
    zip_path = tools_dir / "ffmpeg_temp.zip"
    tools_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        def reporthook(blocknum, blocksize, totalsize):
            readso_far = blocknum * blocksize
            if totalsize > 0:
                percent = readso_far * 1e2 / totalsize
                sys.stdout.write(f"\rProgreso: {percent:5.1f}% ({readso_far // 1024} KB / {totalsize // 1024} KB)")
                sys.stdout.flush()

        urllib.request.urlretrieve(FFMPEG_WIN_URL, zip_path, reporthook)
        print("\nDescarga completada. Extrayendo...")

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Buscamos el ejecutable dentro del zip dinámicamente
            ffmpeg_exe_in_zip = None
            for name in zip_ref.namelist():
                if name.endswith("bin/ffmpeg.exe"):
                    ffmpeg_exe_in_zip = name
                    break
            
            if not ffmpeg_exe_in_zip:
                print("\nError: no se pudo encontrar 'bin/ffmpeg.exe' dentro del archivo ZIP descargado.")
                return 1

            # Extraer solo el ejecutable para ahorrar espacio
            source = zip_ref.open(ffmpeg_exe_in_zip)
            ffmpeg_bin.parent.mkdir(parents=True, exist_ok=True)
            with open(ffmpeg_bin, "wb") as target:
                shutil.copyfileobj(source, target)
                
        print(f"¡Instalacion completada! ffmpeg extraido en: {ffmpeg_bin}")
        
    except urllib.error.URLError as e:
        print(f"\nError de red al descargar FFmpeg: {e}")
        return 1
    except Exception as e:
        print(f"\nError inesperado durante la instalacion: {e}")
        return 1
    finally:
        if zip_path.exists():
            try:
                zip_path.unlink()
            except OSError:
                pass
            
    return 0
