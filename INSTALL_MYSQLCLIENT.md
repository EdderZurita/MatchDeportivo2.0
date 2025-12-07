# Instalación de mysqlclient en Windows

## Problema

`mysqlclient` requiere compilación en Windows y puede fallar con el error:
```
× Failed to build mysqlclient
```

## Soluciones

### Opción 1: Instalar desde Wheel Precompilado (RECOMENDADO)

1. Descarga el wheel apropiado desde: https://www.lfd.uci.edu/~gohlke/pythonlibs/#mysqlclient

2. Busca el archivo que coincida con tu versión de Python y arquitectura:
   - `mysqlclient‑2.2.0‑cp311‑cp311‑win_amd64.whl` (Python 3.11, 64-bit)
   - `mysqlclient‑2.2.0‑cp310‑cp310‑win_amd64.whl` (Python 3.10, 64-bit)

3. Instala el wheel:
   ```bash
   pip install ruta/al/archivo/mysqlclient‑2.2.0‑cp311‑cp311‑win_amd64.whl
   ```

### Opción 2: Instalar Visual C++ Build Tools

1. Descarga e instala [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)

2. Durante la instalación, selecciona:
   - "Desktop development with C++"
   - "MSVC v142 - VS 2019 C++ x64/x86 build tools"
   - "Windows 10 SDK"

3. Reinicia tu computadora

4. Instala mysqlclient:
   ```bash
   pip install mysqlclient
   ```

### Opción 3: Usar PyMySQL (Alternativa)

Si las opciones anteriores no funcionan, puedes usar `PyMySQL` como alternativa:

1. Instala PyMySQL:
   ```bash
   pip install pymysql
   ```

2. Agrega al inicio de `MatchDeportivo/settings.py`:
   ```python
   import pymysql
   pymysql.install_as_MySQLdb()
   ```

## Verificar Instalación

```bash
python -c "import MySQLdb; print('mysqlclient instalado correctamente')"
```

## Verificar Versión de Python

```bash
python --version
```

Asegúrate de tener Python 3.8 o superior.
