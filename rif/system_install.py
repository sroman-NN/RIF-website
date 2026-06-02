import os
import shutil
import sys
import json
import subprocess
import urllib.request
import zipfile
import tempfile
import webbrowser
from datetime import datetime
from pathlib import Path
from .errors import RIFError

GLOBAL_DIR = Path("C:/RIF")
VERSIONS_DIR = GLOBAL_DIR / "versions"
CONFIG_FILE = VERSIONS_DIR / "config.json"

def _get_config():
    if CONFIG_FILE.exists():
        try:
            return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}

def _save_config(config):
    VERSIONS_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(config, indent=2), encoding="utf-8")

def _enforce_max_versions():
    config = _get_config()
    max_versions = config.get("max_versions")
    if not max_versions or max_versions <= 0:
        return
        
    backups = sorted([d for d in VERSIONS_DIR.iterdir() if d.is_dir() and d.name.startswith("backup_")])
    if len(backups) > max_versions:
        # Borrar los mas antiguos
        for b in backups[:-max_versions]:
            try:
                shutil.rmtree(b)
                print(f"Limpiado backup antiguo: {b.name}")
            except Exception as e:
                print(f"No se pudo borrar {b.name}: {e}")

def add_to_path() -> None:
    ps_command = r"""
    $path = [Environment]::GetEnvironmentVariable('Path', 'User')
    if ($path -notmatch ';C:\\\\RIF(;|$)') {
        $newPath = $path + ';C:\RIF'
        $newPath = $newPath -replace '^;', ''
        [Environment]::SetEnvironmentVariable('Path', $newPath, 'User')
        Write-Output "C:\RIF anadido al PATH del usuario."
    }
    """
    subprocess.run(["powershell", "-Command", ps_command], check=False)

def remove_from_path() -> None:
    ps_command = r"""
    $path = [Environment]::GetEnvironmentVariable('Path', 'User')
    if ($path -match ';C:\\\\RIF(;|$)') {
        $newPath = $path -replace ';C:\\\\RIF(;$|$)', '$1'
        $newPath = $newPath -replace '^C:\\\\RIF;', ''
        $newPath = $newPath -replace '^C:\\\\RIF$', ''
        [Environment]::SetEnvironmentVariable('Path', $newPath, 'User')
        Write-Output "C:\RIF removido del PATH."
    }
    """
    subprocess.run(["powershell", "-Command", ps_command], check=False)

def self_freeze() -> int:
    if GLOBAL_DIR.exists():
        print(f"La carpeta {GLOBAL_DIR} ya existe. Usa 'rif self update' para actualizar desde GitHub.")
        return 1

    import rif
    source_dir = Path(rif.__file__).parent
    
    GLOBAL_DIR.mkdir(parents=True, exist_ok=True)
    
    target_rif_dir = GLOBAL_DIR / "rif"
    shutil.copytree(source_dir, target_rif_dir, ignore=shutil.ignore_patterns("__pycache__", ".cache"))
    
    bat_path = GLOBAL_DIR / "rif.bat"
    bat_content = f"@echo off\r\nset PYTHONPATH={GLOBAL_DIR}\r\npython -m rif %*\r\n"
    bat_path.write_text(bat_content, encoding="utf-8")
    
    add_to_path()
    print(f"RIF congelado globalmente en {GLOBAL_DIR}.")
    print("Abre una nueva terminal para usar el comando 'rif' globalmente.")
    return 0

def self_uninstall() -> int:
    if not GLOBAL_DIR.exists():
        print("RIF no esta instalado globalmente en C:\\RIF.")
        return 1

    remove_from_path()
    
    print(f"Borrando {GLOBAL_DIR}...")
    try:
        shutil.rmtree(GLOBAL_DIR)
        print("RIF desinstalado exitosamente.")
    except Exception as e:
        print(f"No se pudo borrar completamente la carpeta {GLOBAL_DIR}: {e}")
        return 1
    return 0

