# Construcción de Instrucciones (API del Compilador)

En RIF, las instrucciones nativas o primitivas que se usan dentro de los bloques `.rules` no están hardcodeadas en el núcleo (Core) del compilador. En su lugar, el comportamiento semántico se define y expande a través de **Plugins**.

El núcleo del compilador lee el archivo fuente, tokeniza las líneas, y transfiere el control a los plugins correspondientes cada vez que encuentra la invocación de una instrucción. Para que tu plugin pueda analizar operandos, reportar fallos y emitir resultados, RIF proporciona una potente **Core API**.

> **Nota:** Directivas comunes como `need`, `emit`, `call`, `ON`, y `switch` no son parte del Core. Son simplemente plugins incluidos en el paquete `basics` que usan esta misma API para funcionar.

## Core API para Plugins

Todos los plugins que implementan instrucciones de RIF (típicamente definidos con la función `_start()` o `main()`) deben importar y usar los siguientes objetos del módulo `rif`.

### 1. `Line` (Línea de Análisis)

El objeto global `Line` contiene el estado actual de los tokens que el parser le pasó a la instrucción. Es la principal herramienta del plugin para consumir el código fuente de izquierda a derecha.

**Propiedades:**
- `Line.toks`: Lista de tokens restantes (strings) en la instrucción actual.
- `Line.elements`: Cantidad inicial total de tokens en la instrucción (incluyendo el nombre de la instrucción).
- `Line.line`: Número de línea en el archivo fuente original donde se invocó la instrucción.

**Métodos principales:**
- `Line.Advance()`: Remueve y devuelve el siguiente token en la lista. Retorna `None` si no hay más.
- `Line.Peek()`: Devuelve el siguiente token sin removerlo.
- `Line.expect(value)`: Si el siguiente token coincide con `value`, lo remueve y devuelve. Si no coincide, retorna `None` y no lo remueve.
- `Line.expects(*values)`: Verifica que los tokens restantes estén vacíos o coincidan solo con tokens irrelevantes. Arroja un error interno si quedaron tokens residuales inesperados que el plugin no procesó.
- `Line.Unpack(separator)`: Extrae y agrupa todos los tokens basándose en un separador indicado (ej. `","`), separando los tokens en múltiples listas sub-empaquetadas y limpiando completamente `Line.toks`.

### 2. `Err` (Reporte de Errores)

Si la sintaxis del usuario es incorrecta o un operando es inválido, el plugin **no debe** usar `raise Exception` ni detener el proceso bruscamente. En su lugar, debe instanciar y retornar directamente un objeto `Err`.

```python
from rif import Err

if Line.elements == 0:
    return Err("Faltan operandos. Se esperaba al menos un valor.")
```
El compilador capturará el objeto `Err` retornado por el plugin y formateará un mensaje de error elegante en la terminal (señalando la línea exacta donde ocurrió la falla y mostrando el contexto).

### 3. `Expr` (Expresión de Retorno)

Cuando el plugin finaliza de procesar una instrucción exitosamente, debe devolver un objeto `Expr` representando la semántica o el Código Intermedio (IR) generado por dicha instrucción.

```python
from rif import Expr

# Ejemplo: Emitiendo una estructura IR personalizada
return Expr(["mi_instruccion_ir", arg1, arg2])
```
Los elementos empaquetados dentro del `Expr` serán recogidos por la fase de **Codegen** (Generación de Código) del compilador para ser interpretados posteriormente en la fase de ensamblado de binarios.

### 4. `Operator` (Vinculación de Símbolos)

El objeto `Operator` (o `Operators`) permite guardar y vincular símbolos, tipos de datos y literales durante la evaluación de una regla. Es esencial si la instrucción necesita capturar variables u operandos (como hace `need`) para usarlos o validarlos más adelante.

- `Operator.Save(name, rule_name, valid_types, literal)`: Guarda un identificador dentro del contexto de una regla, indicando qué tipos son válidos para él.
- `Operator.Binding(name, rule_name)`: Recupera la información de un operador capturado previamente en la regla.
- `Operator.is_operator(name, rule_name)`: Verifica si un identificador existe como operador guardado, registro o símbolo en la memoria `.data`.

### 5. `RuleIndicator` (Contexto de Regla)

Proporciona contexto sobre la regla que se está procesando actualmente en la compilación.
- `RuleIndicator.current`: Devuelve el nombre de la regla padre actual como un `str` (o `None` si la instrucción fue invocada en el ámbito global fuera de un bloque `.rules`).

### 6. `TYPES_MAP` (Mapa de Tipos)

Diccionario global que contiene la resolución de todos los tipos definidos en la arquitectura (por ejemplo, tipos de variables creados por el usuario o secciones especiales). Es muy útil para validar si un token proporcionado es realmente un tipo válido registrado en la arquitectura.

---

## Ejemplo Completo de un Plugin

A continuación, un ejemplo real de cómo se integran estos objetos del compilador para crear una instrucción `my_inst`:

```python
from rif import Line, Err, Expr, Operator, RuleIndicator

def _start():
    # 1. Validación de operandos mínimos usando Line
    if Line.elements <= 1:
        return Err("La instrucción 'my_inst' requiere un operando explícito.")
    
    # 2. Descartar el token de la propia instrucción (el nombre del plugin)
    Line.Advance()
    
    # 3. Extraer el primer operando de forma segura
    operando = Line.Advance()
    
    # 4. Validar que no hayan quedado tokens basura adicionales al final de la línea
    Line.expects(" ", "\n")
    
    # 5. Lógica de negocio y vinculación:
    # Guardar el operando en el contexto de la regla actual como tipo "VALUE".
    Operator.Save(operando, RuleIndicator.current, valid_types=["VALUE"])
    
    # 6. Retornar la Expresión resultante al compilador (Abstract Syntax Tree)
    return Expr(["my_inst_ir", operando])
```

Al seguir esta API y arquitectura, los plugins se vuelven agnósticos a la sintaxis general del usuario, delegan correctamente los errores mediante `Err` y emiten expresiones robustas para la etapa de codegen.
