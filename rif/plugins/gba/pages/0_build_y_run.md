# Build y Ejecucion

El plugin `gba` empaqueta codigo RIF, cabecera de cartucho y recursos en una ROM
`.gba` valida para emuladores y hardware compatible.

## Compilar

```bash
python -m rif build examples/gba --plugin gba --name example
```

El pack usado vive en:

```text
rif/plugins/gba/packs/example/gba.pack
```

Durante el build, RIF:

1. Carga las tablas `.regs`, `.rules`, `.sections`, `.types` y `.words`.
2. Lee archivos `.gbasm` del proyecto, incluyendo subarchivos si el proyecto usa
   `code/`.
3. Resuelve fillables como imagenes, fuentes, audio o cabeceras.
4. Enlaza secciones con sus offsets virtuales.
5. Escribe la ROM final con extension `.gba`.

## Ejecutar con mGBA

Registrar el emulador:

```bash
python -m rif -pcli gba install mGBA --add-path
```

Ejecutar:

```bash
python -m rif -pcli gba run examples/gba/gba.gba
```

Evitar ventanas duplicadas durante desarrollo:

```bash
python -m rif -pcli gba run examples/gba/gba.gba -nd
```

Ver el comando sin abrir el emulador:

```bash
python -m rif -pcli gba run examples/gba/gba.gba --dry-run
```

## Configuracion

La ruta del emulador se guarda en:

```text
~/.rif/plugins/gba/config.json
```

Si mGBA esta en una ruta concreta:

```bash
python -m rif -pcli gba install mGBA --add-path "C:/Program Files/mGBA/mGBA.exe"
```

## Errores comunes

| Mensaje | Causa | Solucion |
|---|---|---|
| `ROM no encontrada` | La ruta al `.gba` no existe. | Compila primero o corrige la ruta. |
| `mGBA no esta configurado` | No hay ruta guardada ni ejecutable en `PATH`. | Ejecuta `install mGBA --add-path`. |
| Pantalla blanca | Cabecera, logo, checksum o entry incompletos. | Revisa `.header`, `set_logo`, `set_checksum` y `set_entry_thumb`. |
| Imagen corrupta | Escrituras byte a byte en VRAM/OAM/Palette RAM. | Usa `strh` o `arm_strh`. |
