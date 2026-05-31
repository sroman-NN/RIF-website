# Directivas Fillables (Generación de Datos)

En RIF, un "fillable" (marcado con `@`) es una macro inteligente pre-procesada. Antes de compilar, el linker de RIF intercepta estas llamadas y genera bloques masivos de código fuente o binario de forma algorítmica.

El plugin de GBA trae herramientas estáticas nativas, pero también se diseña para recibir inyecciones de los plugins `image` y `sound`.

---

## 🎨 Gráficos Básicos Nativos (GBA Plugin)

Estas directivas generan memoria VRAM desde colores simples o texto pre-empaquetado usando las rutinas internas del plugin.

### `@fill_screen`
Genera un buffer completo de 38,400 píxeles de 16-bits (76.8 KB) rellenado del color BGR555 especificado. Es perfecto para limpiar fondos.

```rif
@fill_screen black screen_bg
@fill_screen green mi_fondo
```
- **Arg 1**: Color (`black`, `white`, `green`, `red`, `blue`, etc.)
- **Arg 2**: Nombre de la variable (label) generada.

### `@fill_screen_text`
Genera un buffer de pantalla completa, pero estampa en el centro un texto en fuente de mapa de bits (bitmap) a escala x3.

```rif
@fill_screen_text START white black pantalla_inicio
```
- **Arg 1**: El texto a renderizar (ASCII en mayúsculas).
- **Arg 2**: Color de la fuente.
- **Arg 3**: Color del fondo.
- **Arg 4**: Etiqueta generada.

---

## 🖼️ Imágenes Avanzadas (Plugin `image`)

Si importas el plugin `image` en tu entorno (ej. `--plugin gba --plugin image`), puedes invocar conversiones de disco dinámicas hacia formato GBA.

### `@fill_image_bitmap`
Lee un `.png`, `.jpg` o `.bmp` de tu disco, le aplica *downsampling por promedio de caja* para suprimir el anti-aliasing negro, y lo convierte al estándar **BGR555**.

```rif
; Toma "mario.png" y crea el buffer de VRAM "mario_sprite"
@fill_image_bitmap mario.png mario_sprite
```

> [!TIP]
> **Promedio de Caja (Box Average)**: Si tu imagen original no cuadra matemáticamente con los pixeles de tu buffer, el algoritmo no descarta píxeles de forma ruda (nearest-neighbor), sino que promedia sus canales de color.

---

## 🎵 Motor de Audio (Plugin `sound`)

Si usas el plugin `sound`, puedes pedir a RIF que convierta pistas de audio modernas (`.wav`, `.mp3`) para que el GBA pueda streamearlas vía **Direct Sound A**.

### `@fill_sound_wav`
Llama a **FFmpeg** en segundo plano, re-muestrea tu pista, la convierte a canal mono, la fuerza a 8-bits con signo (`pcm_s8`) y la emite en memoria lista para DMA.

```rif
; Pasa "music.mp3" a 16000 Hz firmados, etiqueta "bgm_sample"
@fill_sound_wav bgm_sample music.mp3 16000
```
- **Arg 1**: Etiqueta (El plugin anexará sufijos automáticos para controlar el DMA: `_timer_reload`, `_dma_control`).
- **Arg 2**: Ruta al archivo local de audio.
- **Arg 3**: Frecuencia de muestreo destino (ej. `16000`, `22050`).
