"""Pruebas del login, logout y protección del panel."""
from __future__ import annotations

from conftest import ADMIN_PASSWORD, ADMIN_USER


def test_formulario_de_login_disponible(client):
    respuesta = client.get("/login")
    assert respuesta.status_code == 200
    assert "Ingresar" in respuesta.get_data(as_text=True)


def test_login_con_credenciales_invalidas(client):
    respuesta = client.post(
        "/login",
        data={"username": ADMIN_USER, "password": "clave-incorrecta"},
        follow_redirects=True,
    )
    assert respuesta.status_code == 200
    assert "Usuario o contraseña incorrectos" in respuesta.get_data(as_text=True)


def test_login_valido_redirige_al_panel(client):
    respuesta = client.post(
        "/login",
        data={"username": ADMIN_USER, "password": ADMIN_PASSWORD},
        follow_redirects=False,
    )
    assert respuesta.status_code == 302
    assert respuesta.headers["Location"].endswith("/admin/")


def test_login_ignora_redirecciones_externas(client):
    respuesta = client.post(
        "/login?next=https://sitio-malicioso.example",
        data={"username": ADMIN_USER, "password": ADMIN_PASSWORD},
        follow_redirects=False,
    )
    assert respuesta.status_code == 302
    assert respuesta.headers["Location"].endswith("/admin/")


def test_panel_protegido_redirige_al_login(client):
    respuesta = client.get("/admin/", follow_redirects=False)
    assert respuesta.status_code == 302
    assert "/login" in respuesta.headers["Location"]


def test_post_administrativo_protegido(client):
    respuesta = client.post("/admin/estudios/1/eliminar", follow_redirects=False)
    assert respuesta.status_code == 302
    assert "/login" in respuesta.headers["Location"]


def test_logout_cierra_la_sesion(auth_client):
    respuesta = auth_client.post("/logout", follow_redirects=False)
    assert respuesta.status_code == 302
    assert respuesta.headers["Location"].endswith("/")

    # Después del logout el panel vuelve a exigir autenticación.
    respuesta = auth_client.get("/admin/", follow_redirects=False)
    assert respuesta.status_code == 302
    assert "/login" in respuesta.headers["Location"]


def test_cuenta_permite_cambiar_password(auth_client):
    respuesta = auth_client.post(
        "/admin/cuenta",
        data={
            "username": ADMIN_USER,
            "actual_password": ADMIN_PASSWORD,
            "nueva_password": "NuevaClave2026!",
            "confirmar_password": "NuevaClave2026!",
        },
        follow_redirects=True,
    )
    assert respuesta.status_code == 200
    assert "Cuenta actualizada" in respuesta.get_data(as_text=True)

    auth_client.post("/logout")
    nuevo_login = auth_client.post(
        "/login",
        data={"username": ADMIN_USER, "password": "NuevaClave2026!"},
        follow_redirects=False,
    )
    assert nuevo_login.status_code == 302
    assert nuevo_login.headers["Location"].endswith("/admin/")


def test_cuenta_rechaza_password_actual_incorrecta(auth_client):
    respuesta = auth_client.post(
        "/admin/cuenta",
        data={
            "username": ADMIN_USER,
            "actual_password": "no-es-la-clave",
            "nueva_password": "OtraClave2026!",
            "confirmar_password": "OtraClave2026!",
        },
        follow_redirects=True,
    )
    assert "La contraseña actual no es correcta" in respuesta.get_data(as_text=True)
