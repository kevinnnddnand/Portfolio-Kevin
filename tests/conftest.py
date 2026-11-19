"""Fixtures compartidas por la suite de pruebas."""
from __future__ import annotations

import pytest

from portfolio import create_app
from portfolio.extensions import db
from portfolio.seed import seed_database

ADMIN_USER = "kevinAdmin"
ADMIN_PASSWORD = "kevin1504"


@pytest.fixture()
def app():
    """Aplicación aislada con SQLite en memoria y datos de demostración."""
    aplicacion = create_app("testing")
    with aplicacion.app_context():
        db.create_all()
        seed_database(ADMIN_USER, ADMIN_PASSWORD, "Kevin")
        yield aplicacion
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def auth_client(client):
    """Cliente con la sesión del administrador iniciada."""
    respuesta = client.post(
        "/login",
        data={"username": ADMIN_USER, "password": ADMIN_PASSWORD},
        follow_redirects=False,
    )
    assert respuesta.status_code == 302
    return client
