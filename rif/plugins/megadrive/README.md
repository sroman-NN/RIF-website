# 🦔 Plugin Mega Drive para RIF - Documentación Completa

Este es el módulo oficial de **Sega Mega Drive (Sega Genesis)** para el framework **Retargetable ISA Foundry (RIF)**. Proporciona un compilador y enlazador de ensamblador de la familia Motorola 68000, junto con soporte estandarizado para tablas de vectores y creación de cabeceras de hardware requeridas.

---

## ✨ Características Principales

### Core del Compilador (M68k)
- **Compilador Motorola 68000 Nativo** - Reglas y opcodes puros en `megadrive.rules.pack` (`move`, `add`, `cmp`, `bra`).
- **Arquitectura Big-Endian** - Soporte nativo para el Motorola 68000 a través del `.world endianness big`.
- **Estructura Dinámica** - Generación inteligente de ROMs sin atar el tamaño a límites fijos de terceros ensambladores.

### Inyección de Hardware
- **Vectores Automáticos** - Inyección inteligente de interrupciones, saltos de booteo y punteros al Stack con `md_vectors`.
- **Cabecera Sega Oficial** - La macro `md_header` inyecta automáticamente los metadatos y sumas de verificación oficiales de 256 bytes exigidos por la consola.
- **Auto-Padding Inteligente** - `md_rompad` para ajustar la imagen ROM al bloque de potencia base del cartucho real.

### Herramientas CLI
- **Compilación Integrada** - `python -m rif build ... --plugin megadrive`
- **Emulador Automático** - `python -m rif -pcli megadrive run archivo.bin`
- **Instalación de Emulador** - Descarga e instala tu suite de pruebas desde línea de comando (Ej. blastem).

---

## 🚀 Inicio Rápido

### 1. Compilar un Proyecto Mega Drive

```bash
# Compilar el ejemplo oficial del repositorio
python -m rif build examples/megadrive --plugin megadrive --name example

# Generar salida en examples/megadrive/megadrive.bin
```

### 2. Ejecutar en Emulador

```bash
# Instalar tu emulador favorito desde RIF
python -m rif -pcli megadrive install blastem --add-path

# Ejecutar el ROM (sin duplicar múltiples ventanas al iterar)
python -m rif -pcli megadrive run examples/megadrive/megadrive.bin -nd
```

### 3. Documentación Interactiva

```bash
# Abre el navegador de ayuda local de RIF
python -m rif help --open

# Navega a 'megadrive' en el panel izquierdo para leer este manual
```

---

## 📁 Estructura del Proyecto

### Directorios Clave

```
rif/plugins/megadrive/
├── README.md                 # Este archivo principal
├── cli.py                    # Interfaz subcomandos (rif -pcli megadrive)
├── packs/example/
│   ├── megadrive.pack        # Archivo maestro de mapeo M68k
│   ├── megadrive.regs.pack   # Tabla de los registros D0-D7 y A0-A7
│   ├── megadrive.sections.pack # Mapa de memoria ROM, WRAM, Z80_RAM
│   └── megadrive.rules.pack  # Reglas densas del M68k (Opcodes y saltos)
├── pages/                    # Páginas de documentación detallada
├── plugins/
│   ├── md_common.py          # Constantes y generadores (Big-Endian)
│   ├── md_header.py          # Constructor de la cabecera SEGA
│   ├── md_vectors.py         # Interrupciones y Reset
│   └── md_pad_to.py          # Padding (Padding final del cartucho)
└── vscode/
    ├── build.json            # Metadatos del plugin VS Code
    ├── syntaxs.json          # Soporte de coloreado M68k en VS Code
    ├── doc.json              # Hovers con documentación
    └── assets/               # Iconos y multimedia
```

---

## 🧠 Arquitectura Mega Drive (M68k + VDP + Z80)

### Motorola 68000

| Especificación | Detalles |
|------|----------------|
| **Modo Operación** | **Big Endian** - Instrucciones de longitud variable (Word-aligned). |
| **Registros Generales** | 8 Data Registers (`D0-D7`), 8 Address Registers (`A0-A7`). |
| **Cálculo Gráfico** | Carece de soporte frame-buffer; debe enviarse al **VDP**. |
| **Sonido** | Delegado generalmente a chips de síntesis paralelos o al Z80. |

### Mapa de Memoria Principal

| Sección | Dirección | Tamaño | Uso en Hardware |
|---------|-----------|--------|----------|
| **ROM** | `0x00000000` | <= 4 MB | Cartucho ROM (Datos inmutables) |
| **Z80 RAM**| `0x00A00000` | 8 KB | Coprocesador Zilog (Música y FM) |
| **VDP Puertos**| `0x00C00000` | MMIO | I/O Principal hacia procesador Gráfico |
| **RAM (WRAM)** | `0x00FF0000` | 64 KB | Work RAM principal para el M68k |

---

## 📖 Páginas de Documentación

### [0. Construcción y Ejecución](0_build_y_run.md)
- Flujo completo de construcción
- Herramientas CLI de SEGA
- Flag No-Duplicates (`-nd`)

### [1. Visión General de Arquitectura](1_overview.md)
- CPU M68k CISC y tamaños
- Distribución de bloques y extensiones lógicas
- Sinergia del ecosistema RIF

### [2. Conjunto de Instrucciones](2_instrucciones.md)
- Opcodes clásicos Motorola en RIF (`move`, `add`, `cmp`)
- Aritmética y ramas de control `bra`/`bne`
- Direccionamientos `(SP)+` o `-(SP)`

### [3. Registros de CPU](3_registros.md)
- Familias de Datos (D0-D7) vs Direcciones (A0-A7)
- Flags de CCR (Condition Code Register)
- Puertos del Video Display Processor (VDP_DATA / VDP_CTRL)

### [4. Macros Estructurales de ROM](4_macros_rom.md)
- Tablas vectoriales iniciales `md_vectors`
- Cabecera obligatoria SEGA `md_header`
- Acolchado dinámico `md_rompad`

### [5. Memoria y VDP](5_memoria_y_vdp.md)
- Puertos de control (`0x00C00004`) y datos (`0x00C00000`)
- Patrones (Tiles) y Planos de fondo (Plane A, B)
- CRAM (Color RAM y paletas)

### [6. Ejemplo Mínimo Completo](6_ejemplo_minimo.md)
- Esqueleto vacío compatible M68k
- Inicialización y bucles inifinitos comprobables en emulador

---

## ⚠️ Diferencias Sintácticas en RIF

A diferencia del ensamblador estándar de SEGA (ej. ASM68k/SNASM68k), RIF prefiere comandos fuertemente estructurados que resuelvan en expresiones nativas:

**Estándar Motorola (ASM68k):**
```m68k
    MOVE.W #1, D0
    ADD.W #1, D0
    BEQ _fin
```

**Sintaxis Nativa RIF (M68k):**
```rif
    move_w_imm_d 1, D0
    add_w_imm_d 1, D0
    beq fin
```

## 📄 Licencia

El plugin Mega Drive forma parte del proyecto Retargetable ISA Foundry (RIF), licenciado bajo MIT.

---

## 🔍 Índice de Páginas

1. [Construcción y Ejecución](0_build_y_run.md)
2. [Visión General de Arquitectura](1_overview.md)
3. [Conjunto de Instrucciones](2_instrucciones.md)
4. [Registros de CPU y MMIO](3_registros.md)
5. [Macros Estructurales de ROM](4_macros_rom.md)
6. [Memoria y VDP](5_memoria_y_vdp.md)
7. [Ejemplo Mínimo Completo](6_ejemplo_minimo.md)
