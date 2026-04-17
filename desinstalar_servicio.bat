@echo off
title Desinstalador Servicio - API Inventario y Precios
cd /d "%~dp0"

echo.
echo ============================================================
echo   DESINSTALADOR - API Inventario y Precios
echo ============================================================
echo.

net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Ejecutar como ADMINISTRADOR
    pause
    exit /b 1
)

set SERVICE_NAME=ProductosSyncAPI
set NSSM=%~dp0tools\nssm\nssm.exe

if not exist "%NSSM%" (
    echo [ERROR] NSSM no encontrado en: %NSSM%
    pause
    exit /b 1
)

echo [..] Deteniendo servicio...
"%NSSM%" stop %SERVICE_NAME%
timeout /t 2 /nobreak >nul

echo [..] Eliminando servicio...
"%NSSM%" remove %SERVICE_NAME% confirm

echo [..] Eliminando regla de firewall...
netsh advfirewall firewall delete rule name="ProductosSyncAPI"

echo.
echo [OK] Servicio desinstalado correctamente
echo.
pause
