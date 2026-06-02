from rif.compiler.imports import *

_FIXED_EMIT_WIDTHS = {
    "cmbit": 4,
    "cbit": 8,
    "ccbit": 16,
    "cdbit": 32,
    "cebit": 64,
}


@dataclass
class _Runtime:
    """Estado de ejecución dinámico durante la compilación de una instrucción.

    Mantiene los enlaces de variables, la secuencia acumulada de bits emitidos,
    así como los placeholders y expresiones pendientes de resolución.
    """
    rule_name: str
    source: str
    bindings: dict[str, OperandValue]
    bits: BitBuffer | None = None
    bit_values: dict[str, str] | None = None
    placeholders: list[Placeholder] | None = None
    relocations: list[Relocation] | None = None
    expressions: list[Any] | None = None
    stack: list[str] | None = None
    base_offset_bits: int = 0
    labels: dict[str, int] | None = None
    section: str | None = None

    def __post_init__(self) -> None:
        if self.bits is None:
            self.bits = BitBuffer()
        if self.bit_values is None:
            self.bit_values = {}
        if self.placeholders is None:
            self.placeholders = []
        if self.relocations is None:
            self.relocations = []
        if self.expressions is None:
            self.expressions = []
        if self.stack is None:
            self.stack = []
        if self.labels is None:
            self.labels = {}

__all__ = ['_Runtime']