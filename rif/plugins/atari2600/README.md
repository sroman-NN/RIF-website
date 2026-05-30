# Atari 2600

Plugin base para crear ROMs de Atari 2600 con reglas RIF. Incluye un pack minimo 6502/TIA, vectores de reset al final del banco de 4 KiB y CLI para ejecutar binarios con Stella.

Comandos utiles:

```bash
python -m rif build atari2600
python -m rif -pcli atari2600 install Stella --add-path
python -m rif -pcli atari2600 run atari2600/out.bin
```
