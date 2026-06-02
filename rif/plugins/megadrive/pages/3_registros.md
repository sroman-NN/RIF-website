# Registros de CPU (M68000)

A diferencia de las arquitecturas RISC (como ARM), el procesador Motorola 68000 de la Mega Drive divide sus registros en dos categorías con reglas matemáticas estrictas para su uso.

## 🗄️ Registros de Datos (D0 - D7)

Son 8 registros de propósito general, desde `D0` hasta `D7`.
Se utilizan para cálculos aritméticos, lógicos y almacenamiento general.

- Tienen un tamaño de **32 bits** (Long).
- **Flexibilidad**: Puedes aplicar instrucciones para modificar sólo el `.B` (los 8 bits más bajos), la `.W` (los 16 bits inferiores), o el `.L` (los 32 bits completos).
- Si usas instrucciones `.B` o `.W`, **el resto de los bits superiores del registro se mantienen intactos**, no se rellenan con ceros automáticamente a menos que uses instrucciones de extensión (`EXT`).

## 📍 Registros de Direcciones (A0 - A7)

Son 8 registros orientados estrictamente a contener direcciones de memoria o punteros. 

- Van desde `A0` hasta `A7`.
- **`A7` es el Puntero de Pila (Stack Pointer - SP)** del sistema.
- Las operaciones con registros `A` no actualizan las banderas (Flags) de condición en el CCR (Condition Code Register), ya que se asume que sumar o restar un puntero no es una operación matemática sino un desplazamiento de memoria.
- A diferencia de los registros de Datos, las escrituras en registros `A` como `Word` (16 bits) **siempre se extienden con signo a los 32 bits**.

> [!WARNING]  
> Nunca utilices registros de direcciones (`A`) para cálculos lógicos puros o banderas de `CMP` ya que su comportamiento difiere del hardware aritmético normal.

---

# Puertos MMIO (VDP - Video Display Processor)

Todo el apartado gráfico de la Mega Drive no está "mapeado en memoria" como en otros sistemas (no puedes escribir `MOVE` a una dirección RAM y que aparezca un píxel). Tienes que mandarle instrucciones binarias explícitas al chip VDP.

El chip de Video (VDP) se controla enviando comandos largos a direcciones en la memoria MMIO superiores.

| Registro Físico | Dirección Hex | Función Principal |
| :--- | :--- | :--- |
| **`VDP_DATA`** | `0x00C00000` | Puerto FIFO donde envías datos de Tiles (Patrones), Paletas (CRAM) y Sprites. |
| **`VDP_CTRL`** | `0x00C00004` | Puerto de Comandos para configurar VRAM, activar DMA o apagar/encender la pantalla. |
| **`Z80_BUSREQ`**| `0x00A11100` | Puerto para solicitar al chip de sonido Z80 que se detenga y te deje escribir en su RAM. |
| **`CTRL_1`**   | `0x00A10003` | Puerto del Mando Player 1 (Lectura del pad). |

> [!TIP]
> Escribir en VRAM requiere siempre dos pasos en el M68000:
> 1. Escribir un comando Long (`0x40000000` para "Escribir VRAM a dir 0") en `VDP_CTRL`.
> 2. Enviar inmediatamente un dato a `VDP_DATA`. El VDP internamente incrementará su propio puntero por cada escritura subsiguiente.
