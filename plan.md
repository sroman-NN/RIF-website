# Plan de mejoras y errores encontrados — RIF Foundry v0.0 Beta

## Objetivo

Convertir la beta técnica actual en una primera versión funcional más segura, instalable y confiable, corrigiendo primero los errores que pueden romper plugins, codegen, labels, relocations, headers y layout final.

---

## 1. Plugin declarado pero no encontrado se ignora silenciosamente

### Error

Cuando un `.pack` declara:

```rif
plugin "basics"
```

si el plugin no existe en la ruta esperada, el sistema no falla de inmediato. Continúa sin cargar reglas y después produce errores confusos, por ejemplo:

```text
tokens sobrantes después de matchear byte: 0xf
```

Esto oculta la causa real del problema.

### Solución

Hacer que todo plugin declarado sea obligatorio.

Si no existe, lanzar un error fatal claro:

```text
Plugin declarado no encontrado: basics
Rutas buscadas:
- plugins/basics
- rif/plugins/basics
- ...
```

### Acción concreta

- Modificar `load_plugins()` para validar plugins declarados.
- No permitir que el compilador continúe si falta un plugin explícito.
- Añadir test negativo con un plugin inexistente.

### Prioridad

Alta.

---

## 2. Plugins fuera del paquete instalable

### Error

Los plugins actuales viven en:

```text
plugins/basics/plugins/*.py
```

Pero el paquete Python solo incluye:

```toml
include = ["rif*"]
```

Eso significa que al instalar el proyecto con `pip`, los plugins `basics` pueden no incluirse. En local funciona porque estás parado en la raíz del repo, pero instalado como librería puede fallar.

### Solución

Mover los plugins oficiales dentro del paquete principal o empaquetarlos explícitamente.

Opción recomendada:

```text
rif/plugins/basics/plugins/*.py
```

Luego `plugin "basics"` debería buscar primero dentro del paquete `rif`.

### Acción concreta

- Mover `plugins/basics` a `rif/plugins/basics`.
- Actualizar el loader de plugins.
- Actualizar `pyproject.toml` para incluir esos archivos.
- Probar instalación limpia en un virtualenv.

### Prioridad

Alta.

---

## 3. `need` dentro de `switch`, `case`, `ON` u `OFF` rompe el matching

### Error

El sistema actual recolecta todos los `need` de una regla aunque estén dentro de ramas condicionales.

Ejemplo problemático:

```rif
foo:
    need VALUE, x
    switch x.size:
        case 4:
            emit 00000001
        case 8:
            need VALUE, y
            emit 00000010
```

Aunque se use `foo 0xf`, el compilador también exige `y`, porque lo encontró dentro de otra rama.

Eso produce errores falsos como:

```text
faltan operandos para la regla
```

### Solución

Separar claramente:

```text
firma de regla
```

de:

```text
codegen condicional
```

Los `need` de firma sirven para decidir si la regla matchea.
Los `need` internos deben evaluarse solo si la rama realmente se ejecuta.

### Acción concreta

- Cambiar `collect_codegen()` para que no mezcle firma y cuerpo.
- Crear una fase explícita de `signature`.
- Prohibir temporalmente `need` condicional si todavía no se implementa bien.
- Añadir tests para `need` dentro de `switch`, `case`, `ON` y `OFF`.

### Prioridad

Alta.

---

## 4. Código y datos intercalados rompen offsets

### Error

El compilador calcula offsets como si todo estuviera en una sola secuencia lineal, pero el linker separa después bloques como:

```text
text
data
rodata
bss
```

Ejemplo conceptual:

```rif
target:
byte 0x01
msg char[1] = A
rel8
```

El compilador cuenta el byte de `msg` como si estuviera dentro del flujo de código, pero el linker luego lo mueve a `.data`.

Resultado: labels, distancias relativas y relocations pueden quedar mal.

### Solución

Hacer el compilador consciente de secciones.

Cada label debe guardar:

```text
section
offset dentro de esa section
```

No solo un offset global.

### Acción concreta

- Cambiar labels de `offset` a `{ section, offset }`.
- Cambiar relocations para que guarden la sección real donde viven.
- Cambiar el cálculo de `reldis` para usar offsets finales correctos.
- Añadir tests con código y data intercalados.

