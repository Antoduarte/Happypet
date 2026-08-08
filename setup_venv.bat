@echo off
REM ============================================================================
REM Setup venv para Happypet (Django 4.2 + xhtml2pdf)
REM Ejecutar desde C:\Apache24\htdocs\Happypet  (o la ruta donde este el proyecto)
REM
REM Happypet se sirve con waitress en 127.0.0.1:8001 (proceso propio).
REM Apache solo actua como reverse proxy: NO se usa mod_wsgi.
REM Ver deploy\README-deploy.md para el detalle.
REM ============================================================================
cd /d %~dp0

echo [1/2] Creando venv con Python 3.12...
py -3.12 -m venv venv

echo [2/2] Instalando dependencias desde requirements.txt...
venv\Scripts\pip install --upgrade pip
venv\Scripts\pip install -r requirements.txt

@REM echo [3/4] Aplicando migraciones...
@REM venv\Scripts\python manage.py migrate

@REM echo [4/4] Recolectando archivos estaticos...
@REM venv\Scripts\python manage.py collectstatic --noinput

echo.
echo Listo. Prueba el arranque a mano antes de crear el servicio:
echo    venv\Scripts\python.exe -m waitress --listen=127.0.0.1:8001 --threads=8 ims.wsgi:application
echo.
echo Para registrar el servicio de Windows:  deploy\install_service.bat
echo Para reiniciarlo:  net stop Happypet ^&^& net start Happypet
pause
