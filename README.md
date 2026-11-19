# Portfolio Web Full Stack — Proyecto Integrador

Aplicación web full stack desarrollada con **Python, Flask, MySQL, Jinja2 y POO** que funciona como portfolio personal y como sistema administrable. Incluye panel privado con autenticación, base de datos relacional, API JSON, **CV real descargable en PDF**, editor de textos persistentes y una interfaz responsive con animaciones.

> **Estado:** el desarrollo y las pruebas están completos. La publicación en Clever Cloud y la subida a GitHub quedan pendientes de las credenciales del alumno (ver [Despliegue](#despliegue-en-clever-cloud)).

---

## Índice

- [Características](#características)
- [Stack tecnológico](#stack-tecnológico)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Instalación local](#instalación-local)
- [Configuración de MySQL](#configuración-de-mysql)
- [Ejecución](#ejecución)
- [Acceso al panel](#acceso-al-panel)
- [Pruebas](#pruebas)
- [Documentación](#documentación)
- [Despliegue en Clever Cloud](#despliegue-en-clever-cloud)
- [Git y GitHub](#git-y-github)
- [Seguridad](#seguridad)
- [Mapeo de requisitos](#mapeo-de-requisitos)
- [Solución de problemas](#solución-de-problemas)

---

## Características

### Sitio público
- Hero animado con typewriter, avatar, disponibilidad y estadísticas.
- Secciones de **Sobre mí, Estudios, Experiencia, Tecnologías, Proyectos, Ubicación y Contacto**.
- Líneas de tiempo, tarjetas de tecnologías con barras de nivel y proyectos con etiquetas.
- Mapa embebido de OpenStreetMap (**iframe** requerido).
- Formulario de contacto con CSRF, validación del servidor y honeypot anti-spam.
- **CV real descargable en PDF** (subido desde el panel). Si no hay archivo, se genera uno con los datos de la base como respaldo.
- API pública de solo lectura: `GET /api/portfolio`.
- Metadatos SEO y Open Graph, favicon y logo SVG locales.
- Iconos FontAwesome, Google Fonts y diseño responsive (móvil, tablet y escritorio).
- Animaciones con CSS y JavaScript nativo, respetando `prefers-reduced-motion`.

### Panel privado
- Login con Flask-Login, contraseña hasheada (Werkzeug scrypt) y protección CSRF.
- Dashboard con métricas y últimos mensajes.
- CRUD completo de estudios, experiencias, tecnologías y proyectos.
- Edición del perfil, avatar, redes y resumen del CV.
- **Editor de contenido del sitio**: frases, títulos, etiquetas y parámetros del mapa se guardan en MySQL (`textos_sitio`).
- **Reemplazo del CV PDF** desde el panel (`/admin/cv`).
- Relación **N:M** entre proyectos y tecnologías mediante selección múltiple.
- Bandeja de mensajes con estado leído/no leído y eliminación.
- Cambio de nombre de usuario y contraseña con verificación de la clave actual.
- Visibilidad por registro (`activo`) y orden personalizable.

---

## Stack tecnológico

| Capa | Tecnología |
| --- | --- |
| Backend | Python 3.12+, Flask 3, Flask-SQLAlchemy, Flask-Login, Flask-WTF |
| Base de datos | MySQL 8 en producción, SQLite en desarrollo local |
| ORM / driver | SQLAlchemy + PyMySQL |
| Frontend | Jinja2, HTML5, CSS3, JavaScript ES6 |
| PDF | PDF real servido por Flask; ReportLab para el respaldo del CV y la documentación |
| Pruebas | pytest |
| Producción | Gunicorn + Clever Cloud |
| Recursos | FontAwesome 6.7.2, Google Fonts (Fraunces, Inter) |

---

## Estructura del proyecto

```text
portfolio2/
├── app.py                  # Entrada de desarrollo
├── wsgi.py                 # Entrada WSGI para producción
├── config.py               # Configuración y URI de la base
├── requirements.txt
├── Procfile                # Arranque alternativo con gunicorn
├── pytest.ini
├── .env.example            # Plantilla de variables de entorno
├── portfolio/
│   ├── __init__.py         # Application factory, filtros, CLI, errores
│   ├── extensions.py       # db, login_manager, csrf
│   ├── models.py           # POO (4 pilares) y tablas del modelo relacional
│   ├── forms.py            # Formularios Flask-WTF
│   ├── seed.py             # Datos reales del CV + textos iniciales
│   ├── pdf.py              # Generación del CV como respaldo
│   ├── routes/
│   │   ├── public.py       # Portfolio, contacto, CV, API, salud
│   │   ├── auth.py         # Login y logout
│   │   └── admin.py        # Panel CRUD protegido
│   ├── templates/          # Jinja2: público, admin, auth y errores
│   └── static/             # CSS, JS, imágenes SVG y uploads/CV_Kevin_Basualdo.pdf
├── database/
│   ├── schema_mysql.sql    # Diseño físico MySQL
│   └── seed.sql            # Datos iniciales en SQL
├── docs/
│   ├── Documentacion_Preliminar_Portfolio.pdf
│   └── Guia_Despliegue.md
├── scripts/
│   └── generar_documentacion.py
└── tests/                  # 41 pruebas automatizadas
```

---

## Instalación local

### Requisitos
- Python 3.12 o superior (probado con 3.14 en Windows).
- MySQL 8 (opcional en desarrollo; sin MySQL se usa SQLite).
- Git (para el versionado).

### Pasos

```powershell
# 1. Crear el entorno virtual
python -m venv .venv

# 2. Activarlo (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

# Si PowerShell bloquea la ejecución:
# Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned

# 3. Instalar dependencias
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# 4. Crear el archivo de configuración
copy .env.example .env

# 5. Ejecutar
python app.py
```

Abrir <http://127.0.0.1:5000>.

Sin `DATABASE_URL`, la aplicación crea automáticamente `instance/portfolio.db` (SQLite) y carga los datos del CV. Esto permite ejecutar y evaluar el proyecto sin instalar MySQL.

---

## Configuración de MySQL

### Opción A — Scripts SQL incluidos

```bash
mysql -u root -p < database/schema_mysql.sql
mysql -u root -p < database/seed.sql
```

- `database/schema_mysql.sql`: crea la base `portfolio`, las **9 tablas**, claves foráneas, índices y restricciones.
- `database/seed.sql`: carga el **perfil real del CV**, estudios (ITR e IEC), experiencia en Portones Automáticos, tecnologías, proyectos, la relación N:M y los **109 textos editables**. No carga mensajes falsos.

Ambos scripts se pueden ejecutar también desde phpMyAdmin, MySQL Workbench o DBeaver.

### Opción B — Comandos de Flask

```powershell
$env:DATABASE_URL="mysql+pymysql://root:tu_clave@localhost:3306/portfolio?charset=utf8mb4"
.\.venv\Scripts\flask --app wsgi init-db
.\.venv\Scripts\flask --app wsgi seed-db

# Si la base ya existía y faltan claves de texto nuevas:
.\.venv\Scripts\flask --app wsgi seed-textos
```

`seed-textos` agrega las claves nuevas **sin sobrescribir** las que editaste desde `/admin/contenido`.

### Variables de entorno

| Variable | Descripción |
| --- | --- |
| `SECRET_KEY` | Clave para firmar sesiones y CSRF. Obligatoria en producción. |
| `FLASK_CONFIG` | `development` (por defecto) o `production`. |
| `DATABASE_URL` | URI completa de MySQL. Tiene prioridad. |
| `MYSQL_ADDON_URI` | URI inyectada por el add-on MySQL de Clever Cloud. |
| `MYSQL_ADDON_HOST/USER/PASSWORD/PORT/DB` | Construcción alternativa de la URI. |
| `ADMIN_USERNAME` | Usuario inicial del panel. |
| `ADMIN_PASSWORD` | Contraseña inicial del panel. |
| `ADMIN_NOMBRE` | Nombre visible del administrador. |
| `SITE_NAME` | Nombre del sitio en metadatos. |
| `SITE_URL` | URL pública para canonical y Open Graph. |
| `CONTACT_EMAIL` | Email mostrado en el pie del sitio. |
| `SEED_ON_START` | `1` carga datos de ejemplo al iniciar si la base está vacía. |
| `SESSION_COOKIE_SECURE` | `true` en producción con HTTPS. |

> El archivo `.env` está excluido por `.gitignore`. Nunca subir claves reales al repositorio.

---

## Ejecución

```powershell
# Desarrollo
python app.py

# Producción local (Linux/macOS o WSL)
gunicorn wsgi:app --bind 0.0.0.0:8000
```

Rutas útiles:

| Ruta | Descripción |
| --- | --- |
| `/` | Portfolio completo |
| `/cv` | Descarga del CV real en PDF (con respaldo dinámico) |
| `/api/portfolio` | Contenido en JSON |
| `/salud` | Health check |
| `/login` | Acceso al panel |
| `/admin/` | Panel de administración |
| `/admin/contenido` | Editor de textos del sitio |
| `/admin/cv` | Reemplazo del PDF del CV |

---

## Acceso al panel

Credenciales iniciales:

```text
Usuario:    kevinAdmin
Contraseña: kevin1504
```

> **Cambiar la contraseña antes de publicar** desde *Panel → Mi cuenta*. También se pueden definir otras credenciales iniciales con `ADMIN_USERNAME` y `ADMIN_PASSWORD` antes del primer arranque.

Desde el panel se puede:

1. Editar el perfil y el resumen del CV.
2. Crear, editar, ocultar o eliminar estudios y experiencias.
3. Administrar tecnologías con su nivel, icono y color.
4. Crear proyectos y asociarles varias tecnologías.
5. Leer y eliminar mensajes del formulario de contacto.
6. Cambiar el usuario y la contraseña.
7. Editar los textos del sitio desde **Panel → Contenido del sitio**.
8. Reemplazar el PDF del CV desde **Panel → Mi CV (PDF)**.

Todos los cambios se guardan en MySQL y se reflejan de inmediato en el sitio público. El CV descargable cambia solo cuando se sube un PDF nuevo desde `/admin/cv`.

---

## Pruebas

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Resultado esperado:

```text
41 passed
```

La suite cubre:

- Render de las secciones públicas, iframe, recursos y cabeceras de seguridad.
- API JSON, descarga del CV y páginas de error.
- Login válido/inválido, redirección segura, logout y protección del panel.
- CRUD de estudios, experiencias, tecnologías, proyectos y perfil.
- Relación N:M y validaciones de formularios.
- Contacto, honeypot y validación de email/longitud.
- Modelos: hash de contraseña, encapsulamiento, polimorfismo, fechas y serialización.
- Editor de textos: guardado en MySQL, persistencia y reflejo en la página pública.
- CV: prioridad del PDF real sobre el generado y reemplazo desde el panel.

---

## Documentación

- **Documentación preliminar (PDF):** `docs/Documentacion_Preliminar_Portfolio.pdf`
  Incluye planificación, objetivos, arquitectura, modelo lógico y físico, POO, seguridad, responsive, animaciones, pruebas, despliegue, DDL completo y la **sección 2.3 con los 13 requisitos explicados como «para qué sirve» y «cómo se implementó»**.
- **Guía de despliegue:** `docs/Guia_Despliegue.md`
- **Regenerar la documentación:**

```powershell
.\.venv\Scripts\python.exe scripts\generar_documentacion.py
```

---

## Despliegue en Clever Cloud

La guía detallada está en [`docs/Guia_Despliegue.md`](docs/Guia_Despliegue.md). Resumen:

1. Crear una aplicación **Python** en Clever Cloud.
2. Agregar el add-on **MySQL**.
3. Configurar las variables de entorno:

```text
CC_PYTHON_MODULE=wsgi:app
CC_PYTHON_BACKEND=gunicorn
CC_PYTHON_VERSION=3.12
SECRET_KEY=<clave aleatoria larga>
ADMIN_USERNAME=kevinAdmin
ADMIN_PASSWORD=<contraseña segura>
SITE_URL=https://<tu-app>.cleverapps.io
SITE_NAME=Kevin | Portfolio
SEED_ON_START=1
SESSION_COOKIE_SECURE=true
```

4. Vincular el repositorio de GitHub y desplegar.
5. Verificar `https://<tu-app>.cleverapps.io/salud`.
6. Abrir el sitio, iniciar sesión y cambiar la contraseña.
7. Reemplazar los datos de ejemplo (email, teléfono, redes y URLs de proyectos).
8. Descargar el CV y verificar que refleje los datos reales.

> Clever Cloud inyecta automáticamente `MYSQL_ADDON_URI` y las variables `MYSQL_ADDON_*` al vincular el add-on. La aplicación detecta esas variables sin configuración adicional.

---

## Git y GitHub

```bash
git init
git add .
git commit -m "Proyecto integrador: portfolio full stack Flask + MySQL"
git branch -M main
git remote add origin https://github.com/USUARIO/portfolio2.git
git push -u origin main
```

El repositorio incluye `.gitignore` para excluir `.venv`, `.env`, `instance/`, cachés y archivos temporales.

> En este equipo Git no está instalado actualmente. Instalarlo desde <https://git-scm.com/download/win> y reiniciar la terminal antes de ejecutar los comandos.

---

## Seguridad

- Contraseñas con hash **scrypt** (Werkzeug); nunca se guardan en texto plano.
- **CSRF** en todos los formularios y operaciones POST (Flask-WTF).
- **Flask-Login** protege todo el blueprint `/admin` mediante `before_request`.
- Validación del servidor con WTForms (tipos, longitudes, emails, URLs, fechas y rangos).
- Consultas parametrizadas por SQLAlchemy (sin concatenar SQL).
- Autoescape de Jinja2 y escape de texto en los PDF.
- Redirección `next` validada para evitar *open redirect*.
- Mensaje genérico ante credenciales incorrectas (sin enumerar usuarios).
- Honeypot anti-spam en el formulario público.
- Cookies `HttpOnly`, `SameSite=Lax` y `Secure` configurable.
- Cabeceras `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy` y `Permissions-Policy`.
- `/admin` bloqueado en `robots.txt` y con `noindex, nofollow`.

**Checklist antes de publicar:**

- [ ] `SECRET_KEY` aleatoria y privada.
- [ ] Contraseña del administrador cambiada.
- [ ] `SESSION_COOKIE_SECURE=true` y HTTPS.
- [ ] Datos personales reales cargados.
- [ ] `SITE_URL` con el dominio final.
- [ ] `.env` fuera del repositorio.
- [ ] Base de datos con backup o plan de respaldo.

---

## Mapeo de los 13 requisitos (para qué y cómo)

| N.º | Requisito | ¿Para qué sirve? | ¿Cómo se implementó? |
| --- | --- | --- | --- |
| 1 | Contenido con Jinja2, diseño propio, usabilidad y funcionalidad | Mostrar datos reales con navegación clara | Herencia, macros y filtros en `templates/`; textos en `textos_sitio` |
| 2 | Maquetación + modelo relacional y físico MySQL | Estructurar la interfaz y la persistencia | HTML/CSS + 9 tablas InnoDB con PK/FK y DDL en `database/` |
| 3 | Diseño estético: iframe, iconos y fuentes | Identidad visual y recursos obligatorios | Mapa OpenStreetMap, FontAwesome CDN y Google Fonts |
| 4 | POO con los cuatro pilares y comentarios | Código reutilizable y explicable | `models.py`: abstracción, herencia, encapsulamiento y polimorfismo |
| 5 | Responsive mobile/tablet/escritorio | Funcionar en cualquier pantalla | Grid/flex y breakpoints `1024/820/560 px` |
| 6 | Animación o transición documentada | Interfaz viva sin distraer | `main.js` (typewriter, reveal, contadores) + CSS (`pulse`, hover) |
| 7 | Bootstrap (opcional) | Se decidió no usarlo | CSS propio con variables, sin dependencias de maquetación |
| 8 | Publicación online, Git/GitHub y MySQL en Clever Cloud | Versionar y publicar el proyecto | `Procfile`, `.env.example` y guía listos; **pendiente de credenciales** |
| 9 | Login seguro: hash + Flask-WTF | Proteger el panel | Flask-Login, scrypt, CSRF, validadores y honeypot |
| 10 | Diseño integral (alineación, márgenes, tipografía, imágenes, paleta, logo, iconos, favicon) | Coherencia visual profesional | Variables de diseño y SVG locales optimizados |
| 11 | Documentación preliminar PDF | Explicar planificación, organización, objetivo y descripción | `scripts/generar_documentacion.py` → `docs/Documentacion_Preliminar_Portfolio.pdf` |
| 12 | CV de RRHH descargable en PDF | Entregar el CV real al reclutador | `/admin/cv` sube el PDF y `/cv` lo sirve; ReportLab como respaldo |
| 13 | Defensa oral | Explicar el código y demostrar autoría | Documentación por capas, comentarios de POO, tests y esta tabla |

La tabla completa con rutas exactas está en la **sección 2.3** del PDF de documentación.

---

## Solución de problemas

**`ModuleNotFoundError` al ejecutar**
Verificar que el entorno virtual esté activo y las dependencias instaladas:
```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

**Error de conexión a MySQL**
Revisar `DATABASE_URL`, que el servidor MySQL esté iniciado y que la base exista. Para probar sin MySQL, dejar `DATABASE_URL` vacío y usar SQLite.

**`CSRF token missing`**
El formulario debe enviarse desde la página (incluye `hidden_tag()`), no con una petición manual sin token. En pruebas, `TestingConfig` desactiva CSRF.

**La contraseña inicial no funciona**
Si la base ya existía, el seed no se vuelve a ejecutar. Crear/actualizar el administrador:
```powershell
.\.venv\Scripts\flask --app wsgi create-admin --username admin
```

**El CV no refleja los cambios**
El botón sirve el PDF real de `portfolio/static/uploads/CV_Kevin_Basualdo.pdf`. Para cambiarlo, subir un nuevo PDF desde *Panel → Mi CV (PDF)*. Si no hay archivo, se genera uno con los datos de la base.

**Los textos del sitio no cambian**
Verificar que se guardaron desde *Panel → Contenido del sitio* y que las plantillas usen `textos.get('clave', 'valor por defecto')`. Para agregar claves nuevas sin borrar las editadas: `flask --app wsgi seed-textos`.

**Git no se reconoce**
Instalar Git y reiniciar la terminal. Luego verificar con `git --version`.

---

## Autor

**Kevin Basualdo** — Estudiante de carrera técnica · Programación y diseño web
Proyecto Integrador · ITR (Instituto Técnico Renault) · Noviembre de 2026

- Ubicación: Villa San Nicolás, Malagueño, Córdoba, Argentina
- Portfolio: pendiente de publicación
- GitHub: pendiente de publicar
- Contacto: `d48721257@alumnos.itr.ed.ar` · `(351) 3 29-2406`