### Prioridad

Alta.

---

## 5. Relocations con offset incorrecto cuando hay data intercalada

### Error

Si hay data intercalada antes de una relocation, el offset de la relocation puede calcularse con base en la posición lineal del source, no en la posición real dentro del bloque final.

Ejemplo conceptual:

```rif
byte 0x01
msg char[1] = A
relocabs
```

La relocation puede registrar un offset como si `msg` siguiera dentro de `text`, aunque el linker lo separa a `data`.

### Solución

Las relocations deben tener ubicación por sección:

```text
relocation.section = text
relocation.offset_bits = offset real dentro de text
```

### Acción concreta

- Rehacer emisión de relocations para que use el builder de sección actual.
- No calcular relocations desde una posición global mezclada.
- Añadir tests para relocations antes/después de data.

### Prioridad

Alta.

---

## 6. Headers PE definidos en `.world` no se materializan

### Error

En `store.amd64.pack` hay headers tipo PE dentro de `.world`, por ejemplo:

```rif
.world

| NAME             | SIZE | HEX         | FILL     |
| IMAGE_DOS_HEADER | 64   |             | 00000000 |
| PE_SIGNATURE     | 4    | 50 45 00 00 |          |
```

Pero el parser actual solo crea headers reales desde `.headers`, no desde `.world`.

Resultado: esos headers no aparecen realmente en el output final.

### Solución

Definir una sola ruta oficial para headers.

Opción recomendada:

```rif
.headers
| NAME             | SIZE | HEX         | FILL     |
| IMAGE_DOS_HEADER | 64   |             | 00000000 |
| PE_SIGNATURE     | 4    | 50 45 00 00 |          |
```

`.world` debería quedar para metadata global, arquitectura, endianess y configuración.

### Acción concreta

- Mover headers reales a `.headers`.
- O extender el parser para interpretar tablas de headers dentro de `.world`.
- Añadir test donde el binario final contenga `MZ` y `PE\0\0` en offsets correctos.

### Prioridad

Media-Alta.

---

## 7. `precompile "amd64"` no se usa aunque existe un precompiler AMD64

### Error

Existe un archivo:

```text
plugins/amd64/compiler.py
```

con lógica de preparación tipo `_start()`, pero el pack usa:

```rif
plugin "amd64"
```

en vez de:

```rif
precompile "amd64"
```

Si esa lógica debe preparar headers o estado inicial, actualmente no se ejecuta como precompiler.

### Solución

Separar claramente plugins normales y precompilers.

- `plugin`: añade reglas/instrucciones.
- `precompile`: transforma/prepara el programa antes de compilar.

### Acción concreta

- Cambiar el pack si realmente necesita precompilación.
- Documentar cuándo usar `plugin` y cuándo usar `precompile`.
- Añadir test verificando que el precompiler se ejecuta.

### Prioridad

Media-Alta.

---

## 8. `emitadress` / `emitaddress` no reserva bytes reales

### Error

La instrucción conceptual de emitir una dirección genera un placeholder, pero no reserva bytes del ancho necesario.

Ejemplo:

```rif
copy rax, foo
```

puede producir opcodes iniciales, pero la dirección `foo` queda como marcador simbólico sin materialización binaria completa.

Además, el nombre parece tener typo:

```text
emitadress
```

cuando debería ser:

```text
emitaddress
```

### Solución

Toda emisión de dirección debe declarar ancho:

```rif
emitaddress foo, 64
```

O mejor:

```rif
reloc abs, foo, 64
```

Eso debe reservar bytes cero y crear una relocation válida.

### Acción concreta

- Normalizar nombre a `emitaddress`.
- Mantener alias temporal `emitadress` con warning, si ya hay packs que lo usan.
- Exigir ancho explícito.
- Reservar bytes reales en el stream.
- Crear relocation asociada.

### Prioridad

Alta.

---

## 9. Falta una política clara para secciones

### Error

El lenguaje permite mezclar instrucciones, labels y data, pero no está totalmente definido si esto es legal:

```rif
byte 0x01
msg char[5] = Hello
byte 0x02
```

