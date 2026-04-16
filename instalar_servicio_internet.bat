@echo off
title Instalador Product-Sync API - Acceso por Internet
cd /d "%~dp0"

echo.
echo ============================================================
echo   INSTALADOR - Product-Sync API con Acceso por INTERNET
echo   Permite acceso desde CUALQUIER PC del mundo
echo ============================================================
echo.

:: Verificar permisos de administrador
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Este script debe ejecutarse como ADMINISTRADOR
    echo         Clic derecho - Ejecutar como administrador
    pause
    exit /b 1
)
echo [OK] Ejecutando con permisos de administrador

:: Buscar Python
set PYTHON=
echo [..] Buscando Python instalado...
for /f "usebackq delims=" %%P in (`powershell -NoProfile -Command ^
    "$paths = @(); " ^
    "'HKLM','HKCU' | ForEach-Object { " ^
    "  $base = $_+':SOFTWARE\Python\PythonCore'; " ^
    "  if (Test-Path $base) { " ^
    "    Get-ChildItem $base | ForEach-Object { " ^
    "      $ip = $_.PSPath+'\InstallPath'; " ^
    "      if (Test-Path $ip) { " ^
    "        $v = (Get-ItemProperty $ip -ErrorAction SilentlyContinue).'(default)'; " ^
    "        if ($v -and (Test-Path ($v+'python.exe'))) { $paths += $v+'python.exe' } " ^
    "        $ep = (Get-ItemProperty $ip -ErrorAction SilentlyContinue).ExecutablePath; " ^
    "        if ($ep -and (Test-Path $ep)) { $paths += $ep } " ^
    "      } " ^
    "    } " ^
    "  } " ^
    "}; " ^
    "$paths | Select-Object -First 1"`) do (
    if exist "%%P" ( set PYTHON=%%P & goto :python_found )
)

for %%V in (314 313 312 311 310 39 38) do (
    if exist "%LOCALAPPDATA%\Programs\Python\Python%%V\python.exe" (
        set "PYTHON=%LOCALAPPDATA%\Programs\Python\Python%%V\python.exe" & goto :python_found
    )
    if exist "C:\Python%%V\python.exe" (
        set "PYTHON=C:\Python%%V\python.exe" & goto :python_found
    )
)

echo [ERROR] Python no encontrado
echo         Descarga desde: https://python.org
pause
exit /b 1

:python_found
echo [OK] Python encontrado: %PYTHON%

:: Crear entorno virtual
echo.
echo [..] Configurando entorno virtual...
if not exist "venv" (
    %PYTHON% -m venv venv
    if %errorlevel% neq 0 (
        echo [ERROR] No se pudo crear el entorno virtual
        pause
        exit /b 1
    )
)
echo [OK] Entorno virtual listo

:: Instalar dependencias
echo [..] Instalando dependencias...
venv\Scripts\pip.exe install -r requirements.txt --quiet --disable-pip-version-check
if %errorlevel% neq 0 (
    echo [ERROR] Fallo al instalar dependencias
    pause
    exit /b 1
)
echo [OK] Dependencias instaladas

:: Configurar NSSM
set NSSM_DIR=%~dp0tools\nssm
set NSSM=%NSSM_DIR%\nssm.exe

if exist "%NSSM%" goto :nssm_found

echo.
echo [..] Descargando NSSM...
mkdir "%NSSM_DIR%" >nul 2>&1
powershell -Command "try { Invoke-WebRequest -Uri 'https://nssm.cc/release/nssm-2.24.zip' -OutFile '%NSSM_DIR%\nssm.zip' -UseBasicParsing } catch { exit 1 }"
if %errorlevel% neq 0 (
    echo [ERROR] No se pudo descargar NSSM
    pause
    exit /b 1
)
powershell -Command "Expand-Archive -Path '%NSSM_DIR%\nssm.zip' -DestinationPath '%NSSM_DIR%\extracted' -Force"
copy /y "%NSSM_DIR%\extracted\nssm-2.24\win64\nssm.exe" "%NSSM%" >nul
del "%NSSM_DIR%\nssm.zip" >nul 2>&1
echo [OK] NSSM descargado

:nssm_found
echo [OK] NSSM listo

:: Descargar ngrok
echo.
echo [..] Descargando ngrok para acceso por internet...
if not exist "ngrok.exe" (
    powershell -Command "try { Invoke-WebRequest -Uri 'https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip' -OutFile 'ngrok.zip' -UseBasicParsing } catch { exit 1 }"
    if %errorlevel% neq 0 (
        echo [ERROR] No se pudo descargar ngrok
        echo         Descarga manual desde: https://ngrok.com/download
        pause
        exit /b 1
    )
    powershell -Command "Expand-Archive -Path 'ngrok.zip' -DestinationPath '.' -Force"
    del ngrok.zip >nul 2>&1
)
echo [OK] ngrok listo

:: Configurar ngrok authtoken
echo.
echo ============================================================
echo   CONFIGURACION DE NGROK
echo   Necesitas un authtoken gratuito de ngrok
echo ============================================================
echo.
echo   1. Abre: https://dashboard.ngrok.com/signup
echo   2. Registrate (es gratis)
echo   3. Copia tu authtoken desde: https://dashboard.ngrok.com/get-started/your-authtoken
echo.
set /p NGROK_TOKEN="   Pega tu ngrok authtoken aqui: "
ngrok.exe config add-authtoken %NGROK_TOKEN%
if %errorlevel% neq 0 (
    echo [ADVERTENCIA] No se pudo configurar ngrok authtoken
    echo              Puedes configurarlo despues con: ngrok config add-authtoken TU_TOKEN
)

