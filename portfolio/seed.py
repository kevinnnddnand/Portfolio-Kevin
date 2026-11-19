"""Datos iniciales del portfolio.

El seed es idempotente: si ya existe un perfil no vuelve a crear contenido.
Se ejecuta automáticamente en desarrollo (`SEED_ON_START=1`) o mediante
`flask seed-db`. Los textos del sitio se cargan aparte con `seed_textos()`
para que una base existente también reciba las claves nuevas.
"""
from __future__ import annotations

from datetime import date

from .extensions import db
from .models import (
    Estudio,
    Experiencia,
    Perfil,
    Proyecto,
    Tecnologia,
    TextoSitio,
    Usuario,
)

UBICACION = "Villa San Nicolás, Malagueño, Córdoba, Argentina"

# (sección, clave, etiqueta para el panel, valor inicial)
# La clave es la que usa Jinja2: textos.get('clave', 'valor por defecto').
TEXTOS_INICIALES: list[tuple[str, str, str, str]] = [
    ("General", "sitio.marca", "Marca del sitio", "kevin.dev"),
    ("General", "sitio.descripcion", "Descripción para buscadores",
     "Portfolio de Kevin Basualdo: programación, diseño web y contenido digital con Python, Flask y MySQL."),
    ("General", "sitio.og_descripcion", "Descripción para redes sociales",
     "Portfolio full stack con Python, Flask y MySQL."),
    ("General", "sitio.pie_descripcion", "Texto del pie de página",
     "Construyendo experiencias web con código limpio, datos bien modelados y atención al detalle."),
    ("General", "sitio.copyright_nombre", "Nombre en el copyright", "Kevin Basualdo"),
    ("General", "sitio.estado", "Estado en el pie", "Disponible para proyectos"),
    ("General", "sitio.hecho_con", "Tecnologías del pie", "Flask y MySQL"),
    ("General", "sitio.saltar", "Enlace saltar al contenido", "Saltar al contenido principal"),
    ("Navegación", "nav.sobre_mi", "Menú: Sobre mí", "Sobre mí"),
    ("Navegación", "nav.estudios", "Menú: Estudios", "Estudios"),
    ("Navegación", "nav.experiencia", "Menú: Experiencia", "Experiencia"),
    ("Navegación", "nav.tecnologias", "Menú: Tecnologías", "Tecnologías"),
    ("Navegación", "nav.proyectos", "Menú: Proyectos", "Proyectos"),
    ("Navegación", "nav.contacto", "Menú: Contacto", "Contacto"),
    ("Navegación", "nav.cv", "Menú: CV", "CV"),
    ("Navegación", "nav.acceso", "Menú: Acceso", "Acceso"),
    ("Navegación", "footer.navegacion", "Pie: título Navegación", "Navegación"),
    ("Navegación", "footer.stack", "Pie: título Stack", "Stack"),
    ("Navegación", "footer.stack_1", "Pie: Stack línea 1", "Python · Flask"),
    ("Navegación", "footer.stack_2", "Pie: Stack línea 2", "HTML · CSS"),
    ("Navegación", "footer.stack_3", "Pie: Stack línea 3", "JavaScript · MySQL"),
    ("Navegación", "footer.stack_4", "Pie: Stack línea 4", "Git"),
    ("Navegación", "footer.estado", "Pie: título Estado", "Estado"),
    ("Navegación", "footer.derechos", "Pie: derechos", "Todos los derechos reservados."),
    ("Hero", "hero.saludo", "Saludo del hero", "Hola, soy"),
    ("Hero", "hero.chip_python", "Chip Python", "Python"),
    ("Hero", "hero.chip_flask", "Chip Flask", "Flask"),
    ("Hero", "hero.chip_mysql", "Chip MySQL", "MySQL"),
    ("Hero", "hero.scroll", "Indicador Scroll", "Scroll"),
    ("Hero", "hero.rol_2", "Rol animado 2", "Python & Flask"),
    ("Hero", "hero.rol_3", "Rol animado 3", "Backend + MySQL"),
    ("Hero", "hero.rol_4", "Rol animado 4", "Diseño con detalle"),
    ("Hero", "hero.descripcion_extra", "Texto extra bajo el subtítulo",
     "Convierto ideas en aplicaciones web funcionales, cuidando el modelo de datos, la experiencia de uso y cada detalle del código."),
    ("Hero", "hero.stat_proyectos", "Etiqueta estadística proyectos", "Proyectos"),
    ("Hero", "hero.stat_tecnologias", "Etiqueta estadística tecnologías", "Tecnologías"),
    ("Hero", "hero.stat_formaciones", "Etiqueta estadística formaciones", "Formaciones"),
    ("Botones", "boton.ver_proyectos", "Botón Ver proyectos", "Ver proyectos"),
    ("Botones", "boton.descargar_cv", "Botón Descargar CV", "Descargar CV"),
    ("Botones", "boton.descargar_cv_largo", "Botón Descargar CV (contacto)", "Descargar CV en PDF"),
    ("Sobre mí", "sobre.kicker", "Sobre mí: kicker", "01 — Sobre mí"),
    ("Sobre mí", "sobre.titulo_1", "Sobre mí: título", "Código con criterio,"),
    ("Sobre mí", "sobre.titulo_2", "Sobre mí: título destacado", "interfaces con intención."),
    ("Sobre mí", "sobre.texto_extra", "Sobre mí: segundo párrafo",
     "Me interesa especialmente la intersección entre el backend y los datos: diseñar tablas coherentes, escribir APIs claras y construir pantallas que hagan simple lo complejo. Aprendo haciendo y documentando cada decisión."),
    ("Sobre mí", "sobre.etiqueta_ubicacion", "Etiqueta Ubicación", "Ubicación"),
    ("Sobre mí", "sobre.etiqueta_email", "Etiqueta Email", "Email"),
    ("Sobre mí", "sobre.etiqueta_disponibilidad", "Etiqueta Disponibilidad", "Disponibilidad"),
    ("Sobre mí", "sobre.foco_backend_titulo", "Tarjeta Backend: título", "Backend"),
    ("Sobre mí", "sobre.foco_backend_texto", "Tarjeta Backend: texto",
     "APIs REST con Flask, autenticación, formularios seguros y lógica de negocio ordenada."),
    ("Sobre mí", "sobre.foco_datos_titulo", "Tarjeta Datos: título", "Datos"),
    ("Sobre mí", "sobre.foco_datos_texto", "Tarjeta Datos: texto",
     "Modelado relacional en MySQL, consultas eficientes y persistencia con SQLAlchemy."),
    ("Sobre mí", "sobre.foco_interfaz_titulo", "Tarjeta Interfaz: título", "Interfaz"),
    ("Sobre mí", "sobre.foco_interfaz_texto", "Tarjeta Interfaz: texto",
     "Jinja2, HTML semántico, CSS responsive y animaciones que acompañan sin distraer."),
    ("Estudios", "estudios.kicker", "Estudios: kicker", "02 — Formación"),
    ("Estudios", "estudios.titulo", "Estudios: título", "Estudios"),
    ("Estudios", "estudios.titulo_acento", "Estudios: palabra destacada", "cursados"),
    ("Estudios", "estudios.nota", "Estudios: nota",
     "La base técnica detrás de cada proyecto: formación formal, cursos y práctica constante."),
    ("Estudios", "estudios.vacio", "Estudios: sin datos", "Todavía no hay estudios cargados."),
    ("Estudios", "estudios.en_curso", "Estudios: badge En curso", "En curso"),
    ("Experiencia", "experiencia.kicker", "Experiencia: kicker", "03 — Trayectoria"),
    ("Experiencia", "experiencia.titulo", "Experiencia: título", "Experiencia"),
    ("Experiencia", "experiencia.titulo_acento", "Experiencia: palabra destacada", "laboral"),
    ("Experiencia", "experiencia.nota", "Experiencia: nota",
     "Trabajo real, problemas reales y aprendizajes que se traducen en mejores soluciones."),
    ("Experiencia", "experiencia.vacio", "Experiencia: sin datos", "Todavía no hay experiencia cargada."),
    ("Experiencia", "experiencia.actual", "Experiencia: badge Actual", "Actual"),
    ("Tecnologías", "tecnologias.kicker", "Tecnologías: kicker", "04 — Stack"),
    ("Tecnologías", "tecnologias.titulo", "Tecnologías: título", "Tecnologías que"),
    ("Tecnologías", "tecnologias.titulo_acento", "Tecnologías: palabra destacada", "uso"),
    ("Tecnologías", "tecnologias.nota", "Tecnologías: nota",
     "Herramientas con las que construyo, medido en nivel de dominio y experiencia práctica."),
    ("Tecnologías", "tecnologias.vacio", "Tecnologías: sin datos", "Todavía no hay tecnologías cargadas."),
    ("Tecnologías", "tecnologias.herramienta", "Singular herramienta", "herramienta"),
    ("Tecnologías", "tecnologias.herramientas", "Plural herramientas", "herramientas"),
    ("Proyectos", "proyectos.kicker", "Proyectos: kicker", "05 — Portfolio"),
    ("Proyectos", "proyectos.titulo", "Proyectos: título", "Proyectos"),
    ("Proyectos", "proyectos.titulo_acento", "Proyectos: palabra destacada", "destacados"),
    ("Proyectos", "proyectos.nota", "Proyectos: nota",
     "Una selección de trabajos donde aplico el stack completo, del modelo de datos a la interfaz."),
    ("Proyectos", "proyectos.vacio", "Proyectos: sin datos", "Todavía no hay proyectos cargados."),
    ("Proyectos", "proyectos.destacado", "Etiqueta Destacado", "Destacado"),
    ("Proyectos", "proyectos.repositorio", "Enlace Repositorio", "Repositorio"),
    ("Proyectos", "proyectos.demo", "Enlace Demo", "Demo"),
    ("Proyectos", "proyectos.academico", "Proyecto sin enlaces", "Proyecto académico"),
    ("Ubicación", "mapa.kicker", "Mapa: kicker", "Ubicación"),
    ("Ubicación", "mapa.titulo_1", "Mapa: título", "Desde Villa San Nicolás,"),
    ("Ubicación", "mapa.titulo_2", "Mapa: título destacado", "Córdoba, para el mundo."),
    ("Ubicación", "mapa.texto", "Mapa: párrafo",
     "Desde Villa San Nicolás, a minutos de Carlos Paz, trabajo de forma remota con equipos y clientes de cualquier lugar. La distancia no es un límite cuando la comunicación y los procesos son claros."),
    ("Ubicación", "mapa.dato_1", "Mapa: dato 1", "UTC−3 · Argentina"),
    ("Ubicación", "mapa.dato_2", "Mapa: dato 2", "Respuesta en menos de 24 h"),
    ("Ubicación", "mapa.dato_3", "Mapa: dato 3", "Español · Inglés técnico"),
    ("Ubicación", "mapa.titulo_iframe", "Mapa: título del iframe",
     "Mapa de Villa San Nicolás, Malagueño, Córdoba, Argentina"),
    ("Ubicación", "mapa.bbox", "Mapa: bbox (lat/lon separados por coma)",
     "-64.50,-31.47,-64.41,-31.40"),
    ("Ubicación", "mapa.marker", "Mapa: marcador lat,lon", "-31.4365,-64.4538"),
    ("Ubicación", "mapa.badge_titulo", "Mapa: badge título", "Villa San Nicolás"),
    ("Ubicación", "mapa.badge_subtitulo", "Mapa: badge subtítulo", "Malagueño, Córdoba"),
    ("Contacto", "contacto.kicker", "Contacto: kicker", "06 — Contacto"),
    ("Contacto", "contacto.titulo_1", "Contacto: título", "¿Tenés una idea?"),
    ("Contacto", "contacto.titulo_2", "Contacto: título destacado", "Hagámosla realidad."),
    ("Contacto", "contacto.texto", "Contacto: párrafo",
     "Estoy abierto a oportunidades laborales, proyectos freelance y colaboraciones. Contame qué necesitás y te respondo con una propuesta clara."),
    ("Contacto", "contacto.etiqueta_email", "Contacto: etiqueta email", "Escribime"),
    ("Contacto", "contacto.etiqueta_telefono", "Contacto: etiqueta teléfono", "Teléfono"),
    ("Contacto", "contacto.form_titulo", "Formulario: título", "Mandame un mensaje"),
    ("Contacto", "contacto.form_seguro", "Formulario: etiqueta seguridad", "Formulario protegido"),
    ("Contacto", "contacto.form_nota", "Formulario: nota", "Tus datos solo se usan para responder tu mensaje."),
    ("Contacto", "form.nombre", "Formulario: etiqueta Nombre", "Nombre"),
    ("Contacto", "form.nombre_placeholder", "Formulario: placeholder Nombre", "Tu nombre"),
    ("Contacto", "form.email", "Formulario: etiqueta Email", "Email"),
    ("Contacto", "form.asunto", "Formulario: etiqueta Asunto", "Asunto"),
    ("Contacto", "form.asunto_placeholder", "Formulario: placeholder Asunto", "Propuesta, consulta, colaboración..."),
    ("Contacto", "form.mensaje", "Formulario: etiqueta Mensaje", "Mensaje"),
    ("Contacto", "form.mensaje_placeholder", "Formulario: placeholder Mensaje", "Contame un poco más..."),
    ("Contacto", "form.enviar", "Formulario: botón Enviar", "Enviar mensaje"),
]


