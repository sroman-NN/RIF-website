# Importar Plugins y Orden

Bajo la cabecera `.pack`, puedes declarar librerías externas o plugins para extender las funcionalidades del compilador.

## Declaración
La palabra clave `plugin` indicará al compilador la necesidad de buscar la ruta del plugin y cargar sus reglas léxicas.

```rif
.pack
plugin "basics"
plugin "gba"
```

Los plugins son cargados en el orden exacto en el que son declarados. Si el código fuente hace uso de una sintaxis implementada en un plugin, RIF sabrá cómo resolverla de inmediato.

## Control de Colisiones (`pluginsymbolorder`)

Si trabajas con múltiples plugins, es posible que algunas palabras clave o mnemónicos choquen (por ejemplo, dos plugins definiendo `mov`). Para controlar cómo reacciona RIF ante estos escenarios, existe la directiva `pluginsymbolorder`.

```rif
.pack
plugin "basics"
plugin "gba"
pluginsymbolorder 0
```

Valores soportados:
- **`0` (Estricto)**: RIF detendrá la compilación lanzando un error si se encuentran nombres o funciones repetidas entre plugins. Tolerancia cero.
- **`2` (Sobrescritura *Bottom-Up*)**: (Por defecto) Permite hacer un "merge", priorizando el último plugin importado. Las declaraciones ubicadas más abajo reemplazarán a las de arriba en caso de existir choques.
- **`3` (Privilegio *Top-Down*)**: RIF ignorará los métodos repetidos de los plugins subsecuentes. El primer plugin que declare el método es el que se preservará.
