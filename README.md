# Retargetable ISA Foundry (RIF)

RIF es un framework para crear ensambladores, linkers, compiladores, packs de arquitectura y herramientas de editor sin amarrar el nucleo a una CPU concreta. La idea central es simple: describes una ISA con tablas `.pack`, conectas plugins cuando necesitas semantica especial, y RIF genera binarios, documentacion y tooling alrededor de esa definicion.

## Capacidades principales

- **ISA retargetable**: define instrucciones, registros, tipos, secciones, memoria, headers y reglas de emision por medio de archivos `.pack`.
- **Lexer y parser configurables**: permite cambiar comentarios, separadores, bloques, encoding y estructura de tablas desde la propia especificacion.
- **Compilacion de instrucciones**: `rif compile <pack> <instruccion...>` compila una instruccion aislada y muestra los bytes/bits resultantes.
- **Construccion de binarios**: `rif build` enlaza, compila secciones y escribe ROMs o binarios finales con extension de salida configurable.
- **Packer y linker integrados**: `rif pack` y `rif link` unen proyectos repartidos en varios archivos, resuelven secciones requeridas/opcionales y generan fuentes temporales consolidadas.
- **Sistema de fragmentos por extension**: los packs pueden declarar `ext`, `outext`, prefijos de seccion y archivos fuente por seccion, por ejemplo `.gbasm` para GBA.
- **Etiquetas, placeholders y relocaciones**: el linker resuelve simbolos, offsets, referencias entre secciones y valores diferidos durante la construccion final.
- **Memoria y headers declarativos**: permite modelar regiones ROM/RAM, padding, offsets fisicos, bloques de header y datos estaticos antes de emitir el binario.
- **Data definition**: soporta datos tipados como `u8`, `u16`, `u32`, arreglos y bloques binarios dentro del codigo fuente.
- **Fillables**: los plugins pueden exponer funciones `fill_*` para generar codigo o datos en build time, como headers, logos, imagenes, texto bitmap o audio.
- **Plugins Python**: los packs pueden importar plugins de compilacion, precompilacion, fillables, CLI y helpers propios.
- **Carga segura de plugins**: `rif plugins load`, `rif plug` e `rif install --package` validan estructura, manifiestos y rutas antes de instalar plugins locales o externos.
- **CLI por plugin**: `rif -pcli <plugin> ...` permite que cada plugin agregue comandos propios sin inflar el nucleo.
- **Gestion de plugins**: lista, inspecciona, documenta, abre propositos y elimina plugins con `rif plugins`.
- **Cache por plugin/proyecto**: plugins como imagenes, audio y fuentes pueden cachear resultados para evitar reprocesar assets pesados.
- **Comandos de limpieza**: `rif clear cache` y `rif clear table hashing` limpian cache y bitacoras auxiliares.
- **Editor de tablas desde CLI**: `rif table modify`, `format`, `undo`, `redo` y `hashing-table` modifican `.pack` de forma controlada, con previews e historial.
- **Documentacion local**: `rif help` abre el portal HTML local y mezcla automaticamente paginas del nucleo y de plugins instalados.
- **VS Code / VSIX generado**: `rif compile --vscode` construye una extension VS Code con sintaxis TextMate, snippets, completions, hovers, diagnosticos, quick fixes, simbolos y docs embebidas.
- **Extension de lenguaje configurable**: el constructor VSIX puede forzar la extension de archivo desde CLI con `--ext`, por ejemplo `.gbasm`.
- **Icono de VSIX configurable**: el constructor VSIX acepta `-icon` o `--icon` y empaqueta el icono dentro de la extension.
- **Compilador dedicado**: `rif compile -p <plugin>` genera un launcher dedicado para un plugin/pack, y puede crear un ejecutable con PyInstaller cuando esta disponible.
- **Instalacion de VSIX**: `rif install --vscode <archivo.vsix>` instala la extension generada usando el comando `code`.
- **Empaquetado del proyecto RIF**: `rif zip` comprime el paquete RIF ignorando `__pycache__`.
- **Packs incluidos**: hay soporte base para GBA, Atari 2600, AMD64 y utilidades generales.
- **Plugins oficiales incluidos**: `basics`, `gba`, `atari2600`, `image`, `sound`, `fonts`, `color` y `amd64`.

## Plugins incluidos

### basics

Incluye operaciones base para expresiones y reglas de emision: `emit`, `call`, `need`, comparaciones, `fits`, `bitfit`, `bitcat`, `bitsize`, `trunc`, `zext`, `sext`, `align`, `pad`, `reloc`, `reldis`, `fillid`, `vfillid`, errores controlados y helpers para VSIX.

### gba

Incluye pack de Game Boy Advance, instrucciones Thumb y ARM, registros ARM7TDMI, helpers de header ROM, logo Nintendo, checksum, entradas ARM/Thumb, padding de ROM, frame/screen helpers, paginas de documentacion, tooling VS Code y CLI para ejecutar ROMs con emuladores.

### atari2600

Incluye pack y ejemplos para Atari 2600, macros/vectores, padding especializado y CLI para ejecutar ROMs con Stella u otro emulador configurado.

### image

Convierte imagenes a bytes utiles para ROMs y demos, con cache de resultados y soporte de assets desde fillables.

### sound

Convierte audio a formatos simples de bytes PCM para consolas o demos retro. Incluye CLI de conversion y fillables para inyectar datos de sonido.

### fonts

Maneja fuentes bitmap `.f`, genera texto bitmap 5x7x1, expone fillables para texto como datos binarios y trae CLI para listar, editar, abrir, modificar, agregar y borrar glifos.

### amd64

Incluye soporte experimental de pack/compiler para instrucciones AMD64 dentro del modelo retargetable.

## Uso rapido

Instala el proyecto en modo editable:

```bash
python -m pip install -e .
```

Compila el ejemplo de GBA:

```bash
python -m rif build examples/gba --plugin gba --name example
```

Ejecuta una ROM de GBA con el CLI del plugin:

```bash
python -m rif -pcli gba run examples/gba/gba.gba -nd
```

Abre la documentacion local:

```bash
python -m rif help --open
```

## Construir una extension VS Code

El constructor VSIX puede unir varios bundles `vscode/` de plugins y forzar la extension del lenguaje:

```bash
python -m rif compile --vscode --ext .gbasm -icon example/ico.png --p gba sound fonts basics
```

Tambien funciona la forma antigua, pasando los plugins justo despues de `--vscode`:

```bash
python -m rif compile --vscode gba sound fonts basics --ext .gbasm --icon example/ico.png
```

El icono debe existir y ser `.png`, `.jpg`, `.jpeg`, `.gif`, `.webp` o `.svg`. El VSIX se escribe por defecto en `build/vscode/`, salvo que uses `-o`.

Para instalarlo:

```bash
python -m rif install --vscode build/vscode/rif-gba-sound-fonts-basics-0.2.0.vsix
```

## Estructura importante

- `rif/cli.py`: entrada principal de comandos.
- `rif/parser.py`, `rif/lexer.py`, `rif/compiler.py`, `rif/linker.py`, `rif/packer.py`: nucleo de lectura, parseo, compilacion y enlace.
- `rif/plugins/`: plugins oficiales.
- `rif/plugins/*/vscode/`: metadata para generar VSIX.
- `rif/help/`: documentacion local HTML/Markdown.
- `examples/`: proyectos de ejemplo.

## Documentacion

La documentacion completa vive en [`rif/help/README.md`](./rif/help/README.md) y puede abrirse como portal local con:

```bash
python -m rif help --open
```
