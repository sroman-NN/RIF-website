@echo off
REM Compilar usando RIF desde la ruta del proyecto padre
cd /D "%~dp0\..\.."
python -m rif build "examples\gba" -o "examples\gba\build\game.gba" --plugin gba --name example
if %errorlevel% neq 0 exit /b %errorlevel%

echo Compilado exitosamente. 
echo Puedes abrir examples\gba\build\game.gba en tu emulador (ej. mGBA).
