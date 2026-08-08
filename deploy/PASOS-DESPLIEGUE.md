# Pasos de despliegue — migración a waitress + Apache reverse proxy

Checklist operativo para el servidor del cliente. Cubre **los dos proyectos**:
Happypet y happypet-inventory.

El *por qué* de este cambio está en [`README-deploy.md`](README-deploy.md) (resumen:
en Windows mod_wsgi solo soporta modo embebido, así que ambos proyectos compartían el
proceso de Apache y sus extensiones en C chocaban entre sub-intérpretes →
`TypeError: _abc_impl is set to wrong type`).

**Estado final:**

| Proyecto | Ruta en el servidor | Django | Servicio | Puerto | Host |
|---|---|---|---|---|---|
| Happypet | `C:\Apache24\htdocs\Happypet` | 4.2.20 | `Happypet` | 8001 | happypet.local |
| Inventory | `C:\Apache24\htdocs\happypet-inventory` | >=6.0 | `HappypetInventory` | 8002 | inventory.local |

---

## Antes de ir al servidor

- [ ] **1. Commitear y subir los cambios de ambos repos** (o preparar las carpetas para copiar):

  ```
  Happypet:            ims/wsgi.py, requirements.txt, setup_venv.bat, deploy/
  happypet-inventory:  backend/config/wsgi.py, backend/requirements.txt,
                       backend/deploy/{PASOS_A_REALIZAR.txt, setup_inventory.bat,
                                       install_service.bat, apache-inventory.conf.example}
  ```

- [ ] **2. Descargar NSSM** — https://nssm.cc
  Copiar `nssm.exe` (versión win64) a `C:\Windows\System32` o a alguna carpeta del PATH
  del servidor.

---

## En el servidor

### 3. Respaldar Apache

Es lo único difícil de deshacer:

```bat
copy C:\Apache24\conf\httpd.conf C:\Apache24\conf\httpd.conf.bak
xcopy C:\Apache24\conf\extra C:\Apache24\conf\extra.bak\ /E /I
```

- [ ] Respaldo hecho

### 4. Copiar los archivos actualizados

- [ ] `C:\Apache24\htdocs\Happypet`
- [ ] `C:\Apache24\htdocs\happypet-inventory`

> **No pisar** `venv\`, `.env` ni `media\`.

### 5. Instalar waitress en cada venv

```bat
cd C:\Apache24\htdocs\Happypet
venv\Scripts\pip install -r requirements.txt
venv\Scripts\python manage.py collectstatic --noinput
```

```bat
cd C:\Apache24\htdocs\happypet-inventory
venv\Scripts\pip install -r requirements.txt
venv\Scripts\python manage.py collectstatic --noinput
```

- [ ] Happypet
- [ ] Inventory

> El `collectstatic` de Happypet va a mano porque en su `setup_venv.bat` está comentado,
> y Apache va a servir `staticfiles\` por `Alias`.

### 6. Probar cada uno a mano, uno por vez

**No saltear este paso:** separa fallos de la app de fallos de Apache.

```bat
cd C:\Apache24\htdocs\Happypet
venv\Scripts\waitress-serve.exe --listen=127.0.0.1:8001 --threads=8 ims.wsgi:application
```

```bat
cd C:\Apache24\htdocs\happypet-inventory
venv\Scripts\waitress-serve.exe --listen=127.0.0.1:8002 --threads=8 config.wsgi:application
```

Con cada uno corriendo, abrir en el navegador del servidor `http://127.0.0.1:8001/` y
`http://127.0.0.1:8002/`. Cortar con `Ctrl+C`.

- [ ] Happypet arranca y responde
- [ ] Inventory arranca y responde

### 7. Registrar los servicios

CMD **como administrador**:

```bat
C:\Apache24\htdocs\Happypet\deploy\install_service.bat
C:\Apache24\htdocs\happypet-inventory\deploy\install_service.bat
```

- [ ] Servicio `Happypet` creado y arrancado
- [ ] Servicio `HappypetInventory` creado y arrancado

### 8. Configurar Apache

En `C:\Apache24\conf\httpd.conf`:

- [ ] Descomentar `LoadModule proxy_module modules/mod_proxy.so`
- [ ] Descomentar `LoadModule proxy_http_module modules/mod_proxy_http.so`
- [ ] Comentar `LoadFile ...python312.dll`
- [ ] Comentar `LoadModule wsgi_module ...`
- [ ] Comentar `WSGIPythonHome ...`
- [ ] Borrar los `WSGIScriptAlias` y `application-group` de **ambos** proyectos
- [ ] Quitar `Listen 8080`
- [ ] Agregar los dos `Include conf/extra/...`

