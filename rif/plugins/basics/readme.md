# 🛠️ RIF Basics Plugin

`basics` es el plugin fundacional y la biblioteca estándar de **Retargetable ISA Foundry (RIF)**. Su propósito es proveer todas las directivas genéricas de ensamblado, manipulación de bits, control de alineación y relocación necesarias para dar soporte a cualquier arquitectura de hardware sin hardcodear lógica en el núcleo de RIF.

---

## 🧭 Arquitectura y Filosofía

En RIF, el compilador procesa archivos `.pack` que importan el plugin `basics`:
```rif
.pack
plugin "basics"
```

Cada instrucción definida dentro de la tabla `.rules` o `.words` de un pack delega su procesamiento lexer/parser a archivos Python individuales dentro del directorio `plugins/` de `basics`. Al invocar una palabra como `need` o `emit`, el compilador transfiere el control al plugin pasándole el contexto activo (`Line`, `Operator`, `Operators`, `TYPES_MAP`). El plugin analiza los argumentos, realiza validaciones en tiempo de compilación y retorna un objeto `Expr` (Expresión) que instruye al compilador exactamente qué bits emitir o qué símbolos registrar.

---

## 📦 Componentes del Plugin

El plugin `basics` está organizado en los siguientes módulos:

1.  **Directivas de Control (`plugins/`):**
    *   `need`: Captura operandos y valida sus tipos primitivos o derivados.
    *   `emit`: Serializa fragmentos de bits (estáticos o dinámicos) hacia el stream binario.
    *   `call`: Reutiliza y salta a sub-reglas del compilador.
2.  **Operadores de Bits y Conversiones (`plugins/`):**
    *   `bitcat`, `trunc`, `zext`, `sext`, `bitfit`, `bitsize`, `fits`: Aritmética y re-formateado de bits.
3.  **Relocaciones y Símbolos (`plugins/`):**
    *   `reloc`: Emite direcciones absolutas y delega su resolución final al linker.
    *   `reldis`: Calcula desplazamientos relativos al PC de ejecución (para saltos `bcond` o cargas `ldr_pc`).
    *   `emitaddress`, `exists`, `fillid`, `vfillid`: Ubicación y resolución de etiquetas de código y fillables en `fills.json`.
4.  **Alineación y Layout (`plugins/`):**
    *   `align`, `pad`: Relleno de bytes y alineación en límites físicos de memoria.
5.  **Herramientas de Consola (`cli/`):**
    *   `build-doc`: Compilador automatizado de documentación y generador de extensiones VSIX para VS Code.

---

## 📖 Documentación Completa

Para conocer a fondo el funcionamiento de cada directiva y cómo se comunican con el compilador, consulta las subsecciones detalladas:

*   [📖 Catálogo Completo de Instrucciones](file:///c:/Users/Kentucky/Desktop/AMST/Retargetable-ISA-Foundry-RIF-/rif/plugins/basics/pages/0_instrucciones.md): Sintaxis, parámetros, comunicación interna y ejemplos reales de las 20+ instrucciones.
*   [🔌 Integración VS Code (VSIX)](file:///c:/Users/Kentucky/Desktop/AMST/Retargetable-ISA-Foundry-RIF-/rif/plugins/basics/pages/1_vsix.md): Guía de empaquetado de extensiones y soporte lingüístico para tu arquitectura.
