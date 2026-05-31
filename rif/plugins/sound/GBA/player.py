# GBA Sound hardware registers and constants
SOUNDCNT_L = 0x04000080
SOUNDCNT_H = 0x04000082
SOUNDCNT_X = 0x04000084
DSOUND_A   = 0x040000A0
DSOUND_B   = 0x040000A4

def get_ds_play_code(symbol: str, length: int, rate: int) -> str:
    """Genera código ensamblador ARM para reproducir un buffer PCM Direct Sound A en GBA.
    
    Calcula dinámicamente el valor de recarga del Timer 0 para la frecuencia especificada.
    """
    # GBA system clock frequency is 16.78 MHz (16777216 Hz)
    # Timer reload = 65536 - (16777216 / sample_rate)
    reload = 65536 - int(16777216 / rate)
    reload_hex = f"0x{reload:04X}"
    
    code = f"""; =========================================================================
; REPRODUCTOR DIRECT SOUND A (AUTO-GENERADO)
; Sonido: {symbol}
; Frecuencia: {rate} Hz
; Longitud: {length} bytes
; =========================================================================

play_{symbol}:
    ; 1. Habilitar el control maestro de sonido (SOUNDCNT_X)
    arm_mov_imm R0, 0x80
    arm_mov_imm R1, 0x04000080
    arm_strb R0, R1, 4

    ; 2. Configurar Direct Sound A (SOUNDCNT_H):
    ;    - Volumen al 100% (Bit 2 = 1)
    ;    - Salida izquierda y derecha habilitada (Bit 8 = 1, Bit 9 = 1)
    ;    - Usar Timer 0 (Bit 10 = 0)
    ;    - Reiniciar/Vaciar el FIFO (Bit 11 = 1)
    ;    Valor combinado: 0x0B04 -> arm_mov_imm acepta inmediatos comunes
    arm_mov_imm R0, 0x0B
    arm_dp_shift mov, R0, 0, R0, lsl, 8
    arm_add_imm R0, R0, 0x04
    arm_strh R0, R1, 2

    ; 3. Configurar el Timer 0 con el valor de recarga {reload_hex} ({reload})
    arm_mov_imm R0, {reload_hex}
    arm_mov_imm R1, 0x04000100
    arm_strh R0, R1, 0

    ; 4. Iniciar el Timer 0 (Habilitar bit 7 de control)
    arm_mov_imm R0, 0x80
    arm_strh R0, R1, 2

    arm_bx LR
"""
    return code