:: Instalar servicio API
set SERVICE_NAME=ProductSyncAPI
set APP_DIR=%~dp0
if "%APP_DIR:~-1%"=="\" set APP_DIR=%APP_DIR:~0,-1%
set PYTHON_EXE=%APP_DIR%\venv\Scripts\python.exe
set APP_SCRIPT=%APP_DIR%\app.py

echo.
echo [..] Instalando servicio de API...
"%NSSM%" stop %SERVICE_NAME% >nul 2>&1
"%NSSM%" remove %SERVICE_NAME% confirm >nul 2>&1
"%NSSM%" install %SERVICE_NAME% "%PYTHON_EXE%" "\"%APP_SCRIPT%\""
"%NSSM%" set %SERVICE_NAME% DisplayName "Product-Sync API - Inventario DBF"
"%NSSM%" set %SERVICE_NAME% Description "API REST para exponer inventario desde archivos DBF"
"%NSSM%" set %SERVICE_NAME% AppDirectory "%APP_DIR%"
"%NSSM%" set %SERVICE_NAME% Start SERVICE_AUTO_START
"%NSSM%" set %SERVICE_NAME% AppRestartDelay 10000
"%NSSM%" set %SERVICE_NAME% AppStdout "%APP_DIR%\logs\service_out.log"
"%NSSM%" set %SERVICE_NAME% AppStderr "%APP_DIR%\logs\service_err.log"
"%NSSM%" set %SERVICE_NAME% AppRotateFiles 1
"%NSSM%" set %SERVICE_NAME% AppRotateBytes 5242880
echo [OK] Servicio API registrado

:: Instalar servicio ngrok
set NGROK_SERVICE=ProductSyncNgrok
set NGROK_EXE=%APP_DIR%\ngrok.exe

echo [..] Instalando servicio de ngrok...
"%NSSM%" stop %NGROK_SERVICE% >nul 2>&1
"%NSSM%" remove %NGROK_SERVICE% confirm >nul 2>&1
"%NSSM%" install %NGROK_SERVICE% "%NGROK_EXE%" "http 5000"
"%NSSM%" set %NGROK_SERVICE% DisplayName "Product-Sync Ngrok Tunnel"
"%NSSM%" set %NGROK_SERVICE% Description "Tunel ngrok para acceso por internet"
"%NSSM%" set %NGROK_SERVICE% AppDirectory "%APP_DIR%"
"%NSSM%" set %NGROK_SERVICE% Start SERVICE_AUTO_START
"%NSSM%" set %NGROK_SERVICE% AppStdout "%APP_DIR%\logs\ngrok_out.log"
"%NSSM%" set %NGROK_SERVICE% AppStderr "%APP_DIR%\logs\ngrok_err.log"
"%NSSM%" set %NGROK_SERVICE% DependOnService %SERVICE_NAME%
echo [OK] Servicio ngrok registrado

:: Configurar firewall
echo.
echo [..] Configurando firewall...
netsh advfirewall firewall delete rule name="ProductSyncAPI" >nul 2>&1
netsh advfirewall firewall add rule name="ProductSyncAPI" dir=in action=allow protocol=TCP localport=5000 >nul
netsh advfirewall firewall add rule name="ProductSyncNgrok" dir=in action=allow protocol=TCP localport=4040 >nul
echo [OK] Firewall configurado

:: Iniciar servicios
echo.
echo [..] Iniciando servicios...
"%NSSM%" start %SERVICE_NAME%
timeout /t 3 /nobreak >nul
"%NSSM%" start %NGROK_SERVICE%
timeout /t 5 /nobreak >nul

:: Obtener URL de ngrok
echo.
echo [..] Obteniendo URL publica de ngrok...
timeout /t 3 /nobreak >nul
powershell -Command "$url = try { (Invoke-WebRequest -Uri 'http://localhost:4040/api/tunnels' -UseBasicParsing | ConvertFrom-Json).tunnels[0].public_url } catch { 'No disponible aun' }; Write-Host $url" > ngrok_url.txt
set /p NGROK_URL=<ngrok_url.txt

:: Mostrar informacion final
echo.
echo.
echo ============================================================
echo   INSTALACION COMPLETADA - ACCESO POR INTERNET
echo ============================================================
echo.
echo   Estado de servicios:
"%NSSM%" status %SERVICE_NAME%
"%NSSM%" status %NGROK_SERVICE%
echo.
echo   URL PUBLICA (acceso desde cualquier PC del mundo):
echo   %NGROK_URL%
echo.
echo   Endpoints disponibles:
echo     %NGROK_URL%/
echo     %NGROK_URL%/health
echo     %NGROK_URL%/api/inventario
echo.
echo   API Key (incluir en header X-API-Key):
type .env | findstr "API_KEY=" | findstr /v "^#"
echo.
echo   Dashboard de ngrok (ver URL actualizada):
echo     http://localhost:4040
echo.
echo   IP local de este servidor:
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /C:"IPv4"') do echo     http:%%a:5000
echo.
echo   Logs:
echo     API:   %APP_DIR%\logs\service_out.log
echo     ngrok: %APP_DIR%\logs\ngrok_out.log
echo.
echo   IMPORTANTE:
echo   - La URL publica puede cambiar si reinicias el servicio ngrok
echo   - Consulta siempre http://localhost:4040 para ver la URL actual
echo   - Considera el plan de pago de ngrok para URL fija
echo.
echo   Gestionar servicios:
echo     sc query %SERVICE_NAME%
echo     sc query %NGROK_SERVICE%
echo     sc stop %SERVICE_NAME%
echo     sc start %SERVICE_NAME%
echo.
echo ============================================================
echo.
pause
