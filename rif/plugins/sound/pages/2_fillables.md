# Fillables y Macros de Código

En lugar de incrustar manualmente arreglos de datos gigantescos mediante `db 0x00, 0x1A, 0x2B...`, el sistema de *Fillables* de RIF permite inyectar archivos y preprocesarlos desde el propio ensamblador. 

## 🔊 @sound_wav / @fill_sound_wav

Convierte y emite un archivo `.wav` directamente como un bloque de memoria de tipo `s8` (Signed 8-bit PCM) en el punto donde llamas a la macro. Automáticamente registra el tamaño para el linker de RIF.

**Sintaxis completa:**
```rif
@sound_wav <ruta_al_archivo> <etiqueta_opcional> <sample_rate> <duration> <start> <volume> <fade_in>
```

**Parámetros:**
1. `ruta` *(String)*: Ruta relativa al archivo fuente o ruta absoluta al audio.
2. `etiqueta` *(String)*: (Opcional) El nombre del símbolo para referenciarlo, si no se proporciona se intentará inferir, pero es recomendable ponerlo explícito (ej. `mi_musica`).
3. `sample_rate` *(Int)*: Frecuencia destino en Hz (Defecto: 8192).
4. `duration` *(Float)*: Cuántos segundos extraer (Defecto: 6.0).
5. `start` *(Float)*: Desde dónde comenzar (Defecto: 0.0).
6. `volume` *(Float)*: Multiplicador (Defecto: 0.85).
7. `fade_in` *(Float)*: Segundos de fundido inicial (Defecto: 0.25).

**Ejemplo Básico:**
```rif
    .section rodata
mi_cancion:
    @sound_wav assets/audio.wav mi_cancion 16384
```

> [!TIP]
> Si la ruta tiene espacios, encciérrala entre comillas: `"mis assets/audio.wav"`.

## 🎵 @sound_mp3 / @fill_sound_mp3

Es funcionalmente idéntica a `@sound_wav`. Utiliza el mismo motor interno de FFmpeg para extraer y transcodificar un archivo `.mp3` al formato interno de la consola.

```rif
    @sound_mp3 cancion.mp3 bgm_level_1 8192 120.0 0.0 0.5
```

---

## 🚀 Arquitectura: Game Boy Advance

### @gba_dsound_start / @fill_gba_dsound_start

Para reproducir el audio generado en la GBA, necesitas configurar el canal de DMA (Direct Memory Access) para bombear el audio al FIFO y configurar un Timer (Temporizador) que dicte la velocidad.

Esta macro inyecta *todo el código ARM32 necesario* para iniciar la reproducción de un sample inyectado previamente con `@sound_wav`. 

**Sintaxis:**
```rif
@gba_dsound_start <símbolo_del_sonido> <sample_rate>
```

**Ejemplo de implementación:**
```rif
.section rodata
    ; 1. Inyectar los datos crudos a 10.5 kHz
sonido_salto:
    @sound_wav salto.wav sonido_salto 10512

.section rom
    ; (Asumiendo que estás en modo ARM32)
    ; 2. Arrancar la reproducción del sample
    @gba_dsound_start sonido_salto 10512
```

**¿Qué hace internamente?**
- Escribe en `SOUNDCNT_H` para habilitar el canal Direct Sound A.
- Enciende el sonido global en el Master Sound Control.
- Configura la dirección origen (`SAD`) del canal `DMA1` para apuntar a tu `símbolo_del_sonido`.
- Configura el destino (`DAD`) hacia el registro FIFO A (`0x040000A0`).
- Configura el Timer 0 calculando el factor de recarga basado matemáticamente en el `<sample_rate>` que le pases. (Fórmula: `65536 - (16777216 / sample_rate)`).
- Activa el modo "Repetir por FIFO" en el bloque DMA.
