# Registros

El ARM7TDMI tiene 16 registros de propósito general (R0-R15) y 2 de estado (CPSR/SPSR).
En modo Thumb, solo los registros bajos R0-R7 son accesibles en la mayoría de instrucciones.

## Registros de CPU

| Registro | Código (3 bits) | Uso en Thumb | Propósito                          |
|----------|-----------------|--------------|------------------------------------|
| R0       | 000             | ✓            | General purpose                    |
| R1       | 001             | ✓            | General purpose                    |
| R2       | 010             | ✓            | General purpose                    |
| R3       | 011             | ✓            | General purpose                    |
| R4       | 100             | ✓            | General purpose (callee-save)      |
| R5       | 101             | ✓            | General purpose (callee-save)      |
| R6       | 110             | ✓            | General purpose (callee-save)      |
| R7       | 111             | ✓            | General purpose (callee-save)      |
| R8       | 1000            | ✗            | Solo ARM (requiere instrucciones especiales) |
| R9-R12   | 1001-1100       | ✗            | Solo ARM                           |
| SP       | 1101            | ✓ (especial) | Stack Pointer — R13                |
| LR       | 1110            | ✓ (especial) | Link Register — R14 (return addr)  |
| PC       | 1111            | ✓ (especial) | Program Counter — R15              |

## Convención de llamada (APCS)

- `R0-R3`: parámetros / valor de retorno
- `R4-R7`: callee-saved (preservar antes de usar)
- `SP` (R13): Stack Pointer — siempre alineado a 4 bytes
- `LR` (R14): Link Register — guarda la dirección de retorno al hacer `call`
- `PC` (R15): Program Counter — contiene la dirección de la instrucción + 4

## Registros MMIO seleccionados

| Nombre   | Dirección  | Descripción                     |
|----------|------------|---------------------------------|
| DISPCNT  | 0x04000000 | Control de pantalla LCD         |
| DISPSTAT | 0x04000004 | Estado de pantalla (VBlank etc) |
| VCOUNT   | 0x04000006 | Línea vertical actual           |
| KEYINPUT | 0x04000130 | Estado de botones (active low)  |
| IME      | 0x04000208 | Habilitador maestro IRQ         |
| IE       | 0x04000200 | Interrupt Enable                |
| IF       | 0x04000202 | Interrupt Flag (limpiar con 1)  |

Para acceder a un registro MMIO desde Thumb:

```rif
store R0 = 0x00  ; valor a escribir
store R1 = 0x00  ; byte bajo de la dirección
store R2 = 0x00  ; byte alto de la dirección
; luego componer la dirección en un registro y usar strh
```
