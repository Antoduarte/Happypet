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
venv\Scripts\python.exe -m waitress --listen=127.0.0.1:8001 --threads=8 ims.wsgi:application
```

```bat
cd C:\Apache24\htdocs\happypet-inventory
venv\Scripts\python.exe -m waitress --listen=127.0.0.1:8002 --threads=8 config.wsgi:application
```

> Se usa `python.exe -m waitress` y **no** `waitress-serve.exe` a propósito: los `.exe` que
> genera pip/uv llevan grabada la ruta absoluta del intérprete del momento de la instalación,
> así que renombrar o mover el venv los rompe. `python.exe` resuelve su venv por `pyvenv.cfg`,
> que es relativo a su propia ubicación.

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

## Prueba de reinicio (no la saltees antes de entregar)

Los tres servicios quedan en arranque automático: Apache2.4 ya lo estaba, y los dos nuevos
los configura `install_service.bat` con `Start SERVICE_AUTO_START`. Levantan solos al
encender la máquina, sin que nadie inicie sesión.

Es la única forma de saber que realmente funciona:

- [ ] **Reiniciar el servidor.**
- [ ] Sin tocar nada, verificar que los tres estén arriba:

      Get-Service Apache2.4, Happypet, HappypetInventory | Format-Table Name, Status, StartType

      Los tres deben decir `Running` / `Automatic`.
- [ ] Abrir `http://happypet.local/` y `http://inventory.local/` en el navegador.

### Si cambiaste la cuenta de los servicios, leé esto

Mientras los servicios corran como **LocalSystem** (el default) no hay nada que hacer.
Pero si tuviste que cambiarlos a una cuenta de usuario por los permisos de `wkhtmltopdf`
(`nssm set Happypet ObjectName .\USUARIO CONTRASENA`):

- [ ] Esa cuenta necesita el derecho **"Iniciar sesión como servicio"**. Sin él, el servicio
      arranca bien la primera vez pero **falla al reiniciar la máquina** con
      **error 1069** (*"el servicio no se inició debido a un error de inicio de sesión"*).
      NSSM normalmente lo concede al asignar la cuenta, pero verificalo en:
      `secpol.msc` → *Directivas locales* → *Asignación de derechos de usuario* →
      *Iniciar sesión como servicio*.
- [ ] La cuenta debe tener **contraseña sin vencimiento**. El día que expire, los sitios
      dejan de levantar.

### Dos cosas que se resuelven solas

- **PostgreSQL puede tardar más en levantar que Django.** No importa: Django no conecta a
  la base al arrancar, sino en la primera consulta.
- **Si Apache levanta antes que waitress**, las primerísimas peticiones pueden dar **503**.
  Se corrige solo en cuanto waitress termina de arrancar. Se podría forzar el orden con
  dependencias de servicio, pero no vale la pena: `sc config` **reemplaza** la lista de
  dependencias existentes de Apache, y es más riesgo que beneficio para un 503 de unos segundos.

---

## Apéndice — para qué es NSSM

**NSSM** (*Non-Sucking Service Manager*) convierte un `.exe` cualquiera en un servicio de Windows.

Windows no puede arrancar cualquier programa como servicio: un servicio debe hablar el
protocolo del **Service Control Manager** — registrarse al iniciar, responder a stop/pause,
reportar estado. `waitress-serve.exe` no hace nada de eso, es una aplicación de consola común.
Con `sc create` directo, Windows lo lanzaría, esperaría el "acá estoy" que nunca llega, y
abortaría con **error 1053** (*"el servicio no respondió a tiempo"*).

NSSM se mete en el medio:

```
Windows SCM  ──arranca──►  nssm.exe  ──lanza como hijo──►  waitress-serve.exe
             ◄──responde──            ──vigila y reinicia──►
```

Lo que aporta, según lo que configura `install_service.bat`:

| Configuración | Para qué |
|---|---|
| `Start SERVICE_AUTO_START` | Arranca solo al encender la máquina |
| `AppExit Default Restart` + `AppRestartDelay 5000` | Si el proceso se cae, lo relevanta a los 5 s |
| `AppStdout` / `AppStderr` | Manda la salida a `logs\waitress.log` — si no, se perdería |

Antes no hacía falta porque el servicio era Apache y el código Python vivía dentro de
`httpd.exe`. Ahora que Django corre en procesos propios, esos procesos necesitan quién los
arranque al boot y los mantenga vivos.

**Alternativa** si NSSM diera problemas: **WinSW** (mismo concepto, un `.exe` configurado por
XML). El Programador de Tareas también arranca cosas al boot, pero no reinicia ante caída ni
permite `net stop`, así que no se recomienda.

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
| **`Index of /`** en vez de la app | Apache no está leyendo el vhost. Verificar que `Include conf/extra/...` **no** esté comentado en `httpd.conf`, y confirmar con `httpd -S` |
| **`Failed to canonicalize script path`** en `waitress-error.log`, servicio en `Paused` | El venv fue renombrado o movido **después** de instalar los paquetes. Ver abajo |

### `Failed to canonicalize script path`

Los `.exe` de `venv\Scripts\` (incluido `pip.exe`) llevan grabada la ruta absoluta del
intérprete del momento de la instalación. Si el venv se renombra o se mueve, todos apuntan a
un path inexistente. `Paused` es como reporta NSSM un servicio cuya app se cae una y otra vez.

Para ver la ruta que quedó grabada:

```powershell
[Text.Encoding]::ASCII.GetString([IO.File]::ReadAllBytes("venv\Scripts\waitress-serve.exe")) `
  -match '#![^\r\n]+' | Out-Null; $Matches[0]
```

Solución: recrear el venv en su ubicación final, o invocar siempre `python.exe -m <módulo>`
(que es lo que hacen estos scripts).

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