Si se permite, el compilador debe preservar layout semántico correctamente.
Si no se permite, debe fallar con error claro.

### Solución

Definir una de estas dos políticas:

#### Opción A: permitir intercalado

El compilador debe ser completamente section-aware.

#### Opción B: prohibir intercalado temporalmente

Mientras el linker madura, exigir secciones explícitas:

```rif
.text
byte 0x01
byte 0x02

.data
msg char[5] = Hello
```

### Acción concreta

Para beta, recomiendo la opción B como protección temporal.
Después implementar opción A correctamente.

### Prioridad

Alta.

---

## 10. Tests insuficientes para una beta pública

### Error

Los tests actuales validan casos felices, pero faltan pruebas para errores reales de lanzamiento.

No se cubren suficientemente:

- instalación limpia;
- plugin faltante;
- plugin mal formado;
- `need` condicional;
- data intercalada;
- relocations complejas;
- headers reales;
- paths fuera del repo;
- errores de CLI;
- repetición de builds con el mismo programa;
- casos negativos del parser.

### Solución

Subir la cobertura de tests antes de publicar.

### Acción concreta

Crear pruebas para:

```text
tests/test_plugins.py
tests/test_packaging.py
tests/test_conditional_need.py
tests/test_sections_layout.py
tests/test_relocations.py
tests/test_headers.py
tests/test_cli_errors.py
tests/test_negative_parser.py
```

### Prioridad

Alta.

---

## 11. Mensajes de error poco directos

### Error

Cuando algo falla en plugins o matching, el error puede apuntar al síntoma y no a la causa.

Ejemplo:

```text
tokens sobrantes después de matchear byte: 0xf
```

cuando la causa real puede ser:

```text
no se cargó el plugin basics
```

### Solución

Mejorar el pipeline de errores para conservar causa raíz.

### Acción concreta

- Error específico para plugin inexistente.
- Error específico para regla no encontrada.
- Error específico para operandos sobrantes.
- Mostrar regla candidata cuando falle el matching.
- Mostrar archivo, línea y columna cuando sea posible.

### Prioridad

Media-Alta.

---

## 12. `__pycache__` dentro del zip

### Error

El zip incluye archivos compilados:

```text
__pycache__/*.pyc
```

Esto ensucia la distribución y puede confundir el análisis o release.

### Solución

Excluir cachés y archivos temporales.

### Acción concreta

Añadir a `.gitignore` / script de release:

```gitignore
__pycache__/
*.pyc
.pytest_cache/
.mypy_cache/
.ruff_cache/
```

Y crear un comando de limpieza:

```bash
find . -type d -name __pycache__ -prune -exec rm -rf {} +
find . -type f -name '*.pyc' -delete
```

### Prioridad

Baja-Media.

---

## 13. Versión inconsistente

### Error

El proyecto declara una versión en `pyproject.toml`, pero el README o documentación puede mencionar otra beta.

Ejemplo:

```text
pyproject: 0.1.0
README: 0.0 Beta
```

### Solución

Definir una única versión oficial.

Recomendado:

```text
0.0.0-beta.1
```

O:

```text
0.1.0-alpha.1
```

### Acción concreta

- Sincronizar `pyproject.toml`.
- Sincronizar README.
- Añadir `rif.__version__`.
- Hacer que CLI imprima `rif --version`.

### Prioridad

Media.

---

## 14. Seguridad de plugins no documentada

### Error

Los plugins son Python real. Eso significa que un plugin puede ejecutar código arbitrario en la máquina.

Esto está bien para un sistema local/dev, pero no debe parecer sandbox.

### Solución

Documentarlo explícitamente.

### Acción concreta

Añadir advertencia al README:

```text
Los plugins de RIF ejecutan Python real.
No ejecutes packs o plugins no confiables.
RIF no es un sandbox de seguridad.
```

### Prioridad

Media.

---

## 15. `store.amd64.pack` mezcla demo, backend real y headers Windows

### Error

El archivo `store.amd64.pack` mezcla conceptos:

- configuración global;
- headers tipo Windows PE;
- reglas AMD64;
- lógica de copy/store;
- placeholders;
- conceptos todavía incompletos.

Esto hace difícil saber qué parte es lenguaje estable y qué parte es experimento.

