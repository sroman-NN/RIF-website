# Version actual

### RIF 0.0.4 Stable

Esta versión consolida el core retargetable, dejando el flujo de trabajo de editor y la inyección de arquitecturas listos para producción y proyectos reales.

## Soportado

- Parser y AST para archivos `.pack`.
- Compiler runtime con reglas, operandos, placeholders y etiquetas.
- Linker con secciones, headers, memoria, padding y relocaciones.
- Lector de fuente configurable desde `.pack`.
- Build de proyectos por carpeta.
- Fillables `@...` provistos por plugins.
- CLI por plugin con `rif -pcli`.
- Sistema de plugins locales e instalables.
- Plugin `fonts` con bitmap 5x7x1.
- Ecosistema completo para **Game Boy Advance (GBA)** y **Sega Mega Drive / Genesis**.
- Soporte funcional para **Atari 2600** e inyecciones iniciales para **AMD64**.
- Constructor VS Code/VSIX integral con diagnóstico léxico y gramatical desde `.pack`.
- Help interactivo para plugins y core compilable on-the-fly.

## Estado de estabilidad

`Stable` significa que el core de packs, el linker, las extensiones VSIX y la generación de ROMs/binarios de 16-bits (M68k y ARM/Thumb) ya son seguros para su uso. La API de plugins está madura. 

## Aun falta (Roadmap)

- MIR (Medium IR) estable para optimizadores.
- Optimizadores enlazados de selección y reducción de instrucciones.
- Soporte para nuevas plataformas clásicas de 16-bits (e.g., SNES / 65816).
- Empaquetado nativo final del compilador en binarios standalone con PyInstaller.
- Más formatos de salida conectados por plugins (e.g., ELF, PE).
