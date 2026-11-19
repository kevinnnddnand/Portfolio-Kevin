"""Configuración central de la aplicación.

La URI de la base de datos se toma de variables de entorno para poder usar
MySQL en producción (Clever Cloud) y SQLite durante el desarrollo local.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import ClassVar
from urllib.parse import quote_plus

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


def _flag(valor: str | None, por_defecto: bool = False) -> bool:
    """Convierte variables de entorno tipo '1', 'true' o 'si' en booleanos."""
    if valor is None:
        return por_defecto
    return valor.strip().lower() in {"1", "true", "yes", "si", "sí", "on"}


def construir_uri_bd() -> str:
    """Devuelve la URI de SQLAlchemy.

    Prioridad:
    1. DATABASE_URL (formato estándar de plataformas como Clever Cloud/Railway).
    2. MYSQL_ADDON_URI (variable que inyecta el add-on MySQL de Clever Cloud).
    3. Variables individuales MYSQL_ADDON_*.
    4. SQLite local como fallback para poder ejecutar el proyecto sin MySQL.
    """
    uri = os.getenv("DATABASE_URL") or os.getenv("MYSQL_ADDON_URI")

    if not uri:
        host = os.getenv("MYSQL_ADDON_HOST")
        if host:
            usuario = quote_plus(os.getenv("MYSQL_ADDON_USER", "root"))
            clave = quote_plus(os.getenv("MYSQL_ADDON_PASSWORD", ""))
            puerto = os.getenv("MYSQL_ADDON_PORT", "3306")
            nombre = os.getenv("MYSQL_ADDON_DB", "portfolio")
            uri = f"mysql+pymysql://{usuario}:{clave}@{host}:{puerto}/{nombre}"

    if not uri:
        ruta = (BASE_DIR / "instance" / "portfolio.db").as_posix()
        return f"sqlite:///{ruta}"

    # Clever Cloud entrega mysql://; SQLAlchemy necesita el driver explícito.
    if uri.startswith("mysql://"):
        uri = "mysql+pymysql://" + uri[len("mysql://"):]
    elif uri.startswith("mysql+mysqldb://"):
        uri = "mysql+pymysql://" + uri[len("mysql+mysqldb://"):]

    if uri.startswith("mysql+pymysql://") and "charset=" not in uri:
        separador = "&" if "?" in uri else "?"
        uri = f"{uri}{separador}charset=utf8mb4"
    return uri


def _opciones_engine(uri: str) -> dict:
    """Pool conservador para MySQL; SQLite no admite estas opciones."""
    if uri.startswith("sqlite"):
        return {}
    return {"pool_pre_ping": True, "pool_recycle": 280, "pool_size": 5, "max_overflow": 5}


_DATABASE_URI = construir_uri_bd()


class Config:
    """Configuración base (desarrollo y producción)."""

    SECRET_KEY = os.getenv("SECRET_KEY", "clave-de-desarrollo-cambiar-en-produccion")
    SQLALCHEMY_DATABASE_URI = _DATABASE_URI
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = _opciones_engine(_DATABASE_URI)

    # Seguridad de sesión / formularios
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # hasta 10 MB para el PDF del CV
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = _flag(os.getenv("SESSION_COOKIE_SECURE"), False)
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_DURATION = 60 * 60 * 24 * 7  # 7 días

    # Datos iniciales / administrador
    SEED_ON_START = _flag(os.getenv("SEED_ON_START"), True)
    ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "kevinAdmin")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "kevin1504")
    ADMIN_NOMBRE = os.getenv("ADMIN_NOMBRE", "Kevin")

    # Metadatos del sitio
    SITE_NAME = os.getenv("SITE_NAME", "Kevin | Portfolio")
    SITE_URL = os.getenv("SITE_URL", "http://localhost:5000")
    CONTACT_EMAIL = os.getenv("CONTACT_EMAIL", "d48721257@alumnos.itr.ed.ar")

    JSON_SORT_KEYS = False


class DevelopmentConfig(Config):
    DEBUG = True
    TEMPLATES_AUTO_RELOAD = True


class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = _flag(os.getenv("SESSION_COOKIE_SECURE"), True)


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    SQLALCHEMY_ENGINE_OPTIONS: ClassVar[dict] = {}
    WTF_CSRF_ENABLED = False
    SEED_ON_START = False
    SECRET_KEY = "clave-solo-para-pruebas"


CONFIGURACIONES = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}
