# Uso

El proyecto de ejemplo genera una ROM de 4 KiB. La seccion `rom` usa `voffset 0xF000`, por lo que las relocaciones absolutas de 16 bits apuntan al mapa de memoria que espera el 6502 dentro de Stella.

`rompad_to_vectors` rellena hasta `0x0FFA` y `vectors start` escribe NMI, RESET e IRQ. El relleno se apoya en la primitiva interna `pad_to`, no en offsets hardcodeados del linker.
