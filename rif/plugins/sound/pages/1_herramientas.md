# Herramientas de Línea de Comandos (CLI)

El plugin de sonido extiende el entorno de RIF añadiendo subcomandos accesibles mediante el argumento `-pcli sound`.

## 📦 Instalación del Motor FFmpeg

Para que el framework RIF pueda leer archivos como `.mp3`, resamplear el audio o cambiar la profundidad de bits sin depender de pesadas librerías de Python de terceros, se utiliza **FFmpeg** de fondo.

Si tu sistema no cuenta con FFmpeg preinstalado globalmente, puedes indicarle a RIF que lo descargue y lo aísle en su entorno local de herramientas:

```bash
# Descarga e instala FFmpeg localmente (Actualmente solo Windows)
python -m rif -pcli sound install ffmpeg
```

Una vez ejecutado este comando, RIF descargará una build estática de 64-bits sin depender de permisos de administrador ni alterar los registros por defecto, permitiendo que las macros `@sound_wav` comiencen a funcionar inmediatamente en tus archivos `.pack` o `.mdasm`.

---

## 🎛️ Conversión Manual de Audio (`convert`)

A veces no necesitas inyectar el audio en tiempo de compilación a través de tu código, sino que quieres preprocesar una docena de efectos de sonido en crudo `.pcm` para distribuirlos en tus repositorios de Assets. Puedes usar la herramienta `convert`.

```bash
python -m rif -pcli sound convert <input> <output> [opciones]
```

### Opciones Soportadas:

- `--rate`: Frecuencia de muestreo destino en Hz (Ej. `8192` o `16384`). Por defecto es 8192.
- `--duration`: Extrae solo `N` segundos del archivo de audio original.
- `--start`: Comienza la extracción desde el segundo `N`.
- `--volume`: Multiplicador lineal de volumen. Útil para evitar que samples muy saturados clippeen al bajarlos a 8-bits. (Por defecto es `0.85`).
- `--fade-in`: Aplica un fade progresivo en los primeros `N` segundos para evitar clicks duros en el arranque (Por defecto es `0.25`).

### Ejemplo de uso:

```bash
# Convertir un archivo pesado a un PCM de GameBoy a 10.5kHz
python -m rif -pcli sound convert musica.mp3 pista.pcm --rate 10512 --duration 10.5
```
