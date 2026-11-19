"""Pruebas del panel de administración y del CRUD."""
# pyright: reportOptionalMemberAccess=false
# Los `.first()` pueden devolver None según el analizador, pero el fixture
# `auth_client` siembra los datos que estas pruebas consultan.
from __future__ import annotations

from portfolio.extensions import db
from portfolio.models import Estudio, Experiencia, Mensaje, Perfil, Proyecto, Tecnologia


def test_panel_muestra_resumen(auth_client):
    respuesta = auth_client.get("/admin/")
    assert respuesta.status_code == 200
    html = respuesta.get_data(as_text=True)
    assert "Panel" in html
    assert "Mensajes" in html


def test_listados_del_panel(auth_client):
    for ruta in (
        "/admin/perfil",
        "/admin/estudios",
        "/admin/experiencias",
        "/admin/tecnologias",
        "/admin/proyectos",
        "/admin/mensajes",
        "/admin/cuenta",
    ):
        respuesta = auth_client.get(ruta)
        assert respuesta.status_code == 200, ruta


def test_crear_editar_y_eliminar_estudio(auth_client, app):
    respuesta = auth_client.post(
        "/admin/estudios/nuevo",
        data={
            "institucion": "Universidad de Prueba",
            "titulo": "Licenciatura en Sistemas",
            "area": "Sistemas",
            "nivel": "Universitario",
            "fecha_inicio": "2020-03-01",
            "en_curso": "y",
            "descripcion": "Carrera de prueba",
            "orden": "9",
            "activo": "y",
        },
        follow_redirects=False,
    )
    assert respuesta.status_code == 302

    with app.app_context():
        estudio = Estudio.query.filter_by(institucion="Universidad de Prueba").one()
        estudio_id = estudio.id
        assert estudio.en_curso is True
        assert estudio.fecha_fin is None
        assert estudio.periodo.endswith("Actualidad")

    respuesta = auth_client.post(
        f"/admin/estudios/{estudio_id}/editar",
        data={
            "institucion": "Universidad de Prueba",
            "titulo": "Licenciatura en Sistemas (actualizado)",
            "area": "Sistemas",
            "nivel": "Universitario",
            "fecha_inicio": "2020-03-01",
            "fecha_fin": "2025-12-01",
            "en_curso": "",
            "descripcion": "Carrera finalizada",
            "orden": "9",
            "activo": "y",
        },
        follow_redirects=False,
    )
    assert respuesta.status_code == 302
    with app.app_context():
        estudio = db.session.get(Estudio, estudio_id)
        assert estudio.titulo.endswith("(actualizado)")
        assert estudio.fecha_fin is not None

    respuesta = auth_client.post(
        f"/admin/estudios/{estudio_id}/eliminar", follow_redirects=False
    )
    assert respuesta.status_code == 302
    with app.app_context():
        assert db.session.get(Estudio, estudio_id) is None


def test_formulario_invalido_no_guarda(auth_client, app):
    with app.app_context():
        antes = Estudio.query.count()

    respuesta = auth_client.post(
        "/admin/estudios/nuevo",
        data={
            "institucion": "",
            "titulo": "",
            "nivel": "Universitario",
            "fecha_inicio": "",
        },
        follow_redirects=True,
    )
    assert respuesta.status_code == 200
    assert "Revisá los campos marcados" in respuesta.get_data(as_text=True)

    with app.app_context():
        assert Estudio.query.count() == antes


def test_crear_experiencia_con_logros(auth_client, app):
    respuesta = auth_client.post(
        "/admin/experiencias/nuevo",
        data={
            "empresa": "Empresa de Prueba",
            "puesto": "Backend Developer",
            "ubicacion": "Remoto",
            "modalidad": "Remoto",
            "fecha_inicio": "2021-01-01",
            "actual": "y",
            "descripcion": "Desarrollo de APIs",
            "logros": "Logro uno\nLogro dos",
            "orden": "5",
            "activo": "y",
        },
    )
    assert respuesta.status_code == 302
    with app.app_context():
        experiencia = Experiencia.query.filter_by(empresa="Empresa de Prueba").one()
        assert experiencia.lista_logros == ["Logro uno", "Logro dos"]
        assert experiencia.actual is True


