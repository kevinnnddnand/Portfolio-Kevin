"""Rutas públicas: portfolio, contacto, CV y API JSON."""
from __future__ import annotations

import re
from datetime import UTC, datetime
from io import BytesIO
from pathlib import Path

from flask import (
    Blueprint,
    Response,
    abort,
    current_app,
    flash,
    jsonify,
    redirect,
    render_template,
    send_file,
    url_for,
)

from ..extensions import db
from ..forms import ContactoForm
from ..models import Estudio, Experiencia, Mensaje, Perfil, Proyecto, Tecnologia
from ..pdf import generar_cv_pdf

bp = Blueprint("public", __name__)

NOMBRE_CV = "CV_Kevin_Basualdo.pdf"


def ruta_cv() -> Path:
    """Ubicación del CV real subido desde el panel de administración."""
    return Path(current_app.static_folder or "") / "uploads" / NOMBRE_CV


def _perfil() -> Perfil:
    perfil = Perfil.query.first()
    if perfil is None:
        abort(503, description="El portfolio todavía no tiene datos cargados.")
    return perfil


def _estudios() -> list[Estudio]:
    return (
        Estudio.query.filter_by(activo=True)
        .order_by(Estudio.orden.asc(), Estudio.fecha_inicio.desc())
        .all()
    )


def _experiencias() -> list[Experiencia]:
    return (
        Experiencia.query.filter_by(activo=True)
        .order_by(Experiencia.orden.asc(), Experiencia.fecha_inicio.desc())
        .all()
    )


def _tecnologias() -> list[Tecnologia]:
    return (
        Tecnologia.query.filter_by(activo=True)
        .order_by(Tecnologia.orden.asc(), Tecnologia.nombre.asc())
        .all()
    )


def _proyectos() -> list[Proyecto]:
    return (
        Proyecto.query.filter_by(activo=True)
        .order_by(Proyecto.destacado.desc(), Proyecto.orden.asc())
        .all()
    )


def _agrupar_tecnologias(tecnologias: list[Tecnologia]) -> dict[str, list[Tecnologia]]:
    """Agrupa respetando el orden en que llegan de la base."""
    grupos: dict[str, list[Tecnologia]] = {}
    for tecnologia in tecnologias:
        grupos.setdefault(tecnologia.categoria, []).append(tecnologia)
    return grupos


@bp.get("/")
def inicio():
    tecnologias = _tecnologias()
    return render_template(
        "index.html",
        perfil=_perfil(),
        estudios=_estudios(),
        experiencias=_experiencias(),
        tecnologias=tecnologias,
        categorias=_agrupar_tecnologias(tecnologias),
        proyectos=_proyectos(),
        form=ContactoForm(),
    )


@bp.post("/contacto")
def contacto():
    """Procesa el formulario público y guarda el mensaje en MySQL."""
    form = ContactoForm()
    if form.validate_on_submit():
        mensaje = Mensaje(
            nombre=(form.nombre.data or "").strip(),
            email=(form.email.data or "").strip().lower(),
            asunto=(form.asunto.data or "").strip(),
            mensaje=(form.mensaje.data or "").strip(),
        )
        db.session.add(mensaje)
        db.session.commit()
        current_app.logger.info("Nuevo mensaje de contacto de %s", mensaje.email)
        flash("¡Gracias por escribirme! Recibí tu mensaje y te responderé a la brevedad.", "success")
        return redirect(url_for("public.inicio") + "#contacto")

    # Si hay errores, se informan y se vuelve al formulario.
    for errores in form.errors.values():
        for error in errores:
            flash(error, "danger")
    return redirect(url_for("public.inicio") + "#contacto")


@bp.get("/cv")
def descargar_cv():
    """Sirve el CV real (RRHH) subido desde el admin.

    Si todavía no se subió ningún archivo, se genera un PDF con los datos
    actuales de la base para que el botón nunca quede vacío.
    """
    archivo = ruta_cv()
    if archivo.is_file():
        return send_file(
            archivo,
            mimetype="application/pdf",
            as_attachment=True,
            download_name=NOMBRE_CV,
            max_age=0,
        )

    perfil = _perfil()
    contenido = generar_cv_pdf(
        perfil=perfil,
        estudios=_estudios(),
        experiencias=_experiencias(),
        tecnologias=_tecnologias(),
        proyectos=[p for p in _proyectos() if p.destacado][:4],
    )
    nombre = re.sub(r"[^A-Za-z0-9_-]+", "_", perfil.nombre_completo).strip("_") or "portfolio"
    return send_file(
        BytesIO(contenido),
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"CV_{nombre}.pdf",
        max_age=0,
    )


@bp.get("/api/portfolio")
def api_portfolio():
    """API pública de solo lectura que expone el contenido en JSON."""
    perfil = _perfil()
    estudios = _estudios()
    experiencias = _experiencias()
    tecnologias = _tecnologias()
    proyectos = _proyectos()

    return jsonify(
        {
            "perfil": {
                "nombre": perfil.nombre_completo,
                "titulo": perfil.titulo,
                "subtitulo": perfil.subtitulo,
                "bio": perfil.bio,
                "email": perfil.email,
                "telefono": perfil.telefono,
                "ubicacion": perfil.ubicacion,
                "linkedin": perfil.linkedin,
                "github": perfil.github,
                "sitio_web": perfil.sitio_web,
                "disponibilidad": perfil.disponibilidad,
                "avatar": url_for("static", filename=perfil.avatar_url, _external=True),
            },
            "estudios": [
                {
                    **e.to_dict(),
                    "periodo": e.periodo,
                    "resumen": e.resumen(),
                }
                for e in estudios
            ],
            "experiencias": [
                {
                    **e.to_dict(),
                    "periodo": e.periodo,
                    "logros": e.lista_logros,
                    "resumen": e.resumen(),
                }
                for e in experiencias
            ],
            "tecnologias": [
                {**t.to_dict(), "resumen": t.resumen()} for t in tecnologias
            ],
            "proyectos": [
                {
                    **p.to_dict(),
                    "tecnologias": [
                        {"id": t.id, "nombre": t.nombre, "icono": t.icono, "color": t.color}
                        for t in p.tecnologias
                    ],
                    "resumen": p.resumen(),
                }
                for p in proyectos
            ],
            "generado_en": datetime.now(UTC).isoformat(),
            "contacto": url_for("public.inicio", _external=True) + "#contacto",
        }
    )


@bp.get("/salud")
def salud():
    """Health check para el hosting."""
    return jsonify({"status": "ok", "servicio": "portfolio"})


@bp.get("/robots.txt")
def robots():
    lineas = [
        "User-agent: *",
        "Allow: /",
        "Disallow: /admin",
        "Disallow: /login",
        f"Sitemap: {url_for('public.inicio', _external=True)}",
    ]
    return Response("\n".join(lineas), mimetype="text/plain")


@bp.get("/favicon.ico")
def favicon():
    """Redirige el favicon clásico al SVG para evitar 404."""
    return redirect(url_for("static", filename="img/favicon.svg"), code=302)


@bp.errorhandler(503)
def mantenimiento(error):
    return render_template("errors/503.html", error=error), 503
