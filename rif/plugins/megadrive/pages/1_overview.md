# Visión General: Arquitectura Mega Drive

El plugin `megadrive` proporciona soporte integral para ensamblar ROMs comerciales y homebrew de **Sega Mega Drive (Genesis)** utilizando el ecosistema RIF.

A diferencia del GBA que usa arquitecturas modernas (Thumb/ARM), la Mega Drive tiene sus raíces en la era de los 16-bits dorados. El corazón del sistema es el venerable procesador **Motorola 68000 (M68k)**, trabajando junto a un coprocesador Zilog Z80 para el sonido y un potente VDP (Video Display Processor).

## 🧠 Arquitectura y CPU (M68000)

El Motorola 68000 es un procesador **CISC** (Complex Instruction Set Computer) que opera nativamente en **Big Endian**.

- Dispone de 8 Registros de Datos (`D0`-`D7`) y 8 de Direcciones (`A0`-`A7`).
- Las instrucciones pueden operar en 3 tamaños principales: **Byte** (8 bits), **Word** (16 bits) y **Long** (32 bits).
- A diferencia de los sistemas RISC modernos, las instrucciones CISC del M68k tienen una gran variedad de modos de direccionamiento y tamaños variables, permitiendo operaciones directamente sobre la memoria RAM externa.

El compilador RIF de este plugin traduce directamente a los opcodes nativos del Motorola 68000.

---

## 🗺️ Mapa Físico de Memoria

El plugin tiene pre-mapeadas las direcciones base para los bloques clave de la consola en su archivo `.sections.pack`.

| Sección (Hardware) | Dirección Base | Tamaño   | Rol Principal                                   |
|--------------------|----------------|----------|-------------------------------------------------|
| `.rom` / ROM       | `0x00000000`   | Hasta 4MB| Memoria ROM del cartucho (Instrucciones)        |
| `.ram` / WRAM      | `0x00FF0000`   | 64 KB    | Memoria RAM principal (Work RAM) del M68000     |
| `.z80_ram`         | `0x00A00000`   | 8 KB     | Memoria RAM compartida con el Zilog Z80 (Audio) |
| `.vdp_data`        | `0x00C00000`   | -        | Puerto de Datos del Video Display Processor     |
| `.vdp_ctrl`        | `0x00C00004`   | -        | Puerto de Control del Video Display Processor   |

---

## 📁 Estructura del Ecosistema

El soporte arquitectónico de Mega Drive vive dentro de `rif/plugins/megadrive/`.

```text
plugins/megadrive/
├── cli.py                    # 💻 Interfaz de subcomandos `rif -pcli megadrive`
├── packs/example/
│   ├── megadrive.pack        # ⚙️ Punto de entrada principal
│   ├── megadrive.regs.pack   # 🗄️ Tabla de los 16 Registros (D0-D7, A0-A7)
│   ├── megadrive.sections.pack # 🗺️ Mapa de bloques de memoria
│   └── megadrive.rules.pack  # 📐 Reglas densas del M68k (Opcodes)
└── plugins/
    ├── md_common.py          # ⚙️ Constantes y helpers (Big Endian)
    ├── md_vectors.py         # 🏹 Inyección de los Vectores de Interrupción
    ├── md_header.py          # 🧱 Constructor de la Cabecera oficial SEGA
    └── md_pad_to.py          # 🚪 Padding inteligente para el cartucho
```

Todo el ensamblaje de M68k reside en `megadrive.rules.pack`, lo que significa que el lenguaje ensamblador es dinámico y fácilmente expandible sin necesidad de alterar código Python rígido.
