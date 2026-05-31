# Integracion VS Code (VSIX)

RIF puede compilar una extension VS Code en formato `.vsix` desde los metadatos de los plugins. Este soporte es parte del estado `RIF 0.0.3 Semi Stable`: no es un Language Server completo, pero ya entrega una experiencia de editor suficiente para trabajar con archivos RIF y dialectos como `.gbasm`.

## Capacidades incluidas

- Resaltado de sintaxis TextMate.
- Autocompletado y snippets.
- Hover con documentacion Markdown.
- Diagnosticos por expresiones regulares.
- Quick fixes cuando el diagnostico declara `suggest`.
- Simbolos de documento para secciones y etiquetas.
- Documentacion y assets empaquetados dentro del VSIX.
- Asociacion de extensiones de archivo como `.rif`, `.gbasm` o una extension propia.

## Compilar un VSIX desde plugins

La forma recomendada es:

```bash
python -m rif compile --vscode --ext .gbasm -icon rif/plugins/gba/vscode/assets/gba-memory.svg --p gba sound fonts basics
```

Tambien puedes fijar la salida:

```bash
python -m rif compile --vscode --ext .gbasm -icon rif/plugins/gba/vscode/assets/gba-memory.svg --p gba sound fonts basics -o build/vscode/rif-gba-sound-fonts-basics-0.2.0.vsix
```

Argumentos:

- `--vscode`: activa el builder de extensiones.
- `--p`: lista los plugins que aportan bundles `vscode/`.
- `--ext`: fuerza la extension de archivo asociada al lenguaje generado.
- `-icon` o `--icon`: empaqueta el icono de la extension.
- `-o` o `--output`: escribe el `.vsix` en una ruta especifica.

La forma antigua sigue funcionando:

```bash
python -m rif compile --vscode gba sound fonts basics --ext .gbasm --icon rif/plugins/gba/vscode/assets/gba-memory.svg
```

## Instalar en VS Code

Despues de compilar:

```bash
python -m rif install --vscode build/vscode/rif-gba-sound-fonts-basics-0.2.0.vsix
```

RIF usa el ejecutable `code` de VS Code. Si el comando no esta en el PATH, abre la paleta de comandos de VS Code y ejecuta `Shell Command: Install 'code' command in PATH`, o instala manualmente desde `Extensions > Install from VSIX...`.

## Armar soporte para tu plugin

Cada plugin puede incluir:

```text
mi_plugin/
  pack.json
  vscode/
    build.json
    syntaxs.json
    doc.json
    assets/
      icon.svg
```

`build.json` define la identidad:

```json
{
  "displayName": "RIF Mi ISA",
  "description": "Soporte VS Code para mi ISA.",
  "version": "0.2.0",
  "extensions": [".miisa"],
  "categories": ["Programming Languages", "Snippets"],
  "keywords": ["rif", "assembler"]
}
```

`syntaxs.json` define vocabulario y diagnosticos:

```json
{
  "directives": [".text", ".data"],
  "registers": ["R0", "R1", "R2", "R3"],
  "keywords": ["mov", "add", "jump"],
  "types": ["u8", "u16", "u32"],
  "completions": [
    {
      "label": "mov",
      "insertText": "mov ${1:R0}, ${2:R1}",
      "detail": "Mi ISA",
      "documentation": "Copia un registro fuente a un destino.",
      "kind": "Snippet"
    }
  ],
  "errors": [
    {
      "match": "\\bjump\\s+PC\\b",
      "message": "Evita saltar explicitamente a PC.",
      "severity": "warning",
      "code": "jump-pc",
      "suggest": "Usa jump etiqueta."
    }
  ]
}
```

`doc.json` define hovers:

```json
{
  "words": {
    "mov": {
      "doc": [
        {
          "type": "text",
          "content": "Copia un registro en otro."
        },
        {
          "type": "code",
          "content": "mov R0, R1"
        }
      ]
    }
  }
}
```

Luego compila:

```bash
python -m rif compile --vscode --ext .miisa --p mi_plugin basics -o build/vscode/rif-mi-plugin.vsix
```

## Flujo recomendado

1. Define o ajusta tu pack.
2. Agrega `vscode/build.json`, `vscode/syntaxs.json` y `vscode/doc.json`.
3. Compila el VSIX.
4. Instala con `rif install --vscode`.
5. Abre un archivo con la extension configurada.
6. Ajusta completions, diagnosticos y hovers segun lo que duela al escribir codigo real.
