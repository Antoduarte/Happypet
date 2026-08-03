@echo off
REM ============================================================================
REM Setup venv para Happypet (Django 4.2 + xhtml2pdf)
REM Ejecutar desde C:\Apache24\htdocs\Happypet  (o la ruta donde este el proyecto)
REM ============================================================================
cd /d %~dp0

echo [1/5] Creando venv con Python 3.12...
py -3.12 -m venv venv

echo [2/5] Instalando dependencias desde requirements.txt...
venv\Scripts\pip install --upgrade pip
venv\Scripts\pip install -r requirements.txt

echo [3/5] Instalando mod_wsgi (para compatibilidad con Apache)...
venv\Scripts\pip install mod_wsgi

echo [4/5] Aplicando migraciones...
venv\Scripts\python manage.py migrate

echo [5/5] Recolectando archivos estaticos...
venv\Scripts\python manage.py collectstatic --noinput

echo.
echo Listo. Ahora revisa que ims/wsgi.py tenga las lineas de sys.path.insert.
echo Reinicia Apache para aplicar cambios:
echo    net stop Apache2.4 ^&^& net start Apache2.4
pause
