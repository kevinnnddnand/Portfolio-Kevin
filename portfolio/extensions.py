"""Instancias compartidas de las extensiones de Flask."""
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()

# Ruta a la que Flask-Login redirige cuando se intenta editar sin sesión.
login_manager.login_view = "auth.login"
login_manager.login_message = "Iniciá sesión para acceder al panel de edición."
login_manager.login_message_category = "info"
login_manager.session_protection = "strong"
