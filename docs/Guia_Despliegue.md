# Guía de despliegue — Portfolio Full Stack

Esta guía describe cómo publicar el proyecto en **Clever Cloud** con una base de datos **MySQL**, y cómo versionarlo en **GitHub**. Está pensada para ejecutarse paso a paso desde Windows, aunque los comandos de Git son iguales en cualquier sistema.

---

## 1. Requisitos previos

- Cuenta en [Clever Cloud](https://www.clever-cloud.com/).
- Cuenta en [GitHub](https://github.com/).
- Git instalado (`git --version`).
- Repositorio local con el proyecto y todos los archivos de configuración.
- Opcional: [Clever Tools](https://github.com/CleverCloud/clever-tools) para desplegar desde la terminal.

---

## 2. Preparar el repositorio local

```powershell
cd C:\Users\kevin\OneDrive\Documentos\portfolio2

# Inicializar Git (solo la primera vez)
git init

# Verificar que .env no se incluya
git status

# Primer commit
git add .
git commit -m "Proyecto integrador: portfolio full stack Flask + MySQL"
git branch -M main
```

> El archivo `.gitignore` excluye `.venv/`, `.env`, `instance/`, `__pycache__/`, `.pytest_cache/` y archivos temporales.

### Crear el repositorio en GitHub

1. Entrar a <https://github.com/new>.
2. Nombre sugerido: `portfolio2` (público o privado).
3. No inicializar con README ni `.gitignore` (ya existen localmente).
4. Copiar la URL del repositorio y ejecutar:

```powershell
git remote add origin https://github.com/USUARIO/portfolio2.git
git push -u origin main
```

Si GitHub pide autenticación, usar un **Personal Access Token** como contraseña o configurar SSH.

---

## 3. Crear la aplicación en Clever Cloud

1. Iniciar sesión en la consola de Clever Cloud.
2. **Create → an application → Python**.
3. Elegir un nombre, por ejemplo `portfolio-kevin`.
4. Seleccionar la región más cercana (por ejemplo, París o Montreal).
5. En la configuración de despliegue, elegir **GitHub** y autorizar el repositorio `portfolio2`.

### Variables de entorno obligatorias

En **Environment variables** de la aplicación, agregar:

| Variable | Valor |
| --- | --- |
| `CC_PYTHON_MODULE` | `wsgi:app` |
| `CC_PYTHON_BACKEND` | `gunicorn` |
| `CC_PYTHON_VERSION` | `3.12` |
| `FLASK_CONFIG` | `production` |
| `SECRET_KEY` | Una cadena aleatoria larga (ver comando abajo) |
| `ADMIN_USERNAME` | `admin` |
| `ADMIN_PASSWORD` | Una contraseña inicial segura |
| `ADMIN_NOMBRE` | `Kevin` |
| `SITE_NAME` | `Kevin \| Portfolio` |
| `SITE_URL` | `https://<tu-app>.cleverapps.io` |
| `SEED_ON_START` | `1` |
| `SESSION_COOKIE_SECURE` | `true` |

Generar una clave secreta:

```powershell
.\.venv\Scripts\python.exe -c "import secrets; print(secrets.token_hex(32))"
```

> `CC_PYTHON_MODULE=wsgi:app` indica a Clever Cloud que importe el objeto `app` del archivo `wsgi.py`. `CC_PYTHON_BACKEND=gunicorn` selecciona el servidor WSGI. Gunicorn se instala desde `requirements.txt` en Linux.

---

## 4. Agregar la base de datos MySQL

1. En la aplicación, ir a **Add-ons → Add an add-on**.
2. Elegir **MySQL**.
3. Seleccionar el plan (para un portfolio suele alcanzar el plan gratuito o el más pequeño).
4. Confirmar y esperar a que el add-on se cree.
5. Vincularlo a la aplicación cuando se solicite.

Clever Cloud inyecta automáticamente estas variables:

```text
MYSQL_ADDON_URI
MYSQL_ADDON_HOST
MYSQL_ADDON_PORT
MYSQL_ADDON_DB
MYSQL_ADDON_USER
MYSQL_ADDON_PASSWORD
```

La aplicación detecta `MYSQL_ADDON_URI` (o construye la URI con las variables individuales) y normaliza `mysql://` a `mysql+pymysql://` con `charset=utf8mb4`. **No es necesario cargar la URI manualmente.**

### Crear las tablas y los datos

Con `SEED_ON_START=1`, la aplicación ejecuta `db.create_all()` y carga los datos de ejemplo en el primer arranque si la base está vacía. El seed es idempotente: no duplica contenido si ya existe un perfil.

Si se prefiere hacerlo manualmente:

```bash
# Desde una terminal con acceso al host MySQL de Clever Cloud
mysql -h <host> -P <puerto> -u <usuario> -p <base> < database/schema_mysql.sql
mysql -h <host> -P <puerto> -u <usuario> -p <base> < database/seed.sql
```

O usar los comandos de Flask con la variable `DATABASE_URL` apuntando al MySQL de Clever Cloud:

```powershell
$env:DATABASE_URL="mysql+pymysql://usuario:clave@host:puerto/base?charset=utf8mb4"
.\.venv\Scripts\flask --app wsgi init-db
.\.venv\Scripts\flask --app wsgi seed-db
```

---

## 5. Desplegar

### Opción A — Desde GitHub (recomendada)

1. En la consola de Clever Cloud, abrir la aplicación.
2. Ir a **Information → Deployment** y hacer clic en **Deploy** (o hacer push a la rama configurada).
3. Clever Cloud detecta `requirements.txt`, instala las dependencias y arranca con `CC_PYTHON_MODULE=wsgi:app`.
4. Seguir los logs en **Logs** hasta ver que la aplicación responde.

Cada `git push` a la rama configurada puede disparar un despliegue automático.

### Opción B — Clever Tools (CLI)

```powershell
# Instalar Clever Tools (si no está instalado)
npm install -g clever-tools

# Autenticarse
clever login

# Asociar la carpeta con la aplicación
clever link <app_id>

# Desplegar
clever deploy
```

---

## 6. Verificación posterior al despliegue

1. Abrir `https://<tu-app>.cleverapps.io/salud` → debe responder `{"status":"ok","servicio":"portfolio"}`.
2. Abrir `https://<tu-app>.cleverapps.io/` → el portfolio debe cargar con estilos, imágenes y datos.
3. Probar `/cv` → debe descargar un PDF válido.
4. Probar `/api/portfolio` → debe devolver JSON.
5. Iniciar sesión en `/login` con `ADMIN_USERNAME` / `ADMIN_PASSWORD`.
6. Cambiar la contraseña desde **Mi cuenta**.
7. Editar el perfil con los datos reales (email, teléfono, ubicación, LinkedIn, GitHub).
8. Reemplazar los proyectos de ejemplo por proyectos reales.
9. Enviar un mensaje de prueba desde el formulario y verificarlo en el panel.
10. Descargar el CV y comprobar que refleja los datos actualizados.
11. Verificar el sitio en móvil (o con las herramientas de desarrollo del navegador).
12. Opcional: configurar un dominio propio en **Domain names** y actualizar `SITE_URL`.

### Checklist de seguridad

- [ ] `SECRET_KEY` aleatoria y privada.
- [ ] `ADMIN_PASSWORD` segura y cambiada después del primer acceso.
- [ ] `SESSION_COOKIE_SECURE=true`.
- [ ] HTTPS activo (Clever Cloud lo provee).
- [ ] `.env` no está en el repositorio.
- [ ] `/admin` responde `noindex` y está bloqueado en `robots.txt`.
- [ ] Base de datos con backup o plan de respaldo.
- [ ] `SEED_ON_START=0` después de la carga inicial (opcional pero recomendable).

---

## 7. Actualizaciones y rollback

### Actualizar el sitio

```powershell
git add .
git commit -m "Actualizo contenido y mejoras del portfolio"
git push
```

Si el despliegue automático está activo, Clever Cloud reconstruye la aplicación. Si no, usar **Deploy** en la consola o `clever deploy`.

### Volver a una versión anterior

En la consola de Clever Cloud, abrir **Deployments**, elegir un despliegue anterior y usar **Rollback**. También se puede revertir el commit en Git y volver a desplegar.

---

## 8. Solución de problemas

| Síntoma | Causa probable | Solución |
| --- | --- | --- |
| Error 500 al iniciar | Falta `SECRET_KEY` o la base no conecta | Revisar logs y variables de entorno. |
| `Access denied for user` | Credenciales MySQL incorrectas | Verificar el add-on vinculado y `MYSQL_ADDON_URI`. |
| `Table doesn't exist` | No se crearon las tablas | Dejar `SEED_ON_START=1` en el primer arranque o ejecutar `flask init-db`. |
| El sitio carga sin estilos | Archivos estáticos no incluidos | Verificar que `portfolio/static/` esté en el repositorio. |
| El login no funciona | Contraseña inicial distinta o usuario inactivo | Ejecutar `flask create-admin` con `DATABASE_URL` de producción. |
| El CV no descarga | Error en ReportLab o datos incompletos | Revisar logs; el perfil debe existir en la base. |
| El despliegue falla en el build | Dependencia no instalada | Revisar `requirements.txt` y la versión de Python (`CC_PYTHON_VERSION`). |

### Ver logs

- Consola de Clever Cloud → aplicación → **Logs**.
- O desde la terminal: `clever logs`.

---

## 9. Estructura de archivos relevante para el despliegue

```text
requirements.txt      # Dependencias (incluye gunicorn en Linux)
wsgi.py               # app = create_app()
Procfile              # Alternativa: gunicorn wsgi:app --bind 0.0.0.0:$PORT
.env.example          # Plantilla de variables (no contiene secretos)
config.py             # Lee DATABASE_URL / MYSQL_ADDON_* / SQLite
database/*.sql        # Diseño físico y datos iniciales
```

---

## 10. Referencias

- Documentación de Python en Clever Cloud: <https://www.clever.cloud/developers/doc/deploy/applications/python/>
- Add-on MySQL: <https://www.clever.cloud/developers/doc/addons/mysql/>
- Git: <https://git-scm.com/doc>
- GitHub: <https://docs.github.com/>

---

**Última actualización:** noviembre de 2026.
