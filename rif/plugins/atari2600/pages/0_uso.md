# Uso del Plugin Atari 2600

El plugin `atari2600` convierte codigo RIF en una ROM binaria para Atari 2600 /
VCS. Esta pensado para proyectos pequenos de 4 KiB sin bankswitching, que es el
formato historico mas simple de cartucho y el mejor punto de entrada para
probar el modelo TIA + RIOT.

## Compilar el ejemplo oficial

```bash
python -m rif build examples/atari2600 --plugin atari2600 --name example
```

El resultado se escribe como un binario `.bin` de Atari 2600. Puede abrirse con
Stella o con cualquier emulador compatible con ROMs VCS planas.

## Secciones del pack

| Seccion | Tipo | VOffset | Emite bytes | Uso |
|---|---:|---:|---:|---|
| `.rom` | code | `0xF000` | si | Codigo y datos de cartucho visibles al 6507. |
| `.zp` | data | `0x0000` | no | Alias conceptual de pagina cero. En hardware convive con TIA y RAM espejada. |
| `.ram` | data | `0x0080` | no | 128 bytes de RAM interna del RIOT, tambien usada como stack. |

La seccion importante para una ROM es `.rom`. El `voffset 0xF000` hace que
etiquetas, saltos absolutos y vectores sean resueltos como direcciones del bus
del 6507, aunque fisicamente el archivo empiece en `0x0000`.

## Final obligatorio de ROM

Una ROM de 4 KiB se mapea de `0xF000` a `0xFFFF`. Los ultimos seis bytes del
espacio de direcciones contienen los vectores 6502:

| Vector | Direccion CPU | Proposito |
|---|---:|---|
| NMI | `0xFFFA-0xFFFB` | No usado normalmente por Atari 2600. |
| RESET | `0xFFFC-0xFFFD` | Punto de entrada al encender o resetear. |
| IRQ/BRK | `0xFFFE-0xFFFF` | Interrupciones no usadas por el 6507, pero BRK puede consultarlo. |

El pack ofrece dos helpers:

```rif
    rompad_to_vectors
    vectors start
```

`rompad_to_vectors` rellena hasta el offset fisico `0x0FFA`; `vectors start`
emite tres relocaciones absolutas de 16 bits hacia `start`.

## Flujo normal de desarrollo

1. Escribe codigo en `main.a26asm`.
2. Usa `.section rom` para codigo y datos emitidos.
3. Inicializa CPU: `sei`, `cld`, `txs`.
4. Limpia RAM y registros TIA relevantes.
5. Construye cada frame con `VSYNC`, `VBLANK`, `WSYNC` y un kernel de dibujo.
6. Cierra el archivo con `rompad_to_vectors` y `vectors start`.
7. Compila y ejecuta con Stella.

## Fuentes tecnicas usadas por el pack

La semantica de TIA esta alineada con el Stella Programmer's Guide. Los
registros RIOT siguen el mapa comun de Atari 2600: `SWCHA`, `SWCHB`, `INTIM`,
`TIM1T`, `TIM8T`, `TIM64T` y `TIM1024T`.
