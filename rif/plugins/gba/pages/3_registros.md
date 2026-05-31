# Registros de CPU y MMIO (GBA)

La consola GBA tiene a su disposición los 16 registros de la familia ARM. Sin embargo, al operar bajo las reglas del conjunto **Thumb** de 16-bits para reducir el uso de memoria, hay ciertas restricciones sobre qué registros puedes tocar de forma aritmética.

## 🗄️ Registros de Hardware (R0-R15)

| Registro (ARM) | ID Binario | Acceso en Thumb | Propósito Principal (APCS) |
| :--- | :--- | :--- | :--- |
| **`R0` - `R3`** | `000` - `011` | ✅ Absoluto | Argumentos de funciones y valores de retorno. |
| **`R4` - `R7`** | `100` - `111` | ✅ Absoluto | Variables de propósito general (Callee-saved). |
| **`R8` - `R12`**| `1000`-`1100`| ❌ Denegado | *Solo accesibles en modo ARM o con trucos avanzados.* |
| **`SP` (`R13`)**| `1101`        | ⚠️ Especial | **S**tack **P**ointer (Puntero a la Pila). Usa `push`/`pop`. |
| **`LR` (`R14`)**| `1110`        | ⚠️ Especial | **L**ink **R**egister (Dirección de retorno de subrutinas). |
| **`PC` (`R15`)**| `1111`        | ⚠️ Especial | **P**rogram **C**ounter (Puntero de la instrucción actual + 4). |

> [!WARNING]  
> Nunca modifiques el registro `PC` (`R15`) manualmente a través de sumas aritméticas en Thumb. Utiliza siempre las directivas nativas `jump` (para flujos locales) o `call` (para subrutinas).

---

## 📞 Convención de Llamada

Cuando programes rutinas complejas o funciones reutilizables, sigue la convención APCS de ARM:
- Utiliza **`R0`, `R1`, `R2`, y `R3`** para pasar variables a la función.
- El resultado del cálculo devuélvelo siempre en **`R0`**.
- Si tu función necesita usar los registros **`R4-R7`**, estás obligado a guardarlos en la pila con `push` al iniciar tu función, y restaurarlos con `pop` justo antes del salto de retorno.

## 🕹️ Memory-Mapped I/O (Registros de Hardware)

El GBA controla el hardware de la consola, la pantalla y los botones escribiendo números mágicos en direcciones específicas de memoria (`0x04000000`).

| Nombre del Registro | Dirección Hex | Función |
| :--- | :--- | :--- |
| **`DISPCNT`** | `0x04000000` | Display Control. Sirve para activar fondos, objetos y el modo de video (Ej. Mode 3). |
| **`DISPSTAT`** | `0x04000004` | Display Status. Monitorea cuando la pantalla se apaga (VBlank/HBlank) para evitar parpadeos. |
| **`VCOUNT`** | `0x04000006` | Vertical Count. Devuelve qué línea de píxeles (0-227) está dibujando el cañón de electrones. |
| **`SOUNDCNT_L`** | `0x04000060` | Control de volúmenes de los canales del Game Boy clásico. |
| **`SOUNDCNT_H`** | `0x04000082` | Control principal del flujo DMA (Direct Sound) para audio de alta calidad. |
| **`KEYINPUT`** | `0x04000130` | Lector de los botones (Pad y Gatillos). *Atención: La señal es activa en bajo (0 es presionado).* |
| **`IME` / `IE` / `IF`** | `0x04000200` | Sistema maestro de habilitación y banderas de interrupciones de hardware (IRQs). |

> [!TIP]
> Debido a que las direcciones (como `0x04000000`) son muy grandes para cargarse directamente en Thumb con la instrucción `store Rd = imm` (que solo acepta de 0 a 255), RIF incluye soporte para componer números altos iterativamente o apoyarse en el _Literal Pool_ con el plugin GBA.
