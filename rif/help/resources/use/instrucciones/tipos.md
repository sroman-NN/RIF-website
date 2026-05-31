# Sistema de Tipos y Lógica

En RIF, cada operando capturado por directivas (como `need` del plugin `basics`) o evaluado por las instrucciones nativas debe coincidir con una firma de tipo válida. El compilador maneja **Tipos Primitivos** (integrados en el núcleo) y **Tipos Dinámicos** (definidos por tu arquitectura).

## 1. Tipos Primitivos (Built-in)

Estos tipos están siempre disponibles de manera transparente, independientemente de la configuración del archivo `.pack`.

- **`VALUE`**: Representa cualquier constante entera, hexadecimal (`0x...`), binaria (`0b...`), octal, y los valores literales inmediatos (`imm`). El compilador procesa el token aritméticamente y calcula su ancho binario exacto en tiempo de ensamblado.
- **`SYMBOL`**: Un identificador o puntero a una etiqueta de datos. Generalmente apunta a una región estática de memoria como `.data`, `.rodata` o a una posición dentro de la imagen física.
- **`LABEL`**: Identificador utilizado específicamente para referencias de flujos de control o direcciones ejecutables (como sub-rutinas, ramas o posiciones de salto relativo).
- **`TYPE`**: Una referencia hacia un alias o una primitiva de tipo de dato configurado explícitamente en la sección `.types`.
- **`STACK`, `HEAP`, `MEMORY`**: Alias semánticos nativos diseñados para facilitar la representación en memoria y diferenciar visualmente los punteros hacia pila y montículo.

## 2. Tipos Dinámicos de Arquitectura

El núcleo del compilador se inyecta dinámicamente con tipos adicionales a medida que parsea las tablas y configuraciones del archivo `.pack`:

- **`REG`**: Este tipo es registrado automáticamente cuando defines tu tabla de registros ISA en la sección `.regs`. Si un plugin invoca una captura de un `REG`, el compilador validará iterativamente si el token ingresado existe en la columna `NAME` o es un `alias` válido de la tabla `.regs` activa.
- **`SREG` (Sub-Registros)**: Un tipo derivado y manejado internamente (mapeado hacia `.regs.subs`) que permite al motor de compilación identificar si el programador especificó un registro "hijo" (fraccionario) comprobando jerárquicamente su compatibilidad con el registro padre subyacente.

## 3. Tipos Basados en Definiciones de Tablas (`TYPES_MAP`)

Aparte de los integrados, tú puedes definir tus propios esquemas tipados en la sección `.types` de tu paquete. 
Si el diseñador de la arquitectura o lenguaje permite declarar campos personalizados como `i8`, `u32` o `float16`, estos se incorporan estructuralmente de forma global en RIF a través del diccionario general de evaluación `TYPES_MAP`.

Adicionalmente, las llamadas que interceden sobre secciones usando un punto como prefijo (tales como `.regs.subs`, `.rom`, `.data`, o `.bss`) también operan en RIF como tipos formales. Esto le permite al objeto `Operator` aislar en qué ámbito de memoria o de variables reside un parámetro.

## 4. Lógica de Evaluación y Binding

Cuando el intérprete o un plugin captura una instrucción usando `need` (por ejemplo: `need VALUE, imm`), el motor interno orquesta el siguiente flujo:

1. **Resolución de Referencia**: RIF consulta primero si la cadena literal proporcionada existe dentro de `TYPES_MAP` (priorizando los tipos creados localmente).
2. **Fallback Primitivo**: De no ser hallado, intenta equiparar el token a las constantes léxicas nativas (`_BUILTIN_TYPES`).
3. **Mapeo Dimensional**: Si la instrucción capturada exige un registro o componente, RIF inspecciona la meta-tabla (`.regs`, o `.vars`) para localizar los metadatos y el tamaño binario enlazado a ese identificador.
4. **Resguardo (Binding)**: Si existe concordancia entre el tipo real del elemento escrito por el usuario y el tipo pedido por el analizador, se genera un `Binding` transparente incrustado a través del objeto `Operator`. En caso contrario, el escáner declina la regla en caliente y arroja un error estructurado, alertando semánticamente: *"Se esperaba X tipo, pero se recibió Y"*.
