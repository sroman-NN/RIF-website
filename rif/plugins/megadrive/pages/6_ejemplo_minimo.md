# Ejemplo Mínimo de Código (Mega Drive)

Este es un ejemplo de estructura base en lenguaje ensamblador para Mega Drive usando el motor RIF. El código inicializa un programa básico usando los registros M68k para establecer un bucle finito y un bucle infinito al terminar. 

> *Nota: Inicializar los registros visuales del VDP para renderizar una imagen requiere aproximadamente 40 opcodes de preparación (limpiar la VRAM interna, definir los registros del VDP e instalar paletas), por lo que este ejemplo ilustra la arquitectura de software pura.*

Crea un archivo llamado `main.mdasm` dentro de un directorio de tu proyecto:

```rif
; ----------------------------------------------------
; 1. Seccion de Vectores e inicialización de hardware
; ----------------------------------------------------
.section rom
    ; Tabla de interrupciones apuntando al inicio 'start'
    md_vectors start
    
    ; Cabecera oficial SEGA Genesis
    md_header

; ----------------------------------------------------
; 2. Punto de entrada (Comienza ejecucion nativa M68k)
; ----------------------------------------------------
start:
    ; moveq: Poner valor 0 rapido en el registro D0 (Limpia D0)
    moveq 0, D0
    
    ; moveq: Poner 10 en D1 (Límite del contador)
    moveq 10, D1

; ----------------------------------------------------
; 3. Bucle local
; ----------------------------------------------------
loop:
    ; Sumar 1 al valor contenido en D0 (Word)
    add_w_imm_d 1, D0
    
    ; Comparar D0 contra nuestro valor maximo (Word contra D1)
    ; (No hay cmp de registro puro directo en la base rule del pack,
    ;  podemos comparar inmediato, o en este ejemplo usar imm puro)
    cmp_w_imm_d 10, D0
    
    ; Si el resultado no fue igual (Z=0), vuelve a la etiqueta loop
    bne loop

; ----------------------------------------------------
; 4. Bucle infinito para finalizar ejecucion (Trampa)
; ----------------------------------------------------
done:
    ; Salta incondicionalmente a la etiqueta "done"
    bra done

; ----------------------------------------------------
; 5. Ajuste dinamico de tamano de cartucho
; ----------------------------------------------------
    ; Esta instruccion rellenará el resto de la ROM hasta alcanzar 
    ; limites válidos (ej. un cartucho de 128KB, 256KB, etc).
    md_rompad
```

## Compilación y Ejecución en Emulador

Para construir y ver este ejemplo, asumiendo que guardaste `main.mdasm` en la carpeta `my_genesis_game`:

1. Genera la ROM en formato Binario (.bin) puro para Mega Drive:
   ```bash
   python -m rif build my_genesis_game --plugin megadrive --name megadrive_pack
   ```

2. Ejecútalo automáticamente instalando un emulador en RIF:
   ```bash
   python -m rif -pcli megadrive run my_genesis_game/my_genesis_game.bin -nd
   ```

El emulador arrancará mostrando una pantalla negra sin imagen de error roja o blanca, confirmando que la cabecera `md_header` y la tabla `md_vectors` fueron válidas, y que el procesador está exitosamente ejecutando nuestro bucle infinito `done:` de forma estable.
