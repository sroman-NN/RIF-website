# Visión General: Arquitectura GBA

El plugin `gba` proporciona el soporte integral para compilar ROMs comerciales y homebrew de **Game Boy Advance** utilizando el ecosistema de cero-acoplamiento de RIF.

A diferencia de los ensambladores convencionales, este plugin enseña al compilador de RIF cómo estructurar la cabecera exigida por el hardware de Nintendo, cómo validar los sumatorios (checksums), y le inyecta la semántica de la **CPU ARM7TDMI**.

## 🧠 Arquitectura y CPU

El corazón del GBA es un procesador ARM7TDMI que puede operar en dos modos:
- **Estado ARM (32 bits)**: Reservado principalmente para el arranque o rutinas de alto rendimiento en IWRAM.
- **Estado Thumb (16 bits)**: El modo principal usado para ejecutar código desde el cartucho (ROM) debido a su mayor densidad y las limitaciones del bus de 16-bits.

El plugin **GBA de RIF emite código Thumb** nativo, en formato *Little Endian*, lo que garantiza lecturas óptimas desde el cartucho hacia el bus de la memoria sin necesidad de preprocesadores de terceros.

---

## 🗺️ Mapa Físico de Memoria (MMIO)

El plugin ya tiene pre-mapeadas las direcciones de estas secciones en su archivo `.pack`, permitiendo usar referencias directas como `r0, 0x06000000` (VRAM) o apoyarte en sus correspondientes tablas para relocaciones automáticas.

| Sección (Hardware) | Dirección  | Tamaño | Rol Principal                                   |
|--------------------|------------|--------|-------------------------------------------------|
| `.rom` / ROM       | 0x08000000 | 32 MB  | Memoria flash del cartucho (Instrucciones)      |
| `.ewram` / EWRAM   | 0x02000000 | 256 KB | Memoria de trabajo externa (Carga general)      |
| `.iwram` / IWRAM   | 0x03000000 | 32 KB  | Memoria interna (Altísima velocidad para bucles)|
| `.io` / IO         | 0x04000000 | 1 KB   | Registros MMIO (Control de Video, Sonido, DMA)  |
| `.palette`         | 0x05000000 | 1 KB   | Memoria CRAM (Paletas BGR555)                   |
| `.vram` / VRAM     | 0x06000000 | 96 KB  | Video RAM (Pixeles, Tiles y Mapas)              |
| `.oam` / OAM       | 0x07000000 | 1 KB   | Memoria de Atributos de Sprites (Objetos)       |

---

## 📁 Estructura del Ecosistema

Todo el soporte arquitectónico de GBA vive dentro del directorio `rif/plugins/gba/`. Sus responsabilidades están estrictamente divididas:

```text
plugins/gba/
├── cli.py                    # 💻 Interfaz de subcomandos `rif -pcli gba`
├── cli/
│   ├── install.py            # Script que descarga mGBA automáticamente
│   └── run.py                # Wrapper para inyectar la ROM al emulador
├── fillables.py              # 🎨 Directivas @fill_screen / @fill_screen_text
├── packs/example/
│   ├── gba.pack              # ⚙️ Punto de entrada: Importa el universo GBA
│   ├── gba.regs.pack         # 🗄️ Tabla de los 16 Registros (R0-R15)
│   ├── gba.sections.pack     # 🗺️ Inicialización de los VOff y bloques
│   └── gba.rules.pack        # 📐 Expresiones regulares y reglas Thumb
└── plugins/
    ├── thumb_ins.py          # 🤖 Intérprete aritmético del Set de Instrucciones
    ├── gba_headers.py        # 🧱 Constructor binario de la Cabecera 0x00-0xBF
    ├── gba_logo.py           # 🍄 Inyección estricta del Logo de Nintendo
    ├── gba_checksum.py       # 🧮 Cómputo matemático de validación
    └── gba_entry.py          # 🚪 Inyector del salto ARM -> Thumb (bx)
```

## 🤝 Sinergia con otros Plugins

Gracias al diseño agnóstico de RIF, el plugin GBA se beneficia automáticamente de:
- **Plugin Image**: Si compilas tu proyecto GBA incluyendo `--plugin image`, ganarás acceso a `@fill_image_bitmap` para insertar PNGs/BMPs comprimidos a formato VRAM de GBA.
- **Plugin Sound**: Usando `--plugin sound`, puedes inyectar archivos `.wav` de 8-bits e invocar el DMA del GBA para hacer streaming de audio nativo hacia el altavoz de la consola.
