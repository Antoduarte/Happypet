# Despliegue en Windows: waitress + Apache reverse proxy

> **¿Vas a desplegar ahora?** Seguí el checklist paso a paso en
> [`PASOS-DESPLIEGUE.md`](PASOS-DESPLIEGUE.md), que cubre los dos proyectos en orden.
> Este documento explica el **por qué** y el detalle de Happypet.

## Por qué este cambio

Antes, Happypet y Happypet-inventory se servían con **mod_wsgi** desde el mismo Apache.
En Windows mod_wsgi solo soporta **modo embebido** (`WSGIDaemonProcess` requiere `fork()` de
Unix), así que ambas apps corrían dentro del mismo `httpd.exe`, cada una en un **sub-intérprete**
distinto de CPython.

Las extensiones en C del stack (`psycopg2`, `_imaging`, `_cffi_backend`, `lxml`) usan
inicialización de fase única: CPython las carga **una sola vez por proceso** y comparte sus
objetos de tipo entre intérpretes. Cuando una clase creada en el intérprete A cruzaba al
intérprete B, su `_abc_impl` era un `_abc_data` del intérprete A y la verificación de tipo fallaba:

```
TypeError: _abc_impl is set to wrong type
```

Ganaba el intérprete que cargaba la extensión primero y el otro reventaba — por eso el error
alternaba entre el detalle de mascota de Happypet y la impresión de tickets de inventory, y se
mudaba de sitio al reiniciar Apache.

**No se arregla con directivas de Apache.** En sub-intérpretes separados chocan las extensiones C;
en `WSGIApplicationGroup %{GLOBAL}` (un solo intérprete) chocarían el singleton de
`django.conf.settings` y `DJANGO_SETTINGS_MODULE`. Dos proyectos Django no pueden convivir en un
proceso mod_wsgi en Windows: **hay que separarlos en procesos distintos.**

## Arquitectura resultante

```
happypet.local:80    ──┐                    ┌── servicio waitress → 127.0.0.1:8001 → Happypet
                       ├── Apache 2.4 ──────┤
inventory.local:80   ──┘   (mod_proxy_http) └── servicio waitress → 127.0.0.1:8002 → Happypet-inventory
                            + Alias /static /media
```

Cada app: su propio proceso, su propio intérprete, su propio venv. Se reinician por separado.

## Procedimiento

### 0. Respaldar

Copiar `C:\Apache24\conf\httpd.conf` y `C:\Apache24\conf\extra\*.conf` antes de tocar nada.

### 1. Preparar el proyecto

```bat
cd C:\Apache24\htdocs\Happypet
setup_venv.bat
venv\Scripts\python manage.py migrate
venv\Scripts\python manage.py collectstatic --noinput
```

`collectstatic` es obligatorio: Apache sirve `staticfiles\` directamente vía `Alias`.

Probar el arranque a mano antes de crear el servicio:

```bat
venv\Scripts\python.exe -m waitress --listen=127.0.0.1:8001 --threads=8 ims.wsgi:application
```

### 2. Registrar el servicio de Windows

Requiere [NSSM](https://nssm.cc) en el PATH. Ejecutar **como administrador**:

```bat
deploy\install_service.bat
```

- Escucha **solo en `127.0.0.1`**: los puertos 8001/8002 nunca deben quedar expuestos a la red.
- La cuenta del servicio necesita permiso de ejecución sobre
  `C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe` (lo usa `print_medical_record` en
  `petcare/views.py`) y de escritura sobre `media\`. Es el punto más probable de fallo tras la
  migración. Se ajusta con `nssm set Happypet ObjectName .\USUARIO CONTRASENA`.

### 3. Configurar Apache

En `httpd.conf`:

```apache
LoadModule proxy_module      modules/mod_proxy.so
LoadModule proxy_http_module modules/mod_proxy_http.so
#LoadModule wsgi_module ...        <- comentar, ya no se usa
```

Eliminar de ambos VirtualHost todas las directivas `WSGIScriptAlias`, `WSGIPythonPath`,
`WSGIApplicationGroup` y `WSGIPythonHome`, y usar `apache-happypet.conf.example` como plantilla
(copiarlo a `conf\extra\` e incluirlo). Ajustar `ServerName` y rutas al servidor real.

### 4. Aplicar

```bat
net stop Apache2.4
net start Happypet
net start HappypetInventory
net start Apache2.4
```

### 5. Mismo tratamiento en Happypet-inventory

- Quitar el `sys.path.insert(...venv\Lib\site-packages...)` de su `wsgi.py` (ya no hace falta y
  provoca colisiones entre venvs).
- `waitress` en su `requirements.txt`, sin `gunicorn` (no funciona en Windows).
- Su propio servicio en el puerto **8002** y su propio VirtualHost con el mismo patrón.

## Verificación

El bug era intermitente y dependía del orden de carga, así que no basta con abrir cada sitio una vez:

1. **Reproducir el escenario que fallaba:** abrir el detalle de mascota en Happypet **y** generar
   un ticket PDF en inventory, alternando varias veces sin reiniciar nada. Antes esto rompía uno
   de los dos; ahora ambos deben responder siempre.
2. Repetir tras reiniciar Apache y tras reiniciar cada servicio de waitress por separado: el orden
   de arranque ya no debe influir.
3. Reiniciar `Happypet` y confirmar que **no** interrumpe a inventory (prueba de aislamiento).
4. Confirmar que `/static/` y `/media/` los sirve Apache: la respuesta trae `ETag`/`Last-Modified`
   y no aparece nada en `logs\waitress.log`.
5. Buscar `_abc_impl` en `logs\waitress-error.log` de ambos servicios y en
   `C:\Apache24\logs\error.log`. Dejar los sitios en uso normal un día y volver a revisar.
6. Comprobar desde otra máquina de la red que `8001` y `8002` **no** son alcanzables.

## Rollback

Restaurar los `.conf` respaldados, reactivar `LoadModule wsgi_module`, detener y quitar los
servicios (`nssm remove Happypet confirm`). Se vuelve al estado anterior sin pérdida de datos:
nada de esto toca la base de datos ni el esquema.

## Si más adelante se pone HTTPS

Añadir en `settings.py` de ambos proyectos:

```python
CSRF_TRUSTED_ORIGINS = ['https://happypet.local']
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
```

y `RequestHeader set X-Forwarded-Proto "https"` en el VirtualHost TLS.
