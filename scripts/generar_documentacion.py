"""Genera la documentación preliminar del proyecto en PDF.

Uso:
    .\\.venv\\Scripts\\python.exe scripts/generar_documentacion.py

El PDF se guarda en docs/Documentacion_Preliminar_Portfolio.pdf.
Requiere ReportLab (ya incluido en requirements.txt).
"""
from __future__ import annotations

from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    HRFlowable,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    Preformatted,
    Spacer,
    Table,
    TableStyle,
)

BASE_DIR = Path(__file__).resolve().parent.parent
SALIDA = BASE_DIR / "docs" / "Documentacion_Preliminar_Portfolio.pdf"
ESQUEMA = BASE_DIR / "database" / "schema_mysql.sql"

AZUL = colors.HexColor("#0b1220")
AZUL_2 = colors.HexColor("#17263d")
ACENTO = colors.HexColor("#0f9b8e")
ACENTO_CLARO = colors.HexColor("#e3f7f4")
GRIS = colors.HexColor("#5b6779")
GRIS_CLARO = colors.HexColor("#eef2f6")
BORDE = colors.HexColor("#d4dde7")
BLANCO = colors.white

ANCHO_UTIL = A4[0] - 36 * mm


def _estilos() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "portada_kicker": ParagraphStyle(
            "portada_kicker", parent=base["Normal"], fontName="Helvetica-Bold",
            fontSize=11, leading=15, textColor=ACENTO, alignment=TA_CENTER,
            spaceAfter=10, letterSpacing=2,
        ),
        "portada_titulo": ParagraphStyle(
            "portada_titulo", parent=base["Title"], fontName="Helvetica-Bold",
            fontSize=34, leading=40, textColor=AZUL, alignment=TA_CENTER,
            spaceAfter=8,
        ),
        "portada_sub": ParagraphStyle(
            "portada_sub", parent=base["Normal"], fontName="Helvetica",
            fontSize=15, leading=22, textColor=GRIS, alignment=TA_CENTER,
        ),
        "portada_dato": ParagraphStyle(
            "portada_dato", parent=base["Normal"], fontName="Helvetica",
            fontSize=10.5, leading=17, textColor=AZUL_2, alignment=TA_CENTER,
        ),
        "h1": ParagraphStyle(
            "h1", parent=base["Heading1"], fontName="Helvetica-Bold",
            fontSize=18, leading=23, textColor=AZUL, spaceBefore=4, spaceAfter=8,
        ),
        "h2": ParagraphStyle(
            "h2", parent=base["Heading2"], fontName="Helvetica-Bold",
            fontSize=12.5, leading=17, textColor=ACENTO, spaceBefore=14,
            spaceAfter=5,
        ),
        "h3": ParagraphStyle(
            "h3", parent=base["Heading3"], fontName="Helvetica-Bold",
            fontSize=10.5, leading=14, textColor=AZUL_2, spaceBefore=9,
            spaceAfter=3,
        ),
        "cuerpo": ParagraphStyle(
            "cuerpo", parent=base["BodyText"], fontName="Helvetica",
            fontSize=9.6, leading=14.6, textColor=colors.HexColor("#26313f"),
            alignment=TA_JUSTIFY, spaceAfter=6,
        ),
        "vineta": ParagraphStyle(
            "vineta", parent=base["BodyText"], fontName="Helvetica",
            fontSize=9.5, leading=14, textColor=colors.HexColor("#26313f"),
            leftIndent=12, bulletIndent=2, spaceAfter=2.5,
        ),
        "nota": ParagraphStyle(
            "nota", parent=base["BodyText"], fontName="Helvetica-Oblique",
            fontSize=8.8, leading=12.5, textColor=GRIS, spaceAfter=5,
        ),
        "celda": ParagraphStyle(
            "celda", parent=base["Normal"], fontName="Helvetica",
            fontSize=8.3, leading=11.4, textColor=colors.HexColor("#26313f"),
        ),
        "celda_bold": ParagraphStyle(
            "celda_bold", parent=base["Normal"], fontName="Helvetica-Bold",
            fontSize=8.3, leading=11.4, textColor=AZUL,
        ),
        "cabecera": ParagraphStyle(
            "cabecera", parent=base["Normal"], fontName="Helvetica-Bold",
            fontSize=8.4, leading=11, textColor=BLANCO,
        ),
        "codigo": ParagraphStyle(
            "codigo", parent=base["Code"], fontName="Courier",
            fontSize=7.4, leading=9.6, textColor=colors.HexColor("#1d2b3a"),
            backColor=colors.HexColor("#f4f7fa"), borderColor=BORDE,
            borderWidth=0.5, borderPadding=6, spaceBefore=4, spaceAfter=8,
        ),
        "ddl": ParagraphStyle(
            "ddl", parent=base["Code"], fontName="Courier",
            fontSize=6.2, leading=7.9, textColor=colors.HexColor("#1d2b3a"),
            backColor=colors.HexColor("#f7f9fb"), borderColor=BORDE,
            borderWidth=0.4, borderPadding=5,
        ),
    }


def _tabla(datos, anchos, st, ancho_total=ANCHO_UTIL) -> Table:
    """Construye una tabla con encabezado repetido y estilos uniformes."""
    filas = []
    for indice, fila in enumerate(datos):
        estilo = st["cabecera"] if indice == 0 else st["celda"]
        filas.append([Paragraph(str(c), estilo) for c in fila])
    tabla = Table(filas, colWidths=anchos, repeatRows=1, hAlign="LEFT")
    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), AZUL_2),
        ("TEXTCOLOR", (0, 0), (-1, 0), BLANCO),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.4, BORDE),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [BLANCO, GRIS_CLARO]),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 3.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
    ]))
    return tabla


def _vinetas(elementos: list[str], st) -> list[Paragraph]:
    return [Paragraph(escape(texto), st["vineta"], bulletText="•") for texto in elementos]


def _caja(texto: str, st, color_fondo=ACENTO_CLARO) -> Table:
    parrafo = Paragraph(texto, st["cuerpo"])
    caja = Table([[parrafo]], colWidths=[ANCHO_UTIL])
    caja.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), color_fondo),
        ("BOX", (0, 0), (-1, -1), 0.6, ACENTO),
        ("LEFTPADDING", (0, 0), (-1, -1), 9),
        ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    return caja


def _portada(canvas, doc):
    """Fondo y detalles gráficos de la portada."""
    canvas.saveState()
    ancho, alto = A4
    canvas.setFillColor(colors.HexColor("#070c14"))
    canvas.rect(0, 0, ancho, alto, stroke=0, fill=1)

    canvas.setFillColor(ACENTO)
    canvas.circle(ancho - 30 * mm, alto - 30 * mm, 38 * mm, stroke=0, fill=1)
    canvas.setFillColor(colors.HexColor("#7c9cff"))
    canvas.circle(18 * mm, 35 * mm, 26 * mm, stroke=0, fill=1)

    canvas.setFillColor(colors.HexColor("#0e1828"))
    canvas.roundRect(18 * mm, 78 * mm, ancho - 36 * mm, alto - 132 * mm, 9 * mm, stroke=0, fill=1)
    canvas.setStrokeColor(colors.HexColor("#38e0c8"))
    canvas.setLineWidth(1)
    canvas.roundRect(18 * mm, 78 * mm, ancho - 36 * mm, alto - 132 * mm, 9 * mm, stroke=1, fill=0)

    canvas.setFillColor(colors.HexColor("#eaf0f8"))
    canvas.setFont("Helvetica-Bold", 9)
    canvas.drawString(24 * mm, 22 * mm, "Proyecto Integrador · Desarrollo Full Stack")
    canvas.setFillColor(colors.HexColor("#93a4ba"))
    canvas.setFont("Helvetica", 8)
    canvas.drawRightString(ancho - 24 * mm, 22 * mm, "Documentación preliminar")
    canvas.restoreState()


def _pie(canvas, doc):
    """Pie de página de las páginas de contenido."""
    canvas.saveState()
    ancho, _ = A4
    canvas.setStrokeColor(BORDE)
    canvas.setLineWidth(0.5)
    canvas.line(18 * mm, 15 * mm, ancho - 18 * mm, 15 * mm)
    canvas.setFont("Helvetica", 7.2)
    canvas.setFillColor(GRIS)
    canvas.drawString(18 * mm, 10.5 * mm, "Portfolio Web Full Stack · Kevin")
    canvas.drawRightString(ancho - 18 * mm, 10.5 * mm, f"Página {doc.page}")
    canvas.restoreState()


def _ddl() -> str:
    if not ESQUEMA.exists():
        return "-- No se encontró database/schema_mysql.sql"
    return ESQUEMA.read_text(encoding="utf-8")


