# Compilar

Compilar una instruccion:

```bash
python -m rif compile examples/minimal.pack byte 0xf
```

Compilar varias lineas con build:

```bash
python -m rif build examples/minimal.pack --source-text "byte 0x2a"
```

Compilar desde archivo fuente:

```bash
python -m rif build gba/gba.pack --source-file gba/hello.rif -o gba/hello.gba
```

Compilar una carpeta de proyecto:

```bash
python -m rif build gba
python -m rif -pcli gba run gba/hello.gba -nd
```

El resultado muestra bytes, hex y bloques.

Si hay placeholders, la salida los lista para que el linker o una fase posterior los resuelva.

---

## 🛠️ Compiladores Dedicados (Compilar Compiladores)

Una de las características más asombrosas de RIF es su capacidad de "compilar un compilador". Usando la bandera `-p` (o `--plugin`), puedes empaquetar tu ISA entera en un programa ejecutable independiente (`.exe`) que ya no dependerá de RIF ni de Python para funcionar.

```bash
python -m rif compile -p gba --link image sound --name example
```

### ¿Cómo funciona por dentro?

El archivo responsable de esta magia es `rif/dedicated.py`. Cuando ejecutas el comando de arriba, ocurre lo siguiente en segundo plano:

1. **Construcción del Sandbox**: RIF crea una carpeta aislada (`build/rif-gba-compiler/dedicated_pack/`) y copia ahí todos los archivos de tu pack y de los plugins vinculados (`--link`).
2. **Generación del Script Wrapper**: Genera dinámicamente un archivo Python (`rif-gba-compiler.py`) que embebe toda la API de RIF (Lexer, Parser y Linker) hardcodeando la ruta hacia tu pack empaquetado.
3. **Empaquetado Nativo**: Ejecuta **PyInstaller** de manera invisible, recolectando la máquina de estados de RIF y los recursos ocultos.
4. **Vaciado de Caché**: Deposita un solo archivo `.exe` pesado en la carpeta `dist/`.

> [!NOTE]
> Este ejecutable funciona exactamente igual que el comando `rif build`. Puedes distribuirlo libremente. Tus usuarios finales podrán usar tu lenguaje ensamblador desde la terminal ejecutando simplemente `rif-gba-compiler.exe proyecto.asm -o rom.gba`.
