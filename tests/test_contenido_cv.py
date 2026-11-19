"""Pruebas del editor de textos y del CV PDF subido desde el panel."""
from __future__ import annotations

from io import BytesIO

from portfolio.extensions import db
from portfolio.models import TextoSitio
from portfolio.routes.public import NOMBRE_CV, ruta_cv
from portfolio.seed import seed_textos


def test_editor_textos_requiere_sesion(client):
    respuesta = client.get("/admin/contenido")
    assert respuesta.status_code == 302
    assert "/login" in respuesta.headers["Location"]


def test_editor_textos_muestra_claves_y_guarda_en_bd(auth_client, app):
    pagina = auth_client.get("/admin/contenido")
    assert pagina.status_code == 200
    html = pagina.get_data(as_text=True)
    assert "Contenido del sitio" in html
    assert "sitio.marca" in html

    respuesta = auth_client.post(
        "/admin/contenido",
        data={"sitio.marca": "kevin.dev.test", "boton.descargar_cv": "Bajar CV"},
        follow_redirects=False,
    )
    assert respuesta.status_code == 302

    with app.app_context():
        assert TextoSitio.query.filter_by(clave="sitio.marca").one().valor == "kevin.dev.test"
        assert TextoSitio.query.filter_by(clave="boton.descargar_cv").one().valor == "Bajar CV"
        # Las claves no enviadas se conservan.
        assert TextoSitio.query.filter_by(clave="mapa.badge_titulo").one().valor == "Villa San Nicolás"


def test_cambio_de_texto_se_refleja_en_el_sitio_publico(auth_client, app, client):
    auth_client.post("/admin/contenido", data={"sobre.titulo_1": "Texto cambiado,"})
    html = client.get("/").get_data(as_text=True)
    assert "Texto cambiado," in html

    # El change persiste en SQLite aunque se ejecute el seed nuevamente.
    with app.app_context():
        insertados = seed_textos()
        assert insertados == 0
        assert TextoSitio.query.filter_by(clave="sobre.titulo_1").one().valor == "Texto cambiado,"
        db.session.rollback()


def test_cv_real_tiene_prioridad_sobre_el_pdf_generado(app, client, tmp_path, monkeypatch):
    """Si existe el PDF subido, /cv lo sirve sin generar uno nuevo."""
    uploads = tmp_path / "uploads"
    uploads.mkdir()
    pdf = uploads / NOMBRE_CV
    contenido = b"%PDF-1.4\n% CV real de prueba\n%%EOF\n"
    pdf.write_bytes(contenido)

    monkeypatch.setattr(app, "static_folder", str(tmp_path))
    with app.app_context():
        assert ruta_cv() == pdf

    respuesta = client.get("/cv")
    assert respuesta.status_code == 200
    assert respuesta.data == contenido
    assert NOMBRE_CV in respuesta.headers["Content-Disposition"]


def test_subir_cv_desde_el_panel_reemplaza_el_pdf(auth_client, app, tmp_path, monkeypatch):
    monkeypatch.setattr(app, "static_folder", str(tmp_path))

    pagina = auth_client.get("/admin/cv")
    assert pagina.status_code == 200
    assert "Mi CV" in pagina.get_data(as_text=True)

    contenido = b"%PDF-1.4\n% Nuevo CV subido\n%%EOF\n"
    respuesta = auth_client.post(
        "/admin/cv",
        data={"archivo": (BytesIO(contenido), "cv-rrhh.pdf")},
        content_type="multipart/form-data",
        follow_redirects=False,
    )
    assert respuesta.status_code == 302

    with app.app_context():
        assert ruta_cv().read_bytes() == contenido