def construir_documento() -> None:
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    st = _estilos()

    doc = BaseDocTemplate(
        str(SALIDA),
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=20 * mm,
        title="Documentación preliminar — Portfolio Web Full Stack",
        author="Kevin",
        subject="Proyecto Integrador de Desarrollo Full Stack",
        creator="ReportLab",
    )
    marco_portada = Frame(18 * mm, 20 * mm, ANCHO_UTIL, A4[1] - 40 * mm, id="portada")
    marco_contenido = Frame(
        18 * mm, 20 * mm, ANCHO_UTIL, A4[1] - 38 * mm, id="contenido"
    )
    doc.addPageTemplates([
        PageTemplate(id="Portada", frames=[marco_portada], onPage=_portada),
        PageTemplate(id="Contenido", frames=[marco_contenido], onPage=_pie),
    ])

    h: list = []

    # =====================================================================
    # PORTADA
    # =====================================================================
    h += [Spacer(1, 42 * mm)]
    h.append(Paragraph("PROYECTO INTEGRADOR", st["portada_kicker"]))
    h.append(Paragraph("Portfolio Web<br/>Full Stack", st["portada_titulo"]))
    h.append(Spacer(1, 6))
    h.append(HRFlowable(width="38%", thickness=2, color=ACENTO, hAlign="CENTER"))
    h.append(Spacer(1, 12))
    h.append(Paragraph("Documentación preliminar del proyecto", st["portada_sub"]))
    h.append(Spacer(1, 32))
    h.append(Paragraph("Alumno: <b>Kevin</b>", st["portada_dato"]))
    h.append(Paragraph("Tecnicatura Superior en Desarrollo de Software", st["portada_dato"]))
    h.append(Paragraph("Python · Flask · MySQL · Jinja2 · POO", st["portada_dato"]))
    h.append(Spacer(1, 46))
    h.append(Paragraph("Noviembre de 2026", st["portada_dato"]))
    h.append(Paragraph("Versión 1.0", st["portada_dato"]))
    h.append(NextPageTemplate("Contenido"))
    h.append(PageBreak())

    # =====================================================================
    # ÍNDICE
    # =====================================================================
    h.append(Paragraph("Contenido", st["h1"]))
    h.append(HRFlowable(width="100%", thickness=1, color=ACENTO, spaceAfter=10))
    indice = [
        ("1.", "Introducción y objetivos"),
        ("2.", "Alcance y requisitos"),
        ("3.", "Tecnologías utilizadas"),
        ("4.", "Arquitectura de la aplicación"),
        ("5.", "Modelo de datos: diseño lógico y físico"),
        ("6.", "Programación Orientada a Objetos"),
        ("7.", "Seguridad y autenticación"),
        ("8.", "Diseño frontend y responsive"),
        ("9.", "Animaciones y transiciones"),
        ("10.", "Pruebas y aseguramiento de calidad"),
        ("11.", "Despliegue local y en Clever Cloud"),
        ("12.", "Manual de uso del portfolio y del panel"),
        ("13.", "Estado del proyecto y checklist de requisitos"),
        ("14.", "Conclusiones y mejoras futuras"),
        ("A.", "Anexo A — Diseño físico completo (DDL MySQL)"),
    ]
    numero = ParagraphStyle(
        "numero_indice", parent=st["celda"], fontName="Helvetica-Bold",
        fontSize=9.6, textColor=ACENTO,
    )
    titulo_indice = ParagraphStyle(
        "titulo_indice", parent=st["celda"], fontName="Helvetica",
        fontSize=9.6, textColor=colors.HexColor("#26313f"),
    )
    filas_indice = [
        [Paragraph(n, numero), Paragraph(escape(t), titulo_indice)]
        for n, t in indice
    ]
    tabla_indice = Table(filas_indice, colWidths=[14 * mm, ANCHO_UTIL - 14 * mm])
    tabla_indice.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LINEBELOW", (0, 0), (-1, -1), 0.3, BORDE),
    ]))
    h.append(tabla_indice)
    h.append(Spacer(1, 14))
    h.append(_caja(
        "<b>Resumen ejecutivo.</b> El proyecto consiste en un portfolio personal "
        "full stack que presenta datos personales, formación, experiencia, "
        "tecnologías y proyectos. Incluye un panel privado con autenticación para "
        "editar todo el contenido, una base de datos relacional MySQL, un CV que se "
        "genera dinámicamente en PDF y una interfaz responsive con animaciones. La "
        "aplicación se construyó con Python, Flask, Jinja2, SQLAlchemy y MySQL, "
        "aplicando los cuatro pilares de la Programación Orientada a Objetos.",
        st,
    ))
    h.append(PageBreak())

    # =====================================================================
    # 1. INTRODUCCIÓN
    # =====================================================================
    h.append(Paragraph("1. Introducción y objetivos", st["h1"]))
    h.append(HRFlowable(width="100%", thickness=1, color=ACENTO, spaceAfter=8))
    h.append(Paragraph(
        "Este documento describe la planificación, el diseño y la implementación del "
        "Proyecto Integrador: un portfolio web full stack que funciona como sitio "
        "personal y como aplicación administrable. El objetivo es demostrar el dominio "
        "de las tecnologías vistas en la carrera mediante un producto real, publicado "
        "y mantenible, y no solamente una maqueta estática.",
        st["cuerpo"],
    ))
    h.append(Paragraph("1.1. Objetivo general", st["h2"]))
    h.append(Paragraph(
        "Desarrollar y documentar una aplicación web full stack con Python y Flask que "
        "permita mostrar el perfil profesional del autor, administrar su contenido desde "
        "un panel privado y persistir la información en una base de datos MySQL, con una "
        "interfaz responsive, accesible y animada.",
        st["cuerpo"],
    ))
    h.append(Paragraph("1.2. Objetivos específicos", st["h2"]))
    h.extend(_vinetas([
        "Implementar el backend con Flask y el patrón application factory junto con blueprints.",
        "Modelar la información en MySQL con integridad referencial y una relación muchos a muchos entre proyectos y tecnologías.",
        "Aplicar los cuatro pilares de la POO: abstracción, herencia, encapsulamiento y polimorfismo.",
        "Proteger el panel de administración con Flask-Login, contraseñas hasheadas y Flask-WTF (CSRF y validación).",
        "Construir una interfaz responsive con Jinja2, CSS moderno y JavaScript, con animaciones documentadas.",
        "Generar el CV en PDF a partir de los datos actuales de la base.",
        "Incorporar recursos requeridos: iframe, iconos, tipografías, favicon, logo y contenido extra.",
        "Versionar el código con Git/GitHub y publicar la aplicación en un hosting con MySQL.",
    ], st))
    h.append(Paragraph("1.3. Público destinatario", st["h2"]))
    h.append(Paragraph(
        "El sitio está pensado para reclutadores, docentes, clientes potenciales y "
        "colegas del sector. El panel privado está destinado únicamente al autor, "
        "quien mantiene actualizado el contenido sin necesidad de modificar el código.",
        st["cuerpo"],
    ))

    # =====================================================================
    # 2. ALCANCE Y REQUISITOS
    # =====================================================================
    h.append(Paragraph("2. Alcance y requisitos", st["h1"]))
    h.append(HRFlowable(width="100%", thickness=1, color=ACENTO, spaceAfter=8))
    h.append(Paragraph(
        "La siguiente matriz vincula cada requisito del enunciado con la solución "
        "implementada y el archivo donde puede verificarse. Es la sección recomendada "
        "para la defensa oral del proyecto.",
        st["cuerpo"],
    ))
    requisitos = [
        ["Requisito", "Implementación", "Dónde verificarlo"],
        ["Datos personales, estudios, experiencia, tecnologías y contenido extra",
         "Secciones públicas alimentadas desde MySQL; incluye proyectos, mapa y contacto",
         "templates/index.html; routes/public.py"],
        ["Backend en Python con Flask",
         "Application factory, blueprints y capa de servicios/rutas",
         "portfolio/__init__.py; portfolio/routes/"],
        ["Frontend con Jinja2",
         "Plantillas con herencia, macros, filtros y bucles sobre datos reales",
         "portfolio/templates/"],
        ["Base de datos MySQL en Clever Cloud",
         "SQLAlchemy + PyMySQL; URI por variables de entorno; DDL MySQL incluido",
         "config.py; database/schema_mysql.sql"],
        ["Login con usuario y contraseña",
         "Flask-Login, sesión persistente opcional y cierre de sesión",
         "routes/auth.py; templates/auth/login.html"],
        ["Contraseña hasheada y Flask-WTF",
         "Werkzeug scrypt + CSRF, validadores y honeypot anti-spam",
         "models.Usuario; forms.py"],
        ["Al menos un iframe",
         "Mapa de OpenStreetMap embebido en la sección Ubicación",
         "templates/index.html (sección #ubicacion)"],
        ["Iconos FontAwesome / Flaticon",
         "FontAwesome 6.7.2 por CDN en todo el sitio y el panel",
         "templates/base.html; templates/admin/base.html"],
        ["Google Fonts o fuentes locales",
         "Fraunces para títulos e Inter para texto",
         "templates/base.html; static/css/styles.css"],
        ["Favicon y logo",
         "SVG locales referenciados desde el head y la marca del sitio",
         "static/img/favicon.svg; static/img/logo.svg"],
        ["POO con los cuatro pilares",
         "Clases abstractas, herencia, atributos protegidos/propiedades y resumen() polimórfico",
         "portfolio/models.py (comentarios por pilar)"],
        ["Diseño responsive (mobile, tablet, escritorio)",
         "Grid y tipografía fluidos; menú hamburguesa; breakpoints 1024/820/560 px",
         "static/css/styles.css"],
        ["Al menos una animación o transición documentada",
         "Typewriter, reveal on scroll, barras, contadores y hover",
         "static/js/main.js; static/css/styles.css"],
        ["Modelo relacional lógico y físico MySQL",
         "Entidades, cardinalidades, PK/FK, tabla intermedia N:M y DDL",
         "Sección 5; database/schema_mysql.sql"],
        ["CV descargable en PDF (RRHH)",
         "Se sirve el PDF real subido desde /admin/cv; ReportLab solo es respaldo",
         "static/uploads/CV_Kevin_Basualdo.pdf; routes/public.py; routes/admin.py"],
        ["Textos editables del sitio",
         "Tabla textos_sitio + editor /admin/contenido; las plantillas leen textos.get()",
         "models.TextoSitio; templates/admin/textos.html"],
        ["Documentación preliminar PDF",
         "Este documento, generado con scripts/generar_documentacion.py",
         "docs/Documentacion_Preliminar_Portfolio.pdf"],
        ["Git/GitHub y publicación online",
         "Archivos de despliegue preparados; publicación pendiente de credenciales",
         "README.md; Procfile; .env.example"],
    ]
    h.append(_tabla(requisitos, [55 * mm, 65 * mm, 54 * mm], st))
    h.append(Spacer(1, 6))
    h.append(Paragraph("2.1. Requisitos funcionales", st["h2"]))
    h.extend(_vinetas([
        "RF1. El visitante puede recorrer el portfolio y descargar el CV en PDF.",
        "RF2. El visitante puede enviar un mensaje desde el formulario de contacto.",
        "RF3. El administrador puede iniciar y cerrar sesión de forma segura.",
        "RF4. El administrador puede crear, editar, ocultar y eliminar estudios, experiencias, tecnologías y proyectos.",
        "RF5. El administrador puede editar los datos personales, el avatar y el resumen del CV.",
        "RF6. El administrador puede leer, marcar y eliminar los mensajes recibidos.",
        "RF7. El administrador puede cambiar su nombre de usuario y su contraseña.",
        "RF8. La API pública permite consumir el contenido en formato JSON.",
    ], st))
    h.append(Paragraph("2.2. Requisitos no funcionales", st["h2"]))
    h.extend(_vinetas([
        "RNF1. Usabilidad: navegación clara, foco visible, textos alternativos y enlace para saltar al contenido.",
        "RNF2. Responsive: adaptación correcta en teléfonos, tablets y escritorio.",
        "RNF3. Seguridad: contraseñas hasheadas, CSRF, sesiones protegidas y validación del servidor.",
        "RNF4. Mantenibilidad: arquitectura por capas, POO, configuración por entorno y pruebas automatizadas.",
        "RNF5. Rendimiento: imágenes locales optimizadas, carga diferida y consultas ordenadas.",
        "RNF6. Portabilidad: SQLite para desarrollo local y MySQL para producción.",
    ], st))
    h.append(Paragraph("2.3. Los 13 requisitos: para qué y cómo", st["h2"]))
    h.append(Paragraph(
        "Esta tabla responde de forma explícita a las dos preguntas pedidas para cada "
        "requisito: para qué sirve y cómo se implementó. Es el resumen a usar en la "
        "defensa oral.",
        st["cuerpo"],
    ))
    requisitos13 = [
        ["N.º y requisito", "¿Para qué sirve?", "¿Cómo se hizo?", "Dónde verificarlo"],
        ["1. Contenido con Jinja2, diseño propio, usabilidad y funcionalidad",
         "Mostrar datos reales con una experiencia clara y navegable.",
         "Herencia de plantillas, macros y filtros; textos editables; navegación, formularios y enlaces.",
         "templates/base.html; templates/index.html; models.TextoSitio"],
        ["2. Maquetación, modelo relacional (lógico) y físico MySQL",
         "Definir la estructura visual y cómo se guardan y relacionan los datos.",
         "HTML semántico y CSS; entidades, cardinalidades, PK/FK, tabla N:M y DDL InnoDB utf8mb4.",
         "Sección 5; database/schema_mysql.sql"],
        ["3. Diseño estético: iframe, iconos y fuentes",
         "Dar identidad visual y cumplir los recursos obligatorios.",
         "Mapa OpenStreetMap embebido, FontAwesome 6.7.2 por CDN y Google Fonts (Fraunces e Inter).",
         "templates/index.html (#ubicacion); templates/base.html"],
        ["4. POO con los cuatro pilares y comentarios en el código",
         "Organizar clases reutilizables y poder explicarlas en la defensa.",
         "Abstracción, herencia, encapsulamiento y polimorfismo; cada pilar señalado con comentarios.",
         "portfolio/models.py"],
        ["5. Responsive: mobile, tablet y escritorio",
         "Que el sitio se vea y funcione bien en cualquier dispositivo.",
         "Grid y flexbox, tipografía fluida, menú hamburguesa y breakpoints 1024/820/560 px.",
         "static/css/styles.css; static/js/main.js"],
        ["6. Al menos una animación o transición documentada",
         "Hacer la interfaz más viva sin distraer al visitante.",
         "Typewriter, reveal on scroll, contadores, pulse y hover; respeta prefers-reduced-motion.",
         "static/js/main.js; static/css/styles.css"],
        ["7. Bootstrap (opcional)",
         "No era obligatorio: se decidió no usarlo y justificar la decisión.",
         "CSS propio con variables y componentes, sin dependencias externas de maquetación.",
         "static/css/styles.css"],
        ["8. Publicación online, Git/GitHub y BD en Clever Cloud",
         "Versionar el código y dejar el sitio y MySQL accesibles en línea.",
         "Procfile, requirements, .env.example y guía listos; falta la cuenta y las credenciales.",
         "README.md; docs/Guia_Despliegue.md (pendiente)"],
        ["9. Login seguro: hash de contraseña y Flask-WTF",
         "Proteger el panel y evitar accesos no autorizados o formularios falsos.",
         "Flask-Login, hash scrypt de Werkzeug, CSRF, validadores y honeypot anti-spam.",
         "routes/auth.py; models.Usuario; forms.py"],
        ["10. Diseño integral: alineación, márgenes, tipografía, imágenes, paleta, logo, iconos y favicon",
         "Lograr coherencia visual y un resultado profesional.",
         "Variables de diseño, escala tipográfica, SVG locales optimizados, paleta teal y crema.",
         "static/css/styles.css; static/img/favicon.svg; logo.svg"],
        ["11. Documentación preliminar PDF",
         "Explicar planificación, organización, objetivo y descripción del proyecto.",
         "PDF generado con ReportLab desde un script, con DDL completo y esta trazabilidad.",
         "docs/Documentacion_Preliminar_Portfolio.pdf"],
        ["12. CV de RRHH descargable en PDF",
         "Entregar el CV real al reclutador desde el propio sitio.",
         "El PDF real se sube en /admin/cv y se sirve en /cv; si falta, se genera con ReportLab.",
         "static/uploads/CV_Kevin_Basualdo.pdf; routes/public.py"],
        ["13. Defensa oral del proyecto",
         "Poder explicar cada decisión y demostrar autoría del código.",
         "Documentación por capas, comentarios de POO, pruebas y esta tabla de trazabilidad.",
         "Este documento; README.md; tests/"],
    ]
    h.append(_tabla(requisitos13, [37 * mm, 42 * mm, 55 * mm, 40 * mm], st))

    # =====================================================================
    # 3. TECNOLOGÍAS
    # =====================================================================
    h.append(Paragraph("3. Tecnologías utilizadas", st["h1"]))
    h.append(HRFlowable(width="100%", thickness=1, color=ACENTO, spaceAfter=8))
    tecnologias = [
        ["Capa", "Tecnología", "Uso en el proyecto"],
        ["Backend", "Python 3.12+ / 3.14", "Lenguaje principal del servidor y de los scripts."],
        ["Backend", "Flask 3.x", "Aplicación web, rutas, blueprints y manejo de errores."],
        ["Backend", "Flask-SQLAlchemy + SQLAlchemy", "ORM, modelos y consultas portables."],
        ["Backend", "Flask-Login", "Autenticación y protección de sesiones."],
        ["Backend", "Flask-WTF / WTForms", "Formularios, CSRF y validación del servidor."],
        ["Backend", "Werkzeug", "Hash seguro de contraseñas (scrypt)."],
        ["Backend", "ReportLab", "Respaldos: CV dinámico y generación de este PDF."],
        ["Base de datos", "MySQL 8 + PyMySQL", "Persistencia relacional en producción."],
        ["Base de datos", "SQLite", "Fallback local para ejecutar sin servidor MySQL."],
        ["Frontend", "Jinja2", "Plantillas, herencia, macros y filtros."],
        ["Frontend", "HTML5 semántico", "Estructura accesible y SEO."],
        ["Frontend", "CSS3", "Variables, grid, flexbox, animaciones y responsive."],
        ["Frontend", "JavaScript (ES6)", "Typewriter, reveal, contadores, menú y formularios."],
        ["Recursos", "FontAwesome 6.7.2", "Iconografía del sitio y del panel."],
        ["Recursos", "Google Fonts", "Fraunces para títulos e Inter para texto."],
        ["Calidad", "pytest", "41 pruebas automatizadas de rutas, modelos, textos, CV y formularios."],
        ["Infraestructura", "Gunicorn + Clever Cloud", "Servidor WSGI y hosting con add-on MySQL."],
        ["Control de versiones", "Git / GitHub", "Versionado y publicación del código."],
    ]
    h.append(_tabla(tecnologias, [30 * mm, 55 * mm, 89 * mm], st))

    # =====================================================================
    # 4. ARQUITECTURA
    # =====================================================================
    h.append(Paragraph("4. Arquitectura de la aplicación", st["h1"]))
    h.append(HRFlowable(width="100%", thickness=1, color=ACENTO, spaceAfter=8))
    h.append(Paragraph(
        "Se utilizó el patrón <b>application factory</b>: la función create_app() "
        "construye la aplicación, carga la configuración según el entorno, inicializa "
        "las extensiones y registra los blueprints. Esto facilita las pruebas, evita "
        "ciclos de importación y permite tener configuraciones distintas sin cambiar "
        "el código.",
        st["cuerpo"],
    ))
    h.append(Paragraph("4.1. Organización por capas", st["h2"]))
    capas = [
        ["Capa", "Responsabilidad", "Archivos"],
        ["Presentación", "Plantillas, CSS, JavaScript y recursos estáticos.",
         "portfolio/templates/, static/"],
        ["Rutas / controladores", "Reciben la petición, validan permisos, consultan datos y devuelven la respuesta.",
         "routes/public.py, auth.py, admin.py"],
        ["Dominio", "Modelos POO, reglas de negocio, serialización y formateo.",
         "models.py, forms.py, pdf.py"],
        ["Persistencia", "ORM SQLAlchemy, sesión, tablas y relaciones.",
         "extensions.py, models.py"],
        ["Configuración", "Variables de entorno, URI de base, seguridad y metadatos.",
         "config.py, .env"],
        ["Infraestructura", "Punto de entrada de desarrollo y WSGI para producción.",
         "app.py, wsgi.py, Procfile"],
    ]
    h.append(_tabla(capas, [35 * mm, 90 * mm, 49 * mm], st))
    h.append(Paragraph("4.2. Estructura del proyecto", st["h2"]))
    arbol = """portfolio2/
├── app.py                  # Entrada de desarrollo (python app.py)
├── wsgi.py                 # Entrada WSGI para gunicorn
├── config.py               # Configuración por entorno
├── requirements.txt
├── Procfile                # Arranque alternativo con gunicorn
├── .env.example            # Plantilla de variables de entorno
├── portfolio/
│   ├── __init__.py         # create_app(), filtros, CLI, errores
│   ├── extensions.py       # db, login_manager, csrf
│   ├── models.py           # POO + tablas MySQL
│   ├── forms.py            # Formularios Flask-WTF
│   ├── seed.py             # Datos de demostración
│   ├── pdf.py              # Generación del CV
│   ├── routes/             # Blueprints public, auth, admin
│   ├── templates/          # Jinja2 (público, admin, auth, errores)
│   └── static/             # CSS, JS, SVG (logo, favicon, portadas)
├── database/
│   ├── schema_mysql.sql    # Diseño físico
│   └── seed.sql            # Datos iniciales en SQL
├── tests/                  # Suite pytest
├── docs/                   # Este documento y guía de despliegue
└── scripts/                # Generador de la documentación PDF"""
    h.append(Preformatted(arbol, st["codigo"]))
    h.append(Paragraph("4.3. Flujo de una petición", st["h2"]))
    h.extend(_vinetas([
        "El navegador solicita una URL (por ejemplo /admin/proyectos).",
        "El blueprint correspondiente recibe la petición; en el panel, un before_request exige sesión activa.",
        "La vista consulta o modifica datos mediante SQLAlchemy y valida los formularios con Flask-WTF.",
        "Jinja2 renderiza la plantilla con los datos y aplica filtros (fechas, URLs de medios, etc.).",
        "Flask devuelve HTML, JSON o un PDF según la ruta, junto con las cabeceras de seguridad.",
    ], st))
    h.append(Paragraph("4.4. Endpoints principales", st["h2"]))
    endpoints = [
        ["Método", "Ruta", "Descripción", "Acceso"],
        ["GET", "/", "Portfolio completo con todas las secciones.", "Público"],
        ["POST", "/contacto", "Guarda un mensaje validado en la base.", "Público"],
        ["GET", "/cv", "Genera y descarga el CV en PDF.", "Público"],
        ["GET", "/api/portfolio", "Contenido completo en JSON.", "Público"],
        ["GET", "/salud", "Health check para el hosting.", "Público"],
        ["GET", "/login", "Formulario de acceso.", "Público"],
        ["POST", "/logout", "Cierra la sesión.", "Autenticado"],
        ["GET", "/admin/", "Panel con métricas y últimos mensajes.", "Autenticado"],
        ["GET/POST", "/admin/perfil", "Edición de datos personales.", "Autenticado"],
        ["GET/POST", "/admin/estudios...", "Listado, alta, edición y baja de estudios.", "Autenticado"],
        ["GET/POST", "/admin/experiencias...", "Listado, alta, edición y baja de experiencias.", "Autenticado"],
        ["GET/POST", "/admin/tecnologias...", "Listado, alta, edición y baja de tecnologías.", "Autenticado"],
        ["GET/POST", "/admin/proyectos...", "CRUD de proyectos con tecnologías N:M.", "Autenticado"],
        ["GET/POST", "/admin/mensajes...", "Bandeja de entrada y gestión de mensajes.", "Autenticado"],
        ["GET/POST", "/admin/cuenta", "Cambio de usuario y contraseña.", "Autenticado"],
    ]
    h.append(_tabla(endpoints, [17 * mm, 47 * mm, 78 * mm, 32 * mm], st))

    # =====================================================================
    # 5. MODELO DE DATOS
    # =====================================================================
    h.append(Paragraph("5. Modelo de datos: diseño lógico y físico", st["h1"]))
    h.append(HRFlowable(width="100%", thickness=1, color=ACENTO, spaceAfter=8))
    h.append(Paragraph(
        "El modelo relacional se normalizó para evitar duplicación de datos. La "
        "tecnología de cada proyecto no se guarda como texto separado por comas: existe "
        "una tabla intermedia que representa una relación muchos a muchos real. Todas "
        "las tablas usan InnoDB, utf8mb4 y claves foráneas con acciones explícitas.",
        st["cuerpo"],
    ))
    h.append(Paragraph("5.1. Entidades y relaciones", st["h2"]))
    entidades = [
        ["Entidad", "Atributos principales", "Clave primaria", "Relaciones"],
        ["usuarios", "username, password_hash, nombre, activo, ultimo_acceso", "id",
         "1 usuario : 0..1 perfil"],
        ["perfil", "nombre, apellido, titulo, bio, email, telefono, redes, cv_resumen", "id",
         "FK usuario_id -> usuarios.id (SET NULL)"],
        ["estudios", "institucion, titulo, nivel, fechas, descripcion, orden, activo", "id",
         "Contenido del portfolio"],
        ["experiencias", "empresa, puesto, modalidad, fechas, logros, orden, activo", "id",
         "Contenido del portfolio"],
        ["tecnologias", "nombre, categoria, nivel, icono, color, orden, activo", "id",
         "N:M con proyectos"],
        ["proyectos", "titulo, descripcion, repo_url, demo_url, imagen, destacado", "id",
         "N:M con tecnologias"],
        ["proyecto_tecnologia", "proyecto_id, tecnologia_id", "(proyecto_id, tecnologia_id)",
         "Dos FK con ON DELETE CASCADE"],
        ["textos_sitio", "clave, etiqueta, valor, orden, seccion", "id",
         "Entidad independiente; clave UNIQUE"],
        ["mensajes", "nombre, email, asunto, mensaje, leido, creado_en", "id",
         "Consultas del formulario público"],
    ]
    h.append(_tabla(entidades, [31 * mm, 67 * mm, 28 * mm, 48 * mm], st))
    h.append(Paragraph("5.2. Cardinalidades", st["h2"]))
    h.extend(_vinetas([
        "Un usuario administra como máximo un perfil; un perfil puede existir sin usuario asociado (SET NULL).",
        "Un perfil tiene muchos estudios y muchas experiencias (1:N).",
        "Un proyecto usa muchas tecnologías y una tecnología participa en muchos proyectos (N:M).",
        "Cada mensaje es independiente y no depende de otra entidad.",
        "Los estudios, experiencias, tecnologías y proyectos tienen un campo activo para ocultarlos sin eliminarlos.",
    ], st))
    h.append(Paragraph("5.3. Diseño físico resumido", st["h2"]))
    fisico = [
        ["Tabla", "Motor", "Charset", "PK", "FK / Índices relevantes"],
        ["usuarios", "InnoDB", "utf8mb4", "id", "UNIQUE(username)"],
        ["perfil", "InnoDB", "utf8mb4", "id", "UNIQUE(usuario_id), FK usuarios"],
        ["estudios", "InnoDB", "utf8mb4", "id", "idx orden, idx activo"],
        ["experiencias", "InnoDB", "utf8mb4", "id", "idx orden, idx activo"],
        ["tecnologias", "InnoDB", "utf8mb4", "id", "idx categoria, CHECK nivel 0..100"],
        ["proyectos", "InnoDB", "utf8mb4", "id", "idx destacado, idx orden"],
        ["proyecto_tecnologia", "InnoDB", "utf8mb4", "compuesta", "FK proyectos, FK tecnologias"],
        ["textos_sitio", "InnoDB", "utf8mb4", "id", "UNIQUE(clave), idx orden"],
        ["mensajes", "InnoDB", "utf8mb4", "id", "idx leido, idx creado_en"],
    ]
    h.append(_tabla(fisico, [43 * mm, 18 * mm, 20 * mm, 28 * mm, 65 * mm], st))
    h.append(Spacer(1, 4))
    h.append(_caja(
        "<b>Integridad referencial.</b> Si se elimina un usuario, su perfil no se "
        "borra: la clave queda en NULL. Si se elimina un proyecto o una tecnología, "
        "las filas correspondientes de proyecto_tecnologia se eliminan en cascada. "
        "El DDL completo, con tipos y restricciones, se incluye en el Anexo A y en "
        "database/schema_mysql.sql.",
        st,
    ))
    h.append(Paragraph("5.4. Estrategia de persistencia", st["h2"]))
    h.append(Paragraph(
        "En desarrollo, si no hay variables de MySQL, la aplicación usa SQLite en "
        "instance/portfolio.db para que el proyecto pueda ejecutarse sin instalar un "
        "servidor. En producción se define DATABASE_URL o las variables del add-on "
        "MySQL de Clever Cloud (MYSQL_ADDON_URI o MYSQL_ADDON_HOST, USER, PASSWORD, "
        "PORT y DB). La URI mysql:// se normaliza a mysql+pymysql:// y se agrega "
        "charset=utf8mb4 automáticamente.",
        st["cuerpo"],
    ))

    # =====================================================================
    # 6. POO
    # =====================================================================
    h.append(Paragraph("6. Programación Orientada a Objetos", st["h1"]))
    h.append(HRFlowable(width="100%", thickness=1, color=ACENTO, spaceAfter=8))
    h.append(Paragraph(
        "Los cuatro pilares están aplicados en portfolio/models.py y señalados con "
        "comentarios en mayúsculas para facilitar su localización durante la defensa. "
        "La tabla siguiente resume la evidencia concreta.",
        st["cuerpo"],
    ))
    poo = [
        ["Pilar", "Cómo se aplica", "Evidencia en el código"],
        ["Abstracción", ("Se definen contratos que no se instancian: Persona y ContenidoPortfolio. "
                         "Establecen qué debe hacer una persona y qué debe hacer todo contenido, "
                         "sin atarse a una tabla."),
         "class Persona(ABC) y class ContenidoPortfolio(ModeloBase), con métodos @abstractmethod."],
        ["Herencia", ("ModeloBase centraliza la persistencia y la serialización. Perfil hereda de "
                      "Persona y ModeloBase; Estudio, Experiencia, Tecnologia y Proyecto heredan "
                      "de ContenidoPortfolio."),
         "class Perfil(Persona, ModeloBase); class Estudio(ContenidoPortfolio); etc."],
        ["Encapsulamiento", ("La contraseña se guarda en _password_hash y solo se modifica/verifica "
                             "con set_password() y check_password(). El email y el teléfono del "
                             "perfil usan propiedades con validación."),
         "@property email / @email.setter; @telefono.setter; set_password(); check_password()."],
        ["Polimorfismo", ("Cada subclase de ContenidoPortfolio sobrescribe resumen() y responde "
                          "distinto ante el mismo mensaje. La API y las vistas pueden tratarlas "
                          "de forma uniforme."),
         "Estudio.resumen(), Experiencia.resumen(), Tecnologia.resumen(), Proyecto.resumen() y TextoSitio.resumen()."],
    ]
    h.append(_tabla(poo, [26 * mm, 78 * mm, 70 * mm], st))
    h.append(Paragraph("6.1. Abstracción: contrato de contenido", st["h2"]))
    h.append(Preformatted(
        "class Persona(ABC):\n"
        "    @property\n"
        "    @abstractmethod\n"
        "    def nombre_completo(self) -> str: ...\n\n"
        "    @abstractmethod\n"
        "    def resumen(self) -> str: ...\n\n"
        "class ContenidoPortfolio(ModeloBase):\n"
        "    __abstract__ = True\n\n"
        "    @abstractmethod\n"
        "    def resumen(self) -> str:\n"
        "        \"\"\"Texto breve que resume el contenido.\"\"\"",
        st["codigo"],
    ))
    h.append(Paragraph(
        "La metaclase MetaModelo combina DefaultMeta (SQLAlchemy) con ABCMeta para que "
        "las clases abstractas también puedan ser modelos declarativos sin conflictos.",
        st["cuerpo"],
    ))
    h.append(Paragraph("6.2. Encapsulamiento: contraseña y datos de contacto", st["h2"]))
    h.append(Preformatted(
        "def set_password(self, password_plano: str) -> None:\n"
        "    self._password_hash = generate_password_hash(password_plano)\n\n"
        "def check_password(self, password_plano: str) -> bool:\n"
        "    return bool(password_plano) and check_password_hash(\n"
        "        self._password_hash, password_plano\n"
        "    )\n\n"
        "@email.setter\n"
        "def email(self, valor: str) -> None:\n"
        "    valor = (valor or \"\").strip().lower()\n"
        "    if valor and (\"@\" not in valor or \".\" not in valor.split(\"@\")[-1]):\n"
        "        raise ValueError(\"El email no tiene un formato válido.\")\n"
        "    self._email = valor",
        st["codigo"],
    ))
    h.append(Paragraph("6.3. Polimorfismo en acción", st["h2"]))
    h.append(Preformatted(
        "def resumen(self) -> str:   # Estudio\n"
        "    return f\"{self.titulo} en {self.institucion} ({self.periodo}).\"\n\n"
        "def resumen(self) -> str:   # Experiencia\n"
        "    return f\"{self.puesto} en {self.empresa} ({self.periodo}).\"\n\n"
        "def resumen(self) -> str:   # Tecnologia\n"
        "    return f\"{self.nombre}: nivel {self.nivel}% ({self.categoria}).\"\n\n"
        "def resumen(self) -> str:   # TextoSitio\n"
        "    return f\"{self.etiqueta}: {self.valor}\"",
        st["codigo"],
    ))
    h.append(Paragraph(
        "La API recorre una lista de proyectos y llama a resumen() sin preguntar de qué "
        "clase se trata. Si mañana se agrega una nueva subclase, la vista sigue "
        "funcionando siempre que implemente el contrato. Eso es polimorfismo.",
        st["cuerpo"],
    ))

    # =====================================================================
    # 7. SEGURIDAD
    # =====================================================================
    h.append(Paragraph("7. Seguridad y autenticación", st["h1"]))
    h.append(HRFlowable(width="100%", thickness=1, color=ACENTO, spaceAfter=8))
    h.append(Paragraph(
        "El panel de administración es la parte más sensible del sistema. Se aplicaron "
        "controles en capas: contraseñas nunca almacenadas en texto plano, formularios "
        "con token CSRF, validación del servidor, sesiones protegidas y consultas "
        "parametrizadas por el ORM.",
        st["cuerpo"],
    ))
    seguridad = [
        ["Control", "Implementación"],
        ["Hash de contraseñas", ("Werkzeug generate_password_hash() con scrypt; verificación con "
                                 "check_password_hash(). La contraseña original no se guarda ni "
                                 "se muestra.")],
        ["CSRF", ("Flask-WTF protege todos los formularios y las operaciones POST del panel con "
                  "WTF_CSRF_ENABLED=True y tokens ocultos (hidden_tag / csrf_token).")],
        ["Autenticación", ("Flask-Login gestiona la sesión. El blueprint admin aplica "
                           "@login_required en un before_request, por lo que ninguna vista del "
                           "panel queda expuesta.")],
        ["Sesiones", ("Cookies HttpOnly, SameSite=Lax y Secure activable en producción. "
                      "La clave secreta se toma de SECRET_KEY.")],
        ["Validación", ("WTForms valida tipos, longitudes, emails, URLs, fechas y rangos. "
                        "La validación del servidor no depende del HTML.")],
        ["Anti-spam", "Campo honeypot invisible en el formulario de contacto; si un bot lo completa, el mensaje se rechaza."],
        ["Inyección SQL", "SQLAlchemy parametriza las consultas. No se concatenan valores del usuario en SQL."],
        ["XSS", "Jinja2 escapa automáticamente las variables; ReportLab escapa el texto antes de generar el PDF."],
        ["Redirecciones abiertas", "El parámetro next del login se valida con urlparse: solo se aceptan rutas internas."],
        ["Enumeración de usuarios", "El login devuelve un mensaje genérico ante credenciales incorrectas."],
        ["Cabeceras", "X-Content-Type-Options, X-Frame-Options, Referrer-Policy y Permissions-Policy en cada respuesta."],
        ["Panel fuera de buscadores", "El panel incluye meta robots noindex, nofollow y robots.txt bloquea /admin."],
        ["Credenciales iniciales", "kevinAdmin / kevin1504 se definen por variables de entorno. Deben cambiarse antes de publicar."],
    ]
    h.append(_tabla(seguridad, [38 * mm, 136 * mm], st))
    h.append(Spacer(1, 5))
    h.append(_caja(
        "<b>Recomendación para la entrega:</b> definir SECRET_KEY, ADMIN_USERNAME y "
        "ADMIN_PASSWORD como variables de entorno en Clever Cloud, cambiar la "
        "contraseña desde el panel y no versionar el archivo .env. El repositorio "
        "incluye .env.example como plantilla.",
        st,
    ))
    h.append(Paragraph("7.1. Flujo de autenticación", st["h2"]))
    h.extend(_vinetas([
        "El visitante accede a /login y recibe un formulario con token CSRF.",
        "El servidor busca el usuario, verifica que esté activo y compara el hash de la contraseña.",
        "Si es correcto, Flask-Login guarda la sesión (y opcionalmente una cookie de recordatorio por 7 días).",
        "El acceso al panel se redirige según next solo si es una ruta interna; de lo contrario va a /admin/.",
        "El cierre de sesión es un POST protegido por CSRF, no un enlace GET.",
    ], st))

    # =====================================================================
    # 8. FRONTEND RESPONSIVE
    # =====================================================================
    h.append(Paragraph("8. Diseño frontend y responsive", st["h1"]))
    h.append(HRFlowable(width="100%", thickness=1, color=ACENTO, spaceAfter=8))
    h.append(Paragraph(
        "El sitio público usa una estética clara y sobria: fondo papel cálido, tinta "
        "verde profunda y un acento verde azulado. Las tipografías son Fraunces para "
        "títulos e Inter para el texto, con tarjetas simples, bordes suaves y mucho "
        "espacio en blanco. El panel mantiene un fondo claro con barra lateral oscura "
        "para diferenciar el contexto de edición.",
        st["cuerpo"],
    ))
    h.append(Paragraph("8.1. Secciones del portfolio", st["h2"]))
    secciones = [
        ["Sección", "Contenido", "Recurso destacado"],
        ["Hero", "Nombre, rol animado, disponibilidad, avatar, estadísticas y accesos.", "Typewriter y transiciones suaves"],
        ["Sobre mí", "Biografía, ubicación, email, disponibilidad y tarjetas de enfoque.", "Grid de tarjetas"],
        ["Estudios", "Línea de tiempo con institución, período, nivel y descripción.", "Timeline responsive"],
        ["Experiencia", "Puestos, modalidad, período, descripción y logros.", "Línea de tiempo y viñetas"],
        ["Tecnologías", "Tarjetas agrupadas por categoría con icono, color y nivel.", "Barras animadas"],
        ["Proyectos", "Portada, descripción, etiquetas de tecnologías y enlaces.", "Grid con tarjetas destacadas"],
        ["Ubicación", "Mapa embebido de OpenStreetMap y datos de contacto.", "Iframe requerido"],
        ["Contacto", "Formulario protegido y vías directas de contacto.", "Honeypot y CSRF"],
    ]
    h.append(_tabla(secciones, [26 * mm, 93 * mm, 55 * mm], st))
    h.append(Paragraph("8.2. Breakpoints y adaptación", st["h2"]))
    breakpoints = [
        ["Rango", "Comportamiento"],
        ["Escritorio (> 1024 px)", "Grillas de 2 y 3 columnas, navegación horizontal completa, hero a dos columnas."],
        ["Tablet (<= 1024 px)", "Se reducen columnas y espaciados; las tarjetas pasan a grillas de 2 columnas."],
        ["Tablet pequeña / móvil grande (<= 820 px)", "El menú se convierte en hamburguesa; el hero y las secciones pasan a una columna."],
        ["Móvil (<= 560 px)", "Tipografía y botones compactos, una sola columna, tarjetas a ancho completo y formularios apilados."],
    ]
    h.append(_tabla(breakpoints, [52 * mm, 122 * mm], st))
    h.append(Paragraph(
        "Además de los breakpoints, se usan funciones fluidas como clamp() para los "
        "tamaños de fuente, unidades relativas, imágenes con max-width: 100% y "
        "grid/flexbox con wrap. El resultado se verificó en anchos de 360, 768 y "
        "1440 píxeles.",
        st["cuerpo"],
    ))
    h.append(Paragraph("8.3. Accesibilidad y detalles", st["h2"]))
    h.extend(_vinetas([
        "HTML semántico: header, nav, main, section, article y footer.",
        "Enlace 'Saltar al contenido principal' y foco visible en todos los controles.",
        "Textos alternativos en imágenes y aria-label en botones icónicos.",
        "role=progressbar con aria-valuenow en las barras de nivel.",
        "Menú mobile con aria-expanded, cierre con Escape y bloqueo del scroll.",
        "Soporte de prefers-reduced-motion: si el usuario reduce el movimiento, se desactivan las animaciones.",
        "Contraste alto, tamaños táctiles adecuados y formularios con labels asociados.",
    ], st))

    # =====================================================================
    # 9. ANIMACIONES
    # =====================================================================
    h.append(Paragraph("9. Animaciones y transiciones", st["h1"]))
    h.append(HRFlowable(width="100%", thickness=1, color=ACENTO, spaceAfter=8))
    h.append(Paragraph(
        "Las animaciones se implementaron con CSS y JavaScript nativo, sin librerías "
        "externas. Todas respetan la preferencia de movimiento reducido del sistema. "
        "La tabla indica dónde buscarlas para la defensa.",
        st["cuerpo"],
    ))
    animaciones = [
        ["Animación", "Dónde se implementa", "Técnica"],
        ["Typewriter del rol", "main.js, bloque 'Animación 1'; index.html #typedRole", "setTimeout + textContent, ciclos de escritura y borrado."],
        ["Reveal on scroll", "main.js, bloque 'Animación 2'; atributos data-reveal", "IntersectionObserver + clase .is-visible con transición CSS."],
        ["Barras de tecnologías", "styles.css, .tech-fill; index.html .tech-bar", "Transición de width al 0.12 de intersección, con --nivel."],
        ["Contadores del hero", "main.js, 'Animar números de las estadísticas'", "requestAnimationFrame con easing cúbico."],
        ["Navbar al hacer scroll", "main.js, onScroll; styles.css .nav.is-scrolled", "Cambio de fondo, borde y sombra con transición."],
        ["Chips flotantes del hero", "styles.css @keyframes flotar", "Traslación vertical infinita y alternada."],
        ["Punto de disponibilidad", "styles.css .pulse-dot y @keyframes pulse", "Escala y opacidad infinita."],
        ["Hover de tarjetas", "styles.css .project-card, .focus-card, .tech-card", "Transform translateY, borde y sombra."],
        ["Aparición de flashes", "styles.css .flash; main.js cierre automático", "Entrada con animación y salida con opacidad/transform."],
        ["Cambio de tema del panel", "admin.css .sidebar, .card", "Transiciones suaves de color y sombra."],
    ]
    h.append(_tabla(animaciones, [36 * mm, 78 * mm, 60 * mm], st))
    h.append(Spacer(1, 4))
    h.append(_caja(
        "<b>Ubicación exacta para la defensa:</b> abrir portfolio/static/js/main.js "
        "en los comentarios 'Animación 1' y 'Animación 2', y en portfolio/static/css/"
        "styles.css buscar @keyframes flotar, @keyframes pulso y la regla .tech-fill.",
        st,
    ))

    # =====================================================================
    # 10. PRUEBAS
    # =====================================================================
    h.append(Paragraph("10. Pruebas y aseguramiento de calidad", st["h1"]))
    h.append(HRFlowable(width="100%", thickness=1, color=ACENTO, spaceAfter=8))
    h.append(Paragraph(
        "La suite utiliza pytest y una base SQLite en memoria independiente por prueba. "
        "Cada test crea las tablas, carga los datos de demostración y las elimina al "
        "finalizar, de modo que no hay contaminación entre casos. Para ejecutarla:",
        st["cuerpo"],
    ))
    h.append(Preformatted(
        ".\\\\.venv\\\\Scripts\\\\python.exe -m pytest -q\n\n"
        "Resultado esperado: 41 passed",
        st["codigo"],
    ))
    pruebas = [
        ["Archivo", "Qué verifica", "Casos"],
        ["tests/test_public.py", "Render de secciones, iframe, recursos, cabeceras, API, CV, robots y 404.", "7"],
        ["tests/test_auth.py", "Login válido/inválido, redirección segura, protección del panel, logout y cambio de clave.", "9"],
        ["tests/test_admin.py", "Panel, listados, CRUD de estudios, validación, experiencias, N:M, perfil y mensajes.", "8"],
        ["tests/test_contact.py", "Mensaje válido, longitud mínima, email inválido y honeypot.", "4"],
        ["tests/test_models.py", "Hash de contraseña, encapsulamiento, polimorfismo, fechas, N:M, serialización.", "8"],
        ["tests/test_contenido_cv.py", "Editor de textos, persistencia en BD, reflejo en el sitio y descarga del PDF real.", "5"],
    ]
    h.append(_tabla(pruebas, [38 * mm, 112 * mm, 24 * mm], st))
    h.append(Paragraph("10.1. Pruebas manuales recomendadas", st["h2"]))
    h.extend(_vinetas([
        "Abrir el sitio en 360 px, 768 px y 1440 px y comprobar que no hay scroll horizontal.",
        "Navegar con teclado: Tab, Enter, Escape en el menú y foco visible.",
        "Descargar el CV y verificar que los datos coinciden con el perfil actual.",
        "Enviar el formulario con datos válidos e inválidos y revisar los mensajes.",
        "Iniciar sesión con credenciales incorrectas y correctas; probar el cierre de sesión.",
        "Crear, editar y eliminar un registro de cada tipo; comprobar que el sitio público se actualiza.",
        "En /admin/contenido cambiar una frase, guardar y recargar el portfolio en otra pestaña.",
        "Descargar el CV, verificar que es el PDF real y reemplazarlo desde /admin/cv.",
        "Verificar que un visitante sin sesión no puede acceder a /admin/ ni ejecutar POST.",
    ], st))

    # =====================================================================
    # 11. DESPLIEGUE
    # =====================================================================
    h.append(Paragraph("11. Despliegue local y en Clever Cloud", st["h1"]))
    h.append(HRFlowable(width="100%", thickness=1, color=ACENTO, spaceAfter=8))
    h.append(Paragraph("11.1. Puesta en marcha local", st["h2"]))
    h.append(Preformatted(
        "# 1. Crear y activar el entorno virtual\n"
        "python -m venv .venv\n"
        ".\\\\.venv\\\\Scripts\\\\activate\n\n"
        "# 2. Instalar dependencias\n"
        "python -m pip install -r requirements.txt\n\n"
        "# 3. Configurar variables (copiar .env.example a .env)\n"
        "copy .env.example .env\n\n"
        "# 4. Ejecutar (crea las tablas y carga datos de ejemplo)\n"
        "python app.py\n\n"
        "# 5. Abrir http://127.0.0.1:5000",
        st["codigo"],
    ))
    h.append(Paragraph(
        "Sin MySQL instalado, la aplicación usa SQLite en instance/portfolio.db. "
        "Para usar MySQL local, definir DATABASE_URL en .env, por ejemplo: "
        "mysql+pymysql://root:clave@localhost:3306/portfolio?charset=utf8mb4. "
        "También se puede ejecutar database/schema_mysql.sql y database/seed.sql "
        "manualmente.",
        st["cuerpo"],
    ))
    h.append(Paragraph("11.2. Publicación en Clever Cloud", st["h2"]))
    h.extend(_vinetas([
        "Crear una aplicación Python en Clever Cloud y vincular el repositorio de GitHub.",
        "Agregar el add-on MySQL; Clever Cloud inyecta MYSQL_ADDON_URI y las variables MYSQL_ADDON_*.",
        "Configurar CC_PYTHON_MODULE=wsgi:app y CC_PYTHON_BACKEND=gunicorn (backend WSGI).",
        "Configurar SECRET_KEY, ADMIN_USERNAME, ADMIN_PASSWORD, SITE_URL y SITE_NAME en las variables de entorno.",
        "El build instala requirements.txt; la aplicación expone app en wsgi.py y crea las tablas al iniciar.",
        "La aplicación carga el contenido si SEED_ON_START=1 (útil en el primer despliegue).",
        "Verificar /salud, abrir el sitio, iniciar sesión y cambiar la contraseña inicial.",
    ], st))
    h.append(Preformatted(
        "# Variables de entorno mínimas en Clever Cloud\n"
        "CC_PYTHON_MODULE=wsgi:app\n"
        "CC_PYTHON_BACKEND=gunicorn\n"
        "CC_PYTHON_VERSION=3.12\n"
        "SECRET_KEY=<clave-larga-y-aleatoria>\n"
        "ADMIN_USERNAME=kevinAdmin\n"
        "ADMIN_PASSWORD=<contraseña-inicial-segura>\n"
        "SITE_URL=https://<tu-app>.cleverapps.io\n\n"
        "# El add-on MySQL provee automáticamente:\n"
        "# MYSQL_ADDON_URI, MYSQL_ADDON_HOST, MYSQL_ADDON_PORT,\n"
        "# MYSQL_ADDON_DB, MYSQL_ADDON_USER, MYSQL_ADDON_PASSWORD",
        st["codigo"],
    ))
    h.append(Paragraph(
        "El Procfile incluido en el repositorio permite desplegar en otros hostings "
        "(Railway, Render o Heroku) que ejecutan el comando web directamente: "
        "gunicorn wsgi:app --bind 0.0.0.0:$PORT.",
        st["cuerpo"],
    ))
    h.append(Paragraph("11.3. Git y GitHub", st["h2"]))
    h.append(Preformatted(
        "git init\n"
        "git add .\n"
        "git commit -m \"Proyecto integrador: portfolio full stack Flask + MySQL\"\n"
        "git branch -M main\n"
        "git remote add origin https://github.com/USUARIO/portfolio2.git\n"
        "git push -u origin main",
        st["codigo"],
    ))
    h.append(Paragraph(
        "El archivo .gitignore excluye .venv, .env, instance/, __pycache__ y archivos "
        "de prueba. Antes de publicar, reemplazar los datos de ejemplo (email, "
        "teléfono, redes y URLs de proyectos) por los datos reales desde el panel.",
        st["cuerpo"],
    ))
    h.append(Paragraph("11.4. Variables de entorno", st["h2"]))
    variables = [
        ["Variable", "Obligatoria", "Descripción"],
        ["SECRET_KEY", "Sí en producción", "Clave para firmar sesiones y tokens CSRF."],
        ["FLASK_CONFIG", "No", "development (por defecto) o production."],
        ["CC_PYTHON_MODULE", "Sí en Clever Cloud", "Módulo y objeto WSGI: wsgi:app."],
        ["CC_PYTHON_BACKEND", "Sí en Clever Cloud", "Backend WSGI: gunicorn (o uwsgi)."],
        ["CC_PYTHON_VERSION", "Recomendada", "Versión de Python, por ejemplo 3.12."],
        ["DATABASE_URL", "Sí en producción", "URI completa de MySQL; tiene prioridad."],
        ["MYSQL_ADDON_URI", "Alternativa", "URI inyectada por el add-on de Clever Cloud."],
        ["MYSQL_ADDON_HOST / USER / PASSWORD / PORT / DB", "Alternativa", "Construcción individual de la URI."],
        ["ADMIN_USERNAME", "Recomendada", "Usuario inicial del panel (por defecto kevinAdmin)."],
        ["ADMIN_PASSWORD", "Recomendada", "Contraseña inicial (por defecto kevin1504)."],
        ["ADMIN_NOMBRE", "No", "Nombre mostrado del administrador."],
        ["SITE_NAME / SITE_URL / CONTACT_EMAIL", "Recomendada", "Metadatos, canonical y contacto."],
        ["SEED_ON_START", "No", "1 para cargar datos de ejemplo al iniciar."],
        ["SESSION_COOKIE_SECURE", "Sí en HTTPS", "Fuerza cookies solo por HTTPS."],
    ]
    h.append(_tabla(variables, [62 * mm, 27 * mm, 85 * mm], st))

    # =====================================================================
    # 12. MANUAL DE USO
    # =====================================================================
    h.append(Paragraph("12. Manual de uso del portfolio y del panel", st["h1"]))
    h.append(HRFlowable(width="100%", thickness=1, color=ACENTO, spaceAfter=8))
    h.append(Paragraph("12.1. Sitio público", st["h2"]))
    h.append(Paragraph(
        "El visitante puede recorrer las secciones desde la navegación fija, usar los "
        "enlaces del hero, descargar el CV en PDF y enviar un mensaje. En móvil, el "
        "menú se abre con el botón hamburguesa y se cierra al elegir una sección o "
        "presionar Escape. El enlace de acceso al panel está en la barra de navegación "
        "y en el pie del sitio.",
        st["cuerpo"],
    ))
    h.append(Paragraph("12.2. Acceso al panel", st["h2"]))
    h.append(_tabla([
        ["Dato", "Valor inicial"],
        ["URL", "http://127.0.0.1:5000/login"],
        ["Usuario", "kevinAdmin"],
        ["Contraseña", "kevin1504"],
        ["Cambio", "Panel -> Mi cuenta"],
    ], [40 * mm, 134 * mm], st))
    h.append(Paragraph("12.3. Secciones del panel", st["h2"]))
    h.extend(_vinetas([
        "Panel: métricas de contenido y últimos mensajes recibidos.",
        "Perfil: nombre, título, bio, email, teléfono, redes, disponibilidad, avatar y resumen del CV.",
        "Estudios: alta, edición, visibilidad y eliminación de formaciones.",
        "Experiencia: puestos, fechas, modalidad, descripción y logros (uno por línea).",
        "Tecnologías: nombre, categoría, nivel, icono FontAwesome y color hexadecimal.",
        "Proyectos: título, descripción, portada, enlaces, destacado y selección múltiple de tecnologías.",
        "Contenido del sitio: edición de frases, títulos, etiquetas y parámetros del mapa; se guarda en textos_sitio.",
        "Mi CV: reemplazo del PDF real que se descarga desde los botones del portfolio.",
        "Mensajes: bandeja con estado leído/no leído, detalle y eliminación.",
        "Mi cuenta: cambio de nombre de usuario y contraseña con verificación de la clave actual.",
    ], st))
    h.append(Paragraph(
        "El botón «Descargar CV» sirve el PDF real de RRHH ubicado en "
        "static/uploads/CV_Kevin_Basualdo.pdf, que se puede reemplazar desde "
        "/admin/cv. Solo si no hubiera un archivo subido se genera un PDF con "
        "los datos actuales de la base como respaldo.",
        st["cuerpo"],
    ))

    # =====================================================================
    # 13. ESTADO Y CHECKLIST
    # =====================================================================
    h.append(Paragraph("13. Estado del proyecto y checklist de requisitos", st["h1"]))
    h.append(HRFlowable(width="100%", thickness=1, color=ACENTO, spaceAfter=8))
    h.append(Paragraph(
        "El desarrollo funcional está completo y probado. Las tareas que dependen de "
        "credenciales o de una cuenta externa se indican como pendientes para no "
        "declarar como terminado algo que todavía no está publicado.",
        st["cuerpo"],
    ))
    checklist = [
        ["Requisito", "Estado", "Observación"],
        ["Backend Flask + Jinja2 + MySQL", "Completado", "Arquitectura por blueprints y ORM."],
        ["Login y contraseña hasheada", "Completado", "Flask-Login + Werkzeug scrypt."],
        ["Flask-WTF y CSRF", "Completado", "Todos los formularios y POST protegidos."],
        ["POO con cuatro pilares", "Completado", "Comentarios en models.py."],
        ["Responsive mobile/tablet/escritorio", "Completado", "Breakpoints 1024/820/560 px."],
        ["Animaciones documentadas", "Completado", "main.js y styles.css."],
        ["Iframe, iconos, fonts, favicon, logo", "Completado", "OpenStreetMap, FontAwesome, Google Fonts y SVG."],
        ["Modelo relacional y físico", "Completado", "schema_mysql.sql y Anexo A."],
        ["CV PDF descargable", "Completado", "PDF real de RRHH servido en /cv; respaldo con ReportLab."],
        ["Editor de textos del sitio", "Completado", "Tabla textos_sitio y /admin/contenido."],
        ["Documentación PDF", "Completado", "Este documento, con los 13 requisitos."],
        ["Pruebas automatizadas", "Completado", "41 tests aprobados."],
        ["Repositorio Git/GitHub", "Pendiente", "Requiere instalar Git y autenticarse en GitHub."],
        ["Publicación online con MySQL", "Pendiente", "Requiere cuenta en Clever Cloud y add-on MySQL."],
        ["Datos personales reales", "Completado", "Cargados desde el CV; editables en /admin/perfil."],
    ]
    h.append(_tabla(checklist, [62 * mm, 25 * mm, 87 * mm], st))
    h.append(Spacer(1, 4))
    h.append(_caja(
        "<b>Antes de la entrega:</b> publicar el sitio, cambiar la contraseña del "
        "administrador y actualizar SITE_URL con la URL definitiva. Luego descargar "
        "el CV y comprobar que se entrega el PDF real.",
        st,
        colors.HexColor("#fff5e6"),
    ))

    # =====================================================================
    # 14. CONCLUSIONES
    # =====================================================================
    h.append(Paragraph("14. Conclusiones y mejoras futuras", st["h1"]))
    h.append(HRFlowable(width="100%", thickness=1, color=ACENTO, spaceAfter=8))
    h.append(Paragraph(
        "El proyecto integra en una sola aplicación los contenidos centrales de la "
        "carrera: programación en Python, desarrollo web con Flask, modelado relacional, "
        "consultas mediante ORM, autenticación, validación de formularios, diseño "
        "responsive y documentación. La separación en capas y el uso de POO permiten "
        "agregar funcionalidades sin reescribir el sitio.",
        st["cuerpo"],
    ))
    h.append(Paragraph("14.1. Aprendizajes principales", st["h2"]))
    h.extend(_vinetas([
        "Diseñar primero el modelo de datos evita duplicaciones y facilita las consultas.",
        "El encapsulamiento no es solo estético: reduce el riesgo de exponer datos sensibles.",
        "El polimorfismo simplifica las vistas y la API cuando varias entidades comparten un contrato.",
        "Las pruebas automatizadas dan confianza para refactorizar sin romper funcionalidades.",
        "La accesibilidad y el rendimiento se deciden desde el inicio, no al final.",
    ], st))
    h.append(Paragraph("14.2. Mejoras posibles", st["h2"]))
    h.extend(_vinetas([
        "Editor visual de imágenes con recorte y almacenamiento en un servicio de objetos.",
        "Panel de estadísticas de visitas y descargas del CV.",
        "Envío de correos de notificación cuando llega un mensaje.",
        "Recuperación de contraseña por email y autenticación en dos pasos.",
        "Internacionalización español/inglés con Flask-Babel.",
        "CI/CD con GitHub Actions para ejecutar pruebas y desplegar automáticamente.",
        "Backups automáticos de la base MySQL y monitoreo de errores.",
    ], st))

    # =====================================================================
    # ANEXO A: DDL
    # =====================================================================
    h.append(PageBreak())
    h.append(Paragraph("Anexo A — Diseño físico completo (DDL MySQL)", st["h1"]))
    h.append(HRFlowable(width="100%", thickness=1, color=ACENTO, spaceAfter=8))
    h.append(Paragraph(
        "El siguiente es el contenido de database/schema_mysql.sql. Define la base "
        "portfolio, las nueve tablas, claves primarias, claves foráneas, índices y "
        "restricciones. Se puede ejecutar directamente en MySQL 8.",
        st["cuerpo"],
    ))
    h.append(Preformatted(_ddl(), st["ddl"]))

    # =====================================================================
    # CIERRE
    # =====================================================================
    h.append(Spacer(1, 10))
    h.append(HRFlowable(width="100%", thickness=0.8, color=BORDE))
    h.append(Paragraph(
        "Documento generado automáticamente con ReportLab a partir de "
        "scripts/generar_documentacion.py. Noviembre de 2026.",
        st["nota"],
    ))

    doc.build(h)


if __name__ == "__main__":
    construir_documento()
    print(f"Documentación generada: {SALIDA}")
    print(f"Tamaño: {SALIDA.stat().st_size / 1024:.1f} KB")
