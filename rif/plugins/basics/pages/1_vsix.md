# 🔌 Integración VS Code (VSIX)

RIF puede compilar una extensión VS Code profesional en formato `.vsix` desde los metadatos de los plugins. Este soporte está en estado **RIF 0.0.3 Semi Stable**: es un generador completo de extensiones de lenguaje con soporte TextMate, snippets, autocompletado, hovers, diagnósticos y quick fixes.

---

## ✨ Capacidades Incluidas

### Funcionalidades del Lenguaje

- **Resaltado de Sintaxis TextMate** - Colorización automática de directivas, palabras clave y operadores
- **Autocompletado Inteligente** - Snippets contextuales para agilizar la escritura
- **Hover con Documentación** - Información en formato Markdown al pasar el cursor
- **Diagnósticos por Regex** - Validación de patrones comunes durante la escritura
- **Quick Fixes** - Sugerencias automáticas para arreglar problemas detectados
- **Símbolos de Documento** - Navegación rápida por etiquetas y reglas
- **Asociación de Extensiones** - Vinculación automática con extensiones personalizadas

### Distribución

- **Documentación Embebida** - Todo el contenido incluido en el VSIX
- **Assets Empaquetados** - Iconos, imágenes y recursos dentro del paquete
- **Independencia** - No requiere servidor de lenguaje externo
- **Instalación Sencilla** - Un comando para instalar en VS Code

---

## 🚀 Compilar un VSIX desde Plugins

### Forma Recomendada (Nueva)

```bash
python -m rif compile --vscode \
  --ext .gbasm \
  --icon rif/plugins/gba/vscode/assets/gba-memory.svg \
  --p gba sound fonts basics \
  -o build/vscode/rif-gba-sound-fonts-basics-0.2.0.vsix
```

### Forma Alternativa (Antigua, aún compatible)

```bash
python -m rif compile --vscode \
  gba sound fonts basics \
  --ext .gbasm \
  --icon rif/plugins/gba/vscode/assets/gba-memory.svg
```

### Argumentos CLI

| Argumento | Forma corta | Descripción |
|-----------|------------|-----------|
| `--vscode` | - | Activa el compilador de extensiones VS Code |
| `--p` / `--plugins` | - | Lista los plugins que aportan bundles `vscode/` |
| `--ext` | - | Fuerza la extensión de archivo (ej: `.gbasm`, `.rif`) |
| `-icon` / `--icon` | - | Ruta al archivo de icono (PNG, JPG, GIF, WebP, SVG) |
| `-o` / `--output` | - | Ruta de salida del archivo `.vsix` |

---

## 📦 Estructura de Salida

El VSIX se genera por defecto en:
```
build/vscode/rif-{plugins}-{version}.vsix
```

Ejemplo:
```
build/vscode/rif-gba-sound-fonts-basics-0.2.0.vsix
```

---

## 🔧 Instalación en VS Code

Después de compilar, instala la extensión:

```bash
python -m rif install --vscode build/vscode/rif-gba-sound-fonts-basics-0.2.0.vsix
```

### Requisitos Previos

- VS Code debe estar instalado
- El comando `code` debe estar disponible en el PATH

### Si `code` no está en el PATH

1. Abre la **Paleta de Comandos** en VS Code (`Ctrl+Shift+P` / `Cmd+Shift+P`)
2. Escribe: `Shell Command: Install 'code' command in PATH`
3. Presiona Enter
4. Reinicia la terminal si es necesario

### Verificación Manual

```bash
# Verificar que code esté disponible
which code

# Instalar manualmente si falla el autodetección
# (Busca la carpeta de instalación de VS Code en tu sistema)
```

---

## 🏗️ Armar Soporte VSIX para tu Plugin

### Estructura de Directorios

Cada plugin puede incluir metadatos de VS Code:

```text
mi_plugin/
  pack.json
  README.md
  vscode/
    build.json
    syntaxs.json
    doc.json
    assets/
      icon.svg
      logo.png
```

### 1. `build.json` - Identidad de la Extensión

Define los metadatos de la extensión en el Marketplace:

```json
{
  "displayName": "RIF Mi ISA",
  "description": "Soporte VS Code para mi arquitectura ISA personalizada.",
  "author": {
    "name": "Mi Nombre",
    "url": "https://ejemplo.com"
  },
  "version": "0.2.0",
  "license": "MIT",
  "extensions": [".miisa", ".mi-asm"],
  "categories": ["Programming Languages", "Snippets"],
  "keywords": ["rif", "assembler", "mi-isa", "compilador"]
}
```

