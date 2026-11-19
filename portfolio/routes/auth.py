"""Autenticación del panel de edición.

Se combinan contraseñas hasheadas (Werkzeug) con formularios Flask-WTF, que
aportan validación y protección CSRF. No se revela si el usuario existe.
"""
from __future__ import annotations

from urllib.parse import urlparse

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from ..extensions import db
from ..forms import LoginForm
from ..models import Usuario, ahora

bp = Blueprint("auth", __name__)


def _destino_seguro(destino: str | None) -> bool:
    """Evita redirecciones abiertas: solo rutas internas."""
    if not destino:
        return False
    partes = urlparse(destino)
    return not partes.netloc and partes.path.startswith("/")


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("admin.panel"))

    form = LoginForm()
    if form.validate_on_submit():
        usuario = Usuario.query.filter_by(
            username=(form.username.data or "").strip().lower()
        ).first()

        if usuario is not None and usuario.activo and usuario.check_password(
            form.password.data
        ):
            login_user(usuario, remember=form.remember.data)
            usuario.ultimo_acceso = ahora()
            db.session.commit()

            flash(f"¡Bienvenido, {usuario.nombre}! Ya podés editar el portfolio.", "success")
            destino = request.args.get("next")
            return redirect(
                destino if destino and _destino_seguro(destino) else url_for("admin.panel")
            )

        # Mensaje genérico para no filtrar qué dato falló.
        flash("Usuario o contraseña incorrectos.", "danger")

    return render_template("auth/login.html", form=form)


@bp.post("/logout")
@login_required
def logout():
    logout_user()
    flash("Sesión cerrada correctamente.", "info")
    return redirect(url_for("public.inicio"))
