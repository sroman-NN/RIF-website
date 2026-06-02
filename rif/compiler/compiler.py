from rif.compiler.imports import *
from rif.compiler.runtime import _Runtime
from rif.compiler.end_instruction import _EndInstruction

from rif.compiler import compile_at, conversors

class Compiler:
    """Compilador del set de instrucciones de RIF.

    Traduce líneas de código ensamblador que coinciden con las reglas definidas en el
    archivo `.pack`, aplicando semántica DSL y delegación a plugins dinámicos para
    generar bits empaquetados coherentes.
    """
    
    def __init__(self, program: Program):
        """Inicializa el compilador a partir de un programa RIF previamente parseado.

        Args:
            program: Estructura AST de la definición del ISA cargada en memoria.
        """
        self.program = program
        with GLOBAL_STATE_LOCK:
            self.config = parse_packer_config(program)
            self._type_map = dict(program.type_map)
            compile_at.activate_type_map(self)
            run_precompilers(program, self.config)
            self.plugins = load_plugins(program, self.config)
            Operators.set_program(program)
            Operators.saved_operators.clear()
            Operators.saved_operators.update({key: list(value) for key, value in program.operator_saved.items()})
            Operators.bindings.clear()
            Operators.bindings.update({key: dict(value) for key, value in program.operator_bindings.items()})
            self._saved_operators = {key: list(value) for key, value in program.operator_saved.items()}
            self._operator_bindings = {key: dict(value) for key, value in program.operator_bindings.items()}
        self.labels: dict[str, int] = {}
        from rif.source_reader import SourceReader
        self.source_reader = SourceReader(program, self.config)

    @classmethod
    def from_file(cls, source_path: str | Path) -> "Compiler":
        """Crea una instancia del compilador a partir de la ruta de un archivo .pack.

        Args:
            source_path: Ruta al archivo que contiene la definición del ISA.

        Returns:
            Una instancia configurada del Compilador.
        """
        path = Path(source_path)
        if path.suffix == ".pack":
            from rif.package_packer import PackagePacker
            program = PackagePacker(path).pack(write=False).program
        else:
            program = Parser(path.read_text(encoding="utf-8"), path).parse()
        return cls(program)

    def compile_line(self, source: str) -> CompileResult:
        """Compila una única línea de instrucción de lenguaje ensamblador RIF.

        Args:
            source: Línea de texto con la instrucción a compilar.

        Returns:
            Un objeto CompileResult que contiene los bits generados o placeholders diferidos.
        """
        with GLOBAL_STATE_LOCK:
            return compile_at.compile_line_at(self, source, 0, self.labels)

    def compile_lines(self, source: str) -> list[CompileResult]:
        """Compila múltiples líneas de ensamblador RIF en una sola pasada lógica.

        Primero realiza un análisis preliminar de etiquetas y definiciones de datos
        para resolver referencias hacia adelante, y luego compila cada instrucción
        de forma definitiva.

        Args:
            source: Cadena multilínea con el código ensamblador.

        Returns:
            Lista de resultados de compilación para cada instrucción válida.
        """
        with GLOBAL_STATE_LOCK:
            return compile_at.compile_lines_locked(self, source)


    def compile_bytes(self, source: str) -> bytes:
        """Compila código ensamblador multilínea directamente a una secuencia de bytes empaquetados.

        Lanza PackError si existen placeholders sin resolver (como etiquetas o variables libres).

        Args:
            source: Código ensamblador.

        Returns:
            Representación binaria final en bytes.
        """
        results = self.compile_lines(source)
        missing = [ph.name for result in results for ph in result.placeholders]
        if missing:
            raise PackError("no se puede emitir bytes finales con placeholders: " + ", ".join(missing))
        bits = "".join(result.bits for result in results if result.rule_name not in {"stack", "heap"})
        if len(bits) % 8 != 0:
            raise PackError(f"la emisión final no está alineada a byte: {len(bits)} bits")
        return conversors.bits_to_bytes(bits)

    
def compile_instruction(program_or_path: Program | str | Path, source: str) -> CompileResult:
    """Función de conveniencia para compilar una sola instrucción.

    Args:
        program_or_path: Un objeto Program pre-parseado, o la ruta de archivo .pack.
        source: Línea de instrucción ensamblador.

    Returns:
        Objeto CompileResult con el binario generado y metadatos.
    """
    if isinstance(program_or_path, Program):
        compiler = Compiler(program_or_path)
    else:
        compiler = Compiler.from_file(program_or_path)
    return compiler.compile_line(source)

