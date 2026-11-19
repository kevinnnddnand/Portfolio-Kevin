"""Pruebas del formulario público de contacto y sus validaciones."""
from __future__ import annotations

from portfolio.models import Mensaje


def test_contacto_valido_guarda_mensaje(client, app):
    respuesta = client.post(
        "/contacto",
        data={
            "nombre": "  Ana Pérez ",
            "email": "ANA@EXAMPLE.COM",
            "asunto": "  Propuesta ",
            "mensaje": "Me interesa trabajar con vos en un proyecto nuevo.",
        },
        follow_redirects=True,
    )
    assert respuesta.status_code == 200
    assert "Gracias por escribirme" in respuesta.get_data(as_text=True)

    with app.app_context():
        mensaje = Mensaje.query.filter_by(email="ana@example.com").one()
        assert mensaje.nombre == "Ana Pérez"
        assert mensaje.asunto == "Propuesta"
        assert mensaje.leido is False


def test_contacto_con_mensaje_corto_no_guarda(client, app):
    respuesta = client.post(
        "/contacto",
        data={
            "nombre": "Ana",
            "email": "ana@example.com",
            "asunto": "Hola",
            "mensaje": "corto",
        },
        follow_redirects=True,
    )
    assert respuesta.status_code == 200
    with app.app_context():
        assert Mensaje.query.count() == 0


def test_contacto_con_email_invalido_no_guarda(client, app):
    respuesta = client.post(
        "/contacto",
        data={
            "nombre": "Ana",
            "email": "no-es-un-email",
            "asunto": "Hola",
            "mensaje": "Este mensaje tiene la longitud suficiente.",
        },
        follow_redirects=True,
    )
    assert respuesta.status_code == 200
    with app.app_context():
        assert Mensaje.query.count() == 0


def test_honeypot_rechaza_bots(client, app):
    respuesta = client.post(
        "/contacto",
        data={
            "nombre": "Bot",
            "email": "bot@example.com",
            "asunto": "Spam",
            "mensaje": "Contenido automático con longitud suficiente.",
            "website": "https://spam.example",
        },
        follow_redirects=True,
    )
    assert respuesta.status_code == 200
    assert "Mensaje rechazado" in respuesta.get_data(as_text=True)
    with app.app_context():
        assert Mensaje.query.count() == 0
