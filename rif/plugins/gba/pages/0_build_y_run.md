# Construcción y Ejecución de Proyectos GBA

El entorno RIF cuenta con un flujo completo y automatizado para orquestar la fusión de tu código ensamblador con recursos como audio e imágenes, construyendo directamente imágenes de ROM (`.gba`) válidas.

## 🔨 Compilar un Proyecto

Dado que el plugin GBA asume el control del entorno para inyectar su set de instrucciones Thumb y su mapeo de cabeceras, la compilación de proyectos requiere que invoques el empaquetador indicando el plugin GBA:

```bash
# Formato general de construcción:
python -m rif build <ruta_al_directorio_fuente> --plugin gba --name <nombre_del_pack>

# Ejemplo oficial:
python -m rif build examples/gba --plugin gba --name example
```

Al ejecutar este comando, RIF hará lo siguiente:
1. Extraerá las reglas y metadatos alojados en `rif/plugins/gba/packs/example/`.
2. Evaluará secuencialmente cada archivo con extensión `.gbasm` dentro del directorio especificado.
3. Inyectará llamadas dinámicas (como conversión de audio e imágenes) si usas macros como `@fill_sound_wav`.
4. Renderizará en consola un elegante reporte visual indicando el tamaño (Bytes), la ubicación lógica en memoria de tus bloques, el Hash `SHA256` y los offsets de enlace (Linker Labels) generados.

El binario resultante se depositará en el directorio fuente bajo el nombre `<directorio>.gba` (en el caso del ejemplo: `examples/gba/gba.gba`).

---

## 🎮 Ejecución en Emuladores (CLI nativo)

El plugin GBA incorpora herramientas especializadas accesibles bajo el prefijo CLI de RIF `-pcli gba`.

Si no tienes un emulador, el propio RIF puede descargar la última versión portátil del popular emulador **mGBA** e instalarla de forma local:

```bash
# Descarga e instala mGBA automáticamente:
python -m rif -pcli gba install mGBA --add-path
```

Una vez tengas tu archivo `.gba` generado y tu emulador listo, puedes lanzar tu juego directamente desde la terminal de forma fluida:

```bash
python -m rif -pcli gba run examples/gba/gba.gba -nd
```

### 💡 Acerca del flag `-nd` (No Duplicates)

El flag `-nd` es de vital importancia durante el desarrollo. Cuando compilas iterativamente, no querrás acumular cientos de ventanas del emulador abiertas. El motor de RIF rastreará activamente los hilos de `mGBA` a nivel de sistema operativo y reutilizará de forma forzada la ventana abierta anteriormente cerrando el proceso heredado antes de lanzar el nuevo.
