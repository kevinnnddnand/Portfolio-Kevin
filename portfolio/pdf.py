"""Generación dinámica del CV en PDF a partir de los datos de MySQL.

El CV se arma con ReportLab y se descarga desde `/cv`. Si se actualiza el
perfil o la experiencia en el panel, el PDF se regenera automáticamente.
"""
from __future__ import annotations

from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

AZUL = colors.HexColor("#0b1220")
ACENTO = colors.HexColor("#0f9b8e")
GRIS = colors.HexColor("#5b6779")
CLARO = colors.HexColor("#e6eaef")


def _html(texto: str | None) -> str:
    """Escapa texto del usuario y respeta saltos de línea."""
    limpio = escape((texto or "").strip())
    return limpio.replace("\n", "<br/>")


def _estilos() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "nombre": ParagraphStyle(
            "nombre", parent=base["Title"], fontName="Helvetica-Bold",
            fontSize=24, leading=27, textColor=AZUL, spaceAfter=2, alignment=0,
        ),
        "titulo": ParagraphStyle(
            "titulo", parent=base["Normal"], fontName="Helvetica-Bold",
            fontSize=11.5, leading=15, textColor=ACENTO, spaceAfter=6,
        ),
        "contacto": ParagraphStyle(
            "contacto", parent=base["Normal"], fontName="Helvetica",
            fontSize=8.7, leading=12, textColor=GRIS,
        ),
        "seccion": ParagraphStyle(
            "seccion", parent=base["Heading2"], fontName="Helvetica-Bold",
            fontSize=10.5, leading=13, textColor=AZUL, spaceBefore=12, spaceAfter=5,
            letterSpacing=1.1,
        ),
        "cuerpo": ParagraphStyle(
            "cuerpo", parent=base["Normal"], fontName="Helvetica",
            fontSize=9.3, leading=13.4, textColor=colors.HexColor("#26313f"),
        ),
        "item": ParagraphStyle(
            "item", parent=base["Normal"], fontName="Helvetica-Bold",
            fontSize=9.8, leading=13, textColor=AZUL,
        ),
        "fecha": ParagraphStyle(
            "fecha", parent=base["Normal"], fontName="Helvetica",
            fontSize=8.3, leading=11, textColor=GRIS, alignment=TA_RIGHT,
        ),
        "vineta": ParagraphStyle(
            "vineta", parent=base["Normal"], fontName="Helvetica",
            fontSize=9.1, leading=13, textColor=colors.HexColor("#26313f"),
            leftIndent=10, bulletIndent=1, spaceAfter=1.5,
        ),
    }


def _linea() -> HRFlowable:
    return HRFlowable(width="100%", thickness=0.8, color=CLARO, spaceBefore=2, spaceAfter=6)


