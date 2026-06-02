
    // Diccionario estático de Fallback (Soporta file:// CORS sin problemas)
    const docs = {
      "importar_plugins": "# Importar Plugins y Orden\n\nBajo la cabecera `.pack`, puedes declarar librer\u00edas externas o plugins para extender las funcionalidades del compilador.\n\n## Declaraci\u00f3n\nLa palabra clave `plugin` indicar\u00e1 al compilador la necesidad de buscar la ruta del plugin y cargar sus reglas l\u00e9xicas.\n\n```rif\n.pack\nplugin \"basics\"\nplugin \"gba\"\n```\n\nLos plugins son cargados en el orden exacto en el que son declarados. Si el c\u00f3digo fuente hace uso de una sintaxis implementada en un plugin, RIF sabr\u00e1 c\u00f3mo resolverla de inmediato.\n\n## Control de Colisiones (`pluginsymbolorder`)\n\nSi trabajas con m\u00faltiples plugins, es posible que algunas palabras clave o mnem\u00f3nicos choquen (por ejemplo, dos plugins definiendo `mov`). Para controlar c\u00f3mo reacciona RIF ante estos escenarios, existe la directiva `pluginsymbolorder`.\n\n```rif\n.pack\nplugin \"basics\"\nplugin \"gba\"\npluginsymbolorder 0\n```\n\nValores soportados:\n- **`0` (Estricto)**: RIF detendr\u00e1 la compilaci\u00f3n lanzando un error si se encuentran nombres o funciones repetidas entre plugins. Tolerancia cero.\n- **`2` (Sobrescritura *Bottom-Up*)**: (Por defecto) Permite hacer un \"merge\", priorizando el \u00faltimo plugin importado. Las declaraciones ubicadas m\u00e1s abajo reemplazar\u00e1n a las de arriba en caso de existir choques.\n- **`3` (Privilegio *Top-Down*)**: RIF ignorar\u00e1 los m\u00e9todos repetidos de los plugins subsecuentes. El primer plugin que declare el m\u00e9todo es el que se preservar\u00e1.\n",
      "linker_1": "# Linker I: Archivos Fracturados\n\nEl bloque `linker:` te otorga un control granular sobre c\u00f3mo el ensamblador agrupa e ingiere el c\u00f3digo fuente distribuido en una jerarqu\u00eda de archivos.\n\n```rif\nlinker:\n    filesystem 1 \n    sectexec .rom \n    sectneed .header \n    sectneed .data \n    sectopt  .bss  \n```\n\n## Modo Fracturado (`filesystem 1`)\n\nCuando `filesystem` se declara en `1`, RIF deja de buscar un \u00fanico archivo y comienza a buscar un ensamblado \"fracturado\" o esparcido a lo largo de varios documentos seg\u00fan las secciones estipuladas. Esto permite una programaci\u00f3n m\u00e1s organizada (por ejemplo, separar el c\u00f3digo de lectura de datos de la l\u00f3gica del ROM principal).\n\n### Regla de Construcci\u00f3n de Nombres\n\nLas diferentes secciones exigen una nomenclatura de archivo **estricta** basada en lo configurado en la cabecera `packer:`.\n\nLa sintaxis del nombre de archivo a buscar por el compilador para cada secci\u00f3n fragmentada es: `{entryfilename}{seccion}{ext}`.\n- Ejemplo para `.data`: `main.data.gbasm`\n- Ejemplo para `.header`: `main.header.gbasm`\n\n### Punto de Entrada Ejecutable (`sectexec`)\nDeclara la secci\u00f3n maestra ejecutable. Para esta secci\u00f3n, la regla de nombre se acorta y ser\u00e1 el archivo base: `{entryfilename}{ext}`. \n- Ejemplo: `main.gbasm`. \n- Si un usuario compila el c\u00f3digo, la directiva `.section` (en este caso `.rom`) ser\u00e1 inyectada autom\u00e1ticamente y validada.\n\n### Secciones Requeridas y Opcionales\n- `sectneed`: Indica que RIF **debe obligatoriamente** encontrar y compilar un archivo para dicha secci\u00f3n (siguiendo la regla de nombre). Si el archivo no se encuentra, la compilaci\u00f3n se abortar\u00e1.\n- `sectopt`: Informa al vinculador que busque un archivo con dicha secci\u00f3n, pero de no encontrarlo, omitir\u00e1 el proceso y seguir\u00e1 adelante de forma segura sin lanzar errores.\n\n### Inyecci\u00f3n de Contexto\nAnotar una secci\u00f3n de fractura inyecta impl\u00edcitamente un cambio a esa secci\u00f3n de la memoria en RIF. Es decir, t\u00fa como desarrollador ya no necesitas escribir la declaraci\u00f3n `.seccion_x` al inicio del archivo fracturado; el propio Linker de RIF sabe a qu\u00e9 secci\u00f3n de la memoria pertenece ese c\u00f3digo simplemente por su nombre de archivo, mitigando la duplicaci\u00f3n en el c\u00f3digo base.\n",
      "packer_1": "# Packer I: Configuraci\u00f3n Principal\n\nEl bloque `packer:` es la secci\u00f3n responsable de informarle al compilador d\u00f3nde buscar, bajo qu\u00e9 nombre, y con qu\u00e9 extensiones esperar el archivo de c\u00f3digo fuente del proyecto.\n\n```rif\npacker:\n    entryfilename \"main\"\n    ext \".gbasm\"\n    filesystem 0\n```\n\n## Propiedades Fundamentales\n\n### `entryfilename`\nEspecifica el nombre base del archivo principal del programa que el compilador debe ubicar. Por defecto, si esta instrucci\u00f3n se omite, RIF buscar\u00e1 el nombre `main`.\n\n### `ext`\nObligatorio. Define la extensi\u00f3n del archivo fuente (por ejemplo, `\".gbasm\"`). Si el desarrollador olvida proporcionar la extensi\u00f3n, RIF podr\u00eda fallar al intentar leer un archivo sin ninguna terminaci\u00f3n de formato en el directorio.\n\n### `filesystem`\nPor defecto suele ser `0`, lo que le indica a RIF que toda la l\u00f3gica de programaci\u00f3n vive en un **solo archivo** ininterrumpido (por ejemplo: `main.gbasm`). Si se asigna el valor `1`, habilita el motor fragmentador para buscar archivos separados l\u00f3gicamente por secciones.\n",
      "packer_2_y_errores": "# Packer II y Errores\n\nEl empaquetador tiene otras declaraciones avanzadas, destinadas a la configuraci\u00f3n de salida o de validaci\u00f3n de sintaxis estricta de las secciones.\n\n## Declarando el Entorno (`definesec`)\n\nEl compilador de RIF es altamente estricto. Por defecto, si el compilador est\u00e1 ejecutando tu c\u00f3digo fuente y encuentra una llamada a un salto de secci\u00f3n (por ejemplo, escribir `.rom` como secci\u00f3n para el c\u00f3digo), el sistema levantar\u00e1 un error que se ve as\u00ed:\n\n`[ CODE ] secci\u00f3n de fuente desconocida \".rom\" en l\u00ednea 1`\n\nEsto ocurre porque RIF no tiene conocimiento nativo de cu\u00e1les son las secciones legales para tu ISA. Para prevenir esto, se deben usar variables `definesec`:\n\n```rif\npacker:\n    definesec .rom\n    definesec .data\n```\n\n> **Nota:** Al usar `linker: filesystem 1` con secciones declaradas expl\u00edcitamente (`sectneed`, `sectopt`), RIF autorregistra las secciones, haci\u00e9ndolas \"conocidas\" y anulando autom\u00e1ticamente este error sin necesidad de usar `definesec`.\n\n## Salida y Compilados\n\nOpcionalmente el empaquetador puede encargarse de definir el nombre expl\u00edcito del archivo de volcado final, y su extensi\u00f3n para evitar choques con el c\u00f3digo de entrada:\n\n- `outext \".bin\"`: La extensi\u00f3n final bajo la cual RIF escribir\u00e1 los binarios por defecto.\n- `output \"juego.bin\"`: Fuerza el guardado de la memoria hacia un nombre espec\u00edfico al compilar.\n",
      "crear_un_pack": "# Crear un Pack\n\nLos archivos `.pack` son el coraz\u00f3n de la configuraci\u00f3n de tu proyecto en RIF (Retargetable ISA Foundry). Act\u00faan como el \"manifiesto\" de compilaci\u00f3n que indica al ensamblador c\u00f3mo interpretar el c\u00f3digo fuente, qu\u00e9 reglas aplicar, qu\u00e9 plugins importar y c\u00f3mo estructurar el empaquetado final.\n\n## Estructura B\u00e1sica\n\nUn archivo `.pack` es un archivo de texto simple (con extensi\u00f3n `.pack`). Utiliza un lenguaje de configuraci\u00f3n propietario, limpio y f\u00e1cil de leer.\n\n```rif\ncomment ;\nblocks :\ntable-separator |\nencoding utf-8\n\n.pack\n\npacker:\n    entryfilename \"main\"\n    ext \".gbasm\"\n```\n\n## Secciones Principales\n- **Cabecera global**: Configura la sintaxis general del propio lector (ej. c\u00f3mo son los comentarios o bloques).\n- **.pack**: El punto de entrada principal para cargar definiciones globales.\n- **packer:**: Configura la recolecci\u00f3n, nombre del archivo de origen y comportamiento de lectura.\n- **linker:**: (Opcional) Configura el ensamblado de c\u00f3digo fragmentado en diferentes archivos seg\u00fan sus secciones.\n\nPara que RIF funcione, tu proyecto debe tener o heredar al menos una configuraci\u00f3n de Pack v\u00e1lida.\n",
      "usar_pack_plugin": "# Usar el Pack de un Plugin Espec\u00edfico\n\nEn muchos escenarios, es redundante re-crear un archivo `.pack` para un ensamblador que ya existe. Por ello, si compilas un proyecto que **carece** de archivo `.pack`, RIF puede usar la configuraci\u00f3n de un plugin por defecto.\n\n## Par\u00e1metro por L\u00ednea de Comandos\nSi tu directorio de proyecto no tiene `.pack`, puedes forzar la herencia de un entorno completo a trav\u00e9s de los argumentos del CLI:\n\n```bash\npython -m rif.cli build mi_proyecto --pack gba\n```\n\nEn este caso, RIF ir\u00e1 al directorio de instalaci\u00f3n de plugins (por ejemplo, `plugins/gba/pack/gba.pack`), cargar\u00e1 toda la estructura del sistema (incluidas sus macros, definiciones e importaciones) y se comportar\u00e1 como si el archivo `.pack` residiera en tu propia carpeta `mi_proyecto/`.\n\nEsta funcionalidad es ideal para programar r\u00e1pidamente sin tener que configurar el pipeline desde cero cada vez.\n",
      "usar_pack_propio": "# Usar el Pack Propio\n\nPara que RIF tome tu archivo `.pack` y reaccione a la configuraci\u00f3n, debes colocarlo en la ra\u00edz de la carpeta de tu proyecto. \n\n## Estructura Recomendada\n\nUna arquitectura de proyecto normal de RIF se ve as\u00ed:\n\n```text\nmi_proyecto/\n\u251c\u2500\u2500 mi_proyecto.pack\n\u2514\u2500\u2500 code/\n    \u2514\u2500\u2500 main.gbasm\n```\n\nTambi\u00e9n es v\u00e1lido omitir la carpeta `code/` y poner todo al mismo nivel, aunque para proyectos grandes recomendamos tener los archivos fuente dentro de la carpeta `code`.\n\n```text\nmi_proyecto/\n\u251c\u2500\u2500 mi_proyecto.pack\n\u2514\u2500\u2500 main.gbasm\n```\n\n## Reconocimiento Autom\u00e1tico\n\nAl ejecutar el comando de compilaci\u00f3n:\n```bash\npython -m rif.cli build mi_proyecto\n```\nEl compilador RIF escanear\u00e1 autom\u00e1ticamente el directorio ra\u00edz `mi_proyecto/` buscando cualquier archivo que termine en `.pack`. **Este archivo se convertir\u00e1 en la configuraci\u00f3n local absoluta** del compilador para dicho proyecto, dictando qu\u00e9 archivos leer y qu\u00e9 plugins usar.\n",

      "que_es_rif": `# ¿Qué es RIF?

RIF es un generador **retargetable** de arquitectura diseñada para definir ensambladores, empaquetadores y linkers mediante paquetes de configuración (\`.pack\`) y plugins dinámicos de Python.

El core interno del compilador se mantiene agnóstico a cualquier arquitectura concreta de hardware. No sabe qué es x86, ARM o RISC-V. En su lugar, lee estructuras estructuradas, procesa expresiones de bits genéricas, asocia placeholders, define regiones de memoria y delega la lógica semántica de instrucción directamente a plugins extensibles.

> [!NOTE]
> La modularidad es el núcleo de RIF: una arquitectura de hardware completamente nueva puede ser incorporada al compilador a través de descriptores RIF y plugins, sin realizar modificaciones en la base de código del compilador.

Un paquete RIF describe:

* **Mapeo de mundo y configuración** global del target.
* **Declaración de tipos** y mapeo de tablas (como registros o flags).
* **Especificación de reglas** para instrucciones.
* **Organización de memoria**, cabeceras de salida y secciones de binario.
* **Plugins externos** de Python registrados.`,

      "como_se_usa": `# ¿Cómo se usa?

Para trabajar con RIF, defines la arquitectura en un archivo descriptor \`.pack\`, configuras tus plugins en Python y ejecutas el compilador de comandos.

### Ejemplo de Compilación Rápida

Puedes compilar una única instrucción usando un archivo de paquete ya listo:

\`\`\`bash
python -m rif compile store.amd64.pack "byte 0xf"
\`\`\`

**Salida en consola:**

\`\`\`text
rule=byte
bits=00001111
hex=0f
\`\`\`

> [!TIP]
> Si deseas ensamblar un código de varias líneas de instrucciones consecutivas y estructurar las secciones resultantes, usa el comando \`build\`:

\`\`\`bash
python -m rif build store.amd64.pack --source-text "byte 0x2a"
\`\`\`

### Ayuda en Consola
El compilador integra un potente visor de ayuda integrada. Puedes ver temas de ayuda desde tu terminal:

\`\`\`bash
# Listar todos los temas de ayuda disponibles
python -m rif help

# Leer un documento específico directamente en consola
python -m rif help instrucciones

# Abrir este espectacular portal visual interactivo en el navegador
python -m rif help --open
\`\`\`
`,

      "version_actual": `# Version actual

### RIF 0.0.3 Semi Stable

Esta version consolida el compilador, linker, sistema de plugins, CLI y soporte VS Code/VSIX.

**Nucleo estable:**

- Lexer configurable por pack (comment, separator, block, encoding)
- Parser de archivos \`.pack\` con soporte de secciones \`.regs\`, \`.data\`, \`.rules\`, \`.memory\`, \`.sections\`, \`.types\`, \`.headers\`, \`.words\`
- Compilador de reglas con resolución de operandos, placeholders y etiquetas cruzadas
- Linker con soporte de secciones \`nobits\`, alineación, padding, offsets virtuales/físicos
- Fillables: expansión de \`@nombre\` antes de compilar, cargados desde \`fillables.py\` de cada plugin
- CLI unificada: \`lex\`, \`parse\`, \`pack\`, \`link\`, \`compile\`, \`build\`, \`table\`, \`plug\`, \`list\`, \`packs\`, \`clear\`, \`zip\`, \`help\`
- Sistema de plugins: carga dinámica desde \`plugins/\` local o desde el directorio interno de RIF
- Plugin CLI: \`rif -pcli <plugin>\` delega a \`cli.py\` de cada plugin
- Constructor VS Code/VSIX: \`rif compile --vscode\`
- Instalador VSIX: \`rif install --vscode\`

> [!IMPORTANT]
> La API de plugins y las palabras clave del compilador pueden cambiar en versiones futuras, pero el flujo principal ya esta en estado Semi Stable.`,

      "instrucciones": `# Construcción de Instrucciones (API del Compilador)

En RIF, las instrucciones nativas o primitivas que se usan dentro de los bloques \`.rules\` no están hardcodeadas en el núcleo (Core) del compilador. En su lugar, el comportamiento semántico se define y expande a través de **Plugins**.

El núcleo del compilador lee el archivo fuente, tokeniza las líneas, y transfiere el control a los plugins correspondientes cada vez que encuentra la invocación de una instrucción. Para que tu plugin pueda analizar operandos, reportar fallos y emitir resultados, RIF proporciona una potente **Core API**.

> **Nota:** Directivas comunes como \`need\`, \`emit\`, \`call\`, \`ON\`, y \`switch\` no son parte del Core. Son simplemente plugins incluidos en el paquete \`basics\` que usan esta misma API para funcionar.

## Core API para Plugins

Todos los plugins que implementan instrucciones de RIF (típicamente definidos con la función \`_start()\` o \`main()\`) deben importar y usar los siguientes objetos del módulo \`rif\`.

### 1. \`Line\` (Línea de Análisis)

El objeto global \`Line\` contiene el estado actual de los tokens que el parser le pasó a la instrucción. Es la principal herramienta del plugin para consumir el código fuente de izquierda a derecha.

**Propiedades:**
- \`Line.toks\`: Lista de tokens restantes (strings) en la instrucción actual.
- \`Line.elements\`: Cantidad inicial total de tokens en la instrucción (incluyendo el nombre de la instrucción).
- \`Line.line\`: Número de línea en el archivo fuente original donde se invocó la instrucción.

**Métodos principales:**
- \`Line.Advance()\`: Remueve y devuelve el siguiente token en la lista. Retorna \`None\` si no hay más.
- \`Line.Peek()\`: Devuelve el siguiente token sin removerlo.
- \`Line.expect(value)\`: Si el siguiente token coincide con \`value\`, lo remueve y devuelve. Si no coincide, retorna \`None\` y no lo remueve.
- \`Line.expects(*values)\`: Verifica que los tokens restantes estén vacíos o coincidan solo con tokens irrelevantes. Arroja un error interno si quedaron tokens residuales inesperados que el plugin no procesó.
- \`Line.Unpack(separator)\`: Extrae y agrupa todos los tokens basándose en un separador indicado (ej. \`","\`), separando los tokens en múltiples listas sub-empaquetadas y limpiando completamente \`Line.toks\`.

### 2. \`Err\` (Reporte de Errores)

Si la sintaxis del usuario es incorrecta o un operando es inválido, el plugin **no debe** usar \`raise Exception\` ni detener el proceso bruscamente. En su lugar, debe instanciar y retornar directamente un objeto \`Err\`.

\`\`\`python
from rif import Err

if Line.elements == 0:
    return Err("Faltan operandos. Se esperaba al menos un valor.")
\`\`\`
El compilador capturará el objeto \`Err\` retornado por el plugin y formateará un mensaje de error elegante en la terminal (señalando la línea exacta donde ocurrió la falla y mostrando el contexto).

### 3. \`Expr\` (Expresión de Retorno)

Cuando el plugin finaliza de procesar una instrucción exitosamente, debe devolver un objeto \`Expr\` representando la semántica o el Código Intermedio (IR) generado por dicha instrucción.

\`\`\`python
from rif import Expr

# Ejemplo: Emitiendo una estructura IR personalizada
return Expr(["mi_instruccion_ir", arg1, arg2])
\`\`\`
Los elementos empaquetados dentro del \`Expr\` serán recogidos por la fase de **Codegen** (Generación de Código) del compilador para ser interpretados posteriormente en la fase de ensamblado de binarios.

### 4. \`Operator\` (Vinculación de Símbolos)

El objeto \`Operator\` (o \`Operators\`) permite guardar y vincular símbolos, tipos de datos y literales durante la evaluación de una regla. Es esencial si la instrucción necesita capturar variables u operandos (como hace \`need\`) para usarlos o validarlos más adelante.

- \`Operator.Save(name, rule_name, valid_types, literal)\`: Guarda un identificador dentro del contexto de una regla, indicando qué tipos son válidos para él.
- \`Operator.Binding(name, rule_name)\`: Recupera la información de un operador capturado previamente en la regla.
- \`Operator.is_operator(name, rule_name)\`: Verifica si un identificador existe como operador guardado, registro o símbolo en la memoria \`.data\`.

### 5. \`RuleIndicator\` (Contexto de Regla)

Proporciona contexto sobre la regla que se está procesando actualmente en la compilación.
- \`RuleIndicator.current\`: Devuelve el nombre de la regla padre actual como un \`str\` (o \`None\` si la instrucción fue invocada en el ámbito global fuera de un bloque \`.rules\`).

### 6. \`TYPES_MAP\` (Mapa de Tipos)

Diccionario global que contiene la resolución de todos los tipos definidos en la arquitectura (por ejemplo, tipos de variables creados por el usuario o secciones especiales). Es muy útil para validar si un token proporcionado es realmente un tipo válido registrado en la arquitectura.

---

## Ejemplo Completo de un Plugin

A continuación, un ejemplo real de cómo se integran estos objetos del compilador para crear una instrucción \`my_inst\`:

\`\`\`python
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
    Line.expects(" ", "\\n")
    
    # 5. Lógica de negocio y vinculación:
    # Guardar el operando en el contexto de la regla actual como tipo "VALUE".
    Operator.Save(operando, RuleIndicator.current, valid_types=["VALUE"])
    
    # 6. Retornar la Expresión resultante al compilador (Abstract Syntax Tree)
    return Expr(["my_inst_ir", operando])
\`\`\`

Al seguir esta API y arquitectura, los plugins se vuelven agnósticos a la sintaxis general del usuario, delegan correctamente los errores mediante \`Err\` y emiten expresiones robustas para la etapa de codegen.`,

      "tipos": `# Sistema de Tipos y Lógica

En RIF, cada operando capturado por directivas (como \`need\` del plugin \`basics\`) o evaluado por las instrucciones nativas debe coincidir con una firma de tipo válida. El compilador maneja **Tipos Primitivos** (integrados en el núcleo) y **Tipos Dinámicos** (definidos por tu arquitectura).

## 1. Tipos Primitivos (Built-in)

Estos tipos están siempre disponibles de manera transparente, independientemente de la configuración del archivo \`.pack\`.

- **\`VALUE\`**: Representa cualquier constante entera, hexadecimal (\`0x...\`), binaria (\`0b...\`), octal, y los valores literales inmediatos (\`imm\`). El compilador procesa el token aritméticamente y calcula su ancho binario exacto en tiempo de ensamblado.
- **\`SYMBOL\`**: Un identificador o puntero a una etiqueta de datos. Generalmente apunta a una región estática de memoria como \`.data\`, \`.rodata\` o a una posición dentro de la imagen física.
- **\`LABEL\`**: Identificador utilizado específicamente para referencias de flujos de control o direcciones ejecutables (como sub-rutinas, ramas o posiciones de salto relativo).
- **\`TYPE\`**: Una referencia hacia un alias o una primitiva de tipo de dato configurado explícitamente en la sección \`.types\`.
- **\`STACK\`, \`HEAP\`, \`MEMORY\`**: Alias semánticos nativos diseñados para facilitar la representación en memoria y diferenciar visualmente los punteros hacia pila y montículo.

## 2. Tipos Dinámicos de Arquitectura

El núcleo del compilador se inyecta dinámicamente con tipos adicionales a medida que parsea las tablas y configuraciones del archivo \`.pack\`:

- **\`REG\`**: Este tipo es registrado automáticamente cuando defines tu tabla de registros ISA en la sección \`.regs\`. Si un plugin invoca una captura de un \`REG\`, el compilador validará iterativamente si el token ingresado existe en la columna \`NAME\` o es un \`alias\` válido de la tabla \`.regs\` activa.
- **\`SREG\` (Sub-Registros)**: Un tipo derivado y manejado internamente (mapeado hacia \`.regs.subs\`) que permite al motor de compilación identificar si el programador especificó un registro "hijo" (fraccionario) comprobando jerárquicamente su compatibilidad con el registro padre subyacente.

## 3. Tipos Basados en Definiciones de Tablas (\`TYPES_MAP\`)

Aparte de los integrados, tú puedes definir tus propios esquemas tipados en la sección \`.types\` de tu paquete. 
Si el diseñador de la arquitectura o lenguaje permite declarar campos personalizados como \`i8\`, \`u32\` o \`float16\`, estos se incorporan estructuralmente de forma global en RIF a través del diccionario general de evaluación \`TYPES_MAP\`.

Adicionalmente, las llamadas que interceden sobre secciones usando un punto como prefijo (tales como \`.regs.subs\`, \`.rom\`, \`.data\`, o \`.bss\`) también operan en RIF como tipos formales. Esto le permite al objeto \`Operator\` aislar en qué ámbito de memoria o de variables reside un parámetro.

## 4. Lógica de Evaluación y Binding

Cuando el intérprete o un plugin captura una instrucción usando \`need\` (por ejemplo: \`need VALUE, imm\`), el motor interno orquesta el siguiente flujo:

1. **Resolución de Referencia**: RIF consulta primero si la cadena literal proporcionada existe dentro de \`TYPES_MAP\` (priorizando los tipos creados localmente).
2. **Fallback Primitivo**: De no ser hallado, intenta equiparar el token a las constantes léxicas nativas (\`_BUILTIN_TYPES\`).
3. **Mapeo Dimensional**: Si la instrucción capturada exige un registro o componente, RIF inspecciona la meta-tabla (\`.regs\`, o \`.vars\`) para localizar los metadatos y el tamaño binario enlazado a ese identificador.
4. **Resguardo (Binding)**: Si existe concordancia entre el tipo real del elemento escrito por el usuario y el tipo pedido por el analizador, se genera un \`Binding\` transparente incrustado a través del objeto \`Operator\`. En caso contrario, el escáner declina la regla en caliente y arroja un error estructurado, alertando semánticamente: *"Se esperaba X tipo, pero se recibió Y"*.`,

      "flujos_on_switch": `# Flujos ON y Switch

RIF incluye mecanismos de control condicional integrados en el lenguaje para evitar la necesidad de escribir plugins complejos para bifurcaciones simples.

### Bloques Condicionales ON y OFF

Un bloque \`ON\` evalúa una expresión lógica y procesa sus sentencias hijas si es verdadera. Si se incluye una rama de negación \`OFF\`, ésta se procesa si la evaluación resulta falsa.

\`\`\`rif
rule:
    ON imm.size == 8:
        emit imm.binary
    OFF:
        zext OUT, imm.binary, 8
        emit OUT
\`\`\`

**Operaciones soportadas en condiciones:**
* Literales lógicos de estado: \`true\`, \`false\`, \`on\`, \`off\`.
* Operadores de comparación estándar: \`==\`, \`!=\`, \`<\`, \`<= \`, \`>\`, \`>=\`.
* Propiedades de operandos o variables: \`op.bits\`, \`reg.binary\`, \`imm.size\`.

### Selección por Casos Switch

El bloque \`switch\` evalúa una variable y busca correspondencia secuencial en bloques \`case\`:

\`\`\`rif
rule:
    switch op.PRIVTYPE:
        case "symbol":
            emit 00000000
        case "register":
            emit 11111111
\`\`\`

> [!WARNING]
> Si una expresión lógica de condición involucra un símbolo o placeholder que aún no ha sido enlazado (por ejemplo, una etiqueta externa en la fase de ensamblado), RIF suspende la evaluación condicional y la registra como un placeholder pendiente para que el linker la evalúe en una fase posterior.`,

      "tablas_y_secciones": `# Tablas y Secciones

Los archivos RIF de paquete organizan sus datos en secciones temáticas precedidas por un punto (\`.nombre_seccion\`).

Dentro de muchas de estas secciones se utilizan tablas Markdown para delimitar campos ordenados por registros o metadatos de configuración.

### Definición de Secciones Comunes

* **\`.pack\`**: Define la configuración de importación de plugins de Python, la extensión del binario final y las dependencias de tipos.
* **\`.world\`**: Constantes globales del target (por ejemplo, alineación de bus o tamaño predeterminado de datos).
* **\`.sections\`**: Configuración de los permisos y alineamiento de las secciones del linker.
* **\`.regs\`**: Mapeo y aliases de registros con su respectiva traducción a código de bits binario.
* **\`.vars\`**: Declaración de variables globales de bits.
* **\`.rules\`**: Las reglas de instrucción que forman la gramática del ensamblador.

### Ejemplo de Tabla Estructurada

\`\`\`rif
.regs
| NAME | binary | bits |
| a    | 000    | 8    |
| b    | 001    | 8    |
\`\`\`

> [!NOTE]
> Las tablas declaradas en RIF son analizadas automáticamente y se inyectan en el motor como estructuras de consulta rápida para validaciones rápidas dentro de los plugins de Python y directivas.`,

      "basics": `# Basics (Plugin de Soporte Base)

El plugin \`basics\` es el componente base del núcleo y viene integrado por defecto en la distribución del compilador. Proporciona las instrucciones fundamentales de saneamiento y tratamiento de bits.

### Funciones de Operandos y Utilidades

* **\`need\`**: Captura tokens de operando.
* **\`emit\`**: Concatenación y salida de secuencias binarias.
* **\`exists\`**: Valida si un identificador o etiqueta existe en el ámbito.
* **\`fits\`**: Valida si una constante cabe en un tamaño de bits asignado (ej. \`fits(value, 8)\`).
* **\`bitcat\`**: Concatenación a nivel de bits de múltiples variables.
* **\`bitsize\`**: Devuelve la longitud física de una variable binaria.
* **\`bitfit\`**: Ajusta una secuencia a una anchura específica truncando o rellenando.
* **\`zext\` / \`sext\`**: Extensión de cero y extensión de signo de operandos numéricos.
* **\`lt\`, \`lte\`, \`gt\`, \`gte\`, \`eq\`, \`neq\`: Operadores relacionales sobre operandos y constantes.
* **\`reldis\` / \`reloc\`**: Gestión de placeholders de direccionamiento relativo para saltos.
* **\`error\` / \`raise\`**: Detiene el runtime de compilación y emite un mensaje de error descriptivo personalizado.

> [!TIP]
> Dado que el plugin \`basics\` contiene las directivas esenciales, es altamente recomendable importarlo en la primera línea de la sección \`.pack\` de cualquier nuevo proyecto:
> 
> \`\`\`rif
> .pack
> plugin "basics"
> \`\`\``,

      "crear_y_usar": `# Crear y usar plugins

Los plugins permiten inyectar lógica de procesamiento arbitraria escrita en Python al compilador RIF. Esto es vital para resolver codificaciones complejas de bits (como saltos relativos en ARM o prefijos REX en x86-64).

### Ubicación del Plugin

Un plugin se empaqueta como un directorio dentro de la carpeta \`plugins/\`:

\`\`\`text
plugins/NOMBRE_PLUGIN/plugins/
\`\`\`

Cada archivo \`.py\` dentro de ese subdirectorio registra automáticamente una instrucción en RIF que lleva el nombre exacto del archivo.

* **Ejemplo**: Si creas \`plugins/arquitectura/plugins/prefijo.py\`, podrás usar la instrucción \`prefijo\` en tus reglas RIF.

### Registro del Plugin en el Pack

Para activar y usar las instrucciones del plugin en tu compilación, regístralo en la sección \`.pack\`:

\`\`\`rif
.pack
plugin "arquitectura"
\`\`\`

Luego, úsalo en tus reglas:

\`\`\`rif
.rules
inst:
    prefijo op1
    emit op1.binary
\`\`\``,

      "estructura": `# Estructura Interna del Plugin

Cada módulo de instrucción de un plugin se escribe en Python y debe exportar una estructura modular limpia de dos funciones clave: \`_start()\` y \`main()\`.

### Flujo de Saneamiento y Ejecución

* **\`_start()\`**: Es el punto de entrada que utiliza el compilador RIF para sanitizar el opcode, los comentarios y validar configuraciones iniciales. Siempre debe llamar a \`main()\`.
* **\`main()\`**: Realiza el procesamiento semántico sustancial de la instrucción, interactuando con los tokens activos a través del API de RIF.

### Ejemplo de Archivo de Plugin Mínimo

\`\`\`python
from rif import Expr, Line, Err

def main():
    # Consumir el opcode/instrucción actual en la línea de análisis
    Line.Advance()
    
    # Procesar lógica o validar operandos
    if len(Line.toks) == 0:
        return Err("Se esperaba al menos un operando para esta instrucción.")
    
    # Retornar una expresión binaria de resultado
    return Expr(["01010101"])

def _start():
    """Entrada de saneamiento de opcodes y bootstrap del plugin."""
    return main()
\`\`\`

> [!IMPORTANT]
> Cuando se realiza un salto o llamada inter-regla (\`call\`), RIF llama directamente a \`main()\` de forma interna, evitando re-ejecutar \`_start()\` para garantizar la consistencia en llamadas parciales de flujos anidados.`,

      "importar": `# Carga de Plugins

RIF carga plugins de forma dinámica desde el bloque \`.pack\`. Cada plugin es una carpeta con archivos \`.py\` dentro de su subdirectorio \`plugins/\`.

## Declaración en el pack

\`\`\`pack
.pack
plugin "basics"
plugin "gba"
plugin "mi_arquitectura"
\`\`\`

## Rutas de búsqueda (\`_plugin_roots\`)

RIF busca en este orden, desduplicando por ruta resuelta:

1. \`{base_dir}/plugins/\` — directorio del archivo \`.pack\` actual
2. \`{cwd}/plugins/\` — directorio de trabajo actual
3. \`{rif package}/plugins/\` — plugins internos instalados con RIF

## Seguridad

El nombre del plugin es validado antes de usarlo como ruta. RIF rechaza nombres que sean rutas absolutas, contengan separadores de directorio, o incluyan \`..\` o \`.\`. Esto aplica tanto en \`load_plugins()\` como en \`_find_plugin_cli()\`.

## Carga de módulos

Cada archivo \`.{plugext}\` (por defecto \`.py\`) en \`{plugin_root}/plugins/\` es cargado como un módulo Python con \`importlib.util\`. La carpeta del plugin y su subdirectorio \`plugins/\` se añaden a \`sys.path\` para que los imports relativos funcionen.

## Colisiones de símbolos

Cuando dos plugins definen el mismo símbolo (mismo nombre de archivo):
- \`pluginsymbolorder 0\` — error (default)
- \`pluginsymbolorder 3\` — mantiene el primero, ignora el segundo

## Ejemplo completo

\`\`\`pack
.pack
plugin "basics"
plugin "gba"

packer:
    fsystem 0
    ext .gba
\`\`\``,

      "packer": `# El Packer

El Packer consolida un archivo \`.pack\` y sus fragmentos en una representación unificada. Cuando \`fsystem == 1\`, busca archivos fragmento con el patrón \`{stem}.{subpre}{ext}\` y los fusiona en el fuente antes de reparse.

## Bloque \`packer:\` en el pack

\`\`\`pack
.pack
packer:
    fsystem 0          ; 0 = archivo único, 1 = fragmentos por sección
    ext .bin           ; extensión de salida (auto-agrega el punto)
    outext .bin        ; extensión del archivo de salida final
    entryfilename main ; nombre del archivo principal sin extensión
    sectpre .          ; prefijo de sección en el fuente
    subpre .           ; prefijo de subfragmento (* = cualquiera)
    definesec .text    ; registra secciones conocidas
    setpre world .world  ; mapea prefijo a sección
    needsect world     ; esta sección es obligatoria
    output salida      ; nombre de salida
\`\`\`

## Bloque \`reader:\`

Controla cómo RIF lee el código fuente assembly (no el \`.pack\`):

\`\`\`pack
reader:
    comment ;          ; caracter de comentario
    separator |        ; separador de columnas de tabla
    blocks :           ; caracter de inicio de bloque
    require_section    ; error si hay instrucciones fuera de sección
    validate_sections  ; valida que las secciones existan en el pack
    section .section   ; directiva de sección en el fuente
\`\`\`

## Bloque \`linker:\`

\`\`\`pack
linker:
    fsystem 1          ; 1 = proyecto fracturado por sección
    sectexec .text     ; sección ejecutable (entry point)
    sectneed .data     ; sección obligatoria
    sectopt .bss       ; sección opcional
\`\`\``,

      "linker": `# El Linker

El Linker toma el \`Program\` parseado, calcula los bloques físicos y virtuales en memoria, resuelve etiquetas y placeholders, y genera el binario final.

## Pipeline de \`BinaryLinker.build()\`

1. \`expand_fillables()\` — expande \`@nombre\` en el fuente antes de compilar
2. \`_plan_blocks()\` — construye \`LinkBlock\` por cada header y sección de \`.sections\`
3. \`_assign_offsets()\` — calcula \`physical_offset\`, \`virtual_offset\`, \`physical_size\`, \`virtual_size\`
4. \`_relocate_source_data()\` — asigna \`addrs\` a objetos de \`.data\`
5. \`_relocate_memory_regions()\` — asigna direcciones a stack/heap/buffer
6. \`_materialize_headers()\` — renderiza bloques de cabecera a bytes
7. Pasos 3-6 se repiten (dos pases para resolver referencias cruzadas)
8. \`_apply_relocations()\` — escribe valores de relocación en los bytes de cada bloque
9. \`_assemble_data()\` — concatena todos los bloques en los bytes finales

## \`LinkBlock\`

Cada bloque tiene: \`name\`, \`kind\` (\`"header"\`, \`"section"\`, \`"nobits"\`), \`data: bytes\`, \`physical_offset\`, \`virtual_offset\`, \`physical_size\`, \`virtual_size\`, \`align\`.

Los bloques \`"nobits"\` no ocupan espacio en el archivo (equivalente a secciones BSS). Su \`physical_size\` es 0 pero tienen \`virtual_size\`.

## Secciones (\`.sections\` table)

Cada fila define un bloque. Campos relevantes:

| Campo | Descripcion |
|-------|-------------|
| \`name\` | Nombre de la seccion |
| \`type\` | \`code\`, \`data\`, o \`nobits\` |
| \`emit\` | bytes o ruta del compilado |
| \`align\` | alineacion fisica en bytes |
| \`valign\` | alineacion virtual en bytes |
| \`offset\`/\`paddr\` | offset fisico forzado |
| \`voffset\`/\`vaddr\` | offset virtual forzado |

## Headers (\`.headers\` table)

Fila con \`NAME\`, \`SIZE\`, \`HEX\`, \`FILL\`. Los headers se emiten primero en el binario.

Pueden contener sub-tablas con \`OFFSET\`, \`SIZE\`, \`ENDIAN\`, \`VALUE\` para escribir campos a offsets especificos.

Valores especiales en \`VALUE\`:

\`\`\`pack
link:count .data          ; numero de filas en .data
link:size rom             ; tamaño fisico del bloque rom
link:vsize rom            ; tamaño virtual del bloque rom
link:offset rom           ; offset fisico del bloque rom
link:voffset rom          ; offset virtual del bloque rom
link:raw rom              ; bytes crudos del bloque rom
link:name mi_simbolo 4    ; bytes del nombre del simbolo (4 bytes)
link:expr A+B*2           ; expresion aritmetica
\`\`\`

## Relocaciones

\`\`\`pack
reloc kind target width [addend]   ; relocacion absoluta
reldis origin destination [width]  ; desplazamiento relativo
\`\`\`

El Linker resuelve relocaciones en \`_apply_relocations()\`, escribiendo el valor calculado directamente en los bytes del bloque correspondiente usando \`byteorder\` y \`signed\`.`,

      "cli": `# CLI de RIF

\`\`\`bash
python -m rif <comando> [opciones]
rif <comando> [opciones]         # si está instalado con pip
\`\`\`

## Comandos

### lex
Tokeniza un archivo \`.pack\` e imprime cada token con su tipo e indentación.

\`\`\`bash
python -m rif lex minimal.pack
\`\`\`

Salida por linea: \`NUMERO:INDENT: TIPO1:valor1 TIPO2:valor2 ...\`

### parse
Parsea un archivo \`.pack\` y vuelca toda la información estructurada: secciones, registros, tablas, tipos, memoria, packer config, plugins.

\`\`\`bash
python -m rif parse minimal.pack
\`\`\`

### pack
Consolida un archivo \`.pack\` y sus includes en un único archivo temporal.

\`\`\`bash
python -m rif pack minimal.pack
python -m rif pack minimal.pack -o salida.pack.temp
\`\`\`

### link
Enlaza fragmentos y vuelca las secciones resultantes.

\`\`\`bash
python -m rif link minimal.pack
python -m rif link minimal.pack -o linked.pack.temp
\`\`\`

### compile
Compila una instrucción individual contra un pack de reglas. Imprime \`rule\`, \`bits\` y \`hex\`.

\`\`\`bash
python -m rif compile store.amd64.pack "byte 0xff"
\`\`\`

Salida:
\`\`\`text
rule=byte
bits=11111111
hex=ff
\`\`\`

Si la instrucción contiene placeholders sin resolver (etiquetas futuras), imprime \`hex=<placeholder>\` con \`resolved=\` y \`placeholder=\` por cada uno.

### build
Compila y enlaza código fuente completo. Genera el binario.

\`\`\`bash
# Texto inline
python -m rif build store.amd64.pack -s "byte 0x01\nbyte 0x02"

# Archivo fuente
python -m rif build store.amd64.pack --source-file main.asm

# Carpeta proyecto
python -m rif build examples/gba

# Pack de un plugin instalado
python -m rif build examples/gba --plugin gba --name example
\`\`\`

Salida: \`bytes=\`, \`output=\`, \`sha256=\` o \`hex=\`, bloques físicos (\`block=nombre:kind:off=:voff=:size=:vsize=\`).

### plug
Instala un directorio como plugin en el directorio interno de RIF.

\`\`\`bash
python -m rif plug ./mi_plugin
\`\`\`

### list
Listar plugins instalados.

\`\`\`bash
python -m rif list plugins
\`\`\`

### packs
Listar packs disponibles dentro de un plugin instalado.

\`\`\`bash
python -m rif packs --plugin gba
\`\`\`

### table
Editar tablas \`.pack\` desde la terminal.

\`\`\`bash
python -m rif table modify --from mi.pack "regs add row ax 000 16"
python -m rif table format --from mi.pack
python -m rif table undo
python -m rif table redo
\`\`\`

### clear
Limpiar cachés de compilación.

\`\`\`bash
# Borra todos los __pycache__ de rif/
python -m rif clear cache

# Borra .cache/ y __pycache__ del plugin image
python -m rif clear -p image cache
\`\`\`

### zip
Empaqueta todo el directorio \`rif/\` en un ZIP, excluyendo \`__pycache__\`.

\`\`\`bash
python -m rif zip
python -m rif zip -o mi_backup.zip
\`\`\`

### help
Abre la documentación en el visor interactivo o consulta un tema en consola.

\`\`\`bash
python -m rif help
python -m rif help --open     # abre en el navegador
python -m rif help instrucciones
\`\`\`

## Plugin CLI

Cada plugin puede exponer su propio CLI a través de un archivo \`cli.py\` con función \`main(argv)\`:

\`\`\`bash
python -m rif -pcli fonts list
python -m rif -pcli gba run examples/gba/hello.gba
python -m rif -pcli basics build-doc mi_proyecto
\`\`\`

RIF busca el \`cli.py\` del plugin primero en \`plugins/\` local y luego en el directorio interno.`,

      "compilar": `# Compilación de Instrucciones

## compile

Compila una instrucción individual. Útil para probar reglas sin montar un proyecto completo.

\`\`\`bash
python -m rif compile store.amd64.pack "byte 0xff"
\`\`\`

\`\`\`text
rule=byte
bits=11111111
hex=ff
\`\`\`

Si la instrucción produce placeholders sin resolver (saltos a etiquetas futuras), la salida es:

\`\`\`text
rule=jmp
bits=<placeholder>
hex=<placeholder>
resolved=target:LABEL:0x10
placeholder=target:LABEL:
\`\`\`

## build con código inline

\`\`\`bash
python -m rif build store.amd64.pack --source-text "byte 0x01\nbyte 0x02" -o salida.bin
\`\`\`

## build con archivo fuente

\`\`\`bash
python -m rif build store.amd64.pack --source-file main.asm -o salida.bin
\`\`\`

## build de proyecto (carpeta)

Cuando \`source\` apunta a una carpeta, RIF busca el pack raíz (\`.pack\` con \`fsystem 1\`), lee el código fuente de los archivos con la extensión configurada por el pack, y genera el binario en esa misma carpeta.

\`\`\`bash
python -m rif build examples/gba
python -m rif build examples/gba --plugin gba --name example
\`\`\`

Salida del build:
\`\`\`text
bytes=131264
output=examples\gba\gba.gba
sha256=f5a6ede6...
hex.head=2e0000ea24ffae51...
hex.tail=0000000000000000...
block=header:section:off=0:voff=134217728:size=192:vsize=192
block=rom:section:off=192:voff=134217920:size=131072:vsize=131072
\`\``,

      "comando_table": `# Comando Table (CLI)

El comando \`rif table\` (o \`rif -table\`) permite modificar y formatear programáticamente las tablas \`.pack\` de RIF directamente desde la terminal. Esto es útil para automatizar la adición de instrucciones, registros, campos y formatear el código de tabla.

## Comandos Principales

- \`rif table modify\`: Modifica filas, columnas, tablas o valores.
- \`rif table format\`: Alinea y formatea las columnas de una tabla para que se lean correctamente.
- \`rif table undo\`: Deshace la última modificación de tabla.
- \`rif table redo\`: Rehace la modificación previamente deshecha.

> [!NOTE]
> Todos los comandos de modificación y formateo crean automáticamente un archivo de copia de seguridad (\`.bak\`) de forma predeterminada.

## Especificando el Archivo o Pack

Puedes indicar el archivo o pack objetivo utilizando las siguientes opciones:

- \`--from <archivo|carpeta>\`: Ruta al archivo \`.pack\` o carpeta que los contiene.
- \`-p <plugin> -use <pack>\`: Modifica un pack alojado dentro de un plugin instalado.
- \`--file <nombre>\`: Cuando \`--from\` o \`-p\` apunta a una carpeta, especifica qué archivo modificar.
- \`--section <seccion>\`: Apunta a una sección específica (por ejemplo, \`.regs\` o \`.data\`).

> **Ejemplo:** \`rif table modify --from my_pack/ --file cpu.pack "regs add column bits 32"\`

## Operaciones de Modificación (\`modify\`)

El argumento final de \`modify\` es un string con la operación a ejecutar con la forma \`"TABLA comando argumentos"\`.

### Filas (Rows)
- **Añadir fila:** \`add row <celda1> <celda2> ...\`
  *(Ej: \`"regs add row ax 000 16"\`)*
- **Eliminar fila(s):** \`del row <nombre1> <nombre2> ...\`
- **Renombrar fila:** \`rename row <viejo> <nuevo>\`
- **Copiar fila:** \`copy row <origen> <nuevo>\`
- **Mover fila:** \`move row <nombre> before|after|to <destino>\`

### Columnas (Columns)
- **Añadir columna:** \`add column <nombre> [valor_por_defecto]\`
  *(Ej: \`"regs add column type INT"\`)*
- **Eliminar columna(s):** \`del column <nombre1> <nombre2> ...\`
- **Renombrar columna:** \`rename column <viejo> <nuevo>\`
- **Asignar valor a toda la columna:** \`set column <columna> <valor1> <valor2> ...\`
- **Mover columna:** \`move column <nombre> before|after|to <destino>\`

### Celdas (Cells)
- **Establecer valor:** \`set <fila> <columna> <valor>\`
  *(Ej: \`"regs set ax bits 32"\`)*
- **Operación rápida:** \`<columna> <fila> <valor>\`
  *(Ej: \`"regs bits ax 32"\`)*
- **Alternar valor booleano:** Usa \`switch\` como valor en celdas de tipo yes/no.
  *(Ej: \`"rules set add hidden switch"\`)*
- **Limpiar celda:** \`clear <fila> <columna>\`

### Tablas y Secciones
- **Eliminar tabla:** \`del table\`
- **Añadir sección/separador:** \`addsect <texto>\`

## Opciones Adicionales

- \`--dry-run\`: Simula los cambios y muestra las diferencias sin escribir el archivo.
- \`--no-backup\`: Evita crear el archivo \`.bak\` de seguridad.
- \`--case-sensitive\`: Las coincidencias en nombres de tablas, filas y columnas distinguen entre mayúsculas y minúsculas.
- \`--table <nombre>\`: Para \`rif table format\`, restringe el formateo a una tabla específica.`,

      "vscode": `# VS Code y VSIX

RIF 0.0.3 Semi Stable puede armar extensiones VS Code en formato \`.vsix\` desde los bundles \`vscode/\` de los plugins.

## Compilar

\`\`\`bash
python -m rif compile --vscode --ext .gbasm -icon rif/plugins/gba/vscode/assets/gba-memory.svg --p gba sound fonts basics -o build/vscode/rif-gba-sound-fonts-basics-0.2.0.vsix
\`\`\`

## Instalar

\`\`\`bash
python -m rif install --vscode build/vscode/rif-gba-sound-fonts-basics-0.2.0.vsix
\`\`\`

RIF usa el comando \`code --install-extension\`. Si VS Code no encuentra \`code\`, instala ese comando desde la paleta de comandos de VS Code o usa Extensions > Install from VSIX.

## Armar un bundle

Crea \`vscode/build.json\`, \`vscode/syntaxs.json\`, \`vscode/doc.json\` y opcionalmente \`vscode/assets/\` dentro de tu plugin. \`build.json\` define identidad y extensiones, \`syntaxs.json\` define registros, keywords, snippets y diagnosticos, y \`doc.json\` define hovers/documentacion.

## Estado

El soporte actual incluye resaltado, completions, snippets, hovers, diagnosticos por regex, quick fixes, simbolos y documentacion embebida. No es todavia un Language Server completo.`,

      "mir": `# Soporte MIR (Medium Intermediate Representation)

En el roadmap estratégico de desarrollo de RIF se encuentra contemplada la introducción de **MIR** (Representación Intermedia Media).

### Objetivos de MIR

* **Desacoplamiento Absoluto**: Separar la gramática de coincidencia léxica de las instrucciones del proceso de generación y codificación final de los bits.
* **Optimización Semántica**: Permitir realizar transformaciones lógicas en un lenguaje intermedio común antes de emitir los bytes finales.
* **Selección de Instrucciones**: Facilitar la tarea de mapear lenguajes de alto nivel a reglas RIF mediante un análisis intermedio uniforme.

Con MIR, los desarrolladores de plugins podrán manipular y optimizar árboles de instrucciones genéricos de manera estructurada antes de su ensamblado físico.`,

      "optimizadores": `# Optimizadores de Código

La incorporación de un motor de optimización global sobre la representación intermedia (MIR) y los bloques de secciones está proyectada para futuras fases.

### Áreas de Optimización Planeadas

* **Plegado de Constantes (Constant Folding)**: Evaluación en tiempo de compilación de expresiones aritméticas estáticas en operandos inmediatos.
* **Reducción de Saltos**: Optimización y sustitución de saltos de larga distancia por instrucciones de salto corto relativas al offset para economizar bytes.
* **Eliminación de Código Muerto**: Detección y descarte de secciones o bloques de instrucciones inaccesibles en el análisis de flujo de control.
* **Alineamiento Inteligente**: Optimización en la inyección de instrucciones NOP de relleno para asegurar el rendimiento de bus sin inflar en exceso el tamaño del binario.`,

      "soporte": `# Soporte & Evolución del Core

La evolución del núcleo de RIF está regida por una filosofía de diseño minimalista y de alta estabilidad para evitar sobrecargar el core con particularidades de arquitecturas concretas.

### Criterios de Evolución del Core

* **Generalidad**: Solo se añaden palabras clave, flujos de control o tipos de datos al núcleo central cuando representan una necesidad transversal para múltiples arquitecturas de hardware.
* **Relegación a Plugins**: Si una validación o codificación compleja puede ser resuelta mediante lógica de programación dentro de un plugin en Python, debe permanecer allí para no alterar la agilidad del compilador principal.
* **Compatibilidad**: Conservación rigurosa de la sintaxis estructurada para asegurar la longevidad de las descripciones de paquetes ya implementadas.`,

      "mejoras_del_linker": `# Roadmap: Mejoras del Linker

El enlazador (Linker) de RIF recibirá importantes actualizaciones diseñadas para expandir su flexibilidad y capacidad de análisis estructural en futuros lanzamientos.

### Características Planificadas

* **Soporte de Formatos Estándar**: Plugins que permitan exportar la representación final en formatos binarios estandarizados del sector, tales como archivos ELF (Executable and Linkable Format) o cabeceras PE (Portable Executable).
* **Diagnósticos de Colisiones**: Análisis de solapamiento físico en secciones de memoria de hardware y avisos de desbordamiento de límites de pila o heap.
* **Mapas de Símbolos Avanzados**: Generación de archivos de mapeo (.map) y tablas detalladas de offsets virtuales y físicos para facilitar la depuración de firmware.
* **Relocalización Dinámica**: Soporte para la especificación de tablas de re-localización en caliente para sistemas operativos embebidos rudimentarios.`,

      "compiladores": `# Roadmap: Auto-Compilación y Distribución

Para simplificar la adopción y distribución de ensambladores construidos con RIF, se proyecta la creación de un sistema de empaquetado integrado.

### Ensambladores Autónomos

Esta característica permitirá compilar un descriptor \`.pack\`, todas sus reglas y sus plugins de Python asociados directamente en un único archivo ejecutable autónomo.

**Beneficios Clave:**
* **Cero Dependencias**: Distribución de un ensamblador/compilador para un hardware específico sin requerir la instalación global de Python en la máquina del usuario final.
* **API Inmutable**: Distribución rápida y empaquetada lista para procesos de integración continua (CI/CD).
* **Consola de Comandos Especializada**: El ejecutable generado presentará una CLI simplificada y centrada exclusivamente en la compilación del target de hardware empaquetado.`,

      "vscode_soporte_historico": `# Soporte de VSCode e Integración IDE

La productividad del desarrollador de sistemas es una prioridad absoluta. Por ello, está contemplado el desarrollo de un ecosistema completo de herramientas de desarrollo de software (SDK).

### Características del Plugin Oficial de VSCode

* **Resaltado de Sintaxis Dinámico**: Coloreado de alta calidad para archivos descriptores \`.pack\`, reglas en la sección \`.rules\` y estructuras de memoria.
* **Linter de Sintaxis en Vivo**: Marcado en tiempo real de errores sintácticos, llaves sin cerrar y nombres de secciones no válidos.
* **Autocompletado Contextual**: Sugerencias automáticas de palabras clave del core, directivas de alineación y métodos comunes del plugin base \`basics\`.
* **Templates de Inicio**: Asistentes integrados para generar nuevos esqueletos de plugins de Python e inicializar arquitecturas de forma rápida.`

// DYNAMIC_PLUGINS_DOCS_START
,
      "plugin_atari2600": "# Atari 2600\n\nPlugin base para crear ROMs de Atari 2600 con reglas RIF. Incluye un pack minimo 6502/TIA, vectores de reset al final del banco de 4 KiB y CLI para ejecutar binarios con Stella.\n\nComandos utiles:\n\n```bash\npython -m rif build atari2600\npython -m rif -pcli atari2600 install Stella --add-path\npython -m rif -pcli atari2600 run atari2600/out.bin\n```\n\n\n## Uso\n# Uso\n\nEl proyecto de ejemplo genera una ROM de 4 KiB. La seccion `rom` usa `voffset 0xF000`, por lo que las relocaciones absolutas de 16 bits apuntan al mapa de memoria que espera el 6502 dentro de Stella.\n\n`rompad_to_vectors` rellena hasta `0x0FFA` y `vectors start` escribe NMI, RESET e IRQ. El relleno se apoya en la primitiva interna `pad_to`, no en offsets hardcodeados del linker.\n\n\n## Cli\n# CLI\n\n`rif -pcli atari2600 install Stella --add-path` registra Stella. Si no encuentra el ejecutable, intenta instalarlo con el gestor disponible del sistema.\n\n`rif -pcli atari2600 run out.bin` abre la ROM con Stella.\n",
      "plugin_atari2600/uso": "# Uso\n\nEl proyecto de ejemplo genera una ROM de 4 KiB. La seccion `rom` usa `voffset 0xF000`, por lo que las relocaciones absolutas de 16 bits apuntan al mapa de memoria que espera el 6502 dentro de Stella.\n\n`rompad_to_vectors` rellena hasta `0x0FFA` y `vectors start` escribe NMI, RESET e IRQ. El relleno se apoya en la primitiva interna `pad_to`, no en offsets hardcodeados del linker.\n",
      "plugin_atari2600/cli": "# CLI\n\n`rif -pcli atari2600 install Stella --add-path` registra Stella. Si no encuentra el ejecutable, intenta instalarlo con el gestor disponible del sistema.\n\n`rif -pcli atari2600 run out.bin` abre la ROM con Stella.\n",
      "plugin_basics": "# \ud83d\udee0\ufe0f RIF Basics Plugin\n\n`basics` es el plugin fundacional y la biblioteca est\u00e1ndar de **Retargetable ISA Foundry (RIF)**. Su prop\u00f3sito es proveer todas las directivas gen\u00e9ricas de ensamblado, manipulaci\u00f3n de bits, control de alineaci\u00f3n y relocaci\u00f3n necesarias para dar soporte a cualquier arquitectura de hardware sin hardcodear l\u00f3gica en el n\u00facleo de RIF.\n\n---\n\n## \ud83e\udded Arquitectura y Filosof\u00eda\n\nEn RIF, el compilador procesa archivos `.pack` que importan el plugin `basics`:\n```rif\n.pack\nplugin \"basics\"\n```\n\nCada instrucci\u00f3n definida dentro de la tabla `.rules` o `.words` de un pack delega su procesamiento lexer/parser a archivos Python individuales dentro del directorio `plugins/` de `basics`. Al invocar una palabra como `need` o `emit`, el compilador transfiere el control al plugin pas\u00e1ndole el contexto activo (`Line`, `Operator`, `Operators`, `TYPES_MAP`). El plugin analiza los argumentos, realiza validaciones en tiempo de compilaci\u00f3n y retorna un objeto `Expr` (Expresi\u00f3n) que instruye al compilador exactamente qu\u00e9 bits emitir o qu\u00e9 s\u00edmbolos registrar.\n\n---\n\n## \ud83d\udce6 Componentes del Plugin\n\nEl plugin `basics` est\u00e1 organizado en los siguientes m\u00f3dulos:\n\n1.  **Directivas de Control (`plugins/`):**\n    *   `need`: Captura operandos y valida sus tipos primitivos o derivados.\n    *   `emit`: Serializa fragmentos de bits (est\u00e1ticos o din\u00e1micos) hacia el stream binario.\n    *   `call`: Reutiliza y salta a sub-reglas del compilador.\n2.  **Operadores de Bits y Conversiones (`plugins/`):**\n    *   `bitcat`, `trunc`, `zext`, `sext`, `bitfit`, `bitsize`, `fits`: Aritm\u00e9tica y re-formateado de bits.\n3.  **Relocaciones y S\u00edmbolos (`plugins/`):**\n    *   `reloc`: Emite direcciones absolutas y delega su resoluci\u00f3n final al linker.\n    *   `reldis`: Calcula desplazamientos relativos al PC de ejecuci\u00f3n (para saltos `bcond` o cargas `ldr_pc`).\n    *   `emitaddress`, `exists`, `fillid`, `vfillid`: Ubicaci\u00f3n y resoluci\u00f3n de etiquetas de c\u00f3digo y fillables en `fills.json`.\n4.  **Alineaci\u00f3n y Layout (`plugins/`):**\n    *   `align`, `pad`: Relleno de bytes y alineaci\u00f3n en l\u00edmites f\u00edsicos de memoria.\n5.  **Herramientas de Consola (`cli/`):**\n    *   `build-doc`: Compilador automatizado de documentaci\u00f3n y generador de extensiones VSIX para VS Code.\n\n---\n\n## \ud83d\udcd6 Documentaci\u00f3n Completa\n\nPara conocer a fondo el funcionamiento de cada directiva y c\u00f3mo se comunican con el compilador, consulta las subsecciones detalladas:\n\n*   [\ud83d\udcd6 Cat\u00e1logo Completo de Instrucciones](file:///c:/Users/Kentucky/Desktop/AMST/Retargetable-ISA-Foundry-RIF-/rif/plugins/basics/pages/0_instrucciones.md): Sintaxis, par\u00e1metros, comunicaci\u00f3n interna y ejemplos reales de las 20+ instrucciones.\n*   [\ud83d\udd0c Integraci\u00f3n VS Code (VSIX)](file:///c:/Users/Kentucky/Desktop/AMST/Retargetable-ISA-Foundry-RIF-/rif/plugins/basics/pages/1_vsix.md): Gu\u00eda de empaquetado de extensiones y soporte ling\u00fc\u00edstico para tu arquitectura.\n\n\n## Instrucciones\n# \ud83d\udcda Cat\u00e1logo Completo de Instrucciones - Plugin Basics\n\nEl plugin `basics` proporciona todas las directivas fundamentales para construir reglas de emisi\u00f3n en RIF. Cada instrucci\u00f3n es un componente reutilizable que se comunica con el compilador a trav\u00e9s de la **Core API**.\n\n---\n\n## \ud83d\udd0d \u00cdndice de Instrucciones\n\n### Control de Compilaci\u00f3n\n- [`need`](#need) - Captura y valida operandos\n- [`emit`](#emit) - Serializa fragmentos de bits\n- [`call`](#call) - Reutiliza sub-reglas\n- [`error` / `raise`](#error--raise) - Genera errores controlados\n\n### Operaciones con Bits\n- [`bitcat`](#bitcat) - Concatena fragmentos de bits\n- [`bitsize`](#bitsize) - Obtiene el tama\u00f1o en bits\n- [`bitfit`](#bitfit) - Valida si un valor cabe en N bits\n- [`trunc`](#trunc) - Trunca un valor a N bits\n- [`zext`](#zext) - Extensi\u00f3n cero (sin signo)\n- [`sext`](#sext) - Extensi\u00f3n de signo\n\n### Comparaciones y Validaciones\n- [`eq` / `neq`](#eq--neq) - Igualdad y desigualdad\n- [`lt`, `lte`, `gt`, `gte`](#comparadores-lt-lte-gt-gte) - Comparaciones num\u00e9ricas\n- [`fits`](#fits) - Valida si un valor cabe en un rango\n- [`exists`](#exists) - Verifica si existe una etiqueta\n\n### Memoria y Direcciones\n- [`reloc`](#reloc) - Relocaci\u00f3n de direcci\u00f3n absoluta\n- [`reldis`](#reldis) - Distancia relativa al PC\n- [`emitaddress`](#emitaddress) - Emite direcci\u00f3n de etiqueta\n- [`fillid` / `vfillid`](#fillid--vfillid) - Resuelve IDs de fillables\n\n### Alineaci\u00f3n y Layout\n- [`align`](#align) - Alinea a l\u00edmite N bytes\n- [`pad`](#pad) - Rellena con bytes espec\u00edficos\n\n---\n\n## \ud83d\udcd6 Documentaci\u00f3n Detallada\n\n### `need`\n\n**Prop\u00f3sito:** Captura operandos desde la l\u00ednea de c\u00f3digo y los valida seg\u00fan tipos permitidos.\n\n**Sintaxis:**\n```rif\nneed \u003ctipos...\u003e \u003coperador\u003e\n```\n\n**Tipos Soportados:**\n- `VALUE` - Valores num\u00e9ricos (literales)\n- `LABEL` - Etiquetas de c\u00f3digo\n- `SYMBOL` - S\u00edmbolos y constantes\n- `REG` - Registros (si est\u00e1n definidos en `.regs`)\n- `SREG` - Sub-registros especializados\n- `TYPE` - Tipos de dato complejos\n- `STACK`, `HEAP`, `MEMORY` - Regiones especiales\n\n**Ejemplo:**\n```rif\n.rules\nrule mov_reg:\n    need REG, REG mov_target, mov_source\n    emit 0001 mov_target.bits mov_source.bits\n```\n\n**Comportamiento:**\n- Almacena el operador en un contexto disponible para otras instrucciones\n- Valida que los operandos coincidan con los tipos declarados\n- Genera error si los tipos no concuerdan o faltan operandos\n- M\u00faltiples tipos se escriben separados por comas\n\n**Errores Comunes:**\n```rif\nneed REG, REG  ; \u274c Falta operador al final\nneed REG invalid_name, ax  ; \u274c No identifica el nombre del operador\nneed VALUE, REG, VALUE result  ; \u274c Operador debe ir al final\n```\n\n**API Interna:**\n- Llama a `Line.Unpack(\",\")` para separar componentes\n- `Operator.Save(target, RuleIndicator.current, valid_types)` almacena la ligadura\n- Retorna `Expr([\"need\", valids, target])`\n\n---\n\n### `emit`\n\n**Prop\u00f3sito:** Serializa fragmentos de bits (est\u00e1ticos o din\u00e1micos) al stream binario de salida.\n\n**Sintaxis:**\n```rif\nemit [modo] \u003cfragmento1\u003e, \u003cfragmento2\u003e, ...\n```\n\n**Modos Disponibles:**\n- `bits` (default) - Emisi\u00f3n de bits individuales sin restricci\u00f3n\n- `cbits` - Complementa autom\u00e1ticamente a byte (rellena con ceros si falta)\n- `cbit` - Valida que sea exactamente 8 bits\n- `cmbit` - Valida exactamente 4 bits\n- `ccbit` - Valida exactamente 16 bits\n- `cdbit` - Valida exactamente 32 bits\n- `cebit` - Valida exactamente 64 bits\n\n**Tipos de Fragmentos:**\n- `01001010` - Bits literales en binario\n- `operador.field` - Placeholder que se resuelve en compilaci\u00f3n\n- `variable_bits` - Referencia a variables de bits definidas\n\n**Ejemplos:**\n```rif\nemit 11010101                    ; Emite 8 bits literales\nemit cbits 1101, var_bits       ; Complementa a byte\nemit bits operador.value        ; Emite placeholder\nemit cbit 11111111              ; Asegura exacto 1 byte\n```\n\n**Comportamiento:**\n- Valida que los bits sean v\u00e1lidos (`0` o `1`)\n- Resuelve placeholders autom\u00e1ticamente en build-time\n- Detecta campos faltantes en las tablas del pack\n- Compacta bytes est\u00e1ticos para optimizaci\u00f3n\n- Permite m\u00faltiples fragmentos separados por comas\n\n**Errores Comunes:**\n```rif\nemit 1010 1011 1100 1101  ; \u274c 16 bits sin modo compactado\nemit operador.nonexistent ; \u274c Campo no existe\nemit                      ; \u274c Fragmentos vac\u00edos\n```\n\n**API Interna:**\n- `_parse_chunk()` analiza cada fragmento\n- `EmitChunk` estructura que representa cada componente\n- Retorna `Expr([\"emit_bits_exact\", instruction])`\n\n---\n\n### `call`\n\n**Prop\u00f3sito:** Reutiliza sub-reglas del compilador sin duplicar c\u00f3digo.\n\n**Sintaxis:**\n```rif\ncall \u003cnombre_regla\u003e\n```\n\n**Ejemplo:**\n```rif\n.rules\nrule helper:\n    need VALUE value\n    emit 1111 value.bits\n\nrule main:\n    need VALUE x\n    call helper\n```\n\n**Comportamiento:**\n- Busca la regla con el nombre exacto en el pack\n- Ejecuta la sub-regla en el contexto actual\n- Los operadores capturados en `main` se heredan a `helper`\n- Las emisiones de `helper` se insertan inline en `main`\n- Permite anidaci\u00f3n de llamadas\n\n**Errores Comunes:**\n```rif\ncall unknown_rule        ; \u274c Regla no existe\ncall rule1 rule2         ; \u274c Solo acepta una regla\ncall                     ; \u274c Regla faltante\n```\n\n---\n\n### `error` / `raise`\n\n**Prop\u00f3sito:** Genera errores controlados durante la compilaci\u00f3n.\n\n**Sintaxis:**\n```rif\nerror \"Mensaje de error\"\nraise \"Mensaje de error\"\n```\n\n**Ejemplo:**\n```rif\nrule validate:\n    need VALUE val\n    fits val, 0, 255\n    error \"Valor fuera de rango\"\n```\n\n**Comportamiento:**\n- Detiene inmediatamente la compilaci\u00f3n con un mensaje legible\n- \u00datil para validaciones condicionales\n- Aparece en el output de compilaci\u00f3n\n- El mensaje se propaga al usuario\n\n**Diferencia:**\n- `error` y `raise` se usan indistintamente\n- Ambos generan un `PackError`\n\n---\n\n### `bitcat`\n\n**Prop\u00f3sito:** Concatena m\u00faltiples fragmentos de bits en una secuencia \u00fanica.\n\n**Sintaxis:**\n```rif\nbitcat \u003cfragmento1\u003e, \u003cfragmento2\u003e, ..., \u003cdestino\u003e\n```\n\n**Ejemplo:**\n```rif\nneed REG r1, REG r2\nbitcat r1.value, r2.value, result\nemit cbits result.bits\n```\n\n**Comportamiento:**\n- Ordena los fragmentos en el orden especificado (izquierda a derecha)\n- Almacena el resultado concatenado en el operador destino\n- Preserva la anchura de bits de cada componente\n- El resultado es accesible para emisiones posteriores\n\n---\n\n### `bitsize`\n\n**Prop\u00f3sito:** Obtiene la cantidad de bits de un valor.\n\n**Sintaxis:**\n```rif\nbitsize \u003cvalor\u003e, \u003cdestino\u003e\n```\n\n**Ejemplo:**\n```rif\nneed VALUE imm\nbitsize imm, size\nfits size, 1, 32\n```\n\n**Comportamiento:**\n- Calcula los bits necesarios para representar el valor\n- Almacena el resultado num\u00e9rico en el operador destino\n- Devuelve el m\u00ednimo de bits requeridos (sin padding)\n\n---\n\n### `bitfit`\n\n**Prop\u00f3sito:** Valida si un fragmento de bits cabe exactamente en N bits.\n\n**Sintaxis:**\n```rif\nbitfit \u003cfragmento\u003e, \u003cn_bits\u003e\n```\n\n**Ejemplo:**\n```rif\nneed REG reg\nbitfit reg.value, 4\nemit reg.value  ; Solo si cabe en 4 bits\n```\n\n**Comportamiento:**\n- Verifica que el fragmento tenga exactamente N bits\n- Genera error si no coincide\n- Complementario a `trunc` (validaci\u00f3n vs. truncamiento)\n\n---\n\n### `trunc`\n\n**Prop\u00f3sito:** Trunca un valor a N bits (descarta bits de orden superior).\n\n**Sintaxis:**\n```rif\ntrunc \u003cvalor\u003e, \u003cn_bits\u003e, \u003cdestino\u003e\n```\n\n**Ejemplo:**\n```rif\nneed VALUE val\ntrunc val, 16, truncated\nemit cbits truncated.bits\n```\n\n**Comportamiento:**\n- Mantiene solo los primeros N bits\n- Descarta el resto silenciosamente\n- Almacena el resultado en el operador destino\n- Perder\u00e1 informaci\u00f3n si N es muy peque\u00f1o\n\n---\n\n### `zext`\n\n**Prop\u00f3sito:** Extiende un valor con ceros (extensi\u00f3n sin signo) hasta M bits.\n\n**Sintaxis:**\n```rif\nzext \u003cvalor\u003e, \u003cm_bits\u003e, \u003cdestino\u003e\n```\n\n**Ejemplo:**\n```rif\nneed VALUE val\nzext val, 32, extended\nemit cdbit extended.bits\n```\n\n**Comportamiento:**\n- Agrega ceros a la izquierda hasta alcanzar M bits\n- Mantiene el valor num\u00e9rico id\u00e9ntico\n- \u00datil para conversiones entre tipos sin signo\n- Almacena en el operador destino\n\n---\n\n### `sext`\n\n**Prop\u00f3sito:** Extiende un valor con signo hasta M bits.\n\n**Sintaxis:**\n```rif\nsext \u003cvalor\u003e, \u003cm_bits\u003e, \u003cdestino\u003e\n```\n\n**Ejemplo:**\n```rif\nneed VALUE val\nsext val, 32, extended\n```\n\n**Comportamiento:**\n- Detecta el bit de signo (MSB) del valor original\n- Replica ese bit para llenar los bits faltantes\n- Preserva el valor con signo en la representaci\u00f3n extendida\n- Cr\u00edtico para operaciones con n\u00fameros negativos\n\n---\n\n### `eq` / `neq`\n\n**Prop\u00f3sito:** Valida igualdad o desigualdad entre dos valores.\n\n**Sintaxis:**\n```rif\neq \u003cvalor1\u003e, \u003cvalor2\u003e\nneq \u003cvalor1\u003e, \u003cvalor2\u003e\n```\n\n**Ejemplo:**\n```rif\nneed REG r1, REG r2\neq r1, r2  ; Genera error si son diferentes\n```\n\n**Comportamiento:**\n- `eq` genera error si los valores son diferentes\n- `neq` genera error si los valores son iguales\n- Se usan t\u00edpicamente para validaciones\n\n---\n\n### Comparadores (`lt`, `lte`, `gt`, `gte`)\n\n**Prop\u00f3sito:** Valida rangos num\u00e9ricos.\n\n**Sintaxis:**\n```rif\nlt \u003cvalor\u003e, \u003cl\u00edmite\u003e       ; valor \u003c l\u00edmite\nlte \u003cvalor\u003e, \u003cl\u00edmite\u003e      ; valor \u003c= l\u00edmite\ngt \u003cvalor\u003e, \u003cl\u00edmite\u003e       ; valor \u003e l\u00edmite\ngte \u003cvalor\u003e, \u003cl\u00edmite\u003e      ; valor \u003e= l\u00edmite\n```\n\n**Ejemplo:**\n```rif\nneed VALUE imm\ngte imm, -128\nlte imm, 127\nemit cbits imm.bits\n```\n\n**Comportamiento:**\n- Genera error si la condici\u00f3n falla\n- \u00datil para validar rangos de operandos\n- Soporta n\u00fameros negativos\n\n---\n\n### `fits`\n\n**Prop\u00f3sito:** Valida si un valor cabe completamente en N bits (sin p\u00e9rdida).\n\n**Sintaxis:**\n```rif\nfits \u003cvalor\u003e, \u003cn_bits\u003e\n```\n\n**Ejemplo:**\n```rif\nneed VALUE imm\nfits imm, 8\nemit cbits imm.bits\n```\n\n**Comportamiento:**\n- Verifica que el valor se represente en N bits sin desbordamiento\n- Genera error si no cabe\n- Trabajo complementario a `trunc` (validaci\u00f3n vs. truncamiento)\n\n---\n\n### `exists`\n\n**Prop\u00f3sito:** Verifica si una etiqueta est\u00e1 definida en el programa.\n\n**Sintaxis:**\n```rif\nexists \u003cetiqueta\u003e\n```\n\n**Ejemplo:**\n```rif\nneed LABEL lbl\nexists lbl\nreloc lbl, current_offset\n```\n\n**Comportamiento:**\n- Busca la etiqueta en la tabla de s\u00edmbolos del programa\n- Genera error si no existe\n- Comunica al linker que la etiqueta es requerida\n\n---\n\n### `reloc`\n\n**Prop\u00f3sito:** Emite una direcci\u00f3n absoluta que ser\u00e1 resuelta por el linker.\n\n**Sintaxis:**\n```rif\nreloc \u003cetiqueta\u003e, \u003coffset_actual\u003e\n```\n\n**Ejemplo:**\n```rif\nneed LABEL target\nreloc target, 0x8000\n```\n\n**Comportamiento:**\n- Genera un registro de relocaci\u00f3n\n- El linker resuelve la direcci\u00f3n final en la fase de enlace\n- Se usa para referencias a s\u00edmbolos externos o diferidos\n- Inserta bytes placeholder en la imagen actual\n\n---\n\n### `reldis`\n\n**Prop\u00f3sito:** Calcula la distancia relativa al PC (Program Counter).\n\n**Sintaxis:**\n```rif\nreldis \u003cetiqueta\u003e, \u003cdestino\u003e\n```\n\n**Ejemplo:**\n```rif\nneed LABEL target\nreldis target, offset\nemit cbits offset.bits  ; Emite como branching offset\n```\n\n**Comportamiento:**\n- Computa `target_address - current_pc`\n- Almacena el desplazamiento en el operador destino\n- \u00datil para instrucciones de salto relativo\n\n---\n\n### `emitaddress`\n\n**Prop\u00f3sito:** Emite la direcci\u00f3n de una etiqueta.\n\n**Sintaxis:**\n```rif\nemitaddress \u003cetiqueta\u003e\n```\n\n**Ejemplo:**\n```rif\nneed LABEL start\nemitaddress start  ; Emite los bytes de la direcci\u00f3n\n```\n\n**Comportamiento:**\n- Resuelve la direcci\u00f3n de la etiqueta\n- Emite los bytes correspondientes (tama\u00f1o depende de arquitectura)\n\n---\n\n### `fillid` / `vfillid`\n\n**Prop\u00f3sito:** Resuelve IDs de objetos fillables (datos generados por plugins).\n\n**Sintaxis:**\n```rif\nfillid \u003cnombre\u003e, \u003cdestino\u003e\nvfillid \u003cnombre\u003e, \u003cdestino\u003e\n```\n\n**Ejemplo:**\n```rif\nfillid image_data, id\nemit ccbit id.bits  ; Emite el ID del fillable\n```\n\n**Comportamiento:**\n- Busca el fillable en `fills.json`\n- `fillid` obtiene el ID num\u00e9rico\n- `vfillid` obtiene informaci\u00f3n adicional del fillable\n- Los IDs se asignan durante la fase de build\n\n---\n\n### `align`\n\n**Prop\u00f3sito:** Alinea la posici\u00f3n actual a un l\u00edmite de N bytes.\n\n**Sintaxis:**\n```rif\nalign \u003cn_bytes\u003e\n```\n\n**Ejemplo:**\n```rif\nemit_code_section\nalign 4  ; Asegura alineaci\u00f3n a 4 bytes\nemit 11110000\n```\n\n**Comportamiento:**\n- Si la posici\u00f3n actual no est\u00e1 alineada, inserta padding\n- Completa hasta el siguiente m\u00faltiplo de N bytes\n- Usa bytes `0x00` por defecto para rellenar\n\n---\n\n### `pad`\n\n**Prop\u00f3sito:** Inserta exactamente N bytes de relleno.\n\n**Sintaxis:**\n```rif\npad \u003cn_bytes\u003e\n```\n\n**Ejemplo:**\n```rif\nemit_header\npad 16  ; Reserva 16 bytes\n```\n\n**Comportamiento:**\n- Inserta bytes de relleno sin comprometer la estructura\n- No modifica la posici\u00f3n l\u00f3gica\n- \u00datil para reservar espacio en ROMs\n\n---\n\n## \ud83d\udd27 Patrones Comunes\n\n### Patr\u00f3n 1: Captura y Emisi\u00f3n B\u00e1sica\n```rif\nrule op_add:\n    need REG dest, REG src\n    emit 00 dest.bits src.bits\n```\n\n### Patr\u00f3n 2: Validaci\u00f3n Condicional\n```rif\nrule imm_load:\n    need REG dest, VALUE imm\n    fits imm, 16\n    emit 0001 dest.bits, imm.bits\n```\n\n### Patr\u00f3n 3: Concatenaci\u00f3n de Bits\n```rif\nrule multi_field:\n    need REG r1, REG r2, VALUE flags\n    bitcat r1.bits, r2.bits, flags.value, combined\n    emit ccbit combined.bits\n```\n\n### Patr\u00f3n 4: Rutinas Reutilizables\n```rif\nrule prologue:\n    need VALUE stack_size\n    emit ... ; c\u00f3digo de pr\u00f3logo\n\nrule main_routine:\n    need VALUE sz\n    call prologue\n    need VALUE body_size\n    emit ... ; c\u00f3digo del cuerpo\n```\n\n### Patr\u00f3n 5: Direccionamiento Relativo\n```rif\nrule branch_forward:\n    need LABEL target\n    reldis target, distance\n    fits distance, 12\n    emit 111 distance.bits\n```\n\n---\n\n## \ud83d\udc1b Debugging y Tips\n\n### Habilitar Logs Detallados\n```bash\npython -m rif compile pack.json instruction --verbose\n```\n\n### Verificar Tabla de S\u00edmbolos\n```bash\npython -m rif parse pack.json\n```\n\n### An\u00e1lisis de Emisi\u00f3n\nUsa `--debug` para ver c\u00f3mo se procesan los placeholders:\n```bash\npython -m rif build proyecto --debug\n```\n\n---\n\n## \ud83d\udcda Referencia R\u00e1pida\n\n| Instrucci\u00f3n | Entrada | Salida | Efecto |\n|-------------|---------|--------|--------|\n| `need` | L\u00ednea de tokens | Operador guardado | Captura |\n| `emit` | Fragmentos | Bytes al stream | Serializaci\u00f3n |\n| `call` | Nombre de regla | Ejecuci\u00f3n inline | Reutilizaci\u00f3n |\n| `bitcat` | M\u00faltiples fragmentos | Concatenaci\u00f3n | Composici\u00f3n |\n| `reloc` | Etiqueta | Registro al linker | Defer |\n| `align` | N bytes | Padding | Alineaci\u00f3n |\n| `fits` | Valor, bits | Error o OK | Validaci\u00f3n |\n| `zext`/`sext` | Valor, bits | Extensi\u00f3n | Conversi\u00f3n |\n| `reldis` | Etiqueta | Offset relativo | PC-rel |\n\n---\n\n## \ud83d\udd17 V\u00e9ase Tambi\u00e9n\n\n- [Estructura Interna del Plugin](estructura.md)\n- [Mecanismos de Importaci\u00f3n](importar.md)\n- [Integraci\u00f3n VS Code (VSIX)](1_vsix.md)\n\n\n## Vsix\n# \ud83d\udd0c Integraci\u00f3n VS Code (VSIX)\n\nRIF puede compilar una extensi\u00f3n VS Code profesional en formato `.vsix` desde los metadatos de los plugins. Este soporte est\u00e1 en estado **RIF 0.0.3 Semi Stable**: es un generador completo de extensiones de lenguaje con soporte TextMate, snippets, autocompletado, hovers, diagn\u00f3sticos y quick fixes.\n\n---\n\n## \u2728 Capacidades Incluidas\n\n### Funcionalidades del Lenguaje\n\n- **Resaltado de Sintaxis TextMate** - Colorizaci\u00f3n autom\u00e1tica de directivas, palabras clave y operadores\n- **Autocompletado Inteligente** - Snippets contextuales para agilizar la escritura\n- **Hover con Documentaci\u00f3n** - Informaci\u00f3n en formato Markdown al pasar el cursor\n- **Diagn\u00f3sticos por Regex** - Validaci\u00f3n de patrones comunes durante la escritura\n- **Quick Fixes** - Sugerencias autom\u00e1ticas para arreglar problemas detectados\n- **S\u00edmbolos de Documento** - Navegaci\u00f3n r\u00e1pida por etiquetas y reglas\n- **Asociaci\u00f3n de Extensiones** - Vinculaci\u00f3n autom\u00e1tica con extensiones personalizadas\n\n### Distribuci\u00f3n\n\n- **Documentaci\u00f3n Embebida** - Todo el contenido incluido en el VSIX\n- **Assets Empaquetados** - Iconos, im\u00e1genes y recursos dentro del paquete\n- **Independencia** - No requiere servidor de lenguaje externo\n- **Instalaci\u00f3n Sencilla** - Un comando para instalar en VS Code\n\n---\n\n## \ud83d\ude80 Compilar un VSIX desde Plugins\n\n### Forma Recomendada (Nueva)\n\n```bash\npython -m rif compile --vscode \\\n  --ext .gbasm \\\n  --icon rif/plugins/gba/vscode/assets/gba-memory.svg \\\n  --p gba sound fonts basics \\\n  -o build/vscode/rif-gba-sound-fonts-basics-0.2.0.vsix\n```\n\n### Forma Alternativa (Antigua, a\u00fan compatible)\n\n```bash\npython -m rif compile --vscode \\\n  gba sound fonts basics \\\n  --ext .gbasm \\\n  --icon rif/plugins/gba/vscode/assets/gba-memory.svg\n```\n\n### Argumentos CLI\n\n| Argumento | Forma corta | Descripci\u00f3n |\n|-----------|------------|-----------|\n| `--vscode` | - | Activa el compilador de extensiones VS Code |\n| `--p` / `--plugins` | - | Lista los plugins que aportan bundles `vscode/` |\n| `--ext` | - | Fuerza la extensi\u00f3n de archivo (ej: `.gbasm`, `.rif`) |\n| `-icon` / `--icon` | - | Ruta al archivo de icono (PNG, JPG, GIF, WebP, SVG) |\n| `-o` / `--output` | - | Ruta de salida del archivo `.vsix` |\n\n---\n\n## \ud83d\udce6 Estructura de Salida\n\nEl VSIX se genera por defecto en:\n```\nbuild/vscode/rif-{plugins}-{version}.vsix\n```\n\nEjemplo:\n```\nbuild/vscode/rif-gba-sound-fonts-basics-0.2.0.vsix\n```\n\n---\n\n## \ud83d\udd27 Instalaci\u00f3n en VS Code\n\nDespu\u00e9s de compilar, instala la extensi\u00f3n:\n\n```bash\npython -m rif install --vscode build/vscode/rif-gba-sound-fonts-basics-0.2.0.vsix\n```\n\n### Requisitos Previos\n\n- VS Code debe estar instalado\n- El comando `code` debe estar disponible en el PATH\n\n### Si `code` no est\u00e1 en el PATH\n\n1. Abre la **Paleta de Comandos** en VS Code (`Ctrl+Shift+P` / `Cmd+Shift+P`)\n2. Escribe: `Shell Command: Install 'code' command in PATH`\n3. Presiona Enter\n4. Reinicia la terminal si es necesario\n\n### Verificaci\u00f3n Manual\n\n```bash\n# Verificar que code est\u00e9 disponible\nwhich code\n\n# Instalar manualmente si falla el autodetecci\u00f3n\n# (Busca la carpeta de instalaci\u00f3n de VS Code en tu sistema)\n```\n\n---\n\n## \ud83c\udfd7\ufe0f Armar Soporte VSIX para tu Plugin\n\n### Estructura de Directorios\n\nCada plugin puede incluir metadatos de VS Code:\n\n```text\nmi_plugin/\n  pack.json\n  README.md\n  vscode/\n    build.json\n    syntaxs.json\n    doc.json\n    assets/\n      icon.svg\n      logo.png\n```\n\n### 1. `build.json` - Identidad de la Extensi\u00f3n\n\nDefine los metadatos de la extensi\u00f3n en el Marketplace:\n\n```json\n{\n  \"displayName\": \"RIF Mi ISA\",\n  \"description\": \"Soporte VS Code para mi arquitectura ISA personalizada.\",\n  \"author\": {\n    \"name\": \"Mi Nombre\",\n    \"url\": \"https://ejemplo.com\"\n  },\n  \"version\": \"0.2.0\",\n  \"license\": \"MIT\",\n  \"extensions\": [\".miisa\", \".mi-asm\"],\n  \"categories\": [\"Programming Languages\", \"Snippets\"],\n  \"keywords\": [\"rif\", \"assembler\", \"mi-isa\", \"compilador\"]\n}\n```\n\n**Campos:**\n- `displayName` \u2b50 - Nombre que aparece en VS Code\n- `description` - Descripci\u00f3n breve\n- `version` - Versi\u00f3n sem\u00e1ntica (ej: `0.2.0`)\n- `extensions` - Extensiones de archivo asociadas\n- `categories` - Categor\u00edas en el Marketplace\n- `keywords` - Palabras clave para b\u00fasqueda\n- `license` - Tipo de licencia\n- `author` - Informaci\u00f3n del desarrollador\n\n### 2. `syntaxs.json` - Vocabulario y Diagn\u00f3sticos\n\nDefine palabras clave, colores, completados y diagn\u00f3sticos:\n\n```json\n{\n  \"directives\": [\".text\", \".data\", \".bss\"],\n  \"builtins\": [\"need\", \"emit\", \"call\", \"align\"],\n  \"keywords\": [\"mov\", \"add\", \"jump\", \"call\"],\n  \"types\": [\"u8\", \"u16\", \"u32\", \"u64\"],\n  \"registers\": [\"R0\", \"R1\", \"R2\", \"R3\"],\n  \"completions\": [\n    {\n      \"label\": \"mov\",\n      \"insertText\": \"mov ${1:R0}, ${2:R1}\",\n      \"detail\": \"Mi ISA\",\n      \"documentation\": \"Copia datos de un registro a otro.\",\n      \"kind\": \"Snippet\",\n      \"sortText\": \"001\"\n    },\n    {\n      \"label\": \".section\",\n      \"insertText\": \".section ${1:name}\\n    ${2:contenido}\",\n      \"detail\": \"Directiva\",\n      \"kind\": \"Keyword\"\n    }\n  ],\n  \"patterns\": [\n    {\n      \"name\": \"keyword.operator.rif\",\n      \"match\": \"\\\\b(?:=|,|:|;)\\\\b\"\n    },\n    {\n      \"name\": \"constant.language.boolean.rif\",\n      \"match\": \"\\\\b(?:true|false|on|off)\\\\b\"\n    }\n  ],\n  \"errors\": [\n    {\n      \"match\": \"\\\\bjump\\\\s+PC\\\\b\",\n      \"message\": \"Evita saltar expl\u00edcitamente a PC.\",\n      \"severity\": \"warning\",\n      \"code\": \"jump-pc\",\n      \"suggest\": \"Usa etiquetas en lugar de direcciones hardcodeadas.\"\n    },\n    {\n      \"match\": \"^\\\\s*emit\\\\s*$\",\n      \"message\": \"emit requiere bits, un placeholder o una variable.\",\n      \"severity\": \"error\",\n      \"code\": \"rif-empty-emit\"\n    }\n  ]\n}\n```\n\n**Secciones:**\n\n#### `directives`\nPalabras clave que comienzan con punto (`.pack`, `.rules`, etc.)\n\n#### `builtins`\nFunciones/instrucciones fundamentales del lenguaje\n\n#### `keywords`\nPalabras clave de dominio espec\u00edfico (mnem\u00f3nicos, etc.)\n\n#### `types`\nTipos de dato reconocidos\n\n#### `registers`\nNombres de registros disponibles\n\n#### `completions`\nArray de sugerencias de autocompletado\n\n**Campos de completion:**\n- `label` - Texto mostrado en el men\u00fa\n- `insertText` - C\u00f3digo insertado (puede incluir `${1:placeholder}`)\n- `documentation` - Descripci\u00f3n al seleccionar\n- `kind` - Tipo (Snippet, Keyword, Function, etc.)\n- `sortText` - Orden en el men\u00fa (n\u00fameros sortean primero)\n\n#### `patterns`\nReglas TextMate para colorizaci\u00f3n\n\n#### `errors`\nDiagn\u00f3sticos por expresi\u00f3n regular\n\n**Campos de error:**\n- `match` - Regex para detectar el problema\n- `message` - Mensaje de error\n- `severity` - `error`, `warning` o `hint`\n- `code` - ID \u00fanico del diagn\u00f3stico\n- `suggest` - Quick fix sugerido\n\n### 3. `doc.json` - Documentaci\u00f3n en Hovers\n\nDefine documentaci\u00f3n que aparece al pasar el cursor sobre palabras:\n\n```json\n{\n  \"words\": {\n    \"rif_project\": {\n      \"doc\": [\n        {\n          \"type\": \"text\",\n          \"content\": \"RIF separa arquitectura, herramientas y proyecto.\"\n        },\n        {\n          \"type\": \"code\",\n          \"content\": \".pack\\nplugin \\\"basics\\\"\\nplugin \\\"gba\\\"\"\n        }\n      ]\n    },\n    \"need\": {\n      \"doc\": [\n        {\n          \"type\": \"text\",\n          \"content\": \"Consume y valida operandos de una regla.\"\n        },\n        {\n          \"type\": \"code\",\n          \"content\": \"need VALUE, imm\"\n        },\n        {\n          \"type\": \"text\",\n          \"content\": \"Soporta m\u00faltiples tipos separados por comas.\"\n        }\n      ]\n    },\n    \"emit\": {\n      \"doc\": [\n        {\n          \"type\": \"text\",\n          \"content\": \"Emite bits o placeholders ya capturados.\"\n        },\n        {\n          \"type\": \"code\",\n          \"content\": \"emit imm.binary\"\n        }\n      ]\n    }\n  }\n}\n```\n\n**Estructura:**\n- `words` - Diccionario de palabra \u2192 documentaci\u00f3n\n- `doc` - Array de bloques de documentaci\u00f3n\n- `type` - `\"text\"` o `\"code\"`\n- `content` - Contenido del bloque\n\n---\n\n## \ud83d\udccb Flujo Recomendado\n\n### Para un Nuevo Plugin con Soporte VS Code\n\n```\n1. Define o ajusta tu pack.json\n   \u2193\n2. Crea la carpeta vscode/\n   \u251c\u2500\u2500 build.json  (identidad)\n   \u251c\u2500\u2500 syntaxs.json (vocabulario)\n   \u251c\u2500\u2500 doc.json    (documentaci\u00f3n)\n   \u2514\u2500\u2500 assets/\n       \u2514\u2500\u2500 icon.svg (opcional)\n   \u2193\n3. Compila el VSIX\n   $ python -m rif compile --vscode --p tu_plugin basics\n   \u2193\n4. Instala en VS Code\n   $ python -m rif install --vscode build/vscode/rif-tu-plugin.vsix\n   \u2193\n5. Abre un archivo con la extensi\u00f3n configurada\n   \u2193\n6. Ajusta completions, diagn\u00f3sticos y hovers\n   seg\u00fan lo que se necesite mejorar\n   \u2193\n7. Vuelve a compilar e instalar\n```\n\n---\n\n## \ud83c\udfa8 Ejemplo Completo: Plugin GBA\n\n### Estructura\n\n```\nrif/plugins/gba/\n  pack.json\n  README.md\n  vscode/\n    build.json\n    syntaxs.json\n    doc.json\n    assets/\n      gba-memory.svg\n```\n\n### build.json\n\n```json\n{\n  \"displayName\": \"RIF Game Boy Advance\",\n  \"description\": \"Ensamblador retargetable para GBA con Thumb y ARM.\",\n  \"version\": \"0.2.0\",\n  \"extensions\": [\".gbasm\"],\n  \"categories\": [\"Programming Languages\"],\n  \"keywords\": [\"gba\", \"gameboy\", \"arm\", \"thumb\", \"assembler\"]\n}\n```\n\n### Compilaci\u00f3n\n\n```bash\npython -m rif compile --vscode \\\n  --ext .gbasm \\\n  --icon rif/plugins/gba/vscode/assets/gba-memory.svg \\\n  --p gba sound fonts basics\n```\n\n### Resultado\n\n```\nbuild/vscode/rif-gba-sound-fonts-basics-0.2.0.vsix\n```\n\n---\n\n## \ud83d\udd0d Debugging de Extensiones\n\n### Verificar el Contenido del VSIX\n\nLos archivos `.vsix` son ZIP:\n\n```bash\nunzip -l build/vscode/rif-gba.vsix\n```\n\n### Buscar Errores Comunes\n\n```bash\n# Verificar que los archivos JSON sean v\u00e1lidos\npython -m json.tool rif/plugins/tu_plugin/vscode/build.json\n\n# Validar sintaxis de regex en syntaxs.json\npython -c \"import re; re.compile(r'tu_regex')\"\n```\n\n### Recargar la Extensi\u00f3n\n\nEn VS Code despu\u00e9s de cambios:\n1. Presiona `Ctrl+Shift+P` (Windows/Linux) o `Cmd+Shift+P` (Mac)\n2. Escribe `Reload Window`\n3. Presiona Enter\n\n### Abrir Consola de Desarrollo\n\n```\nHelp \u2192 Toggle Developer Tools\n```\n\nAqu\u00ed puedes ver errores de la extensi\u00f3n en tiempo real.\n\n---\n\n## \ud83d\udcca Casos de Uso\n\n### Caso 1: Extensi\u00f3n Solo para GBA\n\n```bash\npython -m rif compile --vscode \\\n  --ext .gbasm \\\n  --p gba basics\n```\n\n### Caso 2: Extensi\u00f3n Multi-Arquitectura\n\n```bash\npython -m rif compile --vscode \\\n  --ext .rif \\\n  --p gba atari2600 amd64 basics\n```\n\n### Caso 3: Extensi\u00f3n con Icono Personalizado\n\n```bash\npython -m rif compile --vscode \\\n  --ext .myasm \\\n  --icon my_logo.svg \\\n  --p mi_plugin basics \\\n  -o build/vscode/mi-extension.vsix\n```\n\n---\n\n## \ud83d\udc1b Soluci\u00f3n de Problemas\n\n### \"El comando `code` no se encuentra\"\n\n**Soluci\u00f3n:**\n```bash\n# En Windows\n\"C:\\Program Files\\Microsoft VS Code\\bin\\code.cmd\"\n\n# En macOS\n/Applications/Visual\\ Studio\\ Code.app/Contents/Resources/app/bin/code\n\n# En Linux (usualmente ya est\u00e1 en PATH)\nwhich code\n```\n\n### La extensi\u00f3n no se instala\n\n```bash\n# Verifica que VS Code est\u00e9 cerrado\n# Intenta con ruta absoluta\npython -m rif install --vscode /full/path/to/extension.vsix\n\n# O instala manualmente en VS Code\n# Extensions \u2192 Install from VSIX\n```\n\n### Los hovers no aparecen\n\n1. Verifica que `doc.json` sea v\u00e1lido\n2. Aseg\u00farate de que las claves en `doc.json` coincidan con las palabras clave\n3. Recarga la ventana de VS Code\n\n### Autocompletado no funciona\n\n1. Revisa que `syntaxs.json` tenga la secci\u00f3n `completions`\n2. Verifica que `kind` sea un valor v\u00e1lido\n3. Usa `sortText` para controlar el orden\n\n---\n\n## \ud83d\udd17 V\u00e9ase Tambi\u00e9n\n\n- [Cat\u00e1logo de Instrucciones](0_instrucciones.md) - Documentaci\u00f3n de directivas\n- [Estructura Interna del Plugin](estructura.md) - C\u00f3mo crear plugins\n- [Mecanismos de Importaci\u00f3n](importar.md) - Carga de plugins\n",
      "plugin_basics/instrucciones": "# \ud83d\udcda Cat\u00e1logo Completo de Instrucciones - Plugin Basics\n\nEl plugin `basics` proporciona todas las directivas fundamentales para construir reglas de emisi\u00f3n en RIF. Cada instrucci\u00f3n es un componente reutilizable que se comunica con el compilador a trav\u00e9s de la **Core API**.\n\n---\n\n## \ud83d\udd0d \u00cdndice de Instrucciones\n\n### Control de Compilaci\u00f3n\n- [`need`](#need) - Captura y valida operandos\n- [`emit`](#emit) - Serializa fragmentos de bits\n- [`call`](#call) - Reutiliza sub-reglas\n- [`error` / `raise`](#error--raise) - Genera errores controlados\n\n### Operaciones con Bits\n- [`bitcat`](#bitcat) - Concatena fragmentos de bits\n- [`bitsize`](#bitsize) - Obtiene el tama\u00f1o en bits\n- [`bitfit`](#bitfit) - Valida si un valor cabe en N bits\n- [`trunc`](#trunc) - Trunca un valor a N bits\n- [`zext`](#zext) - Extensi\u00f3n cero (sin signo)\n- [`sext`](#sext) - Extensi\u00f3n de signo\n\n### Comparaciones y Validaciones\n- [`eq` / `neq`](#eq--neq) - Igualdad y desigualdad\n- [`lt`, `lte`, `gt`, `gte`](#comparadores-lt-lte-gt-gte) - Comparaciones num\u00e9ricas\n- [`fits`](#fits) - Valida si un valor cabe en un rango\n- [`exists`](#exists) - Verifica si existe una etiqueta\n\n### Memoria y Direcciones\n- [`reloc`](#reloc) - Relocaci\u00f3n de direcci\u00f3n absoluta\n- [`reldis`](#reldis) - Distancia relativa al PC\n- [`emitaddress`](#emitaddress) - Emite direcci\u00f3n de etiqueta\n- [`fillid` / `vfillid`](#fillid--vfillid) - Resuelve IDs de fillables\n\n### Alineaci\u00f3n y Layout\n- [`align`](#align) - Alinea a l\u00edmite N bytes\n- [`pad`](#pad) - Rellena con bytes espec\u00edficos\n\n---\n\n## \ud83d\udcd6 Documentaci\u00f3n Detallada\n\n### `need`\n\n**Prop\u00f3sito:** Captura operandos desde la l\u00ednea de c\u00f3digo y los valida seg\u00fan tipos permitidos.\n\n**Sintaxis:**\n```rif\nneed \u003ctipos...\u003e \u003coperador\u003e\n```\n\n**Tipos Soportados:**\n- `VALUE` - Valores num\u00e9ricos (literales)\n- `LABEL` - Etiquetas de c\u00f3digo\n- `SYMBOL` - S\u00edmbolos y constantes\n- `REG` - Registros (si est\u00e1n definidos en `.regs`)\n- `SREG` - Sub-registros especializados\n- `TYPE` - Tipos de dato complejos\n- `STACK`, `HEAP`, `MEMORY` - Regiones especiales\n\n**Ejemplo:**\n```rif\n.rules\nrule mov_reg:\n    need REG, REG mov_target, mov_source\n    emit 0001 mov_target.bits mov_source.bits\n```\n\n**Comportamiento:**\n- Almacena el operador en un contexto disponible para otras instrucciones\n- Valida que los operandos coincidan con los tipos declarados\n- Genera error si los tipos no concuerdan o faltan operandos\n- M\u00faltiples tipos se escriben separados por comas\n\n**Errores Comunes:**\n```rif\nneed REG, REG  ; \u274c Falta operador al final\nneed REG invalid_name, ax  ; \u274c No identifica el nombre del operador\nneed VALUE, REG, VALUE result  ; \u274c Operador debe ir al final\n```\n\n**API Interna:**\n- Llama a `Line.Unpack(\",\")` para separar componentes\n- `Operator.Save(target, RuleIndicator.current, valid_types)` almacena la ligadura\n- Retorna `Expr([\"need\", valids, target])`\n\n---\n\n### `emit`\n\n**Prop\u00f3sito:** Serializa fragmentos de bits (est\u00e1ticos o din\u00e1micos) al stream binario de salida.\n\n**Sintaxis:**\n```rif\nemit [modo] \u003cfragmento1\u003e, \u003cfragmento2\u003e, ...\n```\n\n**Modos Disponibles:**\n- `bits` (default) - Emisi\u00f3n de bits individuales sin restricci\u00f3n\n- `cbits` - Complementa autom\u00e1ticamente a byte (rellena con ceros si falta)\n- `cbit` - Valida que sea exactamente 8 bits\n- `cmbit` - Valida exactamente 4 bits\n- `ccbit` - Valida exactamente 16 bits\n- `cdbit` - Valida exactamente 32 bits\n- `cebit` - Valida exactamente 64 bits\n\n**Tipos de Fragmentos:**\n- `01001010` - Bits literales en binario\n- `operador.field` - Placeholder que se resuelve en compilaci\u00f3n\n- `variable_bits` - Referencia a variables de bits definidas\n\n**Ejemplos:**\n```rif\nemit 11010101                    ; Emite 8 bits literales\nemit cbits 1101, var_bits       ; Complementa a byte\nemit bits operador.value        ; Emite placeholder\nemit cbit 11111111              ; Asegura exacto 1 byte\n```\n\n**Comportamiento:**\n- Valida que los bits sean v\u00e1lidos (`0` o `1`)\n- Resuelve placeholders autom\u00e1ticamente en build-time\n- Detecta campos faltantes en las tablas del pack\n- Compacta bytes est\u00e1ticos para optimizaci\u00f3n\n- Permite m\u00faltiples fragmentos separados por comas\n\n**Errores Comunes:**\n```rif\nemit 1010 1011 1100 1101  ; \u274c 16 bits sin modo compactado\nemit operador.nonexistent ; \u274c Campo no existe\nemit                      ; \u274c Fragmentos vac\u00edos\n```\n\n**API Interna:**\n- `_parse_chunk()` analiza cada fragmento\n- `EmitChunk` estructura que representa cada componente\n- Retorna `Expr([\"emit_bits_exact\", instruction])`\n\n---\n\n### `call`\n\n**Prop\u00f3sito:** Reutiliza sub-reglas del compilador sin duplicar c\u00f3digo.\n\n**Sintaxis:**\n```rif\ncall \u003cnombre_regla\u003e\n```\n\n**Ejemplo:**\n```rif\n.rules\nrule helper:\n    need VALUE value\n    emit 1111 value.bits\n\nrule main:\n    need VALUE x\n    call helper\n```\n\n**Comportamiento:**\n- Busca la regla con el nombre exacto en el pack\n- Ejecuta la sub-regla en el contexto actual\n- Los operadores capturados en `main` se heredan a `helper`\n- Las emisiones de `helper` se insertan inline en `main`\n- Permite anidaci\u00f3n de llamadas\n\n**Errores Comunes:**\n```rif\ncall unknown_rule        ; \u274c Regla no existe\ncall rule1 rule2         ; \u274c Solo acepta una regla\ncall                     ; \u274c Regla faltante\n```\n\n---\n\n### `error` / `raise`\n\n**Prop\u00f3sito:** Genera errores controlados durante la compilaci\u00f3n.\n\n**Sintaxis:**\n```rif\nerror \"Mensaje de error\"\nraise \"Mensaje de error\"\n```\n\n**Ejemplo:**\n```rif\nrule validate:\n    need VALUE val\n    fits val, 0, 255\n    error \"Valor fuera de rango\"\n```\n\n**Comportamiento:**\n- Detiene inmediatamente la compilaci\u00f3n con un mensaje legible\n- \u00datil para validaciones condicionales\n- Aparece en el output de compilaci\u00f3n\n- El mensaje se propaga al usuario\n\n**Diferencia:**\n- `error` y `raise` se usan indistintamente\n- Ambos generan un `PackError`\n\n---\n\n### `bitcat`\n\n**Prop\u00f3sito:** Concatena m\u00faltiples fragmentos de bits en una secuencia \u00fanica.\n\n**Sintaxis:**\n```rif\nbitcat \u003cfragmento1\u003e, \u003cfragmento2\u003e, ..., \u003cdestino\u003e\n```\n\n**Ejemplo:**\n```rif\nneed REG r1, REG r2\nbitcat r1.value, r2.value, result\nemit cbits result.bits\n```\n\n**Comportamiento:**\n- Ordena los fragmentos en el orden especificado (izquierda a derecha)\n- Almacena el resultado concatenado en el operador destino\n- Preserva la anchura de bits de cada componente\n- El resultado es accesible para emisiones posteriores\n\n---\n\n### `bitsize`\n\n**Prop\u00f3sito:** Obtiene la cantidad de bits de un valor.\n\n**Sintaxis:**\n```rif\nbitsize \u003cvalor\u003e, \u003cdestino\u003e\n```\n\n**Ejemplo:**\n```rif\nneed VALUE imm\nbitsize imm, size\nfits size, 1, 32\n```\n\n**Comportamiento:**\n- Calcula los bits necesarios para representar el valor\n- Almacena el resultado num\u00e9rico en el operador destino\n- Devuelve el m\u00ednimo de bits requeridos (sin padding)\n\n---\n\n### `bitfit`\n\n**Prop\u00f3sito:** Valida si un fragmento de bits cabe exactamente en N bits.\n\n**Sintaxis:**\n```rif\nbitfit \u003cfragmento\u003e, \u003cn_bits\u003e\n```\n\n**Ejemplo:**\n```rif\nneed REG reg\nbitfit reg.value, 4\nemit reg.value  ; Solo si cabe en 4 bits\n```\n\n**Comportamiento:**\n- Verifica que el fragmento tenga exactamente N bits\n- Genera error si no coincide\n- Complementario a `trunc` (validaci\u00f3n vs. truncamiento)\n\n---\n\n### `trunc`\n\n**Prop\u00f3sito:** Trunca un valor a N bits (descarta bits de orden superior).\n\n**Sintaxis:**\n```rif\ntrunc \u003cvalor\u003e, \u003cn_bits\u003e, \u003cdestino\u003e\n```\n\n**Ejemplo:**\n```rif\nneed VALUE val\ntrunc val, 16, truncated\nemit cbits truncated.bits\n```\n\n**Comportamiento:**\n- Mantiene solo los primeros N bits\n- Descarta el resto silenciosamente\n- Almacena el resultado en el operador destino\n- Perder\u00e1 informaci\u00f3n si N es muy peque\u00f1o\n\n---\n\n### `zext`\n\n**Prop\u00f3sito:** Extiende un valor con ceros (extensi\u00f3n sin signo) hasta M bits.\n\n**Sintaxis:**\n```rif\nzext \u003cvalor\u003e, \u003cm_bits\u003e, \u003cdestino\u003e\n```\n\n**Ejemplo:**\n```rif\nneed VALUE val\nzext val, 32, extended\nemit cdbit extended.bits\n```\n\n**Comportamiento:**\n- Agrega ceros a la izquierda hasta alcanzar M bits\n- Mantiene el valor num\u00e9rico id\u00e9ntico\n- \u00datil para conversiones entre tipos sin signo\n- Almacena en el operador destino\n\n---\n\n### `sext`\n\n**Prop\u00f3sito:** Extiende un valor con signo hasta M bits.\n\n**Sintaxis:**\n```rif\nsext \u003cvalor\u003e, \u003cm_bits\u003e, \u003cdestino\u003e\n```\n\n**Ejemplo:**\n```rif\nneed VALUE val\nsext val, 32, extended\n```\n\n**Comportamiento:**\n- Detecta el bit de signo (MSB) del valor original\n- Replica ese bit para llenar los bits faltantes\n- Preserva el valor con signo en la representaci\u00f3n extendida\n- Cr\u00edtico para operaciones con n\u00fameros negativos\n\n---\n\n### `eq` / `neq`\n\n**Prop\u00f3sito:** Valida igualdad o desigualdad entre dos valores.\n\n**Sintaxis:**\n```rif\neq \u003cvalor1\u003e, \u003cvalor2\u003e\nneq \u003cvalor1\u003e, \u003cvalor2\u003e\n```\n\n**Ejemplo:**\n```rif\nneed REG r1, REG r2\neq r1, r2  ; Genera error si son diferentes\n```\n\n**Comportamiento:**\n- `eq` genera error si los valores son diferentes\n- `neq` genera error si los valores son iguales\n- Se usan t\u00edpicamente para validaciones\n\n---\n\n### Comparadores (`lt`, `lte`, `gt`, `gte`)\n\n**Prop\u00f3sito:** Valida rangos num\u00e9ricos.\n\n**Sintaxis:**\n```rif\nlt \u003cvalor\u003e, \u003cl\u00edmite\u003e       ; valor \u003c l\u00edmite\nlte \u003cvalor\u003e, \u003cl\u00edmite\u003e      ; valor \u003c= l\u00edmite\ngt \u003cvalor\u003e, \u003cl\u00edmite\u003e       ; valor \u003e l\u00edmite\ngte \u003cvalor\u003e, \u003cl\u00edmite\u003e      ; valor \u003e= l\u00edmite\n```\n\n**Ejemplo:**\n```rif\nneed VALUE imm\ngte imm, -128\nlte imm, 127\nemit cbits imm.bits\n```\n\n**Comportamiento:**\n- Genera error si la condici\u00f3n falla\n- \u00datil para validar rangos de operandos\n- Soporta n\u00fameros negativos\n\n---\n\n### `fits`\n\n**Prop\u00f3sito:** Valida si un valor cabe completamente en N bits (sin p\u00e9rdida).\n\n**Sintaxis:**\n```rif\nfits \u003cvalor\u003e, \u003cn_bits\u003e\n```\n\n**Ejemplo:**\n```rif\nneed VALUE imm\nfits imm, 8\nemit cbits imm.bits\n```\n\n**Comportamiento:**\n- Verifica que el valor se represente en N bits sin desbordamiento\n- Genera error si no cabe\n- Trabajo complementario a `trunc` (validaci\u00f3n vs. truncamiento)\n\n---\n\n### `exists`\n\n**Prop\u00f3sito:** Verifica si una etiqueta est\u00e1 definida en el programa.\n\n**Sintaxis:**\n```rif\nexists \u003cetiqueta\u003e\n```\n\n**Ejemplo:**\n```rif\nneed LABEL lbl\nexists lbl\nreloc lbl, current_offset\n```\n\n**Comportamiento:**\n- Busca la etiqueta en la tabla de s\u00edmbolos del programa\n- Genera error si no existe\n- Comunica al linker que la etiqueta es requerida\n\n---\n\n### `reloc`\n\n**Prop\u00f3sito:** Emite una direcci\u00f3n absoluta que ser\u00e1 resuelta por el linker.\n\n**Sintaxis:**\n```rif\nreloc \u003cetiqueta\u003e, \u003coffset_actual\u003e\n```\n\n**Ejemplo:**\n```rif\nneed LABEL target\nreloc target, 0x8000\n```\n\n**Comportamiento:**\n- Genera un registro de relocaci\u00f3n\n- El linker resuelve la direcci\u00f3n final en la fase de enlace\n- Se usa para referencias a s\u00edmbolos externos o diferidos\n- Inserta bytes placeholder en la imagen actual\n\n---\n\n### `reldis`\n\n**Prop\u00f3sito:** Calcula la distancia relativa al PC (Program Counter).\n\n**Sintaxis:**\n```rif\nreldis \u003cetiqueta\u003e, \u003cdestino\u003e\n```\n\n**Ejemplo:**\n```rif\nneed LABEL target\nreldis target, offset\nemit cbits offset.bits  ; Emite como branching offset\n```\n\n**Comportamiento:**\n- Computa `target_address - current_pc`\n- Almacena el desplazamiento en el operador destino\n- \u00datil para instrucciones de salto relativo\n\n---\n\n### `emitaddress`\n\n**Prop\u00f3sito:** Emite la direcci\u00f3n de una etiqueta.\n\n**Sintaxis:**\n```rif\nemitaddress \u003cetiqueta\u003e\n```\n\n**Ejemplo:**\n```rif\nneed LABEL start\nemitaddress start  ; Emite los bytes de la direcci\u00f3n\n```\n\n**Comportamiento:**\n- Resuelve la direcci\u00f3n de la etiqueta\n- Emite los bytes correspondientes (tama\u00f1o depende de arquitectura)\n\n---\n\n### `fillid` / `vfillid`\n\n**Prop\u00f3sito:** Resuelve IDs de objetos fillables (datos generados por plugins).\n\n**Sintaxis:**\n```rif\nfillid \u003cnombre\u003e, \u003cdestino\u003e\nvfillid \u003cnombre\u003e, \u003cdestino\u003e\n```\n\n**Ejemplo:**\n```rif\nfillid image_data, id\nemit ccbit id.bits  ; Emite el ID del fillable\n```\n\n**Comportamiento:**\n- Busca el fillable en `fills.json`\n- `fillid` obtiene el ID num\u00e9rico\n- `vfillid` obtiene informaci\u00f3n adicional del fillable\n- Los IDs se asignan durante la fase de build\n\n---\n\n### `align`\n\n**Prop\u00f3sito:** Alinea la posici\u00f3n actual a un l\u00edmite de N bytes.\n\n**Sintaxis:**\n```rif\nalign \u003cn_bytes\u003e\n```\n\n**Ejemplo:**\n```rif\nemit_code_section\nalign 4  ; Asegura alineaci\u00f3n a 4 bytes\nemit 11110000\n```\n\n**Comportamiento:**\n- Si la posici\u00f3n actual no est\u00e1 alineada, inserta padding\n- Completa hasta el siguiente m\u00faltiplo de N bytes\n- Usa bytes `0x00` por defecto para rellenar\n\n---\n\n### `pad`\n\n**Prop\u00f3sito:** Inserta exactamente N bytes de relleno.\n\n**Sintaxis:**\n```rif\npad \u003cn_bytes\u003e\n```\n\n**Ejemplo:**\n```rif\nemit_header\npad 16  ; Reserva 16 bytes\n```\n\n**Comportamiento:**\n- Inserta bytes de relleno sin comprometer la estructura\n- No modifica la posici\u00f3n l\u00f3gica\n- \u00datil para reservar espacio en ROMs\n\n---\n\n## \ud83d\udd27 Patrones Comunes\n\n### Patr\u00f3n 1: Captura y Emisi\u00f3n B\u00e1sica\n```rif\nrule op_add:\n    need REG dest, REG src\n    emit 00 dest.bits src.bits\n```\n\n### Patr\u00f3n 2: Validaci\u00f3n Condicional\n```rif\nrule imm_load:\n    need REG dest, VALUE imm\n    fits imm, 16\n    emit 0001 dest.bits, imm.bits\n```\n\n### Patr\u00f3n 3: Concatenaci\u00f3n de Bits\n```rif\nrule multi_field:\n    need REG r1, REG r2, VALUE flags\n    bitcat r1.bits, r2.bits, flags.value, combined\n    emit ccbit combined.bits\n```\n\n### Patr\u00f3n 4: Rutinas Reutilizables\n```rif\nrule prologue:\n    need VALUE stack_size\n    emit ... ; c\u00f3digo de pr\u00f3logo\n\nrule main_routine:\n    need VALUE sz\n    call prologue\n    need VALUE body_size\n    emit ... ; c\u00f3digo del cuerpo\n```\n\n### Patr\u00f3n 5: Direccionamiento Relativo\n```rif\nrule branch_forward:\n    need LABEL target\n    reldis target, distance\n    fits distance, 12\n    emit 111 distance.bits\n```\n\n---\n\n## \ud83d\udc1b Debugging y Tips\n\n### Habilitar Logs Detallados\n```bash\npython -m rif compile pack.json instruction --verbose\n```\n\n### Verificar Tabla de S\u00edmbolos\n```bash\npython -m rif parse pack.json\n```\n\n### An\u00e1lisis de Emisi\u00f3n\nUsa `--debug` para ver c\u00f3mo se procesan los placeholders:\n```bash\npython -m rif build proyecto --debug\n```\n\n---\n\n## \ud83d\udcda Referencia R\u00e1pida\n\n| Instrucci\u00f3n | Entrada | Salida | Efecto |\n|-------------|---------|--------|--------|\n| `need` | L\u00ednea de tokens | Operador guardado | Captura |\n| `emit` | Fragmentos | Bytes al stream | Serializaci\u00f3n |\n| `call` | Nombre de regla | Ejecuci\u00f3n inline | Reutilizaci\u00f3n |\n| `bitcat` | M\u00faltiples fragmentos | Concatenaci\u00f3n | Composici\u00f3n |\n| `reloc` | Etiqueta | Registro al linker | Defer |\n| `align` | N bytes | Padding | Alineaci\u00f3n |\n| `fits` | Valor, bits | Error o OK | Validaci\u00f3n |\n| `zext`/`sext` | Valor, bits | Extensi\u00f3n | Conversi\u00f3n |\n| `reldis` | Etiqueta | Offset relativo | PC-rel |\n\n---\n\n## \ud83d\udd17 V\u00e9ase Tambi\u00e9n\n\n- [Estructura Interna del Plugin](estructura.md)\n- [Mecanismos de Importaci\u00f3n](importar.md)\n- [Integraci\u00f3n VS Code (VSIX)](1_vsix.md)\n",
      "plugin_basics/vsix": "# \ud83d\udd0c Integraci\u00f3n VS Code (VSIX)\n\nRIF puede compilar una extensi\u00f3n VS Code profesional en formato `.vsix` desde los metadatos de los plugins. Este soporte est\u00e1 en estado **RIF 0.0.3 Semi Stable**: es un generador completo de extensiones de lenguaje con soporte TextMate, snippets, autocompletado, hovers, diagn\u00f3sticos y quick fixes.\n\n---\n\n## \u2728 Capacidades Incluidas\n\n### Funcionalidades del Lenguaje\n\n- **Resaltado de Sintaxis TextMate** - Colorizaci\u00f3n autom\u00e1tica de directivas, palabras clave y operadores\n- **Autocompletado Inteligente** - Snippets contextuales para agilizar la escritura\n- **Hover con Documentaci\u00f3n** - Informaci\u00f3n en formato Markdown al pasar el cursor\n- **Diagn\u00f3sticos por Regex** - Validaci\u00f3n de patrones comunes durante la escritura\n- **Quick Fixes** - Sugerencias autom\u00e1ticas para arreglar problemas detectados\n- **S\u00edmbolos de Documento** - Navegaci\u00f3n r\u00e1pida por etiquetas y reglas\n- **Asociaci\u00f3n de Extensiones** - Vinculaci\u00f3n autom\u00e1tica con extensiones personalizadas\n\n### Distribuci\u00f3n\n\n- **Documentaci\u00f3n Embebida** - Todo el contenido incluido en el VSIX\n- **Assets Empaquetados** - Iconos, im\u00e1genes y recursos dentro del paquete\n- **Independencia** - No requiere servidor de lenguaje externo\n- **Instalaci\u00f3n Sencilla** - Un comando para instalar en VS Code\n\n---\n\n## \ud83d\ude80 Compilar un VSIX desde Plugins\n\n### Forma Recomendada (Nueva)\n\n```bash\npython -m rif compile --vscode \\\n  --ext .gbasm \\\n  --icon rif/plugins/gba/vscode/assets/gba-memory.svg \\\n  --p gba sound fonts basics \\\n  -o build/vscode/rif-gba-sound-fonts-basics-0.2.0.vsix\n```\n\n### Forma Alternativa (Antigua, a\u00fan compatible)\n\n```bash\npython -m rif compile --vscode \\\n  gba sound fonts basics \\\n  --ext .gbasm \\\n  --icon rif/plugins/gba/vscode/assets/gba-memory.svg\n```\n\n### Argumentos CLI\n\n| Argumento | Forma corta | Descripci\u00f3n |\n|-----------|------------|-----------|\n| `--vscode` | - | Activa el compilador de extensiones VS Code |\n| `--p` / `--plugins` | - | Lista los plugins que aportan bundles `vscode/` |\n| `--ext` | - | Fuerza la extensi\u00f3n de archivo (ej: `.gbasm`, `.rif`) |\n| `-icon` / `--icon` | - | Ruta al archivo de icono (PNG, JPG, GIF, WebP, SVG) |\n| `-o` / `--output` | - | Ruta de salida del archivo `.vsix` |\n\n---\n\n## \ud83d\udce6 Estructura de Salida\n\nEl VSIX se genera por defecto en:\n```\nbuild/vscode/rif-{plugins}-{version}.vsix\n```\n\nEjemplo:\n```\nbuild/vscode/rif-gba-sound-fonts-basics-0.2.0.vsix\n```\n\n---\n\n## \ud83d\udd27 Instalaci\u00f3n en VS Code\n\nDespu\u00e9s de compilar, instala la extensi\u00f3n:\n\n```bash\npython -m rif install --vscode build/vscode/rif-gba-sound-fonts-basics-0.2.0.vsix\n```\n\n### Requisitos Previos\n\n- VS Code debe estar instalado\n- El comando `code` debe estar disponible en el PATH\n\n### Si `code` no est\u00e1 en el PATH\n\n1. Abre la **Paleta de Comandos** en VS Code (`Ctrl+Shift+P` / `Cmd+Shift+P`)\n2. Escribe: `Shell Command: Install 'code' command in PATH`\n3. Presiona Enter\n4. Reinicia la terminal si es necesario\n\n### Verificaci\u00f3n Manual\n\n```bash\n# Verificar que code est\u00e9 disponible\nwhich code\n\n# Instalar manualmente si falla el autodetecci\u00f3n\n# (Busca la carpeta de instalaci\u00f3n de VS Code en tu sistema)\n```\n\n---\n\n## \ud83c\udfd7\ufe0f Armar Soporte VSIX para tu Plugin\n\n### Estructura de Directorios\n\nCada plugin puede incluir metadatos de VS Code:\n\n```text\nmi_plugin/\n  pack.json\n  README.md\n  vscode/\n    build.json\n    syntaxs.json\n    doc.json\n    assets/\n      icon.svg\n      logo.png\n```\n\n### 1. `build.json` - Identidad de la Extensi\u00f3n\n\nDefine los metadatos de la extensi\u00f3n en el Marketplace:\n\n```json\n{\n  \"displayName\": \"RIF Mi ISA\",\n  \"description\": \"Soporte VS Code para mi arquitectura ISA personalizada.\",\n  \"author\": {\n    \"name\": \"Mi Nombre\",\n    \"url\": \"https://ejemplo.com\"\n  },\n  \"version\": \"0.2.0\",\n  \"license\": \"MIT\",\n  \"extensions\": [\".miisa\", \".mi-asm\"],\n  \"categories\": [\"Programming Languages\", \"Snippets\"],\n  \"keywords\": [\"rif\", \"assembler\", \"mi-isa\", \"compilador\"]\n}\n```\n\n**Campos:**\n- `displayName` \u2b50 - Nombre que aparece en VS Code\n- `description` - Descripci\u00f3n breve\n- `version` - Versi\u00f3n sem\u00e1ntica (ej: `0.2.0`)\n- `extensions` - Extensiones de archivo asociadas\n- `categories` - Categor\u00edas en el Marketplace\n- `keywords` - Palabras clave para b\u00fasqueda\n- `license` - Tipo de licencia\n- `author` - Informaci\u00f3n del desarrollador\n\n### 2. `syntaxs.json` - Vocabulario y Diagn\u00f3sticos\n\nDefine palabras clave, colores, completados y diagn\u00f3sticos:\n\n```json\n{\n  \"directives\": [\".text\", \".data\", \".bss\"],\n  \"builtins\": [\"need\", \"emit\", \"call\", \"align\"],\n  \"keywords\": [\"mov\", \"add\", \"jump\", \"call\"],\n  \"types\": [\"u8\", \"u16\", \"u32\", \"u64\"],\n  \"registers\": [\"R0\", \"R1\", \"R2\", \"R3\"],\n  \"completions\": [\n    {\n      \"label\": \"mov\",\n      \"insertText\": \"mov ${1:R0}, ${2:R1}\",\n      \"detail\": \"Mi ISA\",\n      \"documentation\": \"Copia datos de un registro a otro.\",\n      \"kind\": \"Snippet\",\n      \"sortText\": \"001\"\n    },\n    {\n      \"label\": \".section\",\n      \"insertText\": \".section ${1:name}\\n    ${2:contenido}\",\n      \"detail\": \"Directiva\",\n      \"kind\": \"Keyword\"\n    }\n  ],\n  \"patterns\": [\n    {\n      \"name\": \"keyword.operator.rif\",\n      \"match\": \"\\\\b(?:=|,|:|;)\\\\b\"\n    },\n    {\n      \"name\": \"constant.language.boolean.rif\",\n      \"match\": \"\\\\b(?:true|false|on|off)\\\\b\"\n    }\n  ],\n  \"errors\": [\n    {\n      \"match\": \"\\\\bjump\\\\s+PC\\\\b\",\n      \"message\": \"Evita saltar expl\u00edcitamente a PC.\",\n      \"severity\": \"warning\",\n      \"code\": \"jump-pc\",\n      \"suggest\": \"Usa etiquetas en lugar de direcciones hardcodeadas.\"\n    },\n    {\n      \"match\": \"^\\\\s*emit\\\\s*$\",\n      \"message\": \"emit requiere bits, un placeholder o una variable.\",\n      \"severity\": \"error\",\n      \"code\": \"rif-empty-emit\"\n    }\n  ]\n}\n```\n\n**Secciones:**\n\n#### `directives`\nPalabras clave que comienzan con punto (`.pack`, `.rules`, etc.)\n\n#### `builtins`\nFunciones/instrucciones fundamentales del lenguaje\n\n#### `keywords`\nPalabras clave de dominio espec\u00edfico (mnem\u00f3nicos, etc.)\n\n#### `types`\nTipos de dato reconocidos\n\n#### `registers`\nNombres de registros disponibles\n\n#### `completions`\nArray de sugerencias de autocompletado\n\n**Campos de completion:**\n- `label` - Texto mostrado en el men\u00fa\n- `insertText` - C\u00f3digo insertado (puede incluir `${1:placeholder}`)\n- `documentation` - Descripci\u00f3n al seleccionar\n- `kind` - Tipo (Snippet, Keyword, Function, etc.)\n- `sortText` - Orden en el men\u00fa (n\u00fameros sortean primero)\n\n#### `patterns`\nReglas TextMate para colorizaci\u00f3n\n\n#### `errors`\nDiagn\u00f3sticos por expresi\u00f3n regular\n\n**Campos de error:**\n- `match` - Regex para detectar el problema\n- `message` - Mensaje de error\n- `severity` - `error`, `warning` o `hint`\n- `code` - ID \u00fanico del diagn\u00f3stico\n- `suggest` - Quick fix sugerido\n\n### 3. `doc.json` - Documentaci\u00f3n en Hovers\n\nDefine documentaci\u00f3n que aparece al pasar el cursor sobre palabras:\n\n```json\n{\n  \"words\": {\n    \"rif_project\": {\n      \"doc\": [\n        {\n          \"type\": \"text\",\n          \"content\": \"RIF separa arquitectura, herramientas y proyecto.\"\n        },\n        {\n          \"type\": \"code\",\n          \"content\": \".pack\\nplugin \\\"basics\\\"\\nplugin \\\"gba\\\"\"\n        }\n      ]\n    },\n    \"need\": {\n      \"doc\": [\n        {\n          \"type\": \"text\",\n          \"content\": \"Consume y valida operandos de una regla.\"\n        },\n        {\n          \"type\": \"code\",\n          \"content\": \"need VALUE, imm\"\n        },\n        {\n          \"type\": \"text\",\n          \"content\": \"Soporta m\u00faltiples tipos separados por comas.\"\n        }\n      ]\n    },\n    \"emit\": {\n      \"doc\": [\n        {\n          \"type\": \"text\",\n          \"content\": \"Emite bits o placeholders ya capturados.\"\n        },\n        {\n          \"type\": \"code\",\n          \"content\": \"emit imm.binary\"\n        }\n      ]\n    }\n  }\n}\n```\n\n**Estructura:**\n- `words` - Diccionario de palabra \u2192 documentaci\u00f3n\n- `doc` - Array de bloques de documentaci\u00f3n\n- `type` - `\"text\"` o `\"code\"`\n- `content` - Contenido del bloque\n\n---\n\n## \ud83d\udccb Flujo Recomendado\n\n### Para un Nuevo Plugin con Soporte VS Code\n\n```\n1. Define o ajusta tu pack.json\n   \u2193\n2. Crea la carpeta vscode/\n   \u251c\u2500\u2500 build.json  (identidad)\n   \u251c\u2500\u2500 syntaxs.json (vocabulario)\n   \u251c\u2500\u2500 doc.json    (documentaci\u00f3n)\n   \u2514\u2500\u2500 assets/\n       \u2514\u2500\u2500 icon.svg (opcional)\n   \u2193\n3. Compila el VSIX\n   $ python -m rif compile --vscode --p tu_plugin basics\n   \u2193\n4. Instala en VS Code\n   $ python -m rif install --vscode build/vscode/rif-tu-plugin.vsix\n   \u2193\n5. Abre un archivo con la extensi\u00f3n configurada\n   \u2193\n6. Ajusta completions, diagn\u00f3sticos y hovers\n   seg\u00fan lo que se necesite mejorar\n   \u2193\n7. Vuelve a compilar e instalar\n```\n\n---\n\n## \ud83c\udfa8 Ejemplo Completo: Plugin GBA\n\n### Estructura\n\n```\nrif/plugins/gba/\n  pack.json\n  README.md\n  vscode/\n    build.json\n    syntaxs.json\n    doc.json\n    assets/\n      gba-memory.svg\n```\n\n### build.json\n\n```json\n{\n  \"displayName\": \"RIF Game Boy Advance\",\n  \"description\": \"Ensamblador retargetable para GBA con Thumb y ARM.\",\n  \"version\": \"0.2.0\",\n  \"extensions\": [\".gbasm\"],\n  \"categories\": [\"Programming Languages\"],\n  \"keywords\": [\"gba\", \"gameboy\", \"arm\", \"thumb\", \"assembler\"]\n}\n```\n\n### Compilaci\u00f3n\n\n```bash\npython -m rif compile --vscode \\\n  --ext .gbasm \\\n  --icon rif/plugins/gba/vscode/assets/gba-memory.svg \\\n  --p gba sound fonts basics\n```\n\n### Resultado\n\n```\nbuild/vscode/rif-gba-sound-fonts-basics-0.2.0.vsix\n```\n\n---\n\n## \ud83d\udd0d Debugging de Extensiones\n\n### Verificar el Contenido del VSIX\n\nLos archivos `.vsix` son ZIP:\n\n```bash\nunzip -l build/vscode/rif-gba.vsix\n```\n\n### Buscar Errores Comunes\n\n```bash\n# Verificar que los archivos JSON sean v\u00e1lidos\npython -m json.tool rif/plugins/tu_plugin/vscode/build.json\n\n# Validar sintaxis de regex en syntaxs.json\npython -c \"import re; re.compile(r'tu_regex')\"\n```\n\n### Recargar la Extensi\u00f3n\n\nEn VS Code despu\u00e9s de cambios:\n1. Presiona `Ctrl+Shift+P` (Windows/Linux) o `Cmd+Shift+P` (Mac)\n2. Escribe `Reload Window`\n3. Presiona Enter\n\n### Abrir Consola de Desarrollo\n\n```\nHelp \u2192 Toggle Developer Tools\n```\n\nAqu\u00ed puedes ver errores de la extensi\u00f3n en tiempo real.\n\n---\n\n## \ud83d\udcca Casos de Uso\n\n### Caso 1: Extensi\u00f3n Solo para GBA\n\n```bash\npython -m rif compile --vscode \\\n  --ext .gbasm \\\n  --p gba basics\n```\n\n### Caso 2: Extensi\u00f3n Multi-Arquitectura\n\n```bash\npython -m rif compile --vscode \\\n  --ext .rif \\\n  --p gba atari2600 amd64 basics\n```\n\n### Caso 3: Extensi\u00f3n con Icono Personalizado\n\n```bash\npython -m rif compile --vscode \\\n  --ext .myasm \\\n  --icon my_logo.svg \\\n  --p mi_plugin basics \\\n  -o build/vscode/mi-extension.vsix\n```\n\n---\n\n## \ud83d\udc1b Soluci\u00f3n de Problemas\n\n### \"El comando `code` no se encuentra\"\n\n**Soluci\u00f3n:**\n```bash\n# En Windows\n\"C:\\Program Files\\Microsoft VS Code\\bin\\code.cmd\"\n\n# En macOS\n/Applications/Visual\\ Studio\\ Code.app/Contents/Resources/app/bin/code\n\n# En Linux (usualmente ya est\u00e1 en PATH)\nwhich code\n```\n\n### La extensi\u00f3n no se instala\n\n```bash\n# Verifica que VS Code est\u00e9 cerrado\n# Intenta con ruta absoluta\npython -m rif install --vscode /full/path/to/extension.vsix\n\n# O instala manualmente en VS Code\n# Extensions \u2192 Install from VSIX\n```\n\n### Los hovers no aparecen\n\n1. Verifica que `doc.json` sea v\u00e1lido\n2. Aseg\u00farate de que las claves en `doc.json` coincidan con las palabras clave\n3. Recarga la ventana de VS Code\n\n### Autocompletado no funciona\n\n1. Revisa que `syntaxs.json` tenga la secci\u00f3n `completions`\n2. Verifica que `kind` sea un valor v\u00e1lido\n3. Usa `sortText` para controlar el orden\n\n---\n\n## \ud83d\udd17 V\u00e9ase Tambi\u00e9n\n\n- [Cat\u00e1logo de Instrucciones](0_instrucciones.md) - Documentaci\u00f3n de directivas\n- [Estructura Interna del Plugin](estructura.md) - C\u00f3mo crear plugins\n- [Mecanismos de Importaci\u00f3n](importar.md) - Carga de plugins\n",
      "plugin_fonts": "# SX7 Fonts Plugin\n\nPlugin de fuentes bitmap retargetables para SX7/RIF.\n\nEstructura principal:\n\n```txt\nfonts/\n\u251c\u2500\u2500 cli.py\n\u251c\u2500\u2500 cli/\n\u2502   \u251c\u2500\u2500 add.py\n\u2502   \u251c\u2500\u2500 common.py\n\u2502   \u251c\u2500\u2500 delete.py\n\u2502   \u251c\u2500\u2500 editor.py\n\u2502   \u251c\u2500\u2500 list.py\n\u2502   \u251c\u2500\u2500 modify.py\n\u2502   \u2514\u2500\u2500 open.py\n\u2514\u2500\u2500 bitmap/\n    \u251c\u2500\u2500 lexer.py\n    \u251c\u2500\u2500 parser.py\n    \u2514\u2500\u2500 font-5x7x1.f\n```\n\nFormato `.f`:\n\n```txt\nfont SX7\nsize 5, 7, 1 ; 5 bits, 7 filas, 1 byte por fila.\nalign right\n\nA:\n   01110\n   10001\n   10001\n   11111\n   10001\n   10001\n   10001\n```\n\n`size 5, 7, 1` significa:\n\n- `5`: bits visuales por fila.\n- `7`: filas por glyph.\n- `1`: bytes fisicos por fila.\n\nCLI:\n\n```bash\npython fonts/cli.py fonts\npython fonts/cli.py list\npython fonts/cli.py modify font-5x7x1.f A\npython fonts/cli.py add font-5x7x1.f T\npython fonts/cli.py delete font-5x7x1.f T\npython fonts/cli.py open font-5x7x1.f\n```\n\nEn RIF, la forma esperada seria equivalente a:\n\n```bash\npython -m rif -pcli fonts fonts\npython -m rif -pcli fonts modify font-5x7x1.f A\n```\n\nAPI minima:\n\n```python\nfrom fonts.bitmap.parser import load_font\n\nfont = load_font(\"fonts/bitmap/font-5x7x1.f\")\nprint(font.get_ascii_entry(\"A\"))\n# [65, [14, 17, 17, 31, 17, 17, 17]]\n```\n\n\n## Formato Bitmap\n# Formato Bitmap\n\nLas fuentes `.f` usan formato SX7:\n\n```txt\nfont SX7\nsize 5, 7, 1\nalign right\n\nA:\n   01110\n   10001\n   10001\n   11111\n   10001\n   10001\n   10001\n```\n\n`size 5, 7, 1` significa 5 bits visibles, 7 filas y 1 byte fisico por fila.\n\n\n## Fillables\n# Fillables\n\nEl plugin `fonts` expone fillables para el linker.\n\n```rif\n@fill_bitmap_array_logo\n```\n\nEl linker busca funciones `fill_*` en los plugins declarados por el `.pack`, ejecuta la funcion y pega el texto retornado en el codigo fuente antes de compilar.\n\nEsto permite crear tablas o datos repetitivos sin hardcodear macros dentro del core.\n\n## Texto 5x7x1\n\nLa forma inversa de fillables permite poner primero el dato y despues la funcion:\n\n```rif\n@\"ESTO ES UN TEXTO\"@fonts_fill_5x7x1\n```\n\n`fonts_fill_5x7x1` genera una tabla `u8[]` con 7 bytes por glifo usando `font-5x7x1.f`, registra el resultado en `fills.json` y usa cache de proyecto para evitar recalcular el mismo texto.\n",
      "plugin_fonts/formato_bitmap": "# Formato Bitmap\n\nLas fuentes `.f` usan formato SX7:\n\n```txt\nfont SX7\nsize 5, 7, 1\nalign right\n\nA:\n   01110\n   10001\n   10001\n   11111\n   10001\n   10001\n   10001\n```\n\n`size 5, 7, 1` significa 5 bits visibles, 7 filas y 1 byte fisico por fila.\n",
      "plugin_fonts/fillables": "# Fillables\n\nEl plugin `fonts` expone fillables para el linker.\n\n```rif\n@fill_bitmap_array_logo\n```\n\nEl linker busca funciones `fill_*` en los plugins declarados por el `.pack`, ejecuta la funcion y pega el texto retornado en el codigo fuente antes de compilar.\n\nEsto permite crear tablas o datos repetitivos sin hardcodear macros dentro del core.\n\n## Texto 5x7x1\n\nLa forma inversa de fillables permite poner primero el dato y despues la funcion:\n\n```rif\n@\"ESTO ES UN TEXTO\"@fonts_fill_5x7x1\n```\n\n`fonts_fill_5x7x1` genera una tabla `u8[]` con 7 bytes por glifo usando `font-5x7x1.f`, registra el resultado en `fills.json` y usa cache de proyecto para evitar recalcular el mismo texto.\n",
      "plugin_gba": "# \ud83c\udfae Plugin GBA para RIF - Documentaci\u00f3n Completa\n\nEste es el m\u00f3dulo oficial de **Game Boy Advance (GBA)** para el framework **Retargetable ISA Foundry (RIF)**. Proporciona un compilador completo del conjunto de instrucciones Thumb de 16-bits para la CPU ARM7TDMI, junto con herramientas de inyecci\u00f3n autom\u00e1tica de hardware, generaci\u00f3n de assets y emulaci\u00f3n integrada.\n\n---\n\n## \u2728 Caracter\u00edsticas Principales\n\n### Core del Compilador\n- **Compilador Thumb Nativo** - Sintaxis limpia para instrucciones ARM7TDMI de 16 bits (mov, add, cmp, bne, ldr, str)\n- **Formato Little-Endian** - Emisi\u00f3n correcta para el bus de 16-bits del GBA\n- **Validaci\u00f3n Autom\u00e1tica** - Verificaci\u00f3n de rangos y restricciones Thumb\n\n### Inyecci\u00f3n de Hardware\n- **Cabecera ROM Autom\u00e1tica** - Genera los primeros 192 bytes requeridos por la BIOS\n- **Logo de Nintendo** - Inyecci\u00f3n autom\u00e1tica del logo oficial (156 bytes comprimidos)\n- **Checksum Cruzado** - C\u00e1lculo matem\u00e1tico de validaci\u00f3n autom\u00e1tico\n- **Vector de Entrada** - Salto ARM\u2192Thumb transparente (bx r15)\n\n### Integraci\u00f3n de Assets\n- **Plugin Image** - Compatibilidad con `@fill_image_bitmap` (PNG/JPG/BMP \u2192 BGR555)\n- **Plugin Sound** - Soporte DMA para audio `@fill_sound_wav` (WAV/MP3 \u2192 PCM 8-bits)\n- **Plugin Fonts** - Renderizado de texto bitmap para pantalla inicial\n\n### Herramientas CLI\n- **Compilaci\u00f3n Integrada** - `python -m rif build ... --plugin gba`\n- **Emulador Autom\u00e1tico** - `python -m rif -pcli gba run archivo.gba`\n- **Instalaci\u00f3n de mGBA** - Descarga e instala el emulador autom\u00e1ticamente\n\n---\n\n## \ud83d\ude80 Inicio R\u00e1pido\n\n### 1. Compilar un Proyecto GBA\n\n```bash\n# Compilar el ejemplo oficial\npython -m rif build examples/gba --plugin gba --name example\n\n# Generar salida en examples/gba/gba.gba\n```\n\n### 2. Ejecutar en Emulador\n\n```bash\n# Instalar mGBA autom\u00e1ticamente (solo una vez)\npython -m rif -pcli gba install mGBA --add-path\n\n# Ejecutar el ROM en mGBA (sin duplicar ventanas)\npython -m rif -pcli gba run examples/gba/gba.gba -nd\n```\n\n### 3. Documentaci\u00f3n Interactiva\n\n```bash\n# Abre el navegador de ayuda local\npython -m rif help --open\n\n# Navega a GBA en el panel izquierdo\n```\n\n---\n\n## \ud83d\udcc1 Estructura del Proyecto\n\n### Directorios Clave\n\n```\nrif/plugins/gba/\n\u251c\u2500\u2500 README.md                 # Este archivo\n\u251c\u2500\u2500 cli.py                    # Interfaz de subcomandos (rif -pcli gba)\n\u251c\u2500\u2500 cli/\n\u2502   \u251c\u2500\u2500 install.py           # Instalador de emulador mGBA\n\u2502   \u2514\u2500\u2500 run.py               # Ejecutor de ROMs en emulador\n\u251c\u2500\u2500 fillables.py             # @fill_screen, @fill_screen_text\n\u251c\u2500\u2500 packs/example/\n\u2502   \u251c\u2500\u2500 gba.pack             # Punto de entrada principal\n\u2502   \u251c\u2500\u2500 gba.regs.pack        # Definici\u00f3n de registros R0-R15\n\u2502   \u251c\u2500\u2500 gba.sections.pack    # Mapeo de memoria (ROM, EWRAM, VRAM, etc.)\n\u2502   \u2514\u2500\u2500 gba.rules.pack       # Reglas Thumb y emisi\u00f3n\n\u251c\u2500\u2500 plugins/\n\u2502   \u251c\u2500\u2500 thumb_ins.py         # Int\u00e9rprete aritm\u00e9tico Thumb\n\u2502   \u251c\u2500\u2500 gba_headers.py       # Constructor de cabecera (0x00-0xBF)\n\u2502   \u251c\u2500\u2500 gba_logo.py          # Inyecci\u00f3n del logo Nintendo\n\u2502   \u251c\u2500\u2500 gba_checksum.py      # C\u00e1lculo de validaci\u00f3n\n\u2502   \u2514\u2500\u2500 gba_entry.py         # Inyector del salto ARM\u2192Thumb\n\u2514\u2500\u2500 vscode/\n    \u251c\u2500\u2500 build.json           # Metadatos de extensi\u00f3n VS Code\n    \u251c\u2500\u2500 syntaxs.json         # Vocabulario Thumb\n    \u251c\u2500\u2500 doc.json             # Documentaci\u00f3n en hovers\n    \u2514\u2500\u2500 assets/\n        \u2514\u2500\u2500 gba-memory.svg   # Icono para extensi\u00f3n\n```\n\n---\n\n## \ud83e\udde0 Arquitectura GBA\n\n### CPU ARM7TDMI - Dos Modos de Operaci\u00f3n\n\n| Modo | Tama\u00f1o | Uso Principal | Limitaciones |\n|------|--------|----------------|--------------|\n| **ARM (32 bits)** | 4 bytes | Booteo, IWRAM, alto rendimiento | Menos denso, cartucho limitado |\n| **Thumb (16 bits)** | 2 bytes | C\u00f3digo principal desde ROM | R0-R7 en la mayor\u00eda de instrucciones |\n\n**RIF emite c\u00f3digo Thumb nativo** para optimizar uso de cartucho.\n\n### Mapa de Memoria F\u00edsico\n\n| Secci\u00f3n | Direcci\u00f3n | Tama\u00f1o | Prop\u00f3sito |\n|---------|-----------|--------|----------|\n| **ROM** | 0x08000000 | 32 MB | Cartucho (c\u00f3digo e instrucciones) |\n| **EWRAM** | 0x02000000 | 256 KB | RAM externa (carga general) |\n| **IWRAM** | 0x03000000 | 32 KB | RAM interna (bucles cr\u00edticos) |\n| **I/O** | 0x04000000 | 1 KB | Registros MMIO (video, sonido, DMA) |\n| **Paleta** | 0x05000000 | 1 KB | CRAM (paletas BGR555) |\n| **VRAM** | 0x06000000 | 96 KB | Video RAM (p\u00edxeles, tiles, mapas) |\n| **OAM** | 0x07000000 | 1 KB | Memoria de sprites |\n\n---\n\n## \ud83d\udcd6 P\u00e1ginas de Documentaci\u00f3n\n\n### [0. Construcci\u00f3n y Ejecuci\u00f3n](0_build_y_run.md)\n- Flujo completo de compilaci\u00f3n\n- Herramientas CLI del plugin\n- Integraci\u00f3n con emulador mGBA\n- Flags de ejecuci\u00f3n\n\n### [1. Visi\u00f3n General de Arquitectura](1_overview.md)\n- Procesador ARM7TDMI y modos\n- Mapa de memoria detallado\n- Estructura interna del plugin\n- Sinergia con otros plugins\n\n### [2. Conjunto de Instrucciones Thumb](2_instrucciones.md)\n- 30+ instrucciones Thumb documentadas\n- Transferencia de datos\n- Aritm\u00e9tica y l\u00f3gica\n- Acceso a memoria (Load/Store)\n- Control de flujo (Saltos)\n- Stack (Push/Pop)\n- Declaraci\u00f3n de datos\n\n### [3. Registros de CPU y MMIO](3_registros.md)\n- Registros R0-R15 con restricciones\n- Convenci\u00f3n APCS de llamadas\n- Registros MMIO importantes (DISPCNT, KEYINPUT, etc.)\n- Memory-Mapped I/O completo\n\n### [4. Directivas Fillables](4_fillables.md)\n- `@fill_screen` - Rellenar pantalla con color\n- `@fill_screen_text` - Renderizar texto bitmap\n- `@fill_image_bitmap` - Convertir im\u00e1genes (PNG/JPG)\n- `@fill_sound_wav` - Procesar audio (WAV/MP3)\n\n### [5. Macros Estructurales de ROM](5_macros_rom.md)\n- `set_headers` - Cabecera y vector de salto\n- `set_logo` - Logo de Nintendo\n- `set_checksum` - Validaci\u00f3n de ROM\n- `set_entry_thumb` - Punto de entrada\n- `set_rompad` - Alineaci\u00f3n final\n\n---\n\n## \ud83d\udee0\ufe0f Secuencia B\u00e1sica de un Proyecto GBA\n\nToda ROM de GBA debe seguir esta estructura base:\n\n```rif\n.section .rom\nset_headers        # Cabecera: vector de salto ARM\nset_logo           # 156 bytes del logo Nintendo\nset_checksum       # T\u00edtulo, makers, checksum\nset_entry_thumb    # Salto a Thumb mode\nset_frame          # Inicializar video (Mode 3)\ngame_code          # Tu c\u00f3digo personalizado\nset_rompad         # Padding final\n```\n\n---\n\n## \ud83d\udcdd Ejemplos de C\u00f3digo\n\n### Ejemplo 1: Hello World M\u00ednimo\n\n```rif\n.pack\nplugin \"basics\"\nplugin \"gba\"\n\n.world\n\n.rules\ninit:\n    store r0 = 0x03\n    reloc abs, DISPCNT, 32\n    str r0, r1, r0\n    jump init\n```\n\n### Ejemplo 2: Cargar Color a VRAM\n\n```rif\n.pack\nplugin \"basics\"\nplugin \"gba\"\n\n.world\n\n.rules\nmain:\n    ; Cargar direcci\u00f3n de VRAM\n    store r0 = 0x06000000\n    store r1 = 0xFFFF      ; Color blanco BGR555\n    \n    ; Escribir en VRAM\n    str r1, r0, r0\n    \n    ; Saltar a s\u00ed mismo (bucle infinito)\n    jump main\n```\n\n### Ejemplo 3: Con Assets (Imagen)\n\n```bash\npython -m rif build proyecto_gba \\\n  --plugin gba \\\n  --plugin image \\\n  --name ejemplo_imagen\n```\n\nLuego en el c\u00f3digo:\n\n```rif\n.section .rom\nset_headers\nset_logo\nset_checksum\nset_entry_thumb\n\n; Cargar imagen de disco\n@fill_image_bitmap sprites.png mi_sprite\n\ngame_loop:\n    ; C\u00f3digo que usa mi_sprite\n    jump game_loop\n```\n\n### Ejemplo 4: Con Audio\n\n```bash\npython -m rif build proyecto_gba \\\n  --plugin gba \\\n  --plugin sound \\\n  --name ejemplo_audio\n```\n\nC\u00f3digo:\n\n```rif\n@fill_sound_wav bgm musica.mp3 16000\n\n; Luego en configuraci\u00f3n DMA:\n; bgm_dma_control (generado autom\u00e1ticamente)\n```\n\n---\n\n## \ud83c\udfa8 Generaci\u00f3n de Extensi\u00f3n VS Code\n\n### Crear VSIX con Soporte Thumb\n\n```bash\npython -m rif compile --vscode \\\n  --ext .gbasm \\\n  --icon rif/plugins/gba/vscode/assets/gba-memory.svg \\\n  --p gba basics\n```\n\n### Instalar en VS Code\n\n```bash\npython -m rif install --vscode build/vscode/rif-gba-basics-0.2.0.vsix\n```\n\n### Caracter\u00edsticas de la Extensi\u00f3n\n\n- \u2705 Resaltado de instrucciones Thumb\n- \u2705 Autocompletado de mnem\u00f3nicos\n- \u2705 Hovers con documentaci\u00f3n\n- \u2705 Diagn\u00f3sticos por regex\n- \u2705 Quick fixes para errores comunes\n\n---\n\n## \ud83d\udc1b Debugging y Tips\n\n### Verificar Compilaci\u00f3n\n\n```bash\n# Modo verbose\npython -m rif build proyecto --plugin gba --name test --verbose\n\n# Ver tabla de s\u00edmbolos\npython -m rif parse rif/plugins/gba/packs/example/gba.pack\n```\n\n### Inspeccionar ROM\n\n```bash\n# Ver primeros 192 bytes (cabecera)\nxxd -l 192 output.gba\n\n# Verificar tama\u00f1o final\nls -lh output.gba\n```\n\n### Emulador Avanzado\n\n```bash\n# Ejecutar sin duplicar ventanas (recomendado para dev)\npython -m rif -pcli gba run output.gba -nd\n\n# Especificar emulador diferente\npython -m rif -pcli gba run output.gba --emulator visualboyadvance\n```\n\n---\n\n## \u26a0\ufe0f Restricciones Thumb Importantes\n\n### Registros Limitados (R0-R7 en operaciones aritm\u00e9ticas)\n\n```rif\nadd r0, r1, r2    ; \u2705 V\u00e1lido (todos \u003c R8)\nadd r8, r9, r10   ; \u274c Error (R8+ no accesibles en Thumb)\nadd r0, r8, r1    ; \u274c Error (R8 no permitido)\n```\n\n### VRAM No Soporta Bytes\n\n```rif\n; Escribir en VRAM siempre de 16 bits (halfword) o m\u00e1s\nstrh r0, r1, r2   ; \u2705 V\u00e1lido (16 bits)\nstrb r0, r1, r2   ; \u274c Error en VRAM (byte)\n```\n\n### Inmediatos Limitados\n\n```rif\nstore r0 = 255    ; \u2705 V\u00e1lido (0-255)\nstore r0 = 256    ; \u274c Error (\u003e 255)\nstore r0 = 0x04000000  ; \u274c Error (demasiado grande)\n```\n\n**Soluci\u00f3n para direcciones grandes:**\n\n```rif\n; Usar relocaciones\nreloc abs, DISPCNT, 32  ; Resuelve la direcci\u00f3n en link-time\n```\n\n---\n\n## \ud83d\udd17 Sinergia con Otros Plugins\n\n### Con Plugin `image`\n\n```bash\npython -m rif build proyecto --plugin gba --plugin image\n```\n\n```rif\n@fill_image_bitmap titulo.png pantalla_titulo\n```\n\n### Con Plugin `sound`\n\n```bash\npython -m rif build proyecto --plugin gba --plugin sound\n```\n\n```rif\n@fill_sound_wav tema_principal intro.mp3 22050\n```\n\n### Con Plugin `fonts`\n\n```bash\npython -m rif build proyecto --plugin gba --plugin fonts\n```\n\n```rif\n@fill_screen_text \"RIF GBA\" white black pantalla_inicio\n```\n\n---\n\n## \ud83d\udcda Referencia R\u00e1pida\n\n### Instrucciones M\u00e1s Comunes\n\n| Instrucci\u00f3n | Formato | Descripci\u00f3n |\n|-------------|---------|-----------|\n| `store` | `store Rd = imm` | Carga inmediato (0-255) |\n| `move` | `move Rd, Rs` | Copia registro |\n| `add` | `add Rd, Rs, Rn` | Suma |\n| `sub` | `sub Rd, Rs, Rn` | Resta |\n| `ldr` | `ldr Rd, Rb, Ro` | Lee 32 bits |\n| `str` | `str Rd, Rb, Ro` | Escribe 32 bits |\n| `beq` | `beq label` | Salta si igual |\n| `bne` | `bne label` | Salta si diferente |\n| `jump` | `jump label` | Salto incondicional |\n| `call` | `call label` | Salto y guarda retorno |\n| `push` | `push Rd` | Empuja a pila |\n| `pop` | `pop Rd` | Extrae de pila |\n\n### Registros Especiales\n\n| Registro | Alias | Prop\u00f3sito |\n|----------|-------|----------|\n| R13 | SP | Stack Pointer |\n| R14 | LR | Link Register (retorno) |\n| R15 | PC | Program Counter (actual + 4) |\n\n---\n\n## \ud83c\udfaf Flujo Recomendado de Desarrollo\n\n```\n1. Dise\u00f1a la arquitectura de tu juego\n   \u2193\n2. Crea estructura base del .pack\n   \u2193\n3. Implementa el main loop\n   \u2193\n4. Agrega gr\u00e1ficos (@fill_image_bitmap)\n   \u2193\n5. Integra audio (@fill_sound_wav)\n   \u2193\n6. Prueba en mGBA (python -m rif -pcli gba run...)\n   \u2193\n7. Optimiza usando profiler del emulador\n   \u2193\n8. Genera VSIX para desarrollo en VS Code\n```\n\n---\n\n## \ud83d\udcde Soporte y Comunidad\n\n- **Documentaci\u00f3n Principal**: `rif/help/README.md`\n- **Issues y Bugs**: GitHub Issues del repositorio\n- **Ejemplos**: `examples/gba/` en el repo\n- **Discusiones**: GitHub Discussions\n\n---\n\n## \ud83d\udcc4 Licencia\n\nEl plugin GBA forma parte de RIF, licenciado bajo MIT.\n\n---\n\n## \ud83d\udd0d \u00cdndice de P\u00e1ginas\n\n1. [Construcci\u00f3n y Ejecuci\u00f3n](0_build_y_run.md)\n2. [Visi\u00f3n General de Arquitectura](1_overview.md)\n3. [Conjunto de Instrucciones Thumb](2_instrucciones.md)\n4. [Registros de CPU y MMIO](3_registros.md)\n5. [Directivas Fillables](4_fillables.md)\n6. [Macros Estructurales de ROM](5_macros_rom.md)\n\n\n## Build Y Run\n# Construcci\u00f3n y Ejecuci\u00f3n de Proyectos GBA\n\nEl entorno RIF cuenta con un flujo completo y automatizado para orquestar la fusi\u00f3n de tu c\u00f3digo ensamblador con recursos como audio e im\u00e1genes, construyendo directamente im\u00e1genes de ROM (`.gba`) v\u00e1lidas.\n\n## \ud83d\udd28 Compilar un Proyecto\n\nDado que el plugin GBA asume el control del entorno para inyectar su set de instrucciones Thumb y su mapeo de cabeceras, la compilaci\u00f3n de proyectos requiere que invoques el empaquetador indicando el plugin GBA:\n\n```bash\n# Formato general de construcci\u00f3n:\npython -m rif build \u003cruta_al_directorio_fuente\u003e --plugin gba --name \u003cnombre_del_pack\u003e\n\n# Ejemplo oficial:\npython -m rif build examples/gba --plugin gba --name example\n```\n\nAl ejecutar este comando, RIF har\u00e1 lo siguiente:\n1. Extraer\u00e1 las reglas y metadatos alojados en `rif/plugins/gba/packs/example/`.\n2. Evaluar\u00e1 secuencialmente cada archivo con extensi\u00f3n `.gbasm` dentro del directorio especificado.\n3. Inyectar\u00e1 llamadas din\u00e1micas (como conversi\u00f3n de audio e im\u00e1genes) si usas macros como `@fill_sound_wav`.\n4. Renderizar\u00e1 en consola un elegante reporte visual indicando el tama\u00f1o (Bytes), la ubicaci\u00f3n l\u00f3gica en memoria de tus bloques, el Hash `SHA256` y los offsets de enlace (Linker Labels) generados.\n\nEl binario resultante se depositar\u00e1 en el directorio fuente bajo el nombre `\u003cdirectorio\u003e.gba` (en el caso del ejemplo: `examples/gba/gba.gba`).\n\n---\n\n## \ud83c\udfae Ejecuci\u00f3n en Emuladores (CLI nativo)\n\nEl plugin GBA incorpora herramientas especializadas accesibles bajo el prefijo CLI de RIF `-pcli gba`.\n\nSi no tienes un emulador, el propio RIF puede descargar la \u00faltima versi\u00f3n port\u00e1til del popular emulador **mGBA** e instalarla de forma local:\n\n```bash\n# Descarga e instala mGBA autom\u00e1ticamente:\npython -m rif -pcli gba install mGBA --add-path\n```\n\nUna vez tengas tu archivo `.gba` generado y tu emulador listo, puedes lanzar tu juego directamente desde la terminal de forma fluida:\n\n```bash\npython -m rif -pcli gba run examples/gba/gba.gba -nd\n```\n\n### \ud83d\udca1 Acerca del flag `-nd` (No Duplicates)\n\nEl flag `-nd` es de vital importancia durante el desarrollo. Cuando compilas iterativamente, no querr\u00e1s acumular cientos de ventanas del emulador abiertas. El motor de RIF rastrear\u00e1 activamente los hilos de `mGBA` a nivel de sistema operativo y reutilizar\u00e1 de forma forzada la ventana abierta anteriormente cerrando el proceso heredado antes de lanzar el nuevo.\n\n\n## Overview\n# Visi\u00f3n General: Arquitectura GBA\n\nEl plugin `gba` proporciona el soporte integral para compilar ROMs comerciales y homebrew de **Game Boy Advance** utilizando el ecosistema de cero-acoplamiento de RIF.\n\nA diferencia de los ensambladores convencionales, este plugin ense\u00f1a al compilador de RIF c\u00f3mo estructurar la cabecera exigida por el hardware de Nintendo, c\u00f3mo validar los sumatorios (checksums), y le inyecta la sem\u00e1ntica de la **CPU ARM7TDMI**.\n\n## \ud83e\udde0 Arquitectura y CPU\n\nEl coraz\u00f3n del GBA es un procesador ARM7TDMI que puede operar en dos modos:\n- **Estado ARM (32 bits)**: Reservado principalmente para el arranque o rutinas de alto rendimiento en IWRAM.\n- **Estado Thumb (16 bits)**: El modo principal usado para ejecutar c\u00f3digo desde el cartucho (ROM) debido a su mayor densidad y las limitaciones del bus de 16-bits.\n\nEl plugin **GBA de RIF emite c\u00f3digo Thumb** nativo, en formato *Little Endian*, lo que garantiza lecturas \u00f3ptimas desde el cartucho hacia el bus de la memoria sin necesidad de preprocesadores de terceros.\n\n---\n\n## \ud83d\uddfa\ufe0f Mapa F\u00edsico de Memoria (MMIO)\n\nEl plugin ya tiene pre-mapeadas las direcciones de estas secciones en su archivo `.pack`, permitiendo usar referencias directas como `r0, 0x06000000` (VRAM) o apoyarte en sus correspondientes tablas para relocaciones autom\u00e1ticas.\n\n| Secci\u00f3n (Hardware) | Direcci\u00f3n  | Tama\u00f1o | Rol Principal                                   |\n|--------------------|------------|--------|-------------------------------------------------|\n| `.rom` / ROM       | 0x08000000 | 32 MB  | Memoria flash del cartucho (Instrucciones)      |\n| `.ewram` / EWRAM   | 0x02000000 | 256 KB | Memoria de trabajo externa (Carga general)      |\n| `.iwram` / IWRAM   | 0x03000000 | 32 KB  | Memoria interna (Alt\u00edsima velocidad para bucles)|\n| `.io` / IO         | 0x04000000 | 1 KB   | Registros MMIO (Control de Video, Sonido, DMA)  |\n| `.palette`         | 0x05000000 | 1 KB   | Memoria CRAM (Paletas BGR555)                   |\n| `.vram` / VRAM     | 0x06000000 | 96 KB  | Video RAM (Pixeles, Tiles y Mapas)              |\n| `.oam` / OAM       | 0x07000000 | 1 KB   | Memoria de Atributos de Sprites (Objetos)       |\n\n---\n\n## \ud83d\udcc1 Estructura del Ecosistema\n\nTodo el soporte arquitect\u00f3nico de GBA vive dentro del directorio `rif/plugins/gba/`. Sus responsabilidades est\u00e1n estrictamente divididas:\n\n```text\nplugins/gba/\n\u251c\u2500\u2500 cli.py                    # \ud83d\udcbb Interfaz de subcomandos `rif -pcli gba`\n\u251c\u2500\u2500 cli/\n\u2502   \u251c\u2500\u2500 install.py            # Script que descarga mGBA autom\u00e1ticamente\n\u2502   \u2514\u2500\u2500 run.py                # Wrapper para inyectar la ROM al emulador\n\u251c\u2500\u2500 fillables.py              # \ud83c\udfa8 Directivas @fill_screen / @fill_screen_text\n\u251c\u2500\u2500 packs/example/\n\u2502   \u251c\u2500\u2500 gba.pack              # \u2699\ufe0f Punto de entrada: Importa el universo GBA\n\u2502   \u251c\u2500\u2500 gba.regs.pack         # \ud83d\uddc4\ufe0f Tabla de los 16 Registros (R0-R15)\n\u2502   \u251c\u2500\u2500 gba.sections.pack     # \ud83d\uddfa\ufe0f Inicializaci\u00f3n de los VOff y bloques\n\u2502   \u2514\u2500\u2500 gba.rules.pack        # \ud83d\udcd0 Expresiones regulares y reglas Thumb\n\u2514\u2500\u2500 plugins/\n    \u251c\u2500\u2500 thumb_ins.py          # \ud83e\udd16 Int\u00e9rprete aritm\u00e9tico del Set de Instrucciones\n    \u251c\u2500\u2500 gba_headers.py        # \ud83e\uddf1 Constructor binario de la Cabecera 0x00-0xBF\n    \u251c\u2500\u2500 gba_logo.py           # \ud83c\udf44 Inyecci\u00f3n estricta del Logo de Nintendo\n    \u251c\u2500\u2500 gba_checksum.py       # \ud83e\uddee C\u00f3mputo matem\u00e1tico de validaci\u00f3n\n    \u2514\u2500\u2500 gba_entry.py          # \ud83d\udeaa Inyector del salto ARM -\u003e Thumb (bx)\n```\n\n## \ud83e\udd1d Sinergia con otros Plugins\n\nGracias al dise\u00f1o agn\u00f3stico de RIF, el plugin GBA se beneficia autom\u00e1ticamente de:\n- **Plugin Image**: Si compilas tu proyecto GBA incluyendo `--plugin image`, ganar\u00e1s acceso a `@fill_image_bitmap` para insertar PNGs/BMPs comprimidos a formato VRAM de GBA.\n- **Plugin Sound**: Usando `--plugin sound`, puedes inyectar archivos `.wav` de 8-bits e invocar el DMA del GBA para hacer streaming de audio nativo hacia el altavoz de la consola.\n\n\n## Instrucciones\n# Conjunto de Instrucciones Thumb (GBA)\n\nLa consola GBA corre una CPU **ARM7TDMI** nativa. El framework de RIF compila sus instrucciones utilizando el modo **Thumb** (Instrucciones de 16-bits alineadas en formato *Little-Endian*), cumpliendo estrictamente con el manual de referencia t\u00e9cnica ARM (DDI 0029G).\n\n\u003e [!IMPORTANT]  \n\u003e En el estado Thumb de 16-bits, casi todas las instrucciones est\u00e1n limitadas a operar exclusivamente sobre los **registros bajos (R0-R7)** para ahorrar espacio en la codificaci\u00f3n binaria.\n\n---\n\n## \ud83e\uddee Transferencia de Datos\n\nEstas instrucciones permiten mover informaci\u00f3n entre los registros o cargar constantes.\n\n| Instrucci\u00f3n RIF | Equivalencia ARM | Descripci\u00f3n |\n| :--- | :--- | :--- |\n| `store Rd = imm` | `MOV Rd, #imm8` | Carga un n\u00famero inmediato (0-255) en un registro. |\n| `move Rd, Rs` | `ADD Rd, Rs, #0` | Copia el contenido del registro origen `Rs` al destino `Rd`. |\n| `lsl Rd, Rs, imm` | `LSL Rd, Rs, #imm5` | **L**ogical **S**hift **L**eft (Multiplica por 2^n). |\n| `lsr Rd, Rs, imm` | `LSR Rd, Rs, #imm5` | **L**ogical **S**hift **R**ight (Divide sin signo). |\n| `asr Rd, Rs, imm` | `ASR Rd, Rs, #imm5` | **A**rithmetic **S**hift **R**ight (Mantiene el signo). |\n\n## \u2694\ufe0f Aritm\u00e9tica y L\u00f3gica\n\nA diferencia de ARM, las instrucciones aritm\u00e9ticas de Thumb actualizan autom\u00e1ticamente las banderas (Flags) de condici\u00f3n en el registro CPSR (Condition Program Status Register).\n\n| Instrucci\u00f3n RIF | Equivalencia ARM | Descripci\u00f3n |\n| :--- | :--- | :--- |\n| `add Rd, Rs, Rn` | `ADD Rd, Rs, Rn` | Suma aritm\u00e9tica (`Rd = Rs + Rn`). |\n| `sub Rd, Rs, Rn` | `SUB Rd, Rs, Rn` | Resta aritm\u00e9tica (`Rd = Rs - Rn`). |\n| `and Rd, Rs` | `AND Rd, Rs` | Y l\u00f3gico bit a bit (`Rd &= Rs`). |\n| `or Rd, Rs` | `ORR Rd, Rs` | O l\u00f3gico bit a bit (`Rd \\|= Rs`). |\n| `xor Rd, Rs` | `EOR Rd, Rs` | O exclusivo l\u00f3gico bit a bit (`Rd ^= Rs`). |\n| `not Rd, Rs` | `MVN Rd, Rs` | Niega los bits (`Rd = ~Rs`). |\n| `neg Rd, Rs` | `NEG Rd, Rs` | Niega el signo (Complemento a 2) (`Rd = 0 - Rs`). |\n| `mul Rd, Rs` | `MUL Rd, Rs` | Multiplicaci\u00f3n (`Rd *= Rs`). |\n| `cmp Rd, Rs` | `CMP Rd, Rs` | Compara restando, actualizando flags pero sin guardar el resultado. |\n\n## \ud83d\udcbe Acceso a Memoria (Load / Store)\n\nEl hardware de GBA requiere usar Load y Store para escribir en VRAM o leer el cartucho. La direcci\u00f3n efectiva de memoria siempre se calcula sumando el registro Base (`Rb`) y un registro de Desplazamiento (`Ro`).\n\n| Instrucci\u00f3n RIF | Equivalencia ARM | Descripci\u00f3n |\n| :--- | :--- | :--- |\n| `ldr Rd, Rb, Ro` | `LDR Rd, [Rb, Ro]` | Lee **32-bits** de memoria (Word). |\n| `ldrb Rd, Rb, Ro` | `LDRB Rd, [Rb, Ro]` | Lee **8-bits** sin signo (Byte). |\n| `ldrh Rd, Rb, Ro` | `LDRH Rd, [Rb, Ro]` | Lee **16-bits** sin signo (Halfword). |\n| `str Rd, Rb, Ro` | `STR Rd, [Rb, Ro]` | Escribe **32-bits** en memoria. |\n| `strb Rd, Rb, Ro` | `STRB Rd, [Rb, Ro]` | Escribe **8-bits** en memoria. |\n| `strh Rd, Rb, Ro` | `STRH Rd, [Rb, Ro]` | Escribe **16-bits** en memoria. |\n\n\u003e [!WARNING]  \n\u003e La VRAM del GBA (donde se dibujan los p\u00edxeles) **no** soporta escrituras de 8-bits (`strb`). Si intentas escribir un solo byte en la RAM de video, el hardware lo reflejar\u00e1 escribiendo el byte duplicado en los 16-bits de la direcci\u00f3n. Usa siempre `strh` para colores.\n\n## \ud83d\udd00 Control de Flujo (Saltos)\n\nLas directivas de control de flujo son resueltas internamente por el motor de RIF. \u00c9l calcular\u00e1 autom\u00e1ticamente si el salto es hacia atr\u00e1s o hacia adelante y generar\u00e1 los saltos relativos de 16-bits correctos.\n\n| Instrucci\u00f3n RIF | Equivalencia ARM | Comportamiento |\n| :--- | :--- | :--- |\n| `jump label` | `B label` | Salto incondicional hacia `label`. |\n| `call label` | `BL label` | Salta y guarda la direcci\u00f3n de retorno en el Link Register (`LR`). |\n| `beq label` | `BEQ label` | Salta si es **igual** (Flag `Z=1`). |\n| `bne label` | `BNE label` | Salta si es **diferente** (Flag `Z=0`). |\n| `blt label` | `BLT label` | Salta si es **menor que** (Flags `N!=V`). |\n| `bgt label` | `BGT label` | Salta si es **mayor que** (Flags `Z=0` y `N=V`). |\n| `ble label` | `BLE label` | Salta si es **menor o igual** (Flags `Z=1` o `N!=V`). |\n| `bge label` | `BGE label` | Salta si es **mayor o igual** (Flags `N=V`). |\n\n## \ud83e\udd5e Stack (Pila)\n\n| Instrucci\u00f3n RIF | Equivalencia ARM | Descripci\u00f3n |\n| :--- | :--- | :--- |\n| `push Rd` | `PUSH {Rd}` | Empuja un registro a la pila de RAM (decrementa `SP`). |\n| `pop Rd` | `POP {Rd}` | Extrae un registro de la pila hacia `Rd` (incrementa `SP`). |\n\n## \ud83d\udcdd Declaraci\u00f3n Directa de Datos\n\nSi necesitas escribir bytes crudos intercalados en medio de tus rutinas (por ejemplo, para colores BGR555 o datos puros):\n\n```rif\ndb 0xFF              ; Declara 1 Byte (8 bits)\ndh 0x1234            ; Declara 1 Halfword (16 bits)\ndw 0x12345678        ; Declara 1 Word (32 bits)\n\n; Tambi\u00e9n puedes usar las directivas externas de fuentes:\nbitmap_text \"RIF\"    ; Emite bits del array de fuente de la consola\n```\n\n\n## Registros\n# Registros de CPU y MMIO (GBA)\n\nLa consola GBA tiene a su disposici\u00f3n los 16 registros de la familia ARM. Sin embargo, al operar bajo las reglas del conjunto **Thumb** de 16-bits para reducir el uso de memoria, hay ciertas restricciones sobre qu\u00e9 registros puedes tocar de forma aritm\u00e9tica.\n\n## \ud83d\uddc4\ufe0f Registros de Hardware (R0-R15)\n\n| Registro (ARM) | ID Binario | Acceso en Thumb | Prop\u00f3sito Principal (APCS) |\n| :--- | :--- | :--- | :--- |\n| **`R0` - `R3`** | `000` - `011` | \u2705 Absoluto | Argumentos de funciones y valores de retorno. |\n| **`R4` - `R7`** | `100` - `111` | \u2705 Absoluto | Variables de prop\u00f3sito general (Callee-saved). |\n| **`R8` - `R12`**| `1000`-`1100`| \u274c Denegado | *Solo accesibles en modo ARM o con trucos avanzados.* |\n| **`SP` (`R13`)**| `1101`        | \u26a0\ufe0f Especial | **S**tack **P**ointer (Puntero a la Pila). Usa `push`/`pop`. |\n| **`LR` (`R14`)**| `1110`        | \u26a0\ufe0f Especial | **L**ink **R**egister (Direcci\u00f3n de retorno de subrutinas). |\n| **`PC` (`R15`)**| `1111`        | \u26a0\ufe0f Especial | **P**rogram **C**ounter (Puntero de la instrucci\u00f3n actual + 4). |\n\n\u003e [!WARNING]  \n\u003e Nunca modifiques el registro `PC` (`R15`) manualmente a trav\u00e9s de sumas aritm\u00e9ticas en Thumb. Utiliza siempre las directivas nativas `jump` (para flujos locales) o `call` (para subrutinas).\n\n---\n\n## \ud83d\udcde Convenci\u00f3n de Llamada\n\nCuando programes rutinas complejas o funciones reutilizables, sigue la convenci\u00f3n APCS de ARM:\n- Utiliza **`R0`, `R1`, `R2`, y `R3`** para pasar variables a la funci\u00f3n.\n- El resultado del c\u00e1lculo devu\u00e9lvelo siempre en **`R0`**.\n- Si tu funci\u00f3n necesita usar los registros **`R4-R7`**, est\u00e1s obligado a guardarlos en la pila con `push` al iniciar tu funci\u00f3n, y restaurarlos con `pop` justo antes del salto de retorno.\n\n## \ud83d\udd79\ufe0f Memory-Mapped I/O (Registros de Hardware)\n\nEl GBA controla el hardware de la consola, la pantalla y los botones escribiendo n\u00fameros m\u00e1gicos en direcciones espec\u00edficas de memoria (`0x04000000`).\n\n| Nombre del Registro | Direcci\u00f3n Hex | Funci\u00f3n |\n| :--- | :--- | :--- |\n| **`DISPCNT`** | `0x04000000` | Display Control. Sirve para activar fondos, objetos y el modo de video (Ej. Mode 3). |\n| **`DISPSTAT`** | `0x04000004` | Display Status. Monitorea cuando la pantalla se apaga (VBlank/HBlank) para evitar parpadeos. |\n| **`VCOUNT`** | `0x04000006` | Vertical Count. Devuelve qu\u00e9 l\u00ednea de p\u00edxeles (0-227) est\u00e1 dibujando el ca\u00f1\u00f3n de electrones. |\n| **`SOUNDCNT_L`** | `0x04000060` | Control de vol\u00famenes de los canales del Game Boy cl\u00e1sico. |\n| **`SOUNDCNT_H`** | `0x04000082` | Control principal del flujo DMA (Direct Sound) para audio de alta calidad. |\n| **`KEYINPUT`** | `0x04000130` | Lector de los botones (Pad y Gatillos). *Atenci\u00f3n: La se\u00f1al es activa en bajo (0 es presionado).* |\n| **`IME` / `IE` / `IF`** | `0x04000200` | Sistema maestro de habilitaci\u00f3n y banderas de interrupciones de hardware (IRQs). |\n\n\u003e [!TIP]\n\u003e Debido a que las direcciones (como `0x04000000`) son muy grandes para cargarse directamente en Thumb con la instrucci\u00f3n `store Rd = imm` (que solo acepta de 0 a 255), RIF incluye soporte para componer n\u00fameros altos iterativamente o apoyarse en el _Literal Pool_ con el plugin GBA.\n\n\n## Fillables\n# Directivas Fillables (Generaci\u00f3n de Datos)\n\nEn RIF, un \"fillable\" (marcado con `@`) es una macro inteligente pre-procesada. Antes de compilar, el linker de RIF intercepta estas llamadas y genera bloques masivos de c\u00f3digo fuente o binario de forma algor\u00edtmica.\n\nEl plugin de GBA trae herramientas est\u00e1ticas nativas, pero tambi\u00e9n se dise\u00f1a para recibir inyecciones de los plugins `image` y `sound`.\n\n---\n\n## \ud83c\udfa8 Gr\u00e1ficos B\u00e1sicos Nativos (GBA Plugin)\n\nEstas directivas generan memoria VRAM desde colores simples o texto pre-empaquetado usando las rutinas internas del plugin.\n\n### `@fill_screen`\nGenera un buffer completo de 38,400 p\u00edxeles de 16-bits (76.8 KB) rellenado del color BGR555 especificado. Es perfecto para limpiar fondos.\n\n```rif\n@fill_screen black screen_bg\n@fill_screen green mi_fondo\n```\n- **Arg 1**: Color (`black`, `white`, `green`, `red`, `blue`, etc.)\n- **Arg 2**: Nombre de la variable (label) generada.\n\n### `@fill_screen_text`\nGenera un buffer de pantalla completa, pero estampa en el centro un texto en fuente de mapa de bits (bitmap) a escala x3.\n\n```rif\n@fill_screen_text START white black pantalla_inicio\n```\n- **Arg 1**: El texto a renderizar (ASCII en may\u00fasculas).\n- **Arg 2**: Color de la fuente.\n- **Arg 3**: Color del fondo.\n- **Arg 4**: Etiqueta generada.\n\n---\n\n## \ud83d\uddbc\ufe0f Im\u00e1genes Avanzadas (Plugin `image`)\n\nSi importas el plugin `image` en tu entorno (ej. `--plugin gba --plugin image`), puedes invocar conversiones de disco din\u00e1micas hacia formato GBA.\n\n### `@fill_image_bitmap`\nLee un `.png`, `.jpg` o `.bmp` de tu disco, le aplica *downsampling por promedio de caja* para suprimir el anti-aliasing negro, y lo convierte al est\u00e1ndar **BGR555**.\n\n```rif\n; Toma \"mario.png\" y crea el buffer de VRAM \"mario_sprite\"\n@fill_image_bitmap mario.png mario_sprite\n```\n\n\u003e [!TIP]\n\u003e **Promedio de Caja (Box Average)**: Si tu imagen original no cuadra matem\u00e1ticamente con los pixeles de tu buffer, el algoritmo no descarta p\u00edxeles de forma ruda (nearest-neighbor), sino que promedia sus canales de color.\n\n---\n\n## \ud83c\udfb5 Motor de Audio (Plugin `sound`)\n\nSi usas el plugin `sound`, puedes pedir a RIF que convierta pistas de audio modernas (`.wav`, `.mp3`) para que el GBA pueda streamearlas v\u00eda **Direct Sound A**.\n\n### `@fill_sound_wav`\nLlama a **FFmpeg** en segundo plano, re-muestrea tu pista, la convierte a canal mono, la fuerza a 8-bits con signo (`pcm_s8`) y la emite en memoria lista para DMA.\n\n```rif\n; Pasa \"music.mp3\" a 16000 Hz firmados, etiqueta \"bgm_sample\"\n@fill_sound_wav bgm_sample music.mp3 16000\n```\n- **Arg 1**: Etiqueta (El plugin anexar\u00e1 sufijos autom\u00e1ticos para controlar el DMA: `_timer_reload`, `_dma_control`).\n- **Arg 2**: Ruta al archivo local de audio.\n- **Arg 3**: Frecuencia de muestreo destino (ej. `16000`, `22050`).\n\n\n## Macros Rom\n# Macros Estructurales de ROM (GBA)\n\nPara que el hardware real de Game Boy Advance (o un emulador estricto) inicie un cartucho, los primeros 192 bytes de la memoria flash (`.rom` desde la direcci\u00f3n `0x08000000`) deben contener una cabecera extremadamente precisa.\n\nEl plugin `gba` proporciona macros que resuelven todas las exigencias binarias autom\u00e1ticamente.\n\n## \ud83e\uddf1 Secuencia Funcional M\u00ednima\n\nEl orden de los siguientes componentes es fundamental. RIF emitir\u00e1 bloques binarios del tama\u00f1o exacto en el orden en que pongas estas macros:\n\n```rif\n.section .rom\nset_headers        ; [0x00-0x03] Salto de la BIOS a tu c\u00f3digo\nset_logo           ; [0x04-0x9F] Logo nativo de Nintendo (Comprimido)\nset_checksum       ; [0xA0-0xBF] T\u00edtulo, C\u00f3digos y Checksums cruzados\nset_entry_thumb    ; [0xC0-...]  Punto de entrada ARM -\u003e Salta a Thumb\n```\n\n\u003e [!CAUTION]  \n\u003e Si omites la macro `set_logo`, la BIOS del GBA asumir\u00e1 que el cartucho es pirata y se negar\u00e1 a bootear.\n\u003e De igual forma, si alteras `set_checksum`, el c\u00e1lculo matem\u00e1tico que valida los bytes del t\u00edtulo fallar\u00e1 y la consola bloquear\u00e1 la ejecuci\u00f3n con una pantalla en blanco.\n\n## \ud83d\udee0\ufe0f Detalles de las Macros\n\n### `set_headers`\nCrea el vector de salto original en ARM (32 bits). Generalmente emite `B 0x080000C0`, instruyendo a la BIOS que el c\u00f3digo del juego comienza justo despu\u00e9s del bloque de la cabecera.\n\n### `set_logo`\nInyecta 156 bytes exactos equivalentes al logo vectorizado de Nintendo. La BIOS lee y compara estos bits a mano.\n\n### `set_checksum`\nInyecta metadatos del juego (Game Title, Maker Code, Version) y calcula un checksum complementario (Complemento a 2 negado) del header completo. RIF calcula esto autom\u00e1ticamente por ti.\n\n### `set_entry_thumb`\nAl finalizar el booteo, la consola est\u00e1 en modo ARM nativo. Esta macro inyecta el estado (Stubs) y ejecuta un `BX` (Branch and Exchange) para forzar a la CPU a cambiar al modo **Thumb** (16-bits). Despu\u00e9s de esta l\u00ednea, todo el c\u00f3digo que escribas debajo ser\u00e1 c\u00f3digo Thumb real validado por RIF.\n\n### `set_rompad`\nSi un cartucho se construye muy corto (por ejemplo, 137 KB), los emuladores podr\u00edan tener problemas de paginaci\u00f3n o alineaci\u00f3n de cach\u00e9. Esta macro se debe colocar al final de tu documento `.gbasm` y rellenar\u00e1 inteligentemente con `0xFF` el archivo hasta alcanzar los bloques oficiales (alineados a potencias de 2 KB, 32 KB, etc.) calculando en caliente cu\u00e1nto c\u00f3digo ya ha sido emitido.\n",
      "plugin_gba/build_y_run": "# Construcci\u00f3n y Ejecuci\u00f3n de Proyectos GBA\n\nEl entorno RIF cuenta con un flujo completo y automatizado para orquestar la fusi\u00f3n de tu c\u00f3digo ensamblador con recursos como audio e im\u00e1genes, construyendo directamente im\u00e1genes de ROM (`.gba`) v\u00e1lidas.\n\n## \ud83d\udd28 Compilar un Proyecto\n\nDado que el plugin GBA asume el control del entorno para inyectar su set de instrucciones Thumb y su mapeo de cabeceras, la compilaci\u00f3n de proyectos requiere que invoques el empaquetador indicando el plugin GBA:\n\n```bash\n# Formato general de construcci\u00f3n:\npython -m rif build \u003cruta_al_directorio_fuente\u003e --plugin gba --name \u003cnombre_del_pack\u003e\n\n# Ejemplo oficial:\npython -m rif build examples/gba --plugin gba --name example\n```\n\nAl ejecutar este comando, RIF har\u00e1 lo siguiente:\n1. Extraer\u00e1 las reglas y metadatos alojados en `rif/plugins/gba/packs/example/`.\n2. Evaluar\u00e1 secuencialmente cada archivo con extensi\u00f3n `.gbasm` dentro del directorio especificado.\n3. Inyectar\u00e1 llamadas din\u00e1micas (como conversi\u00f3n de audio e im\u00e1genes) si usas macros como `@fill_sound_wav`.\n4. Renderizar\u00e1 en consola un elegante reporte visual indicando el tama\u00f1o (Bytes), la ubicaci\u00f3n l\u00f3gica en memoria de tus bloques, el Hash `SHA256` y los offsets de enlace (Linker Labels) generados.\n\nEl binario resultante se depositar\u00e1 en el directorio fuente bajo el nombre `\u003cdirectorio\u003e.gba` (en el caso del ejemplo: `examples/gba/gba.gba`).\n\n---\n\n## \ud83c\udfae Ejecuci\u00f3n en Emuladores (CLI nativo)\n\nEl plugin GBA incorpora herramientas especializadas accesibles bajo el prefijo CLI de RIF `-pcli gba`.\n\nSi no tienes un emulador, el propio RIF puede descargar la \u00faltima versi\u00f3n port\u00e1til del popular emulador **mGBA** e instalarla de forma local:\n\n```bash\n# Descarga e instala mGBA autom\u00e1ticamente:\npython -m rif -pcli gba install mGBA --add-path\n```\n\nUna vez tengas tu archivo `.gba` generado y tu emulador listo, puedes lanzar tu juego directamente desde la terminal de forma fluida:\n\n```bash\npython -m rif -pcli gba run examples/gba/gba.gba -nd\n```\n\n### \ud83d\udca1 Acerca del flag `-nd` (No Duplicates)\n\nEl flag `-nd` es de vital importancia durante el desarrollo. Cuando compilas iterativamente, no querr\u00e1s acumular cientos de ventanas del emulador abiertas. El motor de RIF rastrear\u00e1 activamente los hilos de `mGBA` a nivel de sistema operativo y reutilizar\u00e1 de forma forzada la ventana abierta anteriormente cerrando el proceso heredado antes de lanzar el nuevo.\n",
      "plugin_gba/overview": "# Visi\u00f3n General: Arquitectura GBA\n\nEl plugin `gba` proporciona el soporte integral para compilar ROMs comerciales y homebrew de **Game Boy Advance** utilizando el ecosistema de cero-acoplamiento de RIF.\n\nA diferencia de los ensambladores convencionales, este plugin ense\u00f1a al compilador de RIF c\u00f3mo estructurar la cabecera exigida por el hardware de Nintendo, c\u00f3mo validar los sumatorios (checksums), y le inyecta la sem\u00e1ntica de la **CPU ARM7TDMI**.\n\n## \ud83e\udde0 Arquitectura y CPU\n\nEl coraz\u00f3n del GBA es un procesador ARM7TDMI que puede operar en dos modos:\n- **Estado ARM (32 bits)**: Reservado principalmente para el arranque o rutinas de alto rendimiento en IWRAM.\n- **Estado Thumb (16 bits)**: El modo principal usado para ejecutar c\u00f3digo desde el cartucho (ROM) debido a su mayor densidad y las limitaciones del bus de 16-bits.\n\nEl plugin **GBA de RIF emite c\u00f3digo Thumb** nativo, en formato *Little Endian*, lo que garantiza lecturas \u00f3ptimas desde el cartucho hacia el bus de la memoria sin necesidad de preprocesadores de terceros.\n\n---\n\n## \ud83d\uddfa\ufe0f Mapa F\u00edsico de Memoria (MMIO)\n\nEl plugin ya tiene pre-mapeadas las direcciones de estas secciones en su archivo `.pack`, permitiendo usar referencias directas como `r0, 0x06000000` (VRAM) o apoyarte en sus correspondientes tablas para relocaciones autom\u00e1ticas.\n\n| Secci\u00f3n (Hardware) | Direcci\u00f3n  | Tama\u00f1o | Rol Principal                                   |\n|--------------------|------------|--------|-------------------------------------------------|\n| `.rom` / ROM       | 0x08000000 | 32 MB  | Memoria flash del cartucho (Instrucciones)      |\n| `.ewram` / EWRAM   | 0x02000000 | 256 KB | Memoria de trabajo externa (Carga general)      |\n| `.iwram` / IWRAM   | 0x03000000 | 32 KB  | Memoria interna (Alt\u00edsima velocidad para bucles)|\n| `.io` / IO         | 0x04000000 | 1 KB   | Registros MMIO (Control de Video, Sonido, DMA)  |\n| `.palette`         | 0x05000000 | 1 KB   | Memoria CRAM (Paletas BGR555)                   |\n| `.vram` / VRAM     | 0x06000000 | 96 KB  | Video RAM (Pixeles, Tiles y Mapas)              |\n| `.oam` / OAM       | 0x07000000 | 1 KB   | Memoria de Atributos de Sprites (Objetos)       |\n\n---\n\n## \ud83d\udcc1 Estructura del Ecosistema\n\nTodo el soporte arquitect\u00f3nico de GBA vive dentro del directorio `rif/plugins/gba/`. Sus responsabilidades est\u00e1n estrictamente divididas:\n\n```text\nplugins/gba/\n\u251c\u2500\u2500 cli.py                    # \ud83d\udcbb Interfaz de subcomandos `rif -pcli gba`\n\u251c\u2500\u2500 cli/\n\u2502   \u251c\u2500\u2500 install.py            # Script que descarga mGBA autom\u00e1ticamente\n\u2502   \u2514\u2500\u2500 run.py                # Wrapper para inyectar la ROM al emulador\n\u251c\u2500\u2500 fillables.py              # \ud83c\udfa8 Directivas @fill_screen / @fill_screen_text\n\u251c\u2500\u2500 packs/example/\n\u2502   \u251c\u2500\u2500 gba.pack              # \u2699\ufe0f Punto de entrada: Importa el universo GBA\n\u2502   \u251c\u2500\u2500 gba.regs.pack         # \ud83d\uddc4\ufe0f Tabla de los 16 Registros (R0-R15)\n\u2502   \u251c\u2500\u2500 gba.sections.pack     # \ud83d\uddfa\ufe0f Inicializaci\u00f3n de los VOff y bloques\n\u2502   \u2514\u2500\u2500 gba.rules.pack        # \ud83d\udcd0 Expresiones regulares y reglas Thumb\n\u2514\u2500\u2500 plugins/\n    \u251c\u2500\u2500 thumb_ins.py          # \ud83e\udd16 Int\u00e9rprete aritm\u00e9tico del Set de Instrucciones\n    \u251c\u2500\u2500 gba_headers.py        # \ud83e\uddf1 Constructor binario de la Cabecera 0x00-0xBF\n    \u251c\u2500\u2500 gba_logo.py           # \ud83c\udf44 Inyecci\u00f3n estricta del Logo de Nintendo\n    \u251c\u2500\u2500 gba_checksum.py       # \ud83e\uddee C\u00f3mputo matem\u00e1tico de validaci\u00f3n\n    \u2514\u2500\u2500 gba_entry.py          # \ud83d\udeaa Inyector del salto ARM -\u003e Thumb (bx)\n```\n\n## \ud83e\udd1d Sinergia con otros Plugins\n\nGracias al dise\u00f1o agn\u00f3stico de RIF, el plugin GBA se beneficia autom\u00e1ticamente de:\n- **Plugin Image**: Si compilas tu proyecto GBA incluyendo `--plugin image`, ganar\u00e1s acceso a `@fill_image_bitmap` para insertar PNGs/BMPs comprimidos a formato VRAM de GBA.\n- **Plugin Sound**: Usando `--plugin sound`, puedes inyectar archivos `.wav` de 8-bits e invocar el DMA del GBA para hacer streaming de audio nativo hacia el altavoz de la consola.\n",
      "plugin_gba/instrucciones": "# Conjunto de Instrucciones Thumb (GBA)\n\nLa consola GBA corre una CPU **ARM7TDMI** nativa. El framework de RIF compila sus instrucciones utilizando el modo **Thumb** (Instrucciones de 16-bits alineadas en formato *Little-Endian*), cumpliendo estrictamente con el manual de referencia t\u00e9cnica ARM (DDI 0029G).\n\n\u003e [!IMPORTANT]  \n\u003e En el estado Thumb de 16-bits, casi todas las instrucciones est\u00e1n limitadas a operar exclusivamente sobre los **registros bajos (R0-R7)** para ahorrar espacio en la codificaci\u00f3n binaria.\n\n---\n\n## \ud83e\uddee Transferencia de Datos\n\nEstas instrucciones permiten mover informaci\u00f3n entre los registros o cargar constantes.\n\n| Instrucci\u00f3n RIF | Equivalencia ARM | Descripci\u00f3n |\n| :--- | :--- | :--- |\n| `store Rd = imm` | `MOV Rd, #imm8` | Carga un n\u00famero inmediato (0-255) en un registro. |\n| `move Rd, Rs` | `ADD Rd, Rs, #0` | Copia el contenido del registro origen `Rs` al destino `Rd`. |\n| `lsl Rd, Rs, imm` | `LSL Rd, Rs, #imm5` | **L**ogical **S**hift **L**eft (Multiplica por 2^n). |\n| `lsr Rd, Rs, imm` | `LSR Rd, Rs, #imm5` | **L**ogical **S**hift **R**ight (Divide sin signo). |\n| `asr Rd, Rs, imm` | `ASR Rd, Rs, #imm5` | **A**rithmetic **S**hift **R**ight (Mantiene el signo). |\n\n## \u2694\ufe0f Aritm\u00e9tica y L\u00f3gica\n\nA diferencia de ARM, las instrucciones aritm\u00e9ticas de Thumb actualizan autom\u00e1ticamente las banderas (Flags) de condici\u00f3n en el registro CPSR (Condition Program Status Register).\n\n| Instrucci\u00f3n RIF | Equivalencia ARM | Descripci\u00f3n |\n| :--- | :--- | :--- |\n| `add Rd, Rs, Rn` | `ADD Rd, Rs, Rn` | Suma aritm\u00e9tica (`Rd = Rs + Rn`). |\n| `sub Rd, Rs, Rn` | `SUB Rd, Rs, Rn` | Resta aritm\u00e9tica (`Rd = Rs - Rn`). |\n| `and Rd, Rs` | `AND Rd, Rs` | Y l\u00f3gico bit a bit (`Rd &= Rs`). |\n| `or Rd, Rs` | `ORR Rd, Rs` | O l\u00f3gico bit a bit (`Rd \\|= Rs`). |\n| `xor Rd, Rs` | `EOR Rd, Rs` | O exclusivo l\u00f3gico bit a bit (`Rd ^= Rs`). |\n| `not Rd, Rs` | `MVN Rd, Rs` | Niega los bits (`Rd = ~Rs`). |\n| `neg Rd, Rs` | `NEG Rd, Rs` | Niega el signo (Complemento a 2) (`Rd = 0 - Rs`). |\n| `mul Rd, Rs` | `MUL Rd, Rs` | Multiplicaci\u00f3n (`Rd *= Rs`). |\n| `cmp Rd, Rs` | `CMP Rd, Rs` | Compara restando, actualizando flags pero sin guardar el resultado. |\n\n## \ud83d\udcbe Acceso a Memoria (Load / Store)\n\nEl hardware de GBA requiere usar Load y Store para escribir en VRAM o leer el cartucho. La direcci\u00f3n efectiva de memoria siempre se calcula sumando el registro Base (`Rb`) y un registro de Desplazamiento (`Ro`).\n\n| Instrucci\u00f3n RIF | Equivalencia ARM | Descripci\u00f3n |\n| :--- | :--- | :--- |\n| `ldr Rd, Rb, Ro` | `LDR Rd, [Rb, Ro]` | Lee **32-bits** de memoria (Word). |\n| `ldrb Rd, Rb, Ro` | `LDRB Rd, [Rb, Ro]` | Lee **8-bits** sin signo (Byte). |\n| `ldrh Rd, Rb, Ro` | `LDRH Rd, [Rb, Ro]` | Lee **16-bits** sin signo (Halfword). |\n| `str Rd, Rb, Ro` | `STR Rd, [Rb, Ro]` | Escribe **32-bits** en memoria. |\n| `strb Rd, Rb, Ro` | `STRB Rd, [Rb, Ro]` | Escribe **8-bits** en memoria. |\n| `strh Rd, Rb, Ro` | `STRH Rd, [Rb, Ro]` | Escribe **16-bits** en memoria. |\n\n\u003e [!WARNING]  \n\u003e La VRAM del GBA (donde se dibujan los p\u00edxeles) **no** soporta escrituras de 8-bits (`strb`). Si intentas escribir un solo byte en la RAM de video, el hardware lo reflejar\u00e1 escribiendo el byte duplicado en los 16-bits de la direcci\u00f3n. Usa siempre `strh` para colores.\n\n## \ud83d\udd00 Control de Flujo (Saltos)\n\nLas directivas de control de flujo son resueltas internamente por el motor de RIF. \u00c9l calcular\u00e1 autom\u00e1ticamente si el salto es hacia atr\u00e1s o hacia adelante y generar\u00e1 los saltos relativos de 16-bits correctos.\n\n| Instrucci\u00f3n RIF | Equivalencia ARM | Comportamiento |\n| :--- | :--- | :--- |\n| `jump label` | `B label` | Salto incondicional hacia `label`. |\n| `call label` | `BL label` | Salta y guarda la direcci\u00f3n de retorno en el Link Register (`LR`). |\n| `beq label` | `BEQ label` | Salta si es **igual** (Flag `Z=1`). |\n| `bne label` | `BNE label` | Salta si es **diferente** (Flag `Z=0`). |\n| `blt label` | `BLT label` | Salta si es **menor que** (Flags `N!=V`). |\n| `bgt label` | `BGT label` | Salta si es **mayor que** (Flags `Z=0` y `N=V`). |\n| `ble label` | `BLE label` | Salta si es **menor o igual** (Flags `Z=1` o `N!=V`). |\n| `bge label` | `BGE label` | Salta si es **mayor o igual** (Flags `N=V`). |\n\n## \ud83e\udd5e Stack (Pila)\n\n| Instrucci\u00f3n RIF | Equivalencia ARM | Descripci\u00f3n |\n| :--- | :--- | :--- |\n| `push Rd` | `PUSH {Rd}` | Empuja un registro a la pila de RAM (decrementa `SP`). |\n| `pop Rd` | `POP {Rd}` | Extrae un registro de la pila hacia `Rd` (incrementa `SP`). |\n\n## \ud83d\udcdd Declaraci\u00f3n Directa de Datos\n\nSi necesitas escribir bytes crudos intercalados en medio de tus rutinas (por ejemplo, para colores BGR555 o datos puros):\n\n```rif\ndb 0xFF              ; Declara 1 Byte (8 bits)\ndh 0x1234            ; Declara 1 Halfword (16 bits)\ndw 0x12345678        ; Declara 1 Word (32 bits)\n\n; Tambi\u00e9n puedes usar las directivas externas de fuentes:\nbitmap_text \"RIF\"    ; Emite bits del array de fuente de la consola\n```\n",
      "plugin_gba/registros": "# Registros de CPU y MMIO (GBA)\n\nLa consola GBA tiene a su disposici\u00f3n los 16 registros de la familia ARM. Sin embargo, al operar bajo las reglas del conjunto **Thumb** de 16-bits para reducir el uso de memoria, hay ciertas restricciones sobre qu\u00e9 registros puedes tocar de forma aritm\u00e9tica.\n\n## \ud83d\uddc4\ufe0f Registros de Hardware (R0-R15)\n\n| Registro (ARM) | ID Binario | Acceso en Thumb | Prop\u00f3sito Principal (APCS) |\n| :--- | :--- | :--- | :--- |\n| **`R0` - `R3`** | `000` - `011` | \u2705 Absoluto | Argumentos de funciones y valores de retorno. |\n| **`R4` - `R7`** | `100` - `111` | \u2705 Absoluto | Variables de prop\u00f3sito general (Callee-saved). |\n| **`R8` - `R12`**| `1000`-`1100`| \u274c Denegado | *Solo accesibles en modo ARM o con trucos avanzados.* |\n| **`SP` (`R13`)**| `1101`        | \u26a0\ufe0f Especial | **S**tack **P**ointer (Puntero a la Pila). Usa `push`/`pop`. |\n| **`LR` (`R14`)**| `1110`        | \u26a0\ufe0f Especial | **L**ink **R**egister (Direcci\u00f3n de retorno de subrutinas). |\n| **`PC` (`R15`)**| `1111`        | \u26a0\ufe0f Especial | **P**rogram **C**ounter (Puntero de la instrucci\u00f3n actual + 4). |\n\n\u003e [!WARNING]  \n\u003e Nunca modifiques el registro `PC` (`R15`) manualmente a trav\u00e9s de sumas aritm\u00e9ticas en Thumb. Utiliza siempre las directivas nativas `jump` (para flujos locales) o `call` (para subrutinas).\n\n---\n\n## \ud83d\udcde Convenci\u00f3n de Llamada\n\nCuando programes rutinas complejas o funciones reutilizables, sigue la convenci\u00f3n APCS de ARM:\n- Utiliza **`R0`, `R1`, `R2`, y `R3`** para pasar variables a la funci\u00f3n.\n- El resultado del c\u00e1lculo devu\u00e9lvelo siempre en **`R0`**.\n- Si tu funci\u00f3n necesita usar los registros **`R4-R7`**, est\u00e1s obligado a guardarlos en la pila con `push` al iniciar tu funci\u00f3n, y restaurarlos con `pop` justo antes del salto de retorno.\n\n## \ud83d\udd79\ufe0f Memory-Mapped I/O (Registros de Hardware)\n\nEl GBA controla el hardware de la consola, la pantalla y los botones escribiendo n\u00fameros m\u00e1gicos en direcciones espec\u00edficas de memoria (`0x04000000`).\n\n| Nombre del Registro | Direcci\u00f3n Hex | Funci\u00f3n |\n| :--- | :--- | :--- |\n| **`DISPCNT`** | `0x04000000` | Display Control. Sirve para activar fondos, objetos y el modo de video (Ej. Mode 3). |\n| **`DISPSTAT`** | `0x04000004` | Display Status. Monitorea cuando la pantalla se apaga (VBlank/HBlank) para evitar parpadeos. |\n| **`VCOUNT`** | `0x04000006` | Vertical Count. Devuelve qu\u00e9 l\u00ednea de p\u00edxeles (0-227) est\u00e1 dibujando el ca\u00f1\u00f3n de electrones. |\n| **`SOUNDCNT_L`** | `0x04000060` | Control de vol\u00famenes de los canales del Game Boy cl\u00e1sico. |\n| **`SOUNDCNT_H`** | `0x04000082` | Control principal del flujo DMA (Direct Sound) para audio de alta calidad. |\n| **`KEYINPUT`** | `0x04000130` | Lector de los botones (Pad y Gatillos). *Atenci\u00f3n: La se\u00f1al es activa en bajo (0 es presionado).* |\n| **`IME` / `IE` / `IF`** | `0x04000200` | Sistema maestro de habilitaci\u00f3n y banderas de interrupciones de hardware (IRQs). |\n\n\u003e [!TIP]\n\u003e Debido a que las direcciones (como `0x04000000`) son muy grandes para cargarse directamente en Thumb con la instrucci\u00f3n `store Rd = imm` (que solo acepta de 0 a 255), RIF incluye soporte para componer n\u00fameros altos iterativamente o apoyarse en el _Literal Pool_ con el plugin GBA.\n",
      "plugin_gba/fillables": "# Directivas Fillables (Generaci\u00f3n de Datos)\n\nEn RIF, un \"fillable\" (marcado con `@`) es una macro inteligente pre-procesada. Antes de compilar, el linker de RIF intercepta estas llamadas y genera bloques masivos de c\u00f3digo fuente o binario de forma algor\u00edtmica.\n\nEl plugin de GBA trae herramientas est\u00e1ticas nativas, pero tambi\u00e9n se dise\u00f1a para recibir inyecciones de los plugins `image` y `sound`.\n\n---\n\n## \ud83c\udfa8 Gr\u00e1ficos B\u00e1sicos Nativos (GBA Plugin)\n\nEstas directivas generan memoria VRAM desde colores simples o texto pre-empaquetado usando las rutinas internas del plugin.\n\n### `@fill_screen`\nGenera un buffer completo de 38,400 p\u00edxeles de 16-bits (76.8 KB) rellenado del color BGR555 especificado. Es perfecto para limpiar fondos.\n\n```rif\n@fill_screen black screen_bg\n@fill_screen green mi_fondo\n```\n- **Arg 1**: Color (`black`, `white`, `green`, `red`, `blue`, etc.)\n- **Arg 2**: Nombre de la variable (label) generada.\n\n### `@fill_screen_text`\nGenera un buffer de pantalla completa, pero estampa en el centro un texto en fuente de mapa de bits (bitmap) a escala x3.\n\n```rif\n@fill_screen_text START white black pantalla_inicio\n```\n- **Arg 1**: El texto a renderizar (ASCII en may\u00fasculas).\n- **Arg 2**: Color de la fuente.\n- **Arg 3**: Color del fondo.\n- **Arg 4**: Etiqueta generada.\n\n---\n\n## \ud83d\uddbc\ufe0f Im\u00e1genes Avanzadas (Plugin `image`)\n\nSi importas el plugin `image` en tu entorno (ej. `--plugin gba --plugin image`), puedes invocar conversiones de disco din\u00e1micas hacia formato GBA.\n\n### `@fill_image_bitmap`\nLee un `.png`, `.jpg` o `.bmp` de tu disco, le aplica *downsampling por promedio de caja* para suprimir el anti-aliasing negro, y lo convierte al est\u00e1ndar **BGR555**.\n\n```rif\n; Toma \"mario.png\" y crea el buffer de VRAM \"mario_sprite\"\n@fill_image_bitmap mario.png mario_sprite\n```\n\n\u003e [!TIP]\n\u003e **Promedio de Caja (Box Average)**: Si tu imagen original no cuadra matem\u00e1ticamente con los pixeles de tu buffer, el algoritmo no descarta p\u00edxeles de forma ruda (nearest-neighbor), sino que promedia sus canales de color.\n\n---\n\n## \ud83c\udfb5 Motor de Audio (Plugin `sound`)\n\nSi usas el plugin `sound`, puedes pedir a RIF que convierta pistas de audio modernas (`.wav`, `.mp3`) para que el GBA pueda streamearlas v\u00eda **Direct Sound A**.\n\n### `@fill_sound_wav`\nLlama a **FFmpeg** en segundo plano, re-muestrea tu pista, la convierte a canal mono, la fuerza a 8-bits con signo (`pcm_s8`) y la emite en memoria lista para DMA.\n\n```rif\n; Pasa \"music.mp3\" a 16000 Hz firmados, etiqueta \"bgm_sample\"\n@fill_sound_wav bgm_sample music.mp3 16000\n```\n- **Arg 1**: Etiqueta (El plugin anexar\u00e1 sufijos autom\u00e1ticos para controlar el DMA: `_timer_reload`, `_dma_control`).\n- **Arg 2**: Ruta al archivo local de audio.\n- **Arg 3**: Frecuencia de muestreo destino (ej. `16000`, `22050`).\n",
      "plugin_gba/macros_rom": "# Macros Estructurales de ROM (GBA)\n\nPara que el hardware real de Game Boy Advance (o un emulador estricto) inicie un cartucho, los primeros 192 bytes de la memoria flash (`.rom` desde la direcci\u00f3n `0x08000000`) deben contener una cabecera extremadamente precisa.\n\nEl plugin `gba` proporciona macros que resuelven todas las exigencias binarias autom\u00e1ticamente.\n\n## \ud83e\uddf1 Secuencia Funcional M\u00ednima\n\nEl orden de los siguientes componentes es fundamental. RIF emitir\u00e1 bloques binarios del tama\u00f1o exacto en el orden en que pongas estas macros:\n\n```rif\n.section .rom\nset_headers        ; [0x00-0x03] Salto de la BIOS a tu c\u00f3digo\nset_logo           ; [0x04-0x9F] Logo nativo de Nintendo (Comprimido)\nset_checksum       ; [0xA0-0xBF] T\u00edtulo, C\u00f3digos y Checksums cruzados\nset_entry_thumb    ; [0xC0-...]  Punto de entrada ARM -\u003e Salta a Thumb\n```\n\n\u003e [!CAUTION]  \n\u003e Si omites la macro `set_logo`, la BIOS del GBA asumir\u00e1 que el cartucho es pirata y se negar\u00e1 a bootear.\n\u003e De igual forma, si alteras `set_checksum`, el c\u00e1lculo matem\u00e1tico que valida los bytes del t\u00edtulo fallar\u00e1 y la consola bloquear\u00e1 la ejecuci\u00f3n con una pantalla en blanco.\n\n## \ud83d\udee0\ufe0f Detalles de las Macros\n\n### `set_headers`\nCrea el vector de salto original en ARM (32 bits). Generalmente emite `B 0x080000C0`, instruyendo a la BIOS que el c\u00f3digo del juego comienza justo despu\u00e9s del bloque de la cabecera.\n\n### `set_logo`\nInyecta 156 bytes exactos equivalentes al logo vectorizado de Nintendo. La BIOS lee y compara estos bits a mano.\n\n### `set_checksum`\nInyecta metadatos del juego (Game Title, Maker Code, Version) y calcula un checksum complementario (Complemento a 2 negado) del header completo. RIF calcula esto autom\u00e1ticamente por ti.\n\n### `set_entry_thumb`\nAl finalizar el booteo, la consola est\u00e1 en modo ARM nativo. Esta macro inyecta el estado (Stubs) y ejecuta un `BX` (Branch and Exchange) para forzar a la CPU a cambiar al modo **Thumb** (16-bits). Despu\u00e9s de esta l\u00ednea, todo el c\u00f3digo que escribas debajo ser\u00e1 c\u00f3digo Thumb real validado por RIF.\n\n### `set_rompad`\nSi un cartucho se construye muy corto (por ejemplo, 137 KB), los emuladores podr\u00edan tener problemas de paginaci\u00f3n o alineaci\u00f3n de cach\u00e9. Esta macro se debe colocar al final de tu documento `.gbasm` y rellenar\u00e1 inteligentemente con `0xFF` el archivo hasta alcanzar los bloques oficiales (alineados a potencias de 2 KB, 32 KB, etc.) calculando en caliente cu\u00e1nto c\u00f3digo ya ha sido emitido.\n",
      "plugin_gba/extern_doc": "\u003c!doctype html\u003e\n\u003chtml lang=\"es\"\u003e\n\u003chead\u003e\n  \u003cmeta charset=\"UTF-8\" /\u003e\n  \u003ctitle\u003eDocs GBA / ARM7TDMI / Thumb\u003c/title\u003e\n  \u003cstyle\u003e\n    * {\n      box-sizing: border-box;\n    }\n\n    html, body {\n      margin: 0;\n      width: 100%;\n      height: 100%;\n      overflow: hidden;\n      font-family: system-ui, sans-serif;\n      background: #111;\n      color: #eee;\n    }\n\n    .tabs {\n      display: flex;\n      height: 42px;\n      background: #181818;\n      border-bottom: 1px solid #333;\n      overflow-x: auto;\n    }\n\n    button {\n      border: 0;\n      padding: 0 14px;\n      background: #222;\n      color: #ddd;\n      cursor: pointer;\n      border-right: 1px solid #333;\n      font-size: 13px;\n      white-space: nowrap;\n    }\n\n    button.active {\n      background: #365cff;\n      color: white;\n    }\n\n    iframe {\n      width: 100vw;\n      height: calc(100vh - 42px);\n      border: 0;\n      background: white;\n    }\n  \u003c/style\u003e\n\u003c/head\u003e\n\u003cbody\u003e\n  \u003cdiv class=\"tabs\"\u003e\n    \u003cbutton class=\"active\" onclick=\"openDoc(this, 'https://rust-console.github.io/gbatek-gbaonly/')\"\u003e\n      GBATEK GBA-only\n    \u003c/button\u003e\n\n    \u003cbutton onclick=\"openDoc(this, 'https://gbadev.net/tonc/intro.html')\"\u003e\n      Tonc tutorial\n    \u003c/button\u003e\n\n    \u003cbutton onclick=\"openDoc(this, 'https://www.coranac.com/tonc/text/asm.htm')\"\u003e\n      Tonc ARM/Thumb\n    \u003c/button\u003e\n\n    \u003cbutton onclick=\"openDoc(this, 'https://www.gbadev.org/docs.php')\"\u003e\n      gbadev docs\n    \u003c/button\u003e\n\n    \u003cbutton onclick=\"openDoc(this, 'https://www.copetti.org/es/writings/consoles/game-boy-advance/')\"\u003e\n      Copetti ES\n    \u003c/button\u003e\n  \u003c/div\u003e\n\n  \u003ciframe id=\"viewer\" src=\"https://rust-console.github.io/gbatek-gbaonly/\"\u003e\u003c/iframe\u003e\n\n  \u003cscript\u003e\n    function openDoc(button, url) {\n      document.querySelectorAll(\"button\").forEach(btn =\u003e {\n        btn.classList.remove(\"active\");\n      });\n\n      button.classList.add(\"active\");\n      document.getElementById(\"viewer\").src = url;\n    }\n  \u003c/script\u003e\n\u003c/body\u003e\n\u003c/html\u003e\n"
// DYNAMIC_PLUGINS_DOCS_END
    };

    // Funciones del Portal de Ayuda Premium
    const docContent = document.getElementById("doc-content");
    const contentCard = document.getElementById("content-card");
    const burgerBtn = document.getElementById("burger-btn");
    const sidebar = document.getElementById("sidebar");
    const sidebarOverlay = document.getElementById("sidebar-overlay");
    const themeBtn = document.getElementById("theme-btn");
    const sunIcon = document.getElementById("sun-icon");
    const moonIcon = document.getElementById("moon-icon");
    const searchInput = document.getElementById("search-input");
    const searchBadge = document.getElementById("search-badge");
    const noResults = document.getElementById("no-results");
    const breadcrumbsTitle = document.getElementById("breadcrumbs-title");
    const tocList = document.getElementById("toc-list");
    const tocColumn = document.getElementById("toc-column");

    // Detectar preferencia del sistema para el tema
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)");
    
    // Configurar tema inicial
    function initTheme() {
      const savedTheme = localStorage.getItem("rif-docs-theme");
      if (savedTheme === "light") {
        setLightTheme();
      } else {
        setDarkTheme();
      }
    }

    function setLightTheme() {
      document.body.setAttribute("data-theme", "light");
      sunIcon.style.display = "none";
      moonIcon.style.display = "block";
      localStorage.setItem("rif-docs-theme", "light");
    }

    function setDarkTheme() {
      document.body.removeAttribute("data-theme");
      sunIcon.style.display = "block";
      moonIcon.style.display = "none";
      localStorage.setItem("rif-docs-theme", "dark");
    }

    // Toggle de Tema
    themeBtn.addEventListener("click", () => {
      const isLight = document.body.getAttribute("data-theme") === "light";
      if (isLight) {
        setDarkTheme();
      } else {
        setLightTheme();
      }
    });

    // Menú Burger y Overlay para móvil
    function toggleMobileMenu() {
      sidebar.classList.toggle("active");
      if (sidebar.classList.contains("active")) {
        sidebarOverlay.style.display = "block";
      } else {
        sidebarOverlay.style.display = "none";
      }
    }

    burgerBtn.addEventListener("click", toggleMobileMenu);
    sidebarOverlay.addEventListener("click", toggleMobileMenu);

    // Navegar y Cargar Documentación
    function loadDoc(key) {
      if (docs[key]) {
        // Efecto visual de desvanecimiento
        contentCard.classList.remove("doc-fade");
        void contentCard.offsetWidth; // Forzar reflow
        contentCard.classList.add("doc-fade");

        let rawHtmlStr = docs[key].trim();
        if (rawHtmlStr.charCodeAt(0) === 0xFEFF) {
            rawHtmlStr = rawHtmlStr.slice(1).trim();
        }
        
        if (rawHtmlStr.toLowerCase().startsWith("<!doctype html>") || rawHtmlStr.toLowerCase().startsWith("<html")) {
          // Es un documento HTML puro (como extern-documentation.html)
          const iframe = document.createElement("iframe");
          iframe.style.width = "100%";
          iframe.style.height = "75vh";
          iframe.style.border = "none";
          iframe.style.borderRadius = "8px";
          iframe.srcdoc = rawHtmlStr;

          docContent.innerHTML = "";
          docContent.appendChild(iframe);

          // Ocultar la tabla de contenidos
          tocColumn.style.opacity = "0";
          tocColumn.style.pointerEvents = "none";
        } else {
          // Parsear Markdown e Inyectar
          let htmlContent = marked.parse(docs[key]);
          docContent.innerHTML = htmlContent;
          
          // Post-procesar elementos: Alertas de tipo GitHub blockquotes
          postProcessAlerts();
          
          // Post-procesar bloques de código para añadir envoltorio, cabecera y botón de copia
          postProcessCodeBlocks();
          
          // Autogenerar Tabla de Contenidos (ToC)
          generateToC();

          // Aplicar Prism JS
          if (typeof Prism !== 'undefined') {
            Prism.highlightAllUnder(docContent);
          }
        }

        // Actualizar Migas de Pan (Breadcrumbs)
        const activeLink = document.querySelector(`.menu-link[data-key="${key}"]`);
        if (activeLink) {
          breadcrumbsTitle.textContent = activeLink.textContent.trim();
        }

        // Actualizar UI activa en Sidebar
        document.querySelectorAll(".menu-link").forEach(link => {
          link.classList.remove("active");
          if (link.getAttribute("data-key") === key) {
            link.classList.add("active");
          }
        });
        
        // Desplazar el visor arriba
        document.getElementById("viewport").scrollTop = 0;
        
        // Cerrar Sidebar en Móvil
        sidebar.classList.remove("active");
        sidebarOverlay.style.display = "none";

        // Guardar página actual en hash para permitir recargas persistentes
        window.location.hash = key;
      }
    }

    // Procesamiento de Alertas Markdown (Nota, Tip, Warning, etc.)
    function postProcessAlerts() {
      const blockquotes = docContent.querySelectorAll("blockquote");
      blockquotes.forEach(bq => {
        const text = bq.innerHTML.trim();
        
        const alertPatterns = [
          { key: "[!NOTE]", class: "alert-note", label: "Nota", icon: "M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" },
          { key: "[!IMPORTANT]", class: "alert-danger", label: "Importante", icon: "M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" },
          { key: "[!WARNING]", class: "alert-warning", label: "Advertencia", icon: "M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" },
          { key: "[!TIP]", class: "alert-tip", label: "Consejo", icon: "M9.663 17h4.673M12 3v1m6.364.364l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 01-2 2h0a2 2 0 01-2-2v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" },
          { key: "[!CAUTION]", class: "alert-danger", label: "Peligro", icon: "M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" }
        ];

        for (const pattern of alertPatterns) {
          if (text.includes(pattern.key)) {
            bq.classList.add(pattern.class);
            
            // Remover el token del texto de salida
            let cleanText = text.replace(pattern.key, "").trim();
            // Si el texto queda precedido de un <br> o espacio, limpiarlo
            cleanText = cleanText.replace(/^(<br>|<\/p>|<p>|\s)+/, "");
            if (!cleanText.startsWith("<p>")) {
              cleanText = "<p>" + cleanText + "</p>";
            }

            // Inyectar cabecera de alerta y contenido corregido
            bq.innerHTML = `
              <div class="alert-title">
                <svg fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24" style="width:16px;height:16px;">
                  <path stroke-linecap="round" stroke-linejoin="round" d="${pattern.icon}"></path>
                </svg>
                ${pattern.label}
              </div>
              ${cleanText}
            `;
            break;
          }
        }
      });
    }

    // Post-procesamiento de Bloques de Código (Añadir Cabecera y Botón de Copiado)
    function postProcessCodeBlocks() {
      const preElements = docContent.querySelectorAll("pre");
      preElements.forEach(pre => {
        // Obtener el lenguaje (por defecto txt)
        let lang = "texto";
        const codeElement = pre.querySelector("code");
        if (codeElement) {
          const classes = codeElement.className.split(" ");
          for (const cls of classes) {
            if (cls.startsWith("language-")) {
              lang = cls.replace("language-", "");
              break;
            }
          }
        }

        // Traducir nombres comunes de lenguajes
        const langMap = {
          "bash": "Bash / Terminal",
          "python": "Python Módulo",
          "rif": "RIF Code",
          "text": "Salida",
          "texto": "Texto"
        };
        const displayLang = langMap[lang.toLowerCase()] || lang.toUpperCase();

        // Crear wrapper y cabecera
        const wrapper = document.createElement("div");
        wrapper.className = "code-block-wrapper";
        
        const header = document.createElement("div");
        header.className = "code-header";
        header.innerHTML = `
          <span>${displayLang}</span>
          <button class="copy-btn">
            <svg class="copy-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"></path>
            </svg>
            Copiar
          </button>
        `;

        // Intercambiar nodos en el DOM
        pre.parentNode.insertBefore(wrapper, pre);
        wrapper.appendChild(header);
        wrapper.appendChild(pre);

        // Añadir lógica del botón de copiado
        const copyBtn = header.querySelector(".copy-btn");
        copyBtn.addEventListener("click", () => {
          const textToCopy = codeElement ? codeElement.textContent : pre.textContent;
          navigator.clipboard.writeText(textToCopy).then(() => {
            copyBtn.innerHTML = `
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2.5" style="color:#10b981;">
                <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"></path>
              </svg>
              ¡Copiado!
            `;
            copyBtn.style.backgroundColor = "rgba(16, 185, 129, 0.15)";
            copyBtn.style.borderColor = "#10b981";
            copyBtn.style.color = "#10b981";

            setTimeout(() => {
              copyBtn.innerHTML = `
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"></path>
                </svg>
                Copiar
              `;
              copyBtn.style.backgroundColor = "";
              copyBtn.style.borderColor = "";
              copyBtn.style.color = "";
            }, 2000);
          }).catch(err => {
            console.error("Error al copiar código: ", err);
          });
        });
      });
    }

    // Generar dinámicamente la Tabla de Contenidos (ToC)
    function generateToC() {
      tocList.innerHTML = "";
      const headings = docContent.querySelectorAll("h2, h3");

      if (headings.length === 0) {
        tocColumn.style.opacity = "0";
        tocColumn.style.pointerEvents = "none";
        return;
      }

      tocColumn.style.opacity = "1";
      tocColumn.style.pointerEvents = "all";

      headings.forEach((heading, idx) => {
        // Crear un ID si no existe
        const headingText = heading.textContent.trim();
        const id = "section-" + idx;
        heading.id = id;

        // Crear elemento en ToC
        const li = document.createElement("li");
        const a = document.createElement("a");
        a.href = "#" + id;
        a.className = "toc-link";
        a.textContent = headingText;

        if (heading.tagName.toLowerCase() === "h3") {
          a.classList.add("indent-h3");
        }

        // Scroll suave al pulsar el enlace
        a.addEventListener("click", (e) => {
          e.preventDefault();
          heading.scrollIntoView({ behavior: "smooth" });
          document.querySelectorAll(".toc-link").forEach(l => l.classList.remove("active"));
          a.classList.add("active");
        });

        li.appendChild(a);
        tocList.appendChild(li);
      });

      // Lógica de resalte del ToC activo mediante scroll observer
      setTimeout(setupScrollObserver, 100);
    }

    // Observer para resaltar la sección activa en ToC al hacer scroll
    let currentObserver = null;
    function setupScrollObserver() {
      if (currentObserver) {
        currentObserver.disconnect();
      }

      const links = document.querySelectorAll(".toc-link");
      const headings = Array.from(docContent.querySelectorAll("h2, h3"));

      if (headings.length === 0 || links.length === 0) return;

      const observerOptions = {
        root: document.getElementById("viewport"),
        rootMargin: "-20px 0px -80% 0px",
        threshold: 0
      };

      currentObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            const id = entry.target.id;
            links.forEach(link => {
              link.classList.remove("active");
              if (link.getAttribute("href") === "#" + id) {
                link.classList.add("active");
              }
            });
          }
        });
      }, observerOptions);

      headings.forEach(h => currentObserver.observe(h));
    }

    // Buscador en Tiempo Real por Título y Contenido de los Documentos
    searchInput.addEventListener("input", function() {
      const query = this.value.trim().toLowerCase();
      const links = document.querySelectorAll(".menu-link");
      const groups = document.querySelectorAll(".menu-group");
      let matchesCount = 0;

      if (query === "") {
        // Limpiar búsqueda
        links.forEach(link => {
          link.style.display = "flex";
          // Limpiar resalte visual si existe
          const span = link.querySelector(".match-highlight");
          if (span) {
            link.innerHTML = link.dataset.originalHTML;
          }
        });
        groups.forEach(g => g.style.display = "block");
        noResults.style.display = "none";
        searchBadge.style.display = "none";
        return;
      }

      links.forEach(link => {
        const key = link.getAttribute("data-key");
        const docText = docs[key] ? docs[key].toLowerCase() : "";
        const titleText = link.textContent.trim().toLowerCase();
        
        // Guardar HTML original para restaurar después
        if (!link.dataset.originalHTML) {
          link.dataset.originalHTML = link.innerHTML;
        }

        // Buscar tanto en título como en el contenido del documento Markdown
        const inTitle = titleText.includes(query);
        const inContent = docText.includes(query);

        if (inTitle || inContent) {
          link.style.display = "flex";
          matchesCount++;
          
          // Efecto de resalte si la búsqueda coincide en el título
          if (inTitle) {
            const regex = new RegExp(`(${escapeRegExp(query)})`, "gi");
            // Mantener el SVG del icono intacto al reescribir
            const iconSvg = link.querySelector("svg").outerHTML;
            const textOnly = link.textContent.trim();
            const highlightedText = textOnly.replace(regex, `<span style="background-color:rgba(139, 92, 246, 0.3);color:var(--text-strong);border-radius:3px;padding:0 2px;">$1</span>`);
            link.innerHTML = `${iconSvg} ${highlightedText}`;
          } else {
            // Restaurar original si coincidió por contenido pero no por título
            link.innerHTML = link.dataset.originalHTML;
          }
        } else {
          link.style.display = "none";
        }
      });

      // Ocultar categorías enteras del menú si no tienen enlaces visibles
      groups.forEach(g => {
        const visibleLinks = g.querySelectorAll(".menu-link[style='display: flex;']");
        if (visibleLinks.length === 0) {
          g.style.display = "none";
        } else {
          g.style.display = "block";
        }
      });

      // Mostrar badge de resultados
      searchBadge.textContent = matchesCount;
      searchBadge.style.display = "block";

      // Mostrar mensaje si no hay resultados
      if (matchesCount === 0) {
        noResults.style.display = "block";
      } else {
        noResults.style.display = "none";
      }
    });

    // Helper para escapar regex
    function escapeRegExp(string) {
      return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }

    // Interceptar Clics del Menú
    document.querySelectorAll(".menu-link").forEach(link => {
      link.addEventListener("click", function(e) {
        e.preventDefault();
        const key = this.getAttribute("data-key");
        loadDoc(key);
      });
    });

    // Leer hash inicial al cargar para navegación directa persistente
    function handleInitialHash() {
      const hash = window.location.hash.replace("#", "");
      if (hash && docs[hash]) {
        loadDoc(hash);
      } else {
        loadDoc("que_es_rif"); // Default
      }
    }

    // Inicialización al cargar el DOM
    window.addEventListener("DOMContentLoaded", () => {
      initTheme();
      handleInitialHash();
    });
  