### Solución

Separar por responsabilidad.

Propuesta:

```text
packs/amd64/core.pack
packs/amd64/regs.pack
packs/amd64/mov.pack
packs/amd64/pe64.headers.pack
packs/examples/store.amd64.pack
```

### Acción concreta

- Convertir `store.amd64.pack` en ejemplo.
- Sacar headers PE a un pack específico.
- Sacar registros a un pack específico.
- Sacar reglas mov/copy/store a packs separados.

### Prioridad

Media.

---

# Plan de ejecución recomendado

## Fase 1 — Blindaje de beta

Objetivo: que falle bien, cargue bien y sea instalable.

Tareas:

1. Error fatal para plugin declarado y no encontrado.
2. Mover `basics` dentro del paquete instalable.
3. Test de instalación limpia.
4. Limpiar `__pycache__`.
5. Sincronizar versión.
6. Documentar seguridad de plugins.

Resultado esperado:

```text
RIF puede instalarse y ejecutar examples/minimal.pack desde cualquier carpeta.
```

---

## Fase 2 — Corrección del codegen condicional

Objetivo: que las reglas no pidan operandos de ramas que no se ejecutan.

Tareas:

1. Separar firma de regla y cuerpo codegen.
2. Corregir `collect_codegen()`.
3. Tests para `switch`, `case`, `ON`, `OFF`.
4. Decidir si `need` condicional queda permitido o prohibido temporalmente.

Resultado esperado:

```text
El matching de reglas solo depende de operandos realmente declarados como firma.
```

---

## Fase 3 — Layout y secciones confiables

Objetivo: que labels, offsets, reldis y relocations sean correctos.

Tareas:

1. Labels con `{ section, offset }`.
2. Relocations con sección real.
3. Builder separado por sección.
4. `reldis` usando layout final correcto.
5. Política temporal para data intercalada.
6. Tests de código + data mezclados.

Resultado esperado:

```text
El binario final conserva offsets correctos aunque el linker separe text/data/bss.
```

---

## Fase 4 — Headers y linking más real

Objetivo: que headers declarados se materialicen correctamente.

Tareas:

1. Definir `.headers` como formato oficial.
2. Corregir `store.amd64.pack`.
3. Probar headers PE mínimos.
4. Revisar `precompile "amd64"`.
5. Tests de binario con headers.

Resultado esperado:

```text
Los headers aparecen realmente en el output final, no solo como tabla decorativa.
```

---

## Fase 5 — Direcciones y relocations completas

Objetivo: que referencias simbólicas puedan producir binario final o relocation formal.

Tareas:

1. Reemplazar `emitadress` por `emitaddress`.
2. Exigir ancho explícito.
3. Reservar bytes reales.
4. Crear relocation asociada.
5. Tests con símbolos internos y externos.

Resultado esperado:

```text
copy rax, foo puede producir bytes completos o una relocation válida.
```

---

# Criterio para lanzar primera versión funcional

No lanzar como primera versión funcional hasta cumplir esto:

```text
[ ] Instalación limpia funciona fuera del repo.
[ ] plugin "basics" carga desde paquete instalado.
[ ] plugin faltante falla con error claro.
[ ] need condicional no rompe matching.
[ ] labels tienen sección y offset correcto.
[ ] relocations tienen offset correcto.
[ ] data intercalada está soportada o prohibida explícitamente.
[ ] headers declarados se emiten realmente.
[ ] emitaddress reserva bytes o crea relocation válida.
[ ] README advierte que plugins ejecutan Python real.
[ ] tests cubren casos positivos y negativos críticos.
```

# Veredicto

La base del proyecto ya funciona como beta técnica del core, pero todavía no debe presentarse como ensamblador/linker estable.

El punto más fuerte es que el compilador ya demuestra el modelo retargetable: lee `.pack`, carga plugins, genera IR y emite bytes sin conocer directamente la ISA.

El punto más peligroso es que todavía hay errores de cimentación en:

```text
plugins instalables
firma vs codegen condicional
layout por secciones
relocations
headers reales
```

Corrigiendo esas áreas, la siguiente versión sí puede acercarse a una primera beta pública seria.
