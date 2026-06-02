# Construcción y Ejecución de Proyectos Mega Drive

El entorno RIF cuenta con un flujo completo y automatizado para ensamblar imágenes ROM (`.bin` o `.md`) válidas para la Sega Mega Drive / Genesis, utilizando el motor ensamblador y macros para el M68000.

## 🔨 Compilar un Proyecto

Dado que el plugin de Mega Drive inyecta su propio conjunto de instrucciones M68k y su mapeo de memoria específico, la compilación de proyectos requiere que invoques el empaquetador indicando el plugin correcto:

```bash
# Formato general de construcción:
python -m rif build <ruta_al_directorio_fuente> --plugin megadrive --name <nombre_del_pack>

# Ejemplo oficial:
python -m rif build examples/megadrive --plugin megadrive --name example
```

Al ejecutar este comando, RIF hará lo siguiente:
1. Extraerá las reglas y metadatos alojados en `rif/plugins/megadrive/packs/example/`.
2. Evaluará secuencialmente cada archivo con extensión `.mdasm` dentro del directorio especificado.
3. Resolverá la arquitectura **Big-Endian** intrínseca del M68k, ajustando todas las palabras y relocaciones para el hardware original de Sega.
4. Renderizará en consola un reporte visual indicando el tamaño, la ubicación lógica en memoria de tus bloques y los offsets de enlace generados.

El binario resultante se depositará en el directorio fuente bajo el nombre `<directorio>.bin` (en el caso del ejemplo: `examples/megadrive/megadrive.bin`).

---

## 🎮 Ejecución en Emuladores (CLI nativo)

El plugin de Mega Drive incorpora herramientas especializadas accesibles bajo el prefijo CLI de RIF `-pcli megadrive`.

Si no tienes un emulador, el propio RIF puede descargar la última versión portátil de un emulador popular como **BlastEm** o **Gens** e instalarla de forma local:

```bash
# Descarga e instala el emulador automáticamente:
python -m rif -pcli megadrive install blastem --add-path
```

Una vez tengas tu archivo `.bin` generado, puedes lanzar tu juego directamente desde la terminal:

```bash
python -m rif -pcli megadrive run examples/megadrive/megadrive.bin -nd
```

### 💡 Acerca del flag `-nd` (No Duplicates)

Al igual que en otros plugins de RIF, el flag `-nd` evita acumular docenas de ventanas del emulador. El motor rastreará el proceso del emulador, cerrándolo antes de lanzar la nueva ROM recién compilada, garantizando un flujo iterativo ininterrumpido.
