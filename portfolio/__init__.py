"""Fábrica de la aplicación Flask.

Organiza la app con el patrón application factory + blueprints, inicializa
extensiones, registra filtros de Jinja2, comandos de consola y el seed inicial.
"""
from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path

import click
from flask import Flask, render_template, url_for
from sqlalchemy.exc import SQLAlchemyError

from config import CONFIGURACIONES

from .extensions import csrf, db, login_manager


def create_app(config_name: str | None = None) -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    config_name = config_name or os.getenv("FLASK_CONFIG", "development")
    app.config.from_object(CONFIGURACIONES.get(config_name, CONFIGURACIONES["default"]))
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Modelos y blueprints (importaciones dentro de la factory para evitar ciclos)
    from . import models
    from .routes import admin, auth, public

    app.register_blueprint(public.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(admin.bp)

    @login_manager.user_loader
    def cargar_usuario(usuario_id: str):
        try:
            return db.session.get(models.Usuario, int(usuario_id))
        except (TypeError, ValueError):
            return None

    # Filtros de Jinja2 ----------------------------------------------------
    @app.template_filter("fecha_mes")
    def fecha_mes(valor):
        return models.formatear_mes(valor)

    @app.template_filter("fecha_hora")
    def fecha_hora(valor):
        if not valor:
            return "—"
        return valor.strftime("%d/%m/%Y %H:%M")

    @app.template_filter("media_url")
    def media_url(valor: str | None) -> str:
        """Acepta rutas locales o URLs externas para imágenes."""
        if not valor:
            return url_for("static", filename="img/avatar.svg")
        if valor.startswith(("http://", "https://", "//")):
            return valor
        return url_for("static", filename=valor.lstrip("/"))

    @app.context_processor
    def variables_globales():
        from flask_login import current_user

        sin_leer = 0
        if current_user.is_authenticated:
            sin_leer = models.Mensaje.query.filter_by(leido=False).count()

        # Textos editables desde /admin/contenido. Si la tabla todavía no
        # existe, las plantillas usan sus valores por defecto con .get().
        try:
            textos = {
                fila.clave: fila.valor
                for fila in models.TextoSitio.query.all()
            }
        except SQLAlchemyError:  # pragma: no cover - base sin migrar
            db.session.rollback()
            textos = {}

        return {
            "anio_actual": datetime.now().year,
            "site_name": app.config["SITE_NAME"],
            "site_url": app.config["SITE_URL"],
            "contact_email": app.config["CONTACT_EMAIL"],
            "mensajes_sin_leer": sin_leer,
            "textos": textos,
        }

    # Cabeceras de seguridad ----------------------------------------------
    @app.after_request
    def cabeceras(respuesta):
        respuesta.headers.setdefault("X-Content-Type-Options", "nosniff")
        respuesta.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
        respuesta.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        respuesta.headers.setdefault(
            "Permissions-Policy", "geolocation=(), microphone=(), camera=()"
        )
        return respuesta

    # Manejo de errores ----------------------------------------------------
    @app.errorhandler(403)
    def prohibido(error):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def no_encontrado(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def error_interno(error):
        db.session.rollback()
        app.logger.exception("Error interno")
        return render_template("errors/500.html"), 500

    @app.errorhandler(503)
    def sin_datos(error):
        return render_template("errors/503.html", error=error), 503

    # Comandos de consola --------------------------------------------------
    @app.cli.command("init-db")
    def comando_init_db():
        """Crea las tablas en la base configurada."""
        db.create_all()
        click.echo("✅ Tablas creadas/verificadas en la base de datos.")

    @app.cli.command("seed-db")
    def comando_seed_db():
        """Carga los datos de demostración (idempotente)."""
        from .seed import seed_inicial

        db.create_all()
        creado = seed_inicial(app.config)
        if creado:
            click.echo(
                f"✅ Datos cargados. Usuario: {app.config['ADMIN_USERNAME']} "
                "(contraseña definida en ADMIN_PASSWORD)."
            )
        else:
            click.echo("ℹ️  Ya existe un perfil; no se duplicaron datos.")

    @app.cli.command("seed-textos")
    def comando_seed_textos():
        """Carga las claves de texto nuevas sin sobrescribir las editadas."""
        from .seed import seed_textos

        db.create_all()
        cantidad = seed_textos()
        click.echo(f"✅ {cantidad} textos nuevos cargados (los existentes se conservaron).")

    @app.cli.command("create-admin")
    @click.option("--username", default=None, help="Nombre de usuario.")
    @click.option(
        "--password", default=None, help="Contraseña (mínimo 8 caracteres)."
    )
    def comando_create_admin(username, password):
        """Crea o actualiza la cuenta administradora."""
        from .seed import crear_admin

        username = username or app.config["ADMIN_USERNAME"]
        if not password:
            password = click.prompt(
                "Contraseña", hide_input=True, confirmation_prompt=True
            )
        try:
            usuario = crear_admin(username, password, app.config["ADMIN_NOMBRE"])
        except ValueError as error:
            raise click.ClickException(str(error)) from error
        click.echo(f"✅ Usuario '{usuario.username}' listo.")

    @app.shell_context_processor
    def contexto_shell():
        return {
            "db": db,
            "Usuario": models.Usuario,
            "Perfil": models.Perfil,
            "Estudio": models.Estudio,
            "Experiencia": models.Experiencia,
            "Tecnologia": models.Tecnologia,
            "Proyecto": models.Proyecto,
            "TextoSitio": models.TextoSitio,
            "Mensaje": models.Mensaje,
        }

    # Inicialización automática para desarrollo / primer deploy ------------
    if app.config.get("SEED_ON_START"):
        from .seed import seed_inicial

        with app.app_context():
            try:
                db.create_all()
                if seed_inicial(app.config):
                    app.logger.info("Base de datos inicializada con datos de ejemplo.")
            except Exception:  # pragma: no cover - depende de la BD externa
                app.logger.exception(
                    "No se pudo inicializar la base de datos. "
                    "Revisá DATABASE_URL / MYSQL_ADDON_URI."
                )

    return app