def crear_admin(username: str, password: str, nombre: str = "Administrador") -> Usuario:
    """Crea (o actualiza la clave de) la cuenta administradora."""
    usuario = Usuario.query.filter_by(username=username.strip().lower()).first()
    if usuario is None:
        usuario = Usuario(username=username.strip().lower(), nombre=nombre)
        db.session.add(usuario)
    usuario.nombre = nombre
    usuario.activo = True
    usuario.set_password(password)
    db.session.commit()
    return usuario


def seed_textos() -> int:
    """Agrega las claves de texto que falten sin sobrescribir las editadas.

    Devuelve la cantidad de filas insertadas. Es seguro llamarla en cada arranque:
    los cambios que el administrador hizo desde /admin/contenido se conservan.
    """
    existentes = {fila.clave for fila in TextoSitio.query.all()}
    insertados = 0
    for seccion, clave, etiqueta, valor in TEXTOS_INICIALES:
        if clave in existentes:
            continue
        db.session.add(TextoSitio(
            clave=clave, etiqueta=etiqueta, valor=valor,
            orden=insertados + 1, seccion=seccion,
        ))
        insertados += 1
    if insertados:
        db.session.commit()
    return insertados


def _seed_tecnologias() -> dict[str, Tecnologia]:
    datos = [
        ("Python", "Backend", 82, "fa-brands fa-python", "#3776ab"),
        ("Flask", "Backend", 78, "fa-solid fa-flask", "#0f766e"),
        ("HTML5", "Frontend", 86, "fa-brands fa-html5", "#e34f26"),
        ("CSS3", "Frontend", 82, "fa-brands fa-css3-alt", "#1572b6"),
        ("JavaScript", "Frontend", 70, "fa-brands fa-js", "#b58900"),
        ("MySQL", "Base de datos", 74, "fa-solid fa-database", "#00758f"),
        ("Git", "Herramientas", 68, "fa-brands fa-git-alt", "#f05032"),
        ("Diseño web", "Otros", 88, "fa-solid fa-pen-ruler", "#8b5cf6"),
        ("Redes sociales", "Otros", 80, "fa-solid fa-share-nodes", "#e1306c"),
    ]
    tecnologias: dict[str, Tecnologia] = {}
    for orden, (nombre, categoria, nivel, icono, color) in enumerate(datos, start=1):
        tecnologia = Tecnologia(
            nombre=nombre,
            categoria=categoria,
            nivel=nivel,
            icono=icono,
            color=color,
            orden=orden,
            activo=True,
        )
        db.session.add(tecnologia)
        tecnologias[nombre] = tecnologia
    db.session.flush()
    return tecnologias


