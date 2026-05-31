# 🎮 Plugin GBA para RIF

Este es el módulo oficial de **Game Boy Advance (GBA)** para el framework Retargetable ISA Foundry (RIF). Proporciona el compilador del conjunto de instrucciones Thumb de 16-bits (ARM7TDMI), la resolución nativa de cabeceras de Nintendo, manejo del framebuffer de video y directivas avanzadas de generación ROM.

## 🚀 Características Principales

*   **Compilador Thumb Nativo**: Sintaxis limpia para la CPU ARM7TDMI (`mov`, `add`, `cmp`, `bne`, `ldr`, `str`).
*   **Inyección Automática de Hardware**: Macros listas para inyectar los checksums, el logo oficial y el vector de entrada al instante (`set_headers`, `set_logo`, `set_entry_thumb`).
*   **Ecosistema Gráfico Integrado**: Compatible por diseño con el plugin de imágenes, permitiendo downsampling BGR555 con la directiva `@fill_image_bitmap`.
*   **Motor de Sonido DMA**: Soporte implícito para reproducir audio desde buffers estáticos empujados con el plugin `sound`.

## 📂 Estructura Interna del Módulo

*   `packs/example/gba.pack`: El pack raíz arquitectónico que enlaza registros (`R0-R15`), aliases (`SP, LR, PC`), definiciones de secciones de hardware (ej. `.rom`, `.data`) e importa los sub-módulos y reglas correspondientes.
*   `packs/example/gba.rules.pack`: Contiene las macros declarativas de la ROM y el mapeo sintáctico para las instrucciones Thumb.
*   `plugins/thumb_ins.py`: El core algorítmico escrito en Python que actúa como emisor semántico para el lenguaje Thumb (soporta direccionamiento little-endian e interpreta los bindings de registro y RAM de RIF).
*   `plugins/gba_*.py`: Generadores específicos para inyectar binarios duros requeridos por el GBA (el logotipo de Nintendo y rutinas de validación).
*   `fillables.py`: Procesadores nativos como `@fill_screen` (limpieza de color sólido) y `@fill_screen_text` (renderizado de fuentes).

## 🎮 Guía Rápida de Compilación

Si deseas probar el ecosistema GBA completo, navega a la raíz del repositorio de RIF y compila el ejemplo oficial que fusiona este plugin con gráficos y audio:

```bash
# 1. Compilar el proyecto en formato GBA
python -m rif build examples/gba --plugin gba --name example

# 2. Emular automáticamente el cartucho en mGBA
python -m rif -pcli gba run examples/gba/gba.gba -nd
```

## 🏗️ Secuencia Básica de un Proyecto GBA

Tu código fuente GBA debe preparar el entorno ROM antes de inyectar los juegos. RIF facilita esto mediante una arquitectura declarativa:

```rif
.section .rom
set_headers        # Configura título e ID del juego
set_logo           # Inyecta los 156 bytes del logo de Nintendo
set_checksum       # Calcula validaciones checksum matemáticas del header
set_entry_thumb    # Inyecta un puente ARM->Thumb transparente para arrancar el main loop
set_frame          # Limpia o inicializa el modo de vídeo a GBA Mode 3
game_code          # Rutina personalizada o punto de entrada de tu juego
set_rompad         # Alinea o rellena tu binario según las reglas del hardware
```

> [!NOTE]
> La directiva `set_rompad` del plugin GBA rellena de forma inteligente la ROM para alinearla al final estricto requerido por los emuladores o el hardware flash real. No sobre-asigna bytes, solo llena los bloques sobrantes tomando como referencia el puntero actual en `.rom`.

---

### 📖 Explorar la Documentación Interna

Puedes leer todos los tutoriales, registros soportados, instrucciones integradas y el comportamiento de las macros VBlank ejecutando nuestro servidor de ayuda RIF interactivo:
```bash
python -m rif help --open
```
Busca la sección **GBA** en el panel izquierdo.
