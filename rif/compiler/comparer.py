from rif.compiler.imports import *

def is_label_name(value: str) -> bool:
    """Valida si la cadena proporcionada cumple con las reglas sintácticas para nombres de etiquetas.

    Args:
        value: Cadena a validar.

    Returns:
        True si el nombre es válido, False en caso contrario.
    """
    if not value:
        return False
    if not (value[0].isalpha() or value[0] == "_"):
        return False
    return all(ch.isalnum() or ch in "_-" for ch in value)



def type_allows_string(type_def: TypeDefinition, program: Program) -> bool:
    """Determina si una definición de tipo específica admite la asignación directa de strings literales.

    Args:
        type_def: Estructura del tipo a evaluar.
        program: El AST de configuración global RIF.

    Returns:
        True si admite inicialización con string, False en caso contrario.
    """
    supported = program.data_definition.options.get("supportstring", [])
    if type_def.name in {str(item) for item in supported}:
        return True
    return str(type_def.values.get("string", "")).strip().lower() not in {"", "no", "false", "0"}


def truthy(value: Any) -> bool:
    """Evalúa de forma robusta la veracidad de un valor procedente de las tablas o configuración.

    Args:
        value: Objeto a evaluar.

    Returns:
        True o False.
    """
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "si", "sí", "on"}