def seed_database(admin_username: str, admin_password: str, admin_nombre: str = "Kevin") -> bool:
    """Crea el contenido inicial si la base está vacía.

    Devuelve True cuando insertó datos y False si ya existía un perfil.
    Los datos son los del CV de Kevin Basualdo (RRHH).
    """
    if Perfil.query.first() is not None:
        seed_textos()
        return False

    admin = Usuario.query.filter_by(username=admin_username.strip().lower()).first()
    if admin is None:
        admin = Usuario(username=admin_username.strip().lower(), nombre=admin_nombre)
        db.session.add(admin)
        admin.set_password(admin_password)
    db.session.flush()

    perfil = Perfil(
        usuario_id=admin.id,
        nombre="Kevin",
        apellido="Basualdo",
        titulo="Estudiante de carrera técnica · Programación y diseño web",
        subtitulo="Python · Flask · MySQL · Diseño web · Contenido digital",
        bio=(
            "Soy estudiante de una carrera técnica, apasionado por la programación "
            "y con un perfil creativo. Me encantan deportes como el voleibol y el "
            "baloncesto; además, me interesa el diseño de videojuegos y otros "
            "elementos, como logotipos. Trabajo en diseño web, gestión de redes "
            "sociales, diseño de aplicaciones, creación de contenido y definición "
            "de estrategias."
        ),
        ubicacion=UBICACION,
        disponibilidad="Disponible para proyectos de diseño web y desarrollo",
        cv_resumen=(
            "Estudiante de una carrera técnica, apasionado por la programación y "
            "con un perfil creativo. Diseño web, gestión de redes sociales, diseño "
            "de aplicaciones, creación de contenido y definición de estrategias. "
            "Español nativo, inglés B1 y japonés iniciante."
        ),
        avatar_url="img/avatar.svg",
    )
    perfil.email = "d48721257@alumnos.itr.ed.ar"
    perfil.telefono = "(351) 3 29-2406"
    perfil.linkedin = ""
    perfil.github = ""
    perfil.sitio_web = ""
    db.session.add(perfil)

    estudios = [
        Estudio(
            institucion="ITR — Instituto Técnico Renault",
            titulo="Carrera técnica (ITR)",
            area="Programación y diseño",
            nivel="Terciario",
            fecha_inicio=date(2023, 3, 1),
            en_curso=True,
            descripcion=(
                "Formación técnica en curso: diseño web, diseño de aplicaciones, "
                "gestión de redes sociales, creación de contenido y definición de estrategias."
            ),
            orden=1,
        ),
        Estudio(
            institucion="IEC — Instituto de Educación Córdoba",
            titulo="Secundario",
            area="Formación general",
            nivel="Secundario",
            fecha_inicio=date(2021, 3, 1),
            fecha_fin=date(2023, 12, 1),
            descripcion="Estudios secundarios completados en el IEC (2021-2023).",
            orden=2,
        ),
    ]
    db.session.add_all(estudios)

    experiencias = [
        Experiencia(
            empresa="Portones Automáticos",
            puesto="Reparador de puertas",
            ubicacion=UBICACION,
            modalidad="Presencial",
            fecha_inicio=date(2025, 1, 1),
            actual=True,
            descripcion="Reparación y mantenimiento de puertas y portones automáticos (2025-2026).",
            orden=1,
        ),
        Experiencia(
            empresa="Portones Automáticos",
            puesto="Diseñador web",
            ubicacion=UBICACION,
            modalidad="Remoto",
            fecha_inicio=date(2026, 1, 1),
            actual=True,
            descripcion=(
                "Diseño web para la empresa, combinado con la reparación de portones "
                "automáticos."
            ),
            logros=(
                "Diseño web.\n"
                "Gestión de redes sociales.\n"
                "Diseño de aplicaciones.\n"
                "Creación de contenido.\n"
                "Definición de estrategia."
            ),
            orden=2,
        ),
    ]
    db.session.add_all(experiencias)

    tecnologias = _seed_tecnologias()

    proyectos = [
        Proyecto(
            titulo="Portfolio Web Full Stack",
            descripcion=(
                "Sitio personal administrable: perfil, formación, experiencia, "
                "tecnologías y proyectos se editan desde un panel protegido y se "
                "guardan en MySQL. Incluye CV descargable y diseño responsive."
            ),
            repo_url="",
            demo_url="",
            imagen_url="img/proyecto-portfolio.svg",
            destacado=True,
            orden=1,
            tecnologias=[
                tecnologias["Python"], tecnologias["Flask"],
                tecnologias["MySQL"], tecnologias["HTML5"],
                tecnologias["CSS3"], tecnologias["Diseño web"],
            ],
        ),
        Proyecto(
            titulo="Sitio web para Portones Automáticos",
            descripcion=(
                "Diseño web para una empresa local de portones automáticos: "
                "presentación de servicios, contenido para redes sociales y "
                "estrategia digital."
            ),
            repo_url="",
            demo_url="",
            imagen_url="img/proyecto-tareas.svg",
            destacado=True,
            orden=2,
            tecnologias=[
                tecnologias["HTML5"], tecnologias["CSS3"],
                tecnologias["Diseño web"], tecnologias["Redes sociales"],
            ],
        ),
        Proyecto(
            titulo="Contenido y piezas gráficas",
            descripcion=(
                "Creación de contenido, logotipos y dibujos hiperrealistas. "
                "Interés por el diseño de videojuegos y otros elementos visuales."
            ),
            repo_url="",
            demo_url="",
            imagen_url="img/proyecto-ventas.svg",
            destacado=False,
            orden=3,
            tecnologias=[
                tecnologias["Diseño web"], tecnologias["Redes sociales"],
                tecnologias["JavaScript"],
            ],
        ),
    ]
    db.session.add_all(proyectos)
    db.session.commit()
    seed_textos()
    return True


def seed_inicial(config) -> bool:
    """Helper usado por la app y por la CLI."""
    creado = seed_database(
        admin_username=config.get("ADMIN_USERNAME", "kevinAdmin"),
        admin_password=config.get("ADMIN_PASSWORD", "kevin1504"),
        admin_nombre=config.get("ADMIN_NOMBRE", "Kevin"),
    )
    # Aunque ya exista el perfil, nos aseguramos de que estén las claves nuevas.
    seed_textos()
    return creado
