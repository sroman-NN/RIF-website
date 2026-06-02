# Arquitectura Atari 2600

Atari 2600 es una maquina deliberadamente minima. No tiene framebuffer: el CPU
debe alimentar al TIA mientras el haz de video avanza. Esa condicion define casi
todo el estilo de programacion.

## Chips principales

| Chip | Funcion | Resumen |
|---|---|---|
| MOS 6507 | CPU | Variante del 6502 con bus de direcciones reducido a 13 lineas. Ve hasta 8 KiB de espacio. |
| TIA | Video, audio, entradas analogicas y colisiones | Genera la senal de television, sprites por linea, playfield, audio y latches de entrada. |
| RIOT 6532 | RAM, I/O y timer | Contiene 128 bytes de RAM, puertos para joysticks/switches y temporizadores. |
| Cartucho | ROM | En el pack oficial: 4 KiB mapeados virtualmente en `0xF000-0xFFFF`. |

## CPU 6507

El 6507 ejecuta el set documentado del 6502, pero no expone todas las lineas de
direccion. En Atari 2600 eso significa:

- Registros de CPU: acumulador `A`, indices `X` e `Y`, stack pointer `SP`,
  program counter interno y registro de estado.
- Stack en pagina `0x0100`, que por espejado termina usando la RAM de 128 bytes
  del RIOT.
- No hay IRQ externas en el uso normal del 2600; la programacion se sincroniza
  por polling y escritura a TIA.
- El coste en ciclos importa tanto como el opcode. Una scanline completa da 76
  ciclos de CPU, y el codigo visible del kernel debe contarlos.

## Mapa de memoria practico

El hardware decodifica pocas lineas y por eso muchas zonas son espejos. El pack
declara las direcciones canonicas mas usadas:

| Rango CPU | Dispositivo | Uso |
|---|---|---|
| `0x0000-0x007F` | TIA | Registros write/read por direcciones bajas y espejos. |
| `0x0080-0x00FF` | RIOT RAM | 128 bytes de RAM. |
| `0x0280-0x029F` | RIOT I/O + timer | Joysticks, switches, DDRs y temporizadores. |
| `0xF000-0xFFFF` | Cartucho | ROM de 4 KiB en este pack. |

La ROM fisica de 4 KiB ocupa `0x0000-0x0FFF` dentro del archivo, pero el 6507 la
lee como `0xF000-0xFFFF`. Por eso `.rom` tiene `voffset 0xF000`.

## Secciones RIF

```rif
.section rom
start:
    sei
    cld
    txs
```

La seccion `.rom` es la unica que emite bytes. `.zp` y `.ram` existen como
espacios virtuales para documentar y referenciar el mapa, pero no agregan datos
al binario del cartucho.

## Consecuencia clave

En GBA o Mega Drive puedes preparar memoria de video y dejar que el hardware la
lea. En Atari 2600 no: cada linea visible se construye al vuelo escribiendo a
registros como `PF0`, `PF1`, `PF2`, `GRP0`, `GRP1`, colores y posiciones. Un
programa correcto no solo debe emitir bytes correctos; debe emitirlos en el
ciclo correcto.
