class _EndInstruction(Exception):
    """Señal interna de control de flujo para detener la compilación de la regla actual.

    Esta excepción es lanzada al procesar el comando DSL `end_instruction` para abortar
    el procesamiento de la línea inmediatamente.
    """
    
__all__ = ['_EndInstruction']