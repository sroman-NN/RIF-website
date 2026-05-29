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
