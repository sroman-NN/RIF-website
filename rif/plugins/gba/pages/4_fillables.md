# Fillables

Un fillable es una llamada de build-time. RIF la resuelve antes de compilar,
genera bytes o codigo auxiliar y registra la ubicacion final en `fills.json`.

Forma general:

```rif
@args@namefunc@namelabel
```

| Parte | Significado |
|---|---|
| `args` | Argumentos del fillable. Usa comillas si contienen espacios. |
| `namefunc` | Funcion del plugin que genera el contenido. |
| `namelabel` | Label y clave generada en `fills.json`. |

## Cabecera y ROM

| Fillable | Uso |
|---|---|
| `fill_headers` | Emite la instruccion ARM inicial de la cabecera. |
| `fill_logo` | Inserta el logo requerido por la BIOS. |
| `fill_checksum` | Inserta metadatos y checksum. |
| `fill_gba_header` | Todo en uno: header, logo y checksum. |
| `fill_entry` | Entrada ARM. |
| `fill_entry_thumb` | Entrada que cambia a Thumb. |
| `fill_rompad` | Padding final de ROM. |

Ejemplo:

```rif
@"MY GAME"@fill_gba_header@gba_header
@fill_entry_thumb
```

En proyectos que prefieren macros directas, usa `set_headers`, `set_logo`,
`set_checksum`, `set_entry_thumb` y `rompad`.

## Pantalla

| Fillable | Resultado |
|---|---|
| `fill_screen` | Buffer Mode 3 de 240x160 en BGR555. |
| `fill_screen_text` | Alias de compatibilidad: genera pantalla solida y registra que el texto debe venir de `fonts`. |
| `fill_frame` | Framebuffer Mode 3 solido para rutinas de frame. |

```rif
@green@fill_screen@screen_bg
@green@fill_frame@title_screen
```

GBA no incluye una fuente propia ni sabe como dibujar glyphs. Para texto,
importa `fonts`, genera la tabla bitmap y consumela desde una rutina de render
del proyecto.

## Imagenes

Con el plugin `image` importado por el pack:

```rif
@"assets/mario.png" 128 false@fill_image_bitmap@mario_sprite
```

El pipeline convierte imagenes a datos adecuados para GBA. Para VRAM directa,
prefiere halfwords BGR555 y escritura con `strh`/`arm_strh`.

## Audio

Con el plugin `sound`:

```rif
@"assets/music.mp3" 16000 8 0 0.85 0.25@sound_mp3@bgm_sample
@bgm_sample 16000@gba_dsound_start@bgm_sample_player
```

El primer fillable genera muestras PCM; el segundo genera una rutina de arranque
para Direct Sound/DMA cuando el plugin de sonido la expone.

## Fuentes

Con el plugin `fonts`:

```rif
@"RIF GBA"@fonts_fill_5x7x1@title_text
@"HP 99" 3x5@fonts_fill_text_u16@hud_text
```

El resultado es una tabla bitmap independiente de GBA. El renderer decide si la
copia a Mode 3, tiles, sprites, RAM temporal o cualquier otro formato propio.

## `fills.json`

Despues del link, `fills.json` guarda informacion de labels generados. Los
helpers de `basics` (`fillid`, `vfillid`) pueden resolver direcciones fisicas o
virtuales de esos datos cuando el codigo generado necesita punteros.
