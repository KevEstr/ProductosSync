@echo off
title Diagnostico Pre-Instalacion - Product-Sync API
cd /d "%~dp0"

echo.
echo ============================================================
echo   DIAGNOSTICO PRE-INSTALACION
echo   Verifica que todo este listo antes de instalar
echo ============================================================
echo.

set ERRORES=0

:: 1. Verificar Python
echo [1/6] Verificando Python...
python --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=*" %%v in ('python --version 2^>^&1') do echo     [OK] %%v
) else (
    echo     [ERROR] Python no encontrado
    echo            Instala Python desde: https://python.org
    set /a ERRORES+=1
)
echo.

:: 2. Verificar archivo .env
echo [2/6] Verificando configuracion (.env)...
if exist ".env" (
    echo     [OK] Archivo .env existe
    for /f "tokens=2 delims==" %%a in ('type .env ^| findstr "^DBF_PATH="') do (
        set DBF_PATH=%%a
        echo     [OK] DBF_PATH configurado: %%a
    )
) else (
    echo     [ERROR] Archivo .env no encontrado
    set /a ERRORES+=1
)
echo.

:: 3. Verificar ruta DBF
echo [3/6] Verificando ruta de archivos DBF...
if defined DBF_PATH (
    if exist "%DBF_PATH%" (
        echo     [OK] Ruta DBF existe: %DBF_PATH%
        
        :: Verificar si es ruta local o de red
        echo %DBF_PATH% | findstr /C:"\\\\" >nul
        if %errorlevel% equ 0 (
            echo     [ADVERTENCIA] Es una ruta de RED (\\servidor\)
            echo                   LocalSystem puede no tener acceso
            echo                   Considera usar la version con credenciales
        ) else (
            echo     [OK] Es una ruta LOCAL (disco)
        )
    ) else (
        echo     [ERROR] Ruta DBF no existe: %DBF_PATH%
        echo            Verifica la configuracion en .env
        set /a ERRORES+=1
    )
) else (
    echo     [ADVERTENCIA] DBF_PATH no configurado en .env
)
echo.

:: 4. Verificar archivos DBF
echo [4/6] Verificando archivos DBF...
if defined DBF_PATH (
    if exist "%DBF_PATH%" (
        dir /b "%DBF_PATH%\*.DBF" >nul 2>&1
        if %errorlevel% equ 0 (
            echo     [OK] Archivos DBF encontrados:
            for /f "tokens=*" %%f in ('dir /b "%DBF_PATH%\*.DBF" 2^>nul ^| findstr /i "Producto MovMes"') do (
                echo          - %%f
            )
        ) else (
            echo     [ADVERTENCIA] No se encontraron archivos .DBF
            echo                   Verifica que la ruta sea correcta
        )
    )
)
echo.

:: 5. Verificar puerto disponible
echo [5/6] Verificando puerto 5000...
netstat -an | findstr ":5000" >nul 2>&1
if %errorlevel% equ 0 (
    echo     [ADVERTENCIA] Puerto 5000 ya esta en uso
    echo                   Puedes cambiar el puerto en .env
) else (
    echo     [OK] Puerto 5000 disponible
)
echo.

:: 6. Verificar permisos de administrador
echo [6/6] Verificando permisos...
net session >nul 2>&1
if %errorlevel% equ 0 (
    echo     [OK] Tienes permisos de administrador
) else (
    echo     [INFO] No estas ejecutando como administrador
    echo           (No es necesario para el diagnostico)
)
echo.

:: Resumen
echo ============================================================
echo   RESUMEN DEL DIAGNOSTICO
echo ============================================================
echo.

if %ERRORES% equ 0 (
    echo   [OK] TODO LISTO PARA INSTALAR
    echo.
    echo   Siguiente paso:
    echo     1. Clic derecho en: instalar_servicio_simple.bat
    echo     2. Ejecutar como administrador
    echo     3. Seguir las instrucciones
    echo.
) else (
    echo   [ERROR] Se encontraron %ERRORES% problema(s)
    echo.
    echo   Soluciona los errores antes de instalar:
    if not exist ".env" echo     - Crea el archivo .env
    if not defined DBF_PATH echo     - Configura DBF_PATH en .env
    echo.
)

echo ============================================================
echo.
pause
