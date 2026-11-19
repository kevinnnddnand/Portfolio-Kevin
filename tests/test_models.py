"""Pruebas de los modelos: POO, encapsulamiento y relaciones."""
from __future__ import annotations

from datetime import date

import pytest

from portfolio.extensions import db
from portfolio.models import (
    ContenidoPortfolio,
    Estudio,
    Experiencia,
    Mensaje,
    Perfil,
    Proyecto,
    Tecnologia,
    Usuario,
    formatear_mes,
    formatear_periodo,
)


def test_password_se_guarda_hasheada(app):
    with app.app_context():
        usuario = Usuario(username="prueba", nombre="Prueba")
        usuario.set_password("ClaveSegura123")
        db.session.add(usuario)
        db.session.commit()

        assert usuario._password_hash != "ClaveSegura123"
        assert usuario._password_hash.startswith(("scrypt:", "pbkdf2:"))
        assert usuario.check_password("ClaveSegura123") is True
        assert usuario.check_password("incorrecta") is False
        assert "ClaveSegura123" not in repr(usuario)


def test_password_corta_es_rechazada():
    usuario = Usuario(username="prueba", nombre="Prueba")
    with pytest.raises(ValueError):
        usuario.set_password("corta")


def test_perfil_encapsula_email_y_telefono():
    perfil = Perfil(nombre="Kevin", apellido="Pérez", titulo="Dev", bio="Bio")
    perfil.email = "  KEVIN@EXAMPLE.COM "
    perfil.telefono = "+54 11 1234-5678"

    assert perfil.email == "kevin@example.com"
    assert perfil.telefono == "+54111234-5678"
    assert perfil.nombre_completo == "Kevin Pérez"
    assert perfil.iniciales == "KP"

    with pytest.raises(ValueError):
        perfil.email = "formato-invalido"


def test_resumen_es_polimorfico():
    estudio = Estudio(
        institucion="Instituto", titulo="Tecnicatura",
        fecha_inicio=date(2023, 3, 1), en_curso=True,
    )
    experiencia = Experiencia(
        empresa="Empresa", puesto="Developer",
        fecha_inicio=date(2022, 1, 1), actual=True,
    )
    tecnologia = Tecnologia(nombre="Python", nivel=90, categoria="Backend")
    proyecto = Proyecto(titulo="Portfolio", descripcion="Sitio personal")

    resúmenes = [
        estudio.resumen(), experiencia.resumen(),
        tecnologia.resumen(), proyecto.resumen(),
    ]
    assert all(isinstance(texto, str) and texto for texto in resúmenes)
    assert len(set(resúmenes)) == 4
    assert isinstance(estudio, ContenidoPortfolio)
    assert isinstance(proyecto, ContenidoPortfolio)


def test_formateo_de_fechas():
    assert formatear_mes(date(2024, 3, 15)) == "mar 2024"
    assert formatear_mes(None) == ""
    assert formatear_periodo(date(2022, 1, 1), None, False) == "ene 2022 — Actualidad"
    assert formatear_periodo(date(2020, 5, 1), date(2022, 8, 1), False) == "may 2020 — ago 2022"


def test_relacion_muchos_a_muchos(app):
    with app.app_context():
        python = Tecnologia(nombre="Python", nivel=90)
        flask = Tecnologia(nombre="Flask", nivel=85)
        proyecto = Proyecto(titulo="Demo", descripcion="Proyecto demo")
        proyecto.tecnologias = [python, flask]

        db.session.add_all([python, flask, proyecto])
        db.session.commit()

        assert len(proyecto.tecnologias) == 2
        assert proyecto in python.proyectos

        db.session.delete(python)
        db.session.commit()
        assert len(proyecto.tecnologias) == 1
        assert proyecto.tecnologias[0].nombre == "Flask"


def test_to_dict_serializa_fechas(app):
    with app.app_context():
        estudio = Estudio(
            institucion="Instituto", titulo="Curso", fecha_inicio=date(2024, 1, 1),
            fecha_fin=date(2024, 12, 1),
        )
        db.session.add(estudio)
        db.session.commit()

        datos = estudio.to_dict()
        assert datos["fecha_inicio"] == "2024-01-01"
        assert datos["fecha_fin"] == "2024-12-01"
        assert datos["institucion"] == "Instituto"


def test_resumen_de_mensaje():
    mensaje = Mensaje(nombre="Ana", email="ana@example.com", asunto="Hola", mensaje="Texto")
    assert mensaje.resumen() == "Hola — Ana"
