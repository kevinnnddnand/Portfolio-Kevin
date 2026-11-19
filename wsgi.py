"""Punto de entrada WSGI para producción (gunicorn / Clever Cloud)."""
from portfolio import create_app

app = create_app()
