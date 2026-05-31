# Usar el Pack de un Plugin Específico

En muchos escenarios, es redundante re-crear un archivo `.pack` para un ensamblador que ya existe. Por ello, si compilas un proyecto que **carece** de archivo `.pack`, RIF puede usar la configuración de un plugin por defecto.

## Parámetro por Línea de Comandos
Si tu directorio de proyecto no tiene `.pack`, puedes forzar la herencia de un entorno completo a través de los argumentos del CLI:

```bash
python -m rif.cli build mi_proyecto --pack gba
```

En este caso, RIF irá al directorio de instalación de plugins (por ejemplo, `plugins/gba/pack/gba.pack`), cargará toda la estructura del sistema (incluidas sus macros, definiciones e importaciones) y se comportará como si el archivo `.pack` residiera en tu propia carpeta `mi_proyecto/`.

Esta funcionalidad es ideal para programar rápidamente sin tener que configurar el pipeline desde cero cada vez.
