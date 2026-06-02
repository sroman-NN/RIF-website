# Plugin de Sonido (RIF)

Este plugin expande las capacidades del **Retargetable ISA Foundry (RIF)** dotándolo de un pipeline completo para la conversión e inyección de audio digital moderno (WAV, MP3) hacia los formatos primitivos que demandan las consolas retro (como arreglos PCM puros de 8-bits).

---

## ✨ Características Principales

- **Conversión Automática (Build-Time):** Inyecta y transforma tus audios MP3/WAV a PCM directamente desde tu código `.mdasm` o `.pack` utilizando macros `@fill`.
- **Downsampling Dinámico:** Controla la frecuencia de muestreo, duración, y volúmenes de forma programática.
- **Auto-Instalación de Dependencias:** El CLI del plugin gestiona la descarga local de FFmpeg para que tu proyecto RIF compile sin requerir instalaciones del sistema.
- **Game Boy Advance (Direct Sound):** Incluye generadores de ensamblador nativo ARM32 para configurar dinámicamente los registros DMA1, FIFO A, y Timers según tu sample rate personalizado.

---

## 🚀 Inicio Rápido

### 1. Instalar la Dependencia Base (FFmpeg)

El plugin usa de fondo FFmpeg para decodificar los audios de forma precisa y robusta. Instálalo de forma automatizada usando el CLI de RIF:

```bash
python -m rif -pcli sound install ffmpeg
```

### 2. Conversión Manual (Opcional)

Si prefieres convertir un audio y ver el resultado sin integrarlo todavía al proyecto:

```bash
python -m rif -pcli sound convert mi_cancion.mp3 salida.pcm --rate 16384 --duration 5.0
```

### 3. Integración en tu Código (Ejemplo GBA)

Usa los fillables dentro de tu código RIF para enlazar directamente un archivo MP3 que vivirá en tu ROM como datos binarios estructurados:

```rif
.section rodata
bgm_music:
    @sound_mp3 musica.mp3 bgm_music 10512
```

---

## 📖 Documentación Extensa

Toda la documentación técnica se integra automáticamente en el portal local interactivo del RIF. Para ver todos los detalles, abre la ayuda:

```bash
python -m rif help --open
```

O lee directamente los documentos Markdown que se incluyen:

1. [Visión General (Formatos y PCM)](pages/0_overview.md)
2. [Herramientas CLI (Install & Convert)](pages/1_herramientas.md)
3. [Guía de Fillables (Macros y Direct Sound)](pages/2_fillables.md)

---

## 📁 Estructura del Proyecto

```text
rif/plugins/sound/
├── README.md               # Este archivo
├── cli.py                  # Interfaz de comandos principal
├── cli/
│   ├── convert.py          # Lógica para extraer crudos PCM
│   └── install.py          # Autodescargador de FFmpeg
├── filleable/
│   └── fill_sound.py       # Fillables @sound_wav, @sound_mp3
├── GBA/
│   └── converter.py        # Envoltorio FFmpeg hacia GBA s8
└── pages/                  # Documentación interactiva
```