**Campos:**
- `displayName` ⭐ - Nombre que aparece en VS Code
- `description` - Descripción breve
- `version` - Versión semántica (ej: `0.2.0`)
- `extensions` - Extensiones de archivo asociadas
- `categories` - Categorías en el Marketplace
- `keywords` - Palabras clave para búsqueda
- `license` - Tipo de licencia
- `author` - Información del desarrollador

### 2. `syntaxs.json` - Vocabulario y Diagnósticos

Define palabras clave, colores, completados y diagnósticos:

```json
{
  "directives": [".text", ".data", ".bss"],
  "builtins": ["need", "emit", "call", "align"],
  "keywords": ["mov", "add", "jump", "call"],
  "types": ["u8", "u16", "u32", "u64"],
  "registers": ["R0", "R1", "R2", "R3"],
  "completions": [
    {
      "label": "mov",
      "insertText": "mov ${1:R0}, ${2:R1}",
      "detail": "Mi ISA",
      "documentation": "Copia datos de un registro a otro.",
      "kind": "Snippet",
      "sortText": "001"
    },
    {
      "label": ".section",
      "insertText": ".section ${1:name}\n    ${2:contenido}",
      "detail": "Directiva",
      "kind": "Keyword"
    }
  ],
  "patterns": [
    {
      "name": "keyword.operator.rif",
      "match": "\\b(?:=|,|:|;)\\b"
    },
    {
      "name": "constant.language.boolean.rif",
      "match": "\\b(?:true|false|on|off)\\b"
    }
  ],
  "errors": [
    {
      "match": "\\bjump\\s+PC\\b",
      "message": "Evita saltar explícitamente a PC.",
      "severity": "warning",
      "code": "jump-pc",
      "suggest": "Usa etiquetas en lugar de direcciones hardcodeadas."
    },
    {
      "match": "^\\s*emit\\s*$",
      "message": "emit requiere bits, un placeholder o una variable.",
      "severity": "error",
      "code": "rif-empty-emit"
    }
  ]
}
```

**Secciones:**

#### `directives`
Palabras clave que comienzan con punto (`.pack`, `.rules`, etc.)

#### `builtins`
Funciones/instrucciones fundamentales del lenguaje

#### `keywords`
Palabras clave de dominio específico (mnemónicos, etc.)

#### `types`
Tipos de dato reconocidos

#### `registers`
Nombres de registros disponibles

#### `completions`
Array de sugerencias de autocompletado

**Campos de completion:**
- `label` - Texto mostrado en el menú
- `insertText` - Código insertado (puede incluir `${1:placeholder}`)
- `documentation` - Descripción al seleccionar
- `kind` - Tipo (Snippet, Keyword, Function, etc.)
- `sortText` - Orden en el menú (números sortean primero)

#### `patterns`
Reglas TextMate para colorización

#### `errors`
Diagnósticos por expresión regular

**Campos de error:**
- `match` - Regex para detectar el problema
- `message` - Mensaje de error
- `severity` - `error`, `warning` o `hint`
- `code` - ID único del diagnóstico
- `suggest` - Quick fix sugerido

### 3. `doc.json` - Documentación en Hovers

Define documentación que aparece al pasar el cursor sobre palabras:

```json
{
  "words": {
    "rif_project": {
      "doc": [
        {
          "type": "text",
          "content": "RIF separa arquitectura, herramientas y proyecto."
        },
        {
          "type": "code",
          "content": ".pack\nplugin \"basics\"\nplugin \"gba\""
        }
      ]
    },
    "need": {
      "doc": [
        {
          "type": "text",
          "content": "Consume y valida operandos de una regla."
        },
        {
          "type": "code",
          "content": "need VALUE, imm"
        },
        {
          "type": "text",
          "content": "Soporta múltiples tipos separados por comas."
        }
      ]
    },
    "emit": {
      "doc": [
        {
          "type": "text",
          "content": "Emite bits o placeholders ya capturados."
        },
        {
          "type": "code",
          "content": "emit imm.binary"
        }
      ]
    }
  }
}
```

**Estructura:**
- `words` - Diccionario de palabra → documentación
- `doc` - Array de bloques de documentación
- `type` - `"text"` o `"code"`
- `content` - Contenido del bloque

---

## 📋 Flujo Recomendado

