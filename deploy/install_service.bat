
@echo off
REM ============================================================================
REM Registra Happypet como servicio de Windows usando waitress + NSSM.
REM
REM Requiere NSSM en el PATH (https://nssm.cc). Ejecutar COMO ADMINISTRADOR.
REM
REM Cada proyecto Django DEBE correr en su propio proceso: es justamente lo que
REM evita el error "_abc_impl is set to wrong type" que aparecia cuando Happypet
REM y Happypet-inventory compartian el proceso de Apache via mod_wsgi.
REM ============================================================================
setlocal
cd /d %~dp0..

set SERVICE=Happypet
set PORT=8001
set PROJECT=%CD%

where nssm >nul 2>&1
if errorlevel 1 (
    echo ERROR: no se encontro nssm.exe en el PATH. Instalalo desde https://nssm.cc
    pause
    exit /b 1
)

if not exist "%PROJECT%\venv\Scripts\waitress-serve.exe" (
    echo ERROR: falta waitress en el venv. Ejecuta primero setup_venv.bat
    pause
    exit /b 1
)

echo Registrando servicio %SERVICE% en 127.0.0.1:%PORT% ...

nssm install %SERVICE% "%PROJECT%\venv\Scripts\waitress-serve.exe"
nssm set %SERVICE% AppParameters "--listen=127.0.0.1:%PORT% --threads=8 ims.wsgi:application"
nssm set %SERVICE% AppDirectory "%PROJECT%"
nssm set %SERVICE% DisplayName "Happypet (Django/waitress)"
nssm set %SERVICE% Description "Happypet servido por waitress en 127.0.0.1:%PORT%, detras de Apache"
nssm set %SERVICE% Start SERVICE_AUTO_START

REM Logs del servicio
if not exist "%PROJECT%\logs" mkdir "%PROJECT%\logs"
nssm set %SERVICE% AppStdout "%PROJECT%\logs\waitress.log"
nssm set %SERVICE% AppStderr "%PROJECT%\logs\waitress-error.log"
nssm set %SERVICE% AppRotateFiles 1
nssm set %SERVICE% AppRotateBytes 10485760

REM Reinicio automatico si el proceso muere
nssm set %SERVICE% AppExit Default Restart
nssm set %SERVICE% AppRestartDelay 5000

echo.
echo Servicio registrado. Iniciando...
net start %SERVICE%

echo.
echo RECORDATORIO: la cuenta del servicio necesita permiso de ejecucion sobre
echo   C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe   (impresion de tickets)
echo y permiso de escritura sobre  %PROJECT%\media
echo Se configura con:  nssm set %SERVICE% ObjectName .\USUARIO CONTRASENA
pause
endlocal
