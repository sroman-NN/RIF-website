# Timing de Video

Atari 2600 no dibuja desde memoria de video. El programa debe generar cada frame
escribiendo a TIA con temporizacion precisa. En NTSC, la convencion homebrew mas
comun es un frame de 262 scanlines:

| Fase | Scanlines tipicas | Uso |
|---|---:|---|
| VSYNC | 3 | Pulso de sincronizacion vertical. |
| VBLANK | 37 | Preparar estado, leer controles, actualizar logica. |
| Visible | 192 | Kernel de dibujo. |
| Overscan | 30 | Logica adicional antes del siguiente frame. |

Los numeros pueden ajustarse, pero Stella y televisores esperan una cadencia
estable. Si el conteo total cambia mucho, veras saltos, pantalla inestable o
colores fuera de lugar.

## Scanline y ciclos

Cada scanline tiene 228 color clocks. El CPU corre a un tercio de ese reloj, por
lo que hay 76 ciclos de CPU por linea. Una escritura a `WSYNC` alinea el codigo
con el inicio de la siguiente linea:

```rif
    sta_abs_addr WSYNC
```

El valor escrito no importa; `WSYNC` es un strobe.

## Secuencia VSYNC

```rif
    lda_imm 0x02
    sta_abs_addr VSYNC
    sta_abs_addr WSYNC
    sta_abs_addr WSYNC
    sta_abs_addr WSYNC
    lda_imm 0x00
    sta_abs_addr VSYNC
```

D1 de `VSYNC` inicia el pulso. Tres lineas es la practica NTSC clasica.

## VBLANK

`VBLANK` bit D1 apaga la salida visible. Durante este periodo se limpian
colisiones, se leen entradas, se calculan posiciones y se cargan temporizadores.

```rif
    lda_imm 0x02
    sta_abs_addr VBLANK
```

Para volver a mostrar:

```rif
    lda_imm 0x00
    sta_abs_addr VBLANK
```

## Kernel visible

Un kernel minimo puede limitarse a esperar 192 lineas:

```rif
    ldx_imm 192
draw_loop:
    sta_abs_addr WSYNC
    dex
    bne draw_loop
```

Un kernel real escribe `PF0/PF1/PF2`, `GRP0/GRP1`, colores y posiciones en
ciclos concretos de cada linea. La ventaja es enorme flexibilidad; la desventaja
es que cada instruccion tiene que ser elegida con cuidado.

## HMOVE

`HMOVE` debe ejecutarse inmediatamente despues de `WSYNC` para dar al TIA el
tiempo de blank horizontal completo. El flujo clasico:

```rif
    sta_abs_addr WSYNC
    sta_abs_addr HMOVE
```

Despues de `HMOVE`, evita modificar registros `HMP0/HMP1/HMM0/HMM1/HMBL` durante
unas decenas de ciclos. En kernels avanzados esto afecta tanto posicionamiento
como las conocidas barras de HMOVE.

## Colisiones

Los latches de colision se acumulan mientras se dibuja. Leelos durante VBlank u
overscan, y limpialos antes de empezar la parte visible:

```rif
    lda_abs_addr CXPPMM
    ; analizar D7/D6
    sta_abs_addr CXCLR
```

`CXCLR` es strobe; el contenido de `A` no importa.
