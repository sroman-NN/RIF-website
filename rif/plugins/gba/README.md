# 🎮 Plugin GBA para RIF - Documentación Completa

Este es el módulo oficial de **Game Boy Advance (GBA)** para el framework **Retargetable ISA Foundry (RIF)**. Proporciona un compilador completo del conjunto de instrucciones Thumb de 16-bits para la CPU ARM7TDMI, junto con herramientas de inyección automática de hardware, generación de assets y emulación integrada.

---

## ✨ Características Principales

### Core del Compilador
- **Compilador Thumb Nativo** - Sintaxis limpia para instrucciones ARM7TDMI de 16 bits (mov, add, cmp, bne, ldr, str)
- **Formato Little-Endian** - Emisión correcta para el bus de 16-bits del GBA
- **Validación Automática** - Verificación de rangos y restricciones Thumb

### Inyección de Hardware
- **Cabecera ROM Automática** - Genera los primeros 192 bytes requeridos por la BIOS
- **Logo de Nintendo** - Inyección automática del logo oficial (156 bytes comprimidos)
- **Checksum Cruzado** - Cálculo matemático de validación automático
- **Vector de Entrada** - Salto ARM→Thumb transparente (bx r15)

### Integración de Assets
- **Plugin Image** - Compatibilidad con `@fill_image_bitmap` (PNG/JPG/BMP → BGR555)
- **Plugin Sound** - Soporte DMA para audio `@fill_sound_wav` (WAV/MP3 → PCM 8-bits)
- **Plugin Fonts** - Renderizado de texto bitmap para pantalla inicial

### Herramientas CLI
- **Compilación Integrada** - `python -m rif build ... --plugin gba`
- **Emulador Automático** - `python -m rif -pcli gba run archivo.gba`
- **Instalación de mGBA** - Descarga e instala el emulador automáticamente

---

## 🚀 Inicio Rápido

### 1. Compilar un Proyecto GBA

```bash
# Compilar el ejemplo oficial
python -m rif build examples/gba --plugin gba --name example

# Generar salida en examples/gba/gba.gba
```

### 2. Ejecutar en Emulador

```bash
# Instalar mGBA automáticamente (solo una vez)
python -m rif -pcli gba install mGBA --add-path

# Ejecutar el ROM en mGBA (sin duplicar ventanas)
python -m rif -pcli gba run examples/gba/gba.gba -nd
```

### 3. Documentación Interactiva

```bash
# Abre el navegador de ayuda local
python -m rif help --open

# Navega a GBA en el panel izquierdo
```

---

## 📁 Estructura del Proyecto

### Directorios Clave

```
rif/plugins/gba/
├── README.md                 # Este archivo
├── cli.py                    # Interfaz de subcomandos (rif -pcli gba)
├── cli/
│   ├── install.py           # Instalador de emulador mGBA
│   └── run.py               # Ejecutor de ROMs en emulador
├── fillables.py             # @fill_screen, @fill_screen_text
├── packs/example/
│   ├── gba.pack             # Punto de entrada principal
│   ├── gba.regs.pack        # Definición de registros R0-R15
│   ├── gba.sections.pack    # Mapeo de memoria (ROM, EWRAM, VRAM, etc.)
│   └── gba.rules.pack       # Reglas Thumb y emisión
├── plugins/
│   ├── thumb_ins.py         # Intérprete aritmético Thumb
│   ├── gba_headers.py       # Constructor de cabecera (0x00-0xBF)
│   ├── gba_logo.py          # Inyección del logo Nintendo
│   ├── gba_checksum.py      # Cálculo de validación
│   └── gba_entry.py         # Inyector del salto ARM→Thumb
└── vscode/
    ├── build.json           # Metadatos de extensión VS Code
    ├── syntaxs.json         # Vocabulario Thumb
    ├── doc.json             # Documentación en hovers
    └── assets/
        └── gba-memory.svg   # Icono para extensión
```

---

## 🧠 Arquitectura GBA

### CPU ARM7TDMI - Dos Modos de Operación

| Modo | Tamaño | Uso Principal | Limitaciones |
|------|--------|----------------|--------------|
| **ARM (32 bits)** | 4 bytes | Booteo, IWRAM, alto rendimiento | Menos denso, cartucho limitado |
| **Thumb (16 bits)** | 2 bytes | Código principal desde ROM | R0-R7 en la mayoría de instrucciones |

**RIF emite código Thumb nativo** para optimizar uso de cartucho.

### Mapa de Memoria Físico