### Para un Nuevo Plugin con Soporte VS Code

```
1. Define o ajusta tu pack.json
   ↓
2. Crea la carpeta vscode/
   ├── build.json  (identidad)
   ├── syntaxs.json (vocabulario)
   ├── doc.json    (documentación)
   └── assets/
       └── icon.svg (opcional)
   ↓
3. Compila el VSIX
   $ python -m rif compile --vscode --p tu_plugin basics
   ↓
4. Instala en VS Code
   $ python -m rif install --vscode build/vscode/rif-tu-plugin.vsix
   ↓
5. Abre un archivo con la extensión configurada
   ↓
6. Ajusta completions, diagnósticos y hovers
   según lo que se necesite mejorar
   ↓
7. Vuelve a compilar e instalar
```

---

## 🎨 Ejemplo Completo: Plugin GBA

### Estructura

```
rif/plugins/gba/
  pack.json
  README.md
  vscode/
    build.json
    syntaxs.json
    doc.json
    assets/
      gba-memory.svg
```

### build.json

```json
{
  "displayName": "RIF Game Boy Advance",
  "description": "Ensamblador retargetable para GBA con Thumb y ARM.",
  "version": "0.2.0",
  "extensions": [".gbasm"],
  "categories": ["Programming Languages"],
  "keywords": ["gba", "gameboy", "arm", "thumb", "assembler"]
}
```

### Compilación

```bash
python -m rif compile --vscode \
  --ext .gbasm \
  --icon rif/plugins/gba/vscode/assets/gba-memory.svg \
  --p gba sound fonts basics
```

### Resultado

```
build/vscode/rif-gba-sound-fonts-basics-0.2.0.vsix
```

---

## 🔍 Debugging de Extensiones

### Verificar el Contenido del VSIX

Los archivos `.vsix` son ZIP:

```bash
unzip -l build/vscode/rif-gba.vsix
```

### Buscar Errores Comunes

```bash
# Verificar que los archivos JSON sean válidos
python -m json.tool rif/plugins/tu_plugin/vscode/build.json

# Validar sintaxis de regex en syntaxs.json
python -c "import re; re.compile(r'tu_regex')"
```

### Recargar la Extensión

En VS Code después de cambios:
1. Presiona `Ctrl+Shift+P` (Windows/Linux) o `Cmd+Shift+P` (Mac)
2. Escribe `Reload Window`
3. Presiona Enter

### Abrir Consola de Desarrollo

```
Help → Toggle Developer Tools
```

Aquí puedes ver errores de la extensión en tiempo real.

---

## 📊 Casos de Uso

### Caso 1: Extensión Solo para GBA

```bash
python -m rif compile --vscode \
  --ext .gbasm \
  --p gba basics
```

### Caso 2: Extensión Multi-Arquitectura

```bash
python -m rif compile --vscode \
  --ext .rif \
  --p gba atari2600 amd64 basics
```

### Caso 3: Extensión con Icono Personalizado

```bash
python -m rif compile --vscode \
  --ext .myasm \
  --icon my_logo.svg \
  --p mi_plugin basics \
  -o build/vscode/mi-extension.vsix
```

---

## 🐛 Solución de Problemas

### "El comando `code` no se encuentra"

**Solución:**
```bash
# En Windows
"C:\Program Files\Microsoft VS Code\bin\code.cmd"

# En macOS
/Applications/Visual\ Studio\ Code.app/Contents/Resources/app/bin/code

# En Linux (usualmente ya está en PATH)
which code
```

### La extensión no se instala

```bash
# Verifica que VS Code esté cerrado
# Intenta con ruta absoluta
python -m rif install --vscode /full/path/to/extension.vsix

# O instala manualmente en VS Code
# Extensions → Install from VSIX
```

### Los hovers no aparecen

1. Verifica que `doc.json` sea válido
2. Asegúrate de que las claves en `doc.json` coincidan con las palabras clave
3. Recarga la ventana de VS Code

### Autocompletado no funciona

1. Revisa que `syntaxs.json` tenga la sección `completions`
2. Verifica que `kind` sea un valor válido
3. Usa `sortText` para controlar el orden

---

## 🔗 Véase También

- [Catálogo de Instrucciones](0_instrucciones.md) - Documentación de directivas
- [Estructura Interna del Plugin](estructura.md) - Cómo crear plugins
- [Mecanismos de Importación](importar.md) - Carga de plugins
