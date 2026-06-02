# RIOT 6532, RAM y Controles

El RIOT 6532 combina RAM, puertos de entrada/salida y temporizador. En Atari
2600 se usa para leer joysticks, switches de consola y para medir intervalos
sin gastar un loop exacto de CPU todo el tiempo.

## RAM

El RIOT contiene 128 bytes de RAM. En el mapa usual aparecen en `0x0080-0x00FF`
y se espejan por la decodificacion parcial del bus. Esta RAM tambien sirve como
stack efectivo del 6507, porque la pagina de stack `0x0100-0x01FF` cae en
espejos del mismo bloque fisico.

Recomendacion de arranque:

```rif
    sei
    cld
    txs

    lda_imm 0x00
    tax
clear_loop:
    sta_zpx 0 X
    inx
    bne clear_loop
```

## Puertos RIOT

| Registro | Dir | Acceso | Funcion |
|---|---:|---|---|
| `SWCHA` | `0x0280` | R/W | Port A. Direcciones de joysticks y algunos controladores. |
| `SWACNT` | `0x0281` | R/W | DDR de port A. `0` entrada, `1` salida. |
| `SWCHB` | `0x0282` | R/W | Port B. Switches de consola. |
| `SWBCNT` | `0x0283` | R/W | DDR de port B. |
| `INTIM` | `0x0284` | R | Valor actual del temporizador. |
| `TIMINT` | `0x0285` | R | Estado/flag asociado al timer. |
| `TIM1T` | `0x0294` | W | Carga timer con decremento cada 1 ciclo. |
| `TIM8T` | `0x0295` | W | Carga timer con decremento cada 8 ciclos. |
| `TIM64T` | `0x0296` | W | Carga timer con decremento cada 64 ciclos. |
| `TIM1024T` | `0x0297` | W | Carga timer con decremento cada 1024 ciclos. |
| `T1024T` | `0x0297` | W | Alias compatible con versiones previas del pack. |

## Joysticks en SWCHA

Los bits son activos en bajo: `0` significa presionado o linea activada.

| Bit | Funcion comun |
|---:|---|
| D7 | Player 0 derecha. |
| D6 | Player 0 izquierda. |
| D5 | Player 0 abajo. |
| D4 | Player 0 arriba. |
| D3 | Player 1 derecha. |
| D2 | Player 1 izquierda. |
| D1 | Player 1 abajo. |
| D0 | Player 1 arriba. |

Ejemplo conceptual:

```rif
    lda_abs_addr SWCHA
    and_imm 0x10
    beq p0_up_pressed
```

## Switches en SWCHB

Tambien hay senales activas en bajo para botones momentaneos.

| Bit | Funcion |
|---:|---|
| D7 | Dificultad P1: `0` amateur, `1` pro. |
| D6 | Dificultad P0: `0` amateur, `1` pro. |
| D5 | No usado en el mapa base. |
| D4 | No usado en el mapa base. |
| D3 | Color/BW: `0` B/W, `1` color. |
| D2 | No usado en el mapa base. |
| D1 | Game select: `0` presionado. |
| D0 | Game reset: `0` presionado. |

## Botones y paddles

Los botones de joystick suelen leerse por `INPT4` y `INPT5` en TIA, no por
`SWCHA`. Los paddles usan `INPT0-INPT3`; se descargan con `VBLANK` bit D7 y se
mide cuanto tardan en volver a 1.

## Temporizadores

Para esperar VBlank u overscan sin contar todos los ciclos a mano:

```rif
    lda_imm 43
    sta_abs_addr TIM64T
wait_vblank:
    lda_abs_addr INTIM
    bne wait_vblank
```

La escritura carga el contador. `INTIM` desciende segun el registro elegido. En
un kernel NTSC simple se usa mucho `TIM64T` para aproximar periodos de VBlank y
overscan mientras el codigo prepara estado para el siguiente frame.