def _pie_de_pagina(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(GRIS)
    canvas.drawString(18 * mm, 11 * mm, "CV generado desde el portfolio web")
    canvas.drawRightString(A4[0] - 18 * mm, 11 * mm, f"Página {doc.page}")
    canvas.restoreState()


def generar_cv_pdf(perfil, estudios, experiencias, tecnologias, proyectos=None) -> bytes:
    """Devuelve el binario del CV listo para enviar con send_file."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=16 * mm,
        bottomMargin=18 * mm,
        title=f"CV - {perfil.nombre_completo}",
        author=perfil.nombre_completo,
        subject="Curriculum Vitae",
    )
    st = _estilos()
    historia = []

    # Encabezado ---------------------------------------------------------
    historia.append(Paragraph(escape(perfil.nombre_completo), st["nombre"]))
    historia.append(Paragraph(escape(perfil.titulo), st["titulo"]))

    contacto = [perfil.email, perfil.telefono, perfil.ubicacion]
    contacto = [escape(c) for c in contacto if c]
    if perfil.linkedin:
        contacto.append("LinkedIn")
    if perfil.github:
        contacto.append("GitHub")
    historia.append(Paragraph(" &nbsp;·&nbsp; ".join(contacto), st["contacto"]))
    historia.append(Spacer(1, 5))
    historia.append(_linea())

    # Perfil profesional -------------------------------------------------
    resumen = perfil.cv_resumen or perfil.bio
    if resumen:
        historia.append(Paragraph("PERFIL PROFESIONAL", st["seccion"]))
        historia.append(Paragraph(_html(resumen), st["cuerpo"]))

    # Experiencia --------------------------------------------------------
    if experiencias:
        historia.append(Paragraph("EXPERIENCIA LABORAL", st["seccion"]))
        for exp in experiencias:
            fila = Table(
                [[
                    Paragraph(f"{escape(exp.puesto)} · {escape(exp.empresa)}", st["item"]),
                    Paragraph(escape(exp.periodo), st["fecha"]),
                ]],
                colWidths=[118 * mm, 54 * mm],
            )
            fila.setStyle(TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ]))
            historia.append(fila)
            detalle = " · ".join(
                x for x in (exp.modalidad, exp.ubicacion) if x
            )
            if detalle:
                historia.append(Paragraph(escape(detalle), st["contacto"]))
            if exp.descripcion:
                historia.append(Spacer(1, 2))
                historia.append(Paragraph(_html(exp.descripcion), st["cuerpo"]))
            for logro in exp.lista_logros:
                historia.append(Paragraph(_html(logro), st["vineta"], bulletText="•"))
            historia.append(Spacer(1, 6))

    # Estudios -----------------------------------------------------------
    if estudios:
        historia.append(Paragraph("FORMACIÓN ACADÉMICA", st["seccion"]))
        for estudio in estudios:
            fila = Table(
                [[
                    Paragraph(f"{escape(estudio.titulo)} · {escape(estudio.institucion)}", st["item"]),
                    Paragraph(escape(estudio.periodo), st["fecha"]),
                ]],
                colWidths=[118 * mm, 54 * mm],
            )
            fila.setStyle(TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ]))
            historia.append(fila)
            if estudio.nivel:
                historia.append(Paragraph(escape(estudio.nivel), st["contacto"]))
            if estudio.descripcion:
                historia.append(Paragraph(_html(estudio.descripcion), st["cuerpo"]))
            historia.append(Spacer(1, 5))

    # Tecnologías --------------------------------------------------------
    if tecnologias:
        historia.append(Paragraph("CONOCIMIENTOS TÉCNICOS", st["seccion"]))
        agrupadas: dict[str, list] = {}
        for tecnologia in tecnologias:
            agrupadas.setdefault(tecnologia.categoria, []).append(tecnologia)
        filas = []
        for categoria, items in agrupadas.items():
            filas.append([
                Paragraph(f"<b>{escape(categoria)}</b>", st["cuerpo"]),
                Paragraph(
                    ", ".join(escape(t.nombre) for t in items), st["cuerpo"]
                ),
            ])
        tabla = Table(filas, colWidths=[32 * mm, 140 * mm])
        tabla.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 1.5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 1.5),
        ]))
        historia.append(tabla)

    # Proyectos ----------------------------------------------------------
    if proyectos:
        historia.append(Paragraph("PROYECTOS DESTACADOS", st["seccion"]))
        for proyecto in proyectos:
            historia.append(Paragraph(escape(proyecto.titulo), st["item"]))
            historia.append(Paragraph(_html(proyecto.descripcion), st["cuerpo"]))
            if proyecto.tecnologias:
                historia.append(Paragraph(
                    "Tecnologías: " + ", ".join(escape(t.nombre) for t in proyecto.tecnologias),
                    st["contacto"],
                ))
            historia.append(Spacer(1, 4))

    doc.build(historia, onFirstPage=_pie_de_pagina, onLaterPages=_pie_de_pagina)
    return buffer.getvalue()