def _backup_current() -> Path | None:
    if not GLOBAL_DIR.exists():
        return None
    VERSIONS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_path = VERSIONS_DIR / f"backup_{timestamp}"
    backup_path.mkdir()
    
    target_rif = GLOBAL_DIR / "rif"
    if target_rif.exists():
        shutil.copytree(target_rif, backup_path / "rif", ignore=shutil.ignore_patterns("__pycache__", ".cache"))
        
    _enforce_max_versions()
    return backup_path

def self_update() -> int:
    if not GLOBAL_DIR.exists():
        print("RIF no esta congelado en C:\\RIF. Ejecuta 'rif self freeze' primero.")
        return 1

    print("Creando copia de seguridad...")
    backup_path = _backup_current()
    if backup_path:
        print(f"Copia de seguridad guardada en: {backup_path.name}")

    url = "https://github.com/GrandKenzy/RETARGETABLE-ISA-FOUNDRY-RIF-/archive/refs/heads/prev.zip"
    print(f"Descargando actualizacion desde {url}...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir_path = Path(temp_dir)
        zip_path = temp_dir_path / "prev.zip"
        
        try:
            urllib.request.urlretrieve(url, zip_path)
        except Exception as e:
            raise RIFError(f"Error al descargar la actualizacion: {e}")
            
        print("Extrayendo archivos...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir_path)
            
        repo_dir = temp_dir_path / "RETARGETABLE-ISA-FOUNDRY-RIF--prev"
        new_rif_dir = repo_dir / "rif"
        
        if not new_rif_dir.exists():
            raise RIFError("El formato del repositorio descargado es incorrecto.")
            
        print("Aplicando actualizacion...")
        target_rif = GLOBAL_DIR / "rif"
        target_plugins = target_rif / "plugins"

        new_plugins = []
        new_plugins_dir = new_rif_dir / "plugins"
        if new_plugins_dir.exists():
            new_plugins = [d.name for d in new_plugins_dir.iterdir() if d.is_dir()]
            
        if target_rif.exists():
            for item in target_rif.iterdir():
                if item.name == "plugins":
                    for plugin_item in item.iterdir():
                        if plugin_item.name in new_plugins:
                            if plugin_item.is_dir():
                                shutil.rmtree(plugin_item)
                            else:
                                plugin_item.unlink()
                else:
                    if item.is_dir():
                        shutil.rmtree(item)
                    else:
                        item.unlink()
                        
        for item in new_rif_dir.iterdir():
            if item.name == "plugins":
                target_plugins.mkdir(exist_ok=True)
                for plugin_item in item.iterdir():
                    dest_plugin = target_plugins / plugin_item.name
                    if plugin_item.is_dir():
                        shutil.copytree(plugin_item, dest_plugin)
                    else:
                        shutil.copy2(plugin_item, dest_plugin)
            else:
                dest = target_rif / item.name
                if item.is_dir():
                    shutil.copytree(item, dest)
                else:
                    shutil.copy2(item, dest)
                    
    print("Actualizacion completada exitosamente.")
    return 0

def self_rollback(target: str | None, max_versions: int | None) -> int:
    if max_versions is not None:
        config = _get_config()
        config["max_versions"] = max_versions
        _save_config(config)
        print(f"Maximas versiones guardadas configurado a {max_versions}.")
        _enforce_max_versions()
        if not target:
            return 0
            
    if target == "clear":
        if not VERSIONS_DIR.exists():
            print("No hay versiones para limpiar.")
            return 0
        for item in VERSIONS_DIR.iterdir():
            if item.is_dir() and item.name.startswith("backup_"):
                shutil.rmtree(item)
        print("Historial de versiones limpio.")
        return 0

    if not VERSIONS_DIR.exists():
        print("No hay versiones guardadas para restaurar.")
        return 1
        
    backups = sorted([d for d in VERSIONS_DIR.iterdir() if d.is_dir() and d.name.startswith("backup_")])
    
    if not backups:
        print("No hay versiones guardadas para restaurar.")
        return 1
        
    selected_backup = None
    
    if not target:
        selected_backup = backups[-1]
    else:
        try:
            idx = int(target)
            if idx >= 0 or abs(idx) > len(backups):
                print(f"Indice {idx} invalido. Tienes {len(backups)} backups disponibles.")
                return 1
            selected_backup = backups[idx]
        except ValueError:
            matches = [b for b in backups if target in b.name]
            if not matches:
                print(f"No se encontro ninguna version que coincida con '{target}'.")
                return 1
            selected_backup = matches[-1]
            
    print(f"Creando copia de seguridad de la version actual...")
    _backup_current()

    print(f"Restaurando version: {selected_backup.name}...")
    target_rif = GLOBAL_DIR / "rif"
    if target_rif.exists():
        shutil.rmtree(target_rif)
        
    shutil.copytree(selected_backup / "rif", target_rif)
    print("Version restaurada exitosamente.")
    return 0

def self_doc() -> int:
    import rif
    import re
    
    readme_path = Path(rif.__file__).parent.parent / "README.md"
    if not readme_path.exists():
        print("No se encontro README.md en el proyecto.")
        return 1
        
    content = readme_path.read_text(encoding="utf-8")
    
    content = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', content, flags=re.MULTILINE)
    content = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', content, flags=re.MULTILINE)
    content = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', content, flags=re.MULTILINE)
    content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', content)
    content = re.sub(r'```[a-z]*\n(.*?)```', r'<pre><code>\1</code></pre>', content, flags=re.DOTALL)
    content = re.sub(r'`(.*?)`', r'<code>\1</code>', content)
    content = content.replace('\n', '<br>')
    content = content.replace('<br><br>', '</p><p>').replace('<h1>', '</p><h1>').replace('</h1>', '</h1><p>')
    
    html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>RIF Documentation</title>
        <style>
            :root {{
                --bg: #0f172a;
                --text: #e2e8f0;
                --primary: #38bdf8;
                --surface: rgba(30, 41, 59, 0.7);
                --code-bg: #1e293b;
            }}
            body {{
                font-family: 'Inter', system-ui, -apple-system, sans-serif;
                background-color: var(--bg);
                color: var(--text);
                margin: 0;
                padding: 40px 20px;
                line-height: 1.6;
            }}
            .container {{
                max-width: 900px;
                margin: 0 auto;
                background: var(--surface);
                backdrop-filter: blur(12px);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 16px;
                padding: 40px;
                box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
            }}
            h1, h2, h3 {{
                color: var(--primary);
                font-weight: 600;
                letter-spacing: -0.025em;
            }}
            h1 {{ font-size: 2.5rem; margin-top: 0; border-bottom: 2px solid rgba(56, 189, 248, 0.2); padding-bottom: 10px; }}
            h2 {{ font-size: 1.75rem; margin-top: 2em; }}
            code {{
                background: var(--code-bg);
                padding: 0.2em 0.4em;
                border-radius: 4px;
                font-family: ui-monospace, 'Cascadia Code', monospace;
                color: #7dd3fc;
                font-size: 0.9em;
            }}
            pre code {{
                display: block;
                padding: 1rem;
                overflow-x: auto;
                background: var(--code-bg);
                border-radius: 8px;
                color: #e2e8f0;
                border: 1px solid rgba(255,255,255,0.05);
            }}
            strong {{ color: #fff; }}
            a {{ color: var(--primary); text-decoration: none; }}
            a:hover {{ text-decoration: underline; }}
        </style>
    </head>
    <body>
        <div class="container">
            <p>{content}</p>
        </div>
    </body>
    </html>
    """
    
    out_path = Path(tempfile.gettempdir()) / "rif_doc.html"
    out_path.write_text(html, encoding="utf-8")
    
    path_str = str(out_path.resolve())
    webbrowser.open(f"file:///{path_str.replace(chr(92), '/')}")
    print(f"Abriendo documentacion en {out_path}")
    return 0