def test_proyecto_con_relacion_nm(auth_client, app):
    with app.app_context():
        ids = [t.id for t in Tecnologia.query.order_by(Tecnologia.id).limit(2).all()]

    respuesta = auth_client.post(
        "/admin/proyectos/nuevo",
        data={
            "titulo": "Proyecto N:M",
            "descripcion": "Proyecto con dos tecnologías asociadas",
            "tecnologias": [str(i) for i in ids],
            "repo_url": "https://github.com/example/nm",
            "demo_url": "",
            "imagen_url": "",
            "destacado": "y",
            "orden": "1",
            "activo": "y",
        },
    )
    assert respuesta.status_code == 302
    with app.app_context():
        proyecto = Proyecto.query.filter_by(titulo="Proyecto N:M").one()
        assert {t.id for t in proyecto.tecnologias} == set(ids)
        assert proyecto.imagen_url == "img/proyecto-portfolio.svg"

        proyecto_id = proyecto.id
        proyecto.tecnologias = []
        db.session.commit()
        assert proyecto.tecnologias == []

        # La eliminación en cascada no debe romper la tabla intermedia.
        db.session.delete(proyecto)
        db.session.commit()
        assert db.session.get(Proyecto, proyecto_id) is None


def test_actualizar_perfil(auth_client, app):
    respuesta = auth_client.post(
        "/admin/perfil",
        data={
            "nombre": "Kevin",
            "apellido": "Pérez",
            "titulo": "Desarrollador Full Stack",
            "subtitulo": "Python · Flask",
            "bio": "Biografía actualizada desde el panel.",
            "email": "kevin@example.com",
            "telefono": "+54 11 1234-5678",
            "ubicacion": "Villa San Nicolás, Malagueño, Córdoba",
            "linkedin": "https://linkedin.com/in/kevin",
            "github": "https://github.com/kevin",
            "sitio_web": "",
            "disponibilidad": "Disponible",
            "cv_resumen": "Resumen para el CV",
            "avatar_url": "",
        },
    )
    assert respuesta.status_code == 302
    with app.app_context():
        perfil = Perfil.query.first()
        assert perfil.nombre_completo == "Kevin Pérez"
        assert perfil.email == "kevin@example.com"
        assert perfil.telefono == "+54111234-5678"
        assert perfil.avatar_url == "img/avatar.svg"


def test_mensaje_de_contacto_flujo_completo(auth_client, app):
    respuesta = auth_client.post(
        "/contacto",
        data={
            "nombre": "Ana",
            "email": "ana@example.com",
            "asunto": "Consulta",
            "mensaje": "Este es un mensaje válido con más de diez caracteres.",
        },
        follow_redirects=True,
    )
    assert respuesta.status_code == 200
    assert "Gracias por escribirme" in respuesta.get_data(as_text=True)

    with app.app_context():
        mensaje = Mensaje.query.filter_by(email="ana@example.com").one()
        assert mensaje.leido is False
        mensaje_id = mensaje.id

    listado = auth_client.get("/admin/mensajes")
    assert listado.status_code == 200

    detalle = auth_client.get(f"/admin/mensajes/{mensaje_id}")
    assert detalle.status_code == 200
    assert "Consulta" in detalle.get_data(as_text=True)

    with app.app_context():
        assert db.session.get(Mensaje, mensaje_id).leido is True

    auth_client.post(f"/admin/mensajes/{mensaje_id}/leido")
    with app.app_context():
        assert db.session.get(Mensaje, mensaje_id).leido is False

    auth_client.post(f"/admin/mensajes/{mensaje_id}/eliminar")
    with app.app_context():
        assert db.session.get(Mensaje, mensaje_id) is None
