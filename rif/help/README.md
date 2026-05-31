# Documentacion de RIF

Bienvenido al navegador de documentacion de RIF. Aqui puedes explorar especificaciones, guias, herramientas y arquitecturas desde GitHub o desde el portal local con:

```bash
python -m rif help --open
```

## Inicio Rapido

- [Que es RIF?](resources/system/home/que_es_rif.md)
- [Como se usa?](resources/system/home/como_se_usa.md)
- [Version Actual](resources/system/home/version_actual.md)

## Archivos `.pack` y Entorno

- [Crear un Pack](resources/pack/crear_y_cargar/crear_un_pack.md)
- [Usar Pack Propio](resources/pack/crear_y_cargar/usar_pack_propio.md)
- [Usar Pack Plugin](resources/pack/crear_y_cargar/usar_pack_plugin.md)
- [Importar Plugins y Orden](resources/pack/archivo_pack/importar_plugins.md)

## Compilador Interno

- [Packer I: Configuracion Principal](resources/pack/archivo_pack/packer_1.md)
- [Packer II y Errores](resources/pack/archivo_pack/packer_2_y_errores.md)
- [Linker I: Archivos Fracturados](resources/pack/archivo_pack/linker_1.md)
- [Empaquetador Principal](resources/use/empaquetadores/packer.md)
- [Linker Estatico](resources/use/empaquetadores/linker.md)

## Especificaciones de Instrucciones

- [Construccion de Instrucciones](resources/use/instrucciones/instrucciones.md)
- [Sistema de Tipos y Logica](resources/use/instrucciones/tipos.md)
- [Flujos ON y Switch](resources/use/instrucciones/flujos_on_switch.md)
- [Tablas y Secciones](resources/use/instrucciones/tablas_y_secciones.md)

## Herramientas de Consola

- [Vision General CLI](resources/use/cli/cli.md)
- [Compilacion Rapida](resources/use/cli/compilar.md)
- [Edicion de Tablas en Terminal](resources/use/cli/comando_table.md)
- [VS Code y VSIX](resources/use/cli/vscode.md)

## Plugins Oficiales

- [Basics](../plugins/basics/pages/0_instrucciones.md)
- [VSIX](../plugins/basics/pages/1_vsix.md)

Para guias sobre otros plugins como GBA, Atari2600, Image, Fonts y Sound, consulta sus respectivos directorios dentro de `rif/plugins/`.

## Desarrollo de Plugins

- [Crear y usar plugins](resources/use/plugins/crear_y_usar.md)
- [Estructura Interna del Plugin](resources/use/plugins/estructura.md)
- [Mecanismos de Importacion](resources/use/plugins/importar.md)

## Roadmap y Futuro

- [Autocompiladores](resources/system/futuros/compiladores.md)
- [Mejoras del Linker](resources/system/futuros/mejoras_del_linker.md)
- [Soporte MIR (Medium IR)](resources/system/futuros/mir.md)
- [Optimizadores de Codigo](resources/system/futuros/optimizadores.md)
- [Soporte Core y Arquitecturas](resources/system/futuros/soporte.md)
