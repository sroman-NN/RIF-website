# Visión General: Plugin de Sonido

El plugin `sound` proporciona a Retargetable ISA Foundry (RIF) la capacidad de inyectar y formatear audio digital moderno (WAV, MP3) hacia los formatos de audio primitivos que utilizaban las consolas retro y arquitecturas clásicas.

## 🎵 ¿Por qué convertir el audio?

Sistemas clásicos como la Game Boy Advance o la Mega Drive no tenían decodificadores de MP3 integrados ni ancho de banda para streamear audio a calidad de CD (44.1 kHz, 16-bits estéreo). 

Para reproducir sonido digital real (efectos de voz, samples de batería, o música digital), estas consolas utilizaban técnicas de modulación de ancho de pulso (PWM) o canales *Direct Sound* leyendo arreglos de bytes puros conocidos como **PCM (Pulse Code Modulation)**.

## ⚙️ Características del Plugin

- **Downsampling Automático:** Permite definir la frecuencia de muestreo de destino (ej. 8192 Hz o 16384 Hz).
- **Conversión de Profundidad:** Convierte audio de alta resolución a arreglos `s8` (Signed 8-bit) o `u8` (Unsigned 8-bit) dependiendo de lo que el chip de sonido espere.
- **Transformaciones en Tiempo de Compilación:** En lugar de forzarte a convertir los archivos WAV manualmente usando herramientas externas, el plugin permite inyectar etiquetas como `@sound_wav` en tu código ensamblador RIF. En el proceso de *build*, RIF convertirá el audio on-the-fly.
- **Instalador de Motor CLI:** Descarga automáticamente `ffmpeg` (el estándar dorado en procesamiento multimedia) usando el sistema CLI de plugins para que no tengas que configurar dependencias complejas.

## Arquitecturas Soportadas (Directamente)
Actualmente, el plugin tiene soporte estructurado fuerte para el canal Direct Sound A/B de **Game Boy Advance (ARM/Thumb)**, proveyendo no solo la conversión de datos sino también las rutinas de ensamblador ARM para inicializar los Timers y Canales DMA necesarios para reproducir el arreglo.
