"""Pruebas de las páginas públicas, la API y la descarga del CV."""
from __future__ import annotations


def test_inicio_responde_y_muestra_secciones(client):
    respuesta = client.get("/")
    assert respuesta.status_code == 200
    html = respuesta.get_data(as_text=True)

    for ancla in (
        'id="inicio"',
        'id="sobre-mi"',
        'id="estudios"',
        'id="experiencia"',
        'id="tecnologias"',
        'id="proyectos"',
        'id="ubicacion"',
        'id="contacto"',
    ):
        assert ancla in html

    # Contenido cargado desde la base de datos (datos reales del CV).
    assert "Estudiante de carrera técnica" in html
    assert "Python" in html
    assert "Portfolio Web Full Stack" in html


def test_inicio_incluye_iframe_mapa_y_recursos_requeridos(client):
    html = client.get("/").get_data(as_text=True)

    assert "<iframe" in html
    assert "openstreetmap.org/export/embed.html" in html
    assert "fonts.googleapis.com" in html
    assert "font-awesome" in html
    assert 'rel="icon"' in html
    assert "img/logo.svg" in html


def test_cabeceras_de_seguridad(client):
    respuesta = client.get("/")
    assert respuesta.headers["X-Content-Type-Options"] == "nosniff"
    assert respuesta.headers["X-Frame-Options"] == "SAMEORIGIN"
    assert respuesta.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"


def test_api_portfolio_expone_estructura_json(client):
    respuesta = client.get("/api/portfolio")
    assert respuesta.status_code == 200
    assert respuesta.is_json

    datos = respuesta.get_json()
    assert set(datos) >= {
        "perfil", "estudios", "experiencias", "tecnologias", "proyectos", "generado_en",
    }
    assert datos["perfil"]["nombre"].startswith("Kevin")
    assert len(datos["estudios"]) >= 1
    assert len(datos["tecnologias"]) >= 1
    assert len(datos["proyectos"]) >= 1

    proyecto = datos["proyectos"][0]
    assert isinstance(proyecto["tecnologias"], list)
    assert "resumen" in proyecto


def test_cv_se_descarga_como_pdf(client):
    respuesta = client.get("/cv")
    assert respuesta.status_code == 200
    assert respuesta.mimetype == "application/pdf"
    assert respuesta.data.startswith(b"%PDF")
    assert "attachment" in respuesta.headers["Content-Disposition"]
    assert len(respuesta.data) > 2000


def test_salud_robots_y_favicon(client):
    salud = client.get("/salud")
    assert salud.status_code == 200
    assert salud.get_json()["status"] == "ok"

    robots = client.get("/robots.txt")
    assert robots.status_code == 200
    assert "Disallow: /admin" in robots.get_data(as_text=True)

    favicon = client.get("/favicon.ico")
    assert favicon.status_code == 302
    assert "favicon.svg" in favicon.headers["Location"]


def test_pagina_404_personalizada(client):
    respuesta = client.get("/esta-ruta-no-existe")
    assert respuesta.status_code == 404
    assert "404" in respuesta.get_data(as_text=True)
