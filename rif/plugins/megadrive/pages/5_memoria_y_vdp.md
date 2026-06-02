# Memoria y VDP (Video Display Processor)

En Sega Mega Drive, a diferencia de los bitmaps planos (como Mode 3 de GBA o sistemas modernos de PC), la arquitectura gráfica se basa en el **Tiling** y los **Planos** manejados internamente por el chip VDP.

## 💾 La VRAM (Video RAM) no pertenece al M68k

El procesador Motorola 68000 de la placa principal **no puede ver ni tocar directamente la RAM de Video de la consola**. Si intentas hacer un `MOVE` desde el M68k a la dirección que crees que son los pixeles de tu personaje, no funcionará.

El M68000 sólo tiene una pequeña "ventanilla de correo" en la memoria principal MMIO:
- El puerto `VDP_CTRL` (Control en `0x00C00004`).
- El puerto `VDP_DATA` (Datos en `0x00C00000`).

### ¿Cómo pintar un píxel?

No pintas píxeles crudos. En su lugar:
1. Diseñas *Patrones* (Tiles) de 8x8 pixeles, donde cada pixel define qué índice de color usará de las 4 Paletas disponibles.
2. Le mandas al VDP el comando "Preparar escritura de memoria VRAM en la posición de los Patrones".
3. Le envías la data cruda del Tile a `VDP_DATA`. El VDP atrapará esa data y la guardará en su memoria interna aislada.
4. Le mandas al VDP un nuevo comando de escritura a una dirección del "Plane A" o "Plane B" (los Fondos del juego) y luego envías en Datos el ID de 16-bits de tu patrón. 

La pantalla ensamblará los 4 planos: Backdrop, Plane B, Plane A, y Window, mezclados con el hardware de Sprites. Todo ocurre mágicamente en hardware por el VDP en el momento del escaneo del CRT.

---

## 🎨 Paletas de Color y CRAM (Color RAM)

Mega Drive tiene una paleta maestra muy restrictiva en comparación con consolas posteriores, pero permitía crear el aspecto característico "arcade" rudo y contrastado.

- **Espacio CRAM:** Tiene espacio para **64 colores en total**, divididos en 4 paletas de 16 colores cada una.
- **Formato Color:** Usa un formato interno RGB de 9-bits (3 bits por canal de R, G, y B). Sin embargo, el M68k carga los colores empaquetados en un Word (16-bits) usando desplazamientos. Formato RIF: `0x0EEE` donde la E tiene valores pares (`0, 2, 4, 6, 8, A, C, E`). Por ejemplo, `0x000E` es rojo puro.
- Para escribir colores, mandas un comando `CRAM Write` al `VDP_CTRL` y pasas el Word del color al `VDP_DATA`.

## 📺 Direcciones Comunes del VDP (Ejemplos)

Aunque varían según tu configuración en la inicialización, la convención tradicional ubica las cosas en el VDP así (Recuerda: VRAM interna, no M68000):

| Componente | Qué contiene internamente en VDP |
| :--- | :--- |
| **VRAM General** | Donde cargas todos los gráficos base y los Tiles. |
| **Name Tables (Scroll A / B)** | Grillas bidimensionales donde indicas qué Tile va en qué posición de la pantalla y con qué Paleta y Prioridad. |
| **Sprite Attribute Table (SAT)** | Lista que vincula las coordenadas X, Y, enlace y Tile index de los sprites móviles. |
| **CRAM** | Las 4 paletas reales cargadas (64 colores) |
| **VSRAM** | El desplazamiento vertical para el scrolling asimétrico. |

> [!CAUTION]  
> En las consolas reales de hardware (no emuladores básicos), si le envías demasiados datos muy rápido al `VDP_DATA` mientras está intentando dibujar la pantalla para la TV (fuera del rango VBLANK/HBLANK), interrumpirás su bus y causarás la aparición de glitcheos conocidos como *CRAM Dots* u otras corrupciones en pantalla. Para prototipos básicos de RIF sin interrupciones, apaga la pantalla mandando el bit a `VDP_CTRL` antes de transferir lotes pesados.