Plantillas a copiar en `C:\Apache24\conf\extra\`:

| Plantilla | Destino |
|---|---|
| `Happypet\deploy\apache-happypet.conf.example` | `conf\extra\apache-happypet.conf` |
| `happypet-inventory\backend\deploy\apache-inventory.conf.example` | `conf\extra\apache-inventory.conf` |

Ajustar `ServerName` y las rutas a las reales del servidor.

### 9. Archivo hosts

Ejecutar `happypet-inventory\backend\deploy\editar_hosts.bat` y verificar que estén **las dos**:

```
127.0.0.1 happypet.local
127.0.0.1 inventory.local
```

- [ ] Ambas líneas presentes

### 10. Aplicar

```bat
C:\Apache24\bin\httpd -t     :: debe decir "Syntax OK"
C:\Apache24\bin\httpd -S     :: debe listar los dos vhosts con su ServerName
net stop Apache2.4
net start Happypet
net start HappypetInventory
net start Apache2.4
```

- [ ] `httpd -t` → Syntax OK
- [ ] `httpd -S` → los dos vhosts con su ServerName
- [ ] Todo arriba

---

## Validación

El bug era intermitente y dependía del orden de carga, así que **no alcanza con abrir
cada sitio una vez**.

- [ ] **La prueba que importa:** abrir el detalle de mascota en Happypet **y** generar un
      ticket PDF en inventory, **alternando varias veces sin reiniciar nada**. Eso es
      exactamente lo que antes rompía uno de los dos.
- [ ] Repetir después de reiniciar Apache.
- [ ] Repetir después de reiniciar cada servicio por separado — el orden de arranque ya no
      debe influir.
- [ ] Reiniciar `Happypet` y confirmar que inventory **sigue respondiendo** (prueba de aislamiento).
- [ ] Buscar `_abc_impl` en `C:\Apache24\logs\error.log` y en
      `<proyecto>\logs\waitress-error.log` de ambos.
- [ ] Desde **otra máquina de la red**: confirmar que `8001` y `8002` **no** son alcanzables.
- [ ] Dejar los sitios en uso normal un día y volver a revisar los logs.

---

## Los dos puntos donde esperar fricción

### La impresión de tickets

Los dos proyectos invocan `wkhtmltopdf.exe` como subproceso. Antes corrían bajo la cuenta
del servicio Apache; ahora bajo la de NSSM (LocalSystem por defecto). **Si los PDF fallan y
el resto anda, es permisos:**

```bat
nssm set Happypet ObjectName .\USUARIO CONTRASENA
nssm set HappypetInventory ObjectName .\USUARIO CONTRASENA
```

Esa cuenta necesita ejecutar `C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe` y escribir
en `media\`.

### La conexión a base de datos de Happypet

`ims/settings.py` lee usuario y contraseña de `os.environ.get('USER')` y
`os.environ.get('PASSWORD')` — nombres muy genéricos — y `django-environ` carga el `.env`
**sin `overwrite`**, así que **si el entorno del servicio ya define esas variables, ganan
sobre el `.env`**. El entorno de un servicio NSSM no es idéntico al del servicio Apache.

Verificar temprano que conecte bien. Si da error de autenticación de Postgres, es esto.

> Inventory no tiene este problema: usa `DATABASE_URL` y lee con `overwrite=True`.

---

## Dónde mirar si algo falla

| Síntoma | Log |
|---|---|
| Problemas de proxy, vhost, arranque de Apache | `C:\Apache24\logs\error.log` |
| Errores de la app Django | `<proyecto>\logs\waitress-error.log` |
| 503 Service Unavailable | El servicio de waitress no está corriendo → `services.msc` |
| 400 Bad Request | `ALLOWED_HOSTS`, o falta `ProxyPreserveHost On` en el vhost |
| Se abre el sitio equivocado | Falta `ServerName` en algún vhost → `httpd -S` |

---

## Rollback

```bat
net stop Apache2.4
net stop Happypet
net stop HappypetInventory
nssm remove Happypet confirm
nssm remove HappypetInventory confirm
copy C:\Apache24\conf\httpd.conf.bak C:\Apache24\conf\httpd.conf
xcopy C:\Apache24\conf\extra.bak C:\Apache24\conf\extra\ /E /Y
net start Apache2.4
```

Y reactivar `LoadModule wsgi_module` en `httpd.conf`.

Se vuelve al estado anterior (con el bug) **sin pérdida de datos**: nada de esto toca la
base de datos ni el esquema.
