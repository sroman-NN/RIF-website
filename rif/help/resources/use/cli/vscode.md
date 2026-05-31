# VS Code y VSIX

RIF 0.0.3 Semi Stable ya puede armar extensiones VS Code en formato `.vsix` desde los bundles `vscode/` de los plugins. La extension generada no es un servidor de lenguaje completo, pero si entrega una experiencia usable para escribir ensamblador RIF: resaltado, snippets, completions, hovers, diagnosticos por regex, quick fixes, simbolos de documento y documentacion empaquetada.

## Que compila RIF

Cuando ejecutas `rif compile --vscode`, RIF junta la informacion de los plugins seleccionados y crea un VSIX instalable. Cada plugin puede aportar estos archivos:

- `vscode/build.json`: nombre, version, extensiones de archivo, publisher, descripcion, categorias e icono por defecto.
- `vscode/syntaxs.json`: directivas, registros, palabras clave, tipos, snippets, completions, patrones TextMate y reglas de diagnostico.
- `vscode/doc.json`: documentacion para hovers y paginas Markdown por palabra.
- `vscode/assets/`: imagenes o recursos que se empaquetan con la extension.
- `README.md` y `pages/*.md`: documentacion del plugin incluida dentro del VSIX.

El resultado se escribe como `.vsix` y contiene un `package.json` de VS Code, gramatica TextMate, snippets, runtime `extension.js`, JSON de completions, JSON de diagnosticos y documentacion.

## Compilar una extension VS Code

La forma recomendada es usar `--vscode` con `--p` para declarar los plugins:

```bash
python -m rif compile --vscode --ext .gbasm -icon rif/plugins/gba/vscode/assets/gba-memory.svg --p gba sound fonts basics
```

Argumentos importantes:

- `--vscode`: activa el constructor de VSIX.
- `--p gba sound fonts basics`: lista de plugins cuyos bundles `vscode/` se van a fusionar.
- `--ext .gbasm`: fuerza la extension de archivo que VS Code asociara al lenguaje generado.
- `-icon ruta/icono.png`: empaqueta un icono para la extension. Acepta `.png`, `.jpg`, `.jpeg`, `.gif`, `.webp` o `.svg`.
- `-o ruta/salida.vsix`: opcional. Define el archivo VSIX final.

Tambien puedes pasar los plugins justo despues de `--vscode`:

```bash
python -m rif compile --vscode gba sound fonts basics --ext .gbasm --icon rif/plugins/gba/vscode/assets/gba-memory.svg
```

Si no usas `-o`, RIF crea el VSIX dentro de `build/vscode/` con un nombre derivado de los plugins y la version del bundle.

## Ejemplo completo para GBA

Desde la raiz del repositorio:

```bash
python -m rif compile --vscode --ext .gbasm -icon rif/plugins/gba/vscode/assets/gba-memory.svg --p gba sound fonts basics -o build/vscode/rif-gba-sound-fonts-basics-0.2.0.vsix
```

Esto arma una extension que reconoce archivos `.gbasm`, combina soporte de GBA, audio, fuentes bitmap y las primitivas de `basics`.

## Instalar la extension en VS Code

Instala el VSIX generado con:

```bash
python -m rif install --vscode build/vscode/rif-gba-sound-fonts-basics-0.2.0.vsix
```

RIF busca el comando `code` en el PATH y ejecuta internamente:

```bash
code --install-extension build/vscode/rif-gba-sound-fonts-basics-0.2.0.vsix
```

Si `code` no existe en el PATH, abre VS Code y activa `Shell Command: Install 'code' command in PATH` desde la paleta de comandos. En Windows tambien puedes instalar desde la interfaz: Extensions, menu de tres puntos, `Install from VSIX...`.

## Armar tu propio bundle VS Code

Para que un plugin aporte soporte al VSIX, crea esta estructura:

```text
rif/plugins/mi_plugin/
  pack.json
  vscode/
    build.json
    syntaxs.json
    doc.json
    assets/
      icon.svg
```

`build.json` minimo:

```json
{
  "displayName": "RIF Mi Plugin",
  "description": "Soporte VS Code para mi arquitectura RIF.",
  "version": "0.2.0",
  "extensions": [".miisa"],
  "categories": ["Programming Languages", "Snippets"],
  "keywords": ["rif", "assembler"]
}
```

`syntaxs.json` minimo:

```json
{
  "directives": [".text", ".data", ".rodata"],
  "registers": ["R0", "R1", "R2", "R3"],
  "keywords": ["mov", "add", "sub", "jump"],
  "types": ["u8", "u16", "u32"],
  "completions": [
    {
      "label": "mov",
      "insertText": "mov ${1:R0}, ${2:R1}",
      "detail": "Mi ISA",
      "documentation": "Copia un registro en otro.",
      "kind": "Snippet"
    }
  ],
  "errors": [
    {
      "match": "\\bjump\\s+PC\\b",
      "message": "Evita saltar explicitamente a PC.",
      "severity": "warning",
      "code": "jump-pc"
    }
  ]
}
```

`doc.json` minimo:

```json
{
  "words": {
    "mov": {
      "doc": [
        {
          "type": "text",
          "content": "Copia el valor de un registro fuente en un registro destino."
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

1. Crea o actualiza el pack de tu arquitectura.
2. Agrega `vscode/build.json`, `vscode/syntaxs.json` y `vscode/doc.json` al plugin.
3. Compila el VSIX con `rif compile --vscode`.
4. Instala con `rif install --vscode`.
5. Abre un archivo con la extension configurada, por ejemplo `test.gbasm`.
6. Ajusta snippets, errores y documentacion hasta que el editor sea comodo.

## Limites actuales

El soporte actual es "Semi Stable": suficiente para trabajar con resaltado y ayudas de editor, pero todavia no reemplaza un Language Server completo. Los diagnosticos profundos que dependen de compilar el pack, entender tipos reales o ejecutar analisis semantico avanzado siguen siendo trabajo futuro del ecosistema general, no una promesa del VSIX generado actual.