| Sección | Dirección | Tamaño | Propósito |
|---------|-----------|--------|----------|
| **ROM** | 0x08000000 | 32 MB | Cartucho (código e instrucciones) |
| **EWRAM** | 0x02000000 | 256 KB | RAM externa (carga general) |
| **IWRAM** | 0x03000000 | 32 KB | RAM interna (bucles críticos) |
| **I/O** | 0x04000000 | 1 KB | Registros MMIO (video, sonido, DMA) |
| **Paleta** | 0x05000000 | 1 KB | CRAM (paletas BGR555) |
| **VRAM** | 0x06000000 | 96 KB | Video RAM (píxeles, tiles, mapas) |
| **OAM** | 0x07000000 | 1 KB | Memoria de sprites |

---

## 📖 Páginas de Documentación

### [0. Construcción y Ejecución](0_build_y_run.md)
- Flujo completo de compilación
- Herramientas CLI del plugin
- Integración con emulador mGBA
- Flags de ejecución

### [1. Visión General de Arquitectura](1_overview.md)
- Procesador ARM7TDMI y modos
- Mapa de memoria detallado
- Estructura interna del plugin
- Sinergia con otros plugins

### [2. Conjunto de Instrucciones Thumb](2_instrucciones.md)
- 30+ instrucciones Thumb documentadas
- Transferencia de datos
- Aritmética y lógica
- Acceso a memoria (Load/Store)
- Control de flujo (Saltos)
- Stack (Push/Pop)
- Declaración de datos

### [3. Registros de CPU y MMIO](3_registros.md)
- Registros R0-R15 con restricciones
- Convención APCS de llamadas
- Registros MMIO importantes (DISPCNT, KEYINPUT, etc.)
- Memory-Mapped I/O completo

### [4. Directivas Fillables](4_fillables.md)
- `@fill_screen` - Rellenar pantalla con color
- `@fill_screen_text` - Renderizar texto bitmap
- `@fill_image_bitmap` - Convertir imágenes (PNG/JPG)
- `@fill_sound_wav` - Procesar audio (WAV/MP3)

### [5. Macros Estructurales de ROM](5_macros_rom.md)
- `set_headers` - Cabecera y vector de salto
- `set_logo` - Logo de Nintendo
- `set_checksum` - Validación de ROM
- `set_entry_thumb` - Punto de entrada
- `set_rompad` - Alineación final

---

## 🛠️ Secuencia Básica de un Proyecto GBA

Toda ROM de GBA debe seguir esta estructura base:

```rif
.section .rom
set_headers        # Cabecera: vector de salto ARM
set_logo           # 156 bytes del logo Nintendo
set_checksum       # Título, makers, checksum
set_entry_thumb    # Salto a Thumb mode
set_frame          # Inicializar video (Mode 3)
game_code          # Tu código personalizado
set_rompad         # Padding final
```

---

## 📝 Ejemplos de Código

### Ejemplo 1: Hello World Mínimo

```rif
.pack
plugin "basics"
plugin "gba"

.world

.rules
init:
    store r0 = 0x03
    reloc abs, DISPCNT, 32
    str r0, r1, r0
    jump init
```

### Ejemplo 2: Cargar Color a VRAM

```rif
.pack
plugin "basics"
plugin "gba"

.world

.rules
main:
    ; Cargar dirección de VRAM
    store r0 = 0x06000000
    store r1 = 0xFFFF      ; Color blanco BGR555
    
    ; Escribir en VRAM
    str r1, r0, r0
    
    ; Saltar a sí mismo (bucle infinito)
    jump main
```

### Ejemplo 3: Con Assets (Imagen)

```bash
python -m rif build proyecto_gba \
  --plugin gba \
  --plugin image \
  --name ejemplo_imagen
```

Luego en el código:

```rif
.section .rom
set_headers
set_logo
set_checksum
set_entry_thumb

; Cargar imagen de disco
@fill_image_bitmap sprites.png mi_sprite

game_loop:
    ; Código que usa mi_sprite
    jump game_loop
```

### Ejemplo 4: Con Audio

```bash
python -m rif build proyecto_gba \
  --plugin gba \
  --plugin sound \
  --name ejemplo_audio
```

Código:

```rif
@fill_sound_wav bgm musica.mp3 16000

; Luego en configuración DMA:
; bgm_dma_control (generado automáticamente)
```

---

## 🎨 Generación de Extensión VS Code

### Crear VSIX con Soporte Thumb

```bash
python -m rif compile --vscode \
  --ext .gbasm \
  --icon rif/plugins/gba/vscode/assets/gba-memory.svg \
  --p gba basics
```

### Instalar en VS Code

```bash
python -m rif install --vscode build/vscode/rif-gba-basics-0.2.0.vsix
```

### Características de la Extensión

- ✅ Resaltado de instrucciones Thumb
- ✅ Autocompletado de mnemónicos
- ✅ Hovers con documentación
- ✅ Diagnósticos por regex
- ✅ Quick fixes para errores comunes

---

## 🐛 Debugging y Tips

