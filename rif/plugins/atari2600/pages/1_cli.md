# CLI Atari 2600

El plugin incluye una CLI pequena para trabajar con Stella sin hardcodear rutas
en cada proyecto.

## Registrar Stella

```bash
python -m rif -pcli atari2600 install Stella --add-path
```

El comando busca `Stella`, `stella`, `Stella.exe` o `stella.exe` en el `PATH`.
En Windows tambien revisa `C:/Program Files/Stella`. Si no lo encuentra e
identifica `winget`, intenta instalar Stella desde el catalogo disponible. En
macOS usa `brew --cask stella` si Homebrew existe.

La configuracion se guarda en:

```text
~/.rif/plugins/atari2600/config.json
```

Si ya tienes una ruta concreta:

```bash
python -m rif -pcli atari2600 install Stella --add-path "C:/Program Files/Stella/Stella.exe"
```

## Ejecutar una ROM

```bash
python -m rif -pcli atari2600 run examples/atari2600/atari2600.bin
```

El comando abre el binario con el ejecutable registrado. Para ver el comando sin
abrir el emulador:

```bash
python -m rif -pcli atari2600 run examples/atari2600/atari2600.bin --dry-run
```

## Errores comunes

| Mensaje | Causa | Solucion |
|---|---|---|
| `ROM no encontrada` | La ruta al `.bin` no existe. | Compila primero o corrige la ruta. |
| `Stella no esta configurado` | No hay ruta guardada y no se encontro en `PATH`. | Ejecuta `install Stella --add-path`. |
| Stella abre pantalla negra | La ROM no esta cerrada con vectores o el kernel no genera frame estable. | Revisa `rompad_to_vectors`, `vectors start`, `VSYNC`, `VBLANK` y `WSYNC`. |