### Verificar Compilación

```bash
# Modo verbose
python -m rif build proyecto --plugin gba --name test --verbose

# Ver tabla de símbolos
python -m rif parse rif/plugins/gba/packs/example/gba.pack
```

### Inspeccionar ROM

```bash
# Ver primeros 192 bytes (cabecera)
xxd -l 192 output.gba

# Verificar tamaño final
ls -lh output.gba
```

### Emulador Avanzado

```bash
# Ejecutar sin duplicar ventanas (recomendado para dev)
python -m rif -pcli gba run output.gba -nd

# Especificar emulador diferente
python -m rif -pcli gba run output.gba --emulator visualboyadvance
```

---

## ⚠️ Restricciones Thumb Importantes

### Registros Limitados (R0-R7 en operaciones aritméticas)

```rif
add r0, r1, r2    ; ✅ Válido (todos < R8)
add r8, r9, r10   ; ❌ Error (R8+ no accesibles en Thumb)
add r0, r8, r1    ; ❌ Error (R8 no permitido)
```

### VRAM No Soporta Bytes

```rif
; Escribir en VRAM siempre de 16 bits (halfword) o más
strh r0, r1, r2   ; ✅ Válido (16 bits)
strb r0, r1, r2   ; ❌ Error en VRAM (byte)
```

### Inmediatos Limitados

```rif
store r0 = 255    ; ✅ Válido (0-255)
store r0 = 256    ; ❌ Error (> 255)
store r0 = 0x04000000  ; ❌ Error (demasiado grande)
```

**Solución para direcciones grandes:**

```rif
; Usar relocaciones
reloc abs, DISPCNT, 32  ; Resuelve la dirección en link-time
```

---

## 🔗 Sinergia con Otros Plugins

### Con Plugin `image`

```bash
python -m rif build proyecto --plugin gba --plugin image
```

```rif
@fill_image_bitmap titulo.png pantalla_titulo
```

### Con Plugin `sound`

```bash
python -m rif build proyecto --plugin gba --plugin sound
```

```rif
@fill_sound_wav tema_principal intro.mp3 22050
```

### Con Plugin `fonts`

```bash
python -m rif build proyecto --plugin gba --plugin fonts
```

```rif
@fill_screen_text "RIF GBA" white black pantalla_inicio
```

---

## 📚 Referencia Rápida

### Instrucciones Más Comunes

| Instrucción | Formato | Descripción |
|-------------|---------|-----------|
| `store` | `store Rd = imm` | Carga inmediato (0-255) |
| `move` | `move Rd, Rs` | Copia registro |
| `add` | `add Rd, Rs, Rn` | Suma |
| `sub` | `sub Rd, Rs, Rn` | Resta |
| `ldr` | `ldr Rd, Rb, Ro` | Lee 32 bits |
| `str` | `str Rd, Rb, Ro` | Escribe 32 bits |
| `beq` | `beq label` | Salta si igual |
| `bne` | `bne label` | Salta si diferente |
| `jump` | `jump label` | Salto incondicional |
| `call` | `call label` | Salto y guarda retorno |
| `push` | `push Rd` | Empuja a pila |
| `pop` | `pop Rd` | Extrae de pila |

### Registros Especiales

| Registro | Alias | Propósito |
|----------|-------|----------|
| R13 | SP | Stack Pointer |
| R14 | LR | Link Register (retorno) |
| R15 | PC | Program Counter (actual + 4) |

---

## 🎯 Flujo Recomendado de Desarrollo

```
1. Diseña la arquitectura de tu juego
   ↓
2. Crea estructura base del .pack
   ↓
3. Implementa el main loop
   ↓
4. Agrega gráficos (@fill_image_bitmap)
   ↓
5. Integra audio (@fill_sound_wav)
   ↓
6. Prueba en mGBA (python -m rif -pcli gba run...)
   ↓
7. Optimiza usando profiler del emulador
   ↓
8. Genera VSIX para desarrollo en VS Code
```

---

## 📞 Soporte y Comunidad

- **Documentación Principal**: `rif/help/README.md`
- **Issues y Bugs**: GitHub Issues del repositorio
- **Ejemplos**: `examples/gba/` en el repo
- **Discusiones**: GitHub Discussions

---

## 📄 Licencia

El plugin GBA forma parte de RIF, licenciado bajo MIT.

---

## 🔍 Índice de Páginas

1. [Construcción y Ejecución](0_build_y_run.md)
2. [Visión General de Arquitectura](1_overview.md)
3. [Conjunto de Instrucciones Thumb](2_instrucciones.md)
4. [Registros de CPU y MMIO](3_registros.md)
5. [Directivas Fillables](4_fillables.md)
6. [Macros Estructurales de ROM](5_macros_rom.md)
