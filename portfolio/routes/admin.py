"""Panel privado de edición (CRUD).

Todas las rutas están protegidas con Flask-Login (`@login_required`) y los
formularios con CSRF de Flask-WTF.
"""
from __future__ import annotations

from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from ..extensions import db
from ..forms import (
    CambiarPasswordForm,
    CvForm,
    EstudioForm,
    ExperienciaForm,
    PerfilForm,
    ProyectoForm,
    TecnologiaForm,
    TextosSitioForm,
    opciones_select,
)
from ..models import (
    Estudio,
    Experiencia,
    Mensaje,
    Perfil,
    Proyecto,
    Tecnologia,
    TextoSitio,
    Usuario,
)
from .public import NOMBRE_CV, ruta_cv

bp = Blueprint("admin", __name__, url_prefix="/admin")


@bp.before_request
@login_required
def _exigir_sesion():
    """Protege todo el blueprint antes de ejecutar cualquier vista."""
    return


def _aplicar_campos(form, objeto) -> None:
    """Copia los campos del formulario al modelo de forma segura."""
    for nombre in form.CAMPOS:
        campo = getattr(form, nombre)
        valor = campo.data
        if isinstance(valor, str):
            valor = valor.strip()
        if nombre == "orden" and valor is None:
            valor = 0
        setattr(objeto, nombre, valor)

    # Coherencia de fechas: si sigue vigente, no debe existir fecha de fin.
    if getattr(objeto, "en_curso", False) or getattr(objeto, "actual", False):
        objeto.fecha_fin = None

    if getattr(objeto, "imagen_url", None) == "":
        objeto.imagen_url = "img/proyecto-portfolio.svg"
    if getattr(objeto, "avatar_url", None) == "":
        objeto.avatar_url = "img/avatar.svg"


def _listar(modelo, titulo, descripcion, icono, columnas, prefijo: str, lista: str):
    items = modelo.query.order_by(modelo.orden.asc(), modelo.id.desc()).all()
    return render_template(
        "admin/lista.html",
        items=items,
        titulo=titulo,
        descripcion=descripcion,
        icono=icono,
        columnas=columnas,
        nuevo_endpoint=f"admin.{prefijo}_nuevo",
        editar_endpoint=f"admin.{prefijo}_editar",
        eliminar_endpoint=f"admin.{prefijo}_eliminar",
        prefijo=prefijo,
    )


def _formulario(modelo, Formulario, titulo, descripcion, icono, prefijo, lista, item=None):
    form = Formulario(obj=item)
    if form.validate_on_submit():
        es_nuevo = item is None
        if item is None:
            item = modelo()
        _aplicar_campos(form, item)
        if es_nuevo:
            db.session.add(item)
        db.session.commit()
        flash(f"{titulo} {'creado' if es_nuevo else 'actualizado'} correctamente.", "success")
        return redirect(url_for(f"admin.{lista}"))

    return render_template(
        "admin/contenido_form.html",
        form=form,
        titulo=titulo,
        descripcion=descripcion,
        icono=icono,
        item=item,
        prefijo=prefijo,
        cancelar_endpoint=f"admin.{lista}",
    )


@bp.get("/")
def panel():
    mensajes = Mensaje.query.order_by(Mensaje.creado_en.desc()).limit(5).all()
    return render_template(
        "admin/panel.html",
        total_estudios=Estudio.query.count(),
        total_experiencias=Experiencia.query.count(),
        total_tecnologias=Tecnologia.query.count(),
        total_proyectos=Proyecto.query.count(),
        sin_leer=Mensaje.query.filter_by(leido=False).count(),
        mensajes=mensajes,
    )


# ---------------------------------------------------------------------------
# Perfil
# ---------------------------------------------------------------------------
@bp.route("/perfil", methods=["GET", "POST"])
def perfil():
    datos = Perfil.query.first()
    if datos is None:
        datos = Perfil(
            usuario_id=current_user.id,
            nombre=current_user.nombre,
            titulo="Desarrollador Full Stack",
            bio="",
        )
        db.session.add(datos)
        db.session.flush()

    form = PerfilForm(obj=datos)
    if form.validate_on_submit():
        for nombre in PerfilForm.CAMPOS:
            valor = getattr(form, nombre).data
            if isinstance(valor, str):
                valor = valor.strip()
            setattr(datos, nombre, valor)
        if not datos.avatar_url:
            datos.avatar_url = "img/avatar.svg"
        db.session.commit()
        flash("Perfil actualizado. Los cambios ya se ven en el portfolio.", "success")
        return redirect(url_for("admin.perfil"))

    return render_template("admin/perfil.html", form=form, perfil=datos)


# ---------------------------------------------------------------------------
# Textos del sitio y CV
# ---------------------------------------------------------------------------
@bp.route("/contenido", methods=["GET", "POST"])
def contenido():
    """Edita las frases de las plantillas y las guarda en MySQL."""
    textos = TextoSitio.query.order_by(
        TextoSitio.orden.asc(), TextoSitio.id.asc()
    ).all()
    form = TextosSitioForm()
    if form.validate_on_submit():
        # Solo se actualizan las claves enviadas: así un formulario parcial no
        # borra accidentalmente los demás textos del sitio.
        for texto in textos:
            if texto.clave in request.form:
                texto.valor = request.form[texto.clave].strip()
        db.session.commit()
        flash("Textos actualizados. Los cambios ya se ven en el portfolio.", "success")
        return redirect(url_for("admin.contenido"))
    # Se pasa como `filas` para no pisar el dict `textos` del context processor.
    return render_template("admin/textos.html", form=form, filas=textos)


@bp.route("/cv", methods=["GET", "POST"])
def cv():
    """Reemplaza el PDF real del CV que se descarga desde el sitio."""
    ruta = ruta_cv()
    form = CvForm()
    if form.validate_on_submit():
        archivo = form.archivo.data
        nombre = (archivo.filename or "").lower()
        if not nombre.endswith(".pdf"):
            flash("El archivo debe tener extensión .pdf.", "danger")
        else:
            ruta.parent.mkdir(parents=True, exist_ok=True)
            archivo.save(str(ruta))
            flash("CV reemplazado. Ya se puede descargar desde el sitio.", "success")
            return redirect(url_for("admin.cv"))

    existe = ruta.is_file()
    return render_template(
        "admin/cv.html",
        form=form,
        nombre_archivo=NOMBRE_CV,
        existe=existe,
        tamano=ruta.stat().st_size if existe else 0,
        modificado=(
            datetime.fromtimestamp(ruta.stat().st_mtime).strftime("%d/%m/%Y %H:%M")
            if existe else "—"
        ),
    )


# ---------------------------------------------------------------------------
# Estudios
# ---------------------------------------------------------------------------
@bp.get("/estudios")
def estudios():
    return _listar(
        Estudio,
        "Estudios",
        "Formación académica y cursos que se muestran en el portfolio.",
        "fa-solid fa-graduation-cap",
        [
            {"campo": "titulo", "label": "Título"},
            {"campo": "institucion", "label": "Institución"},
            {"campo": "nivel", "label": "Nivel"},
            {"campo": "periodo", "label": "Período"},
            {"campo": "activo", "label": "Visible", "tipo": "bool"},
        ],
        "estudio", "estudios",
    )


@bp.route("/estudios/nuevo", methods=["GET", "POST"])
def estudio_nuevo():
    return _formulario(
        Estudio, EstudioForm, "Nuevo estudio",
        "Agregá una carrera, curso o formación.", "fa-solid fa-graduation-cap",
        "estudio", "estudios",
    )


@bp.route("/estudios/<int:item_id>/editar", methods=["GET", "POST"])
def estudio_editar(item_id):
    item = db.get_or_404(Estudio, item_id)
    return _formulario(
        Estudio, EstudioForm, "Editar estudio",
        "Modificá los datos de la formación.", "fa-solid fa-graduation-cap",
        "estudio", "estudios", item,
    )


@bp.post("/estudios/<int:item_id>/eliminar")
def estudio_eliminar(item_id):
    item = db.get_or_404(Estudio, item_id)
    db.session.delete(item)
    db.session.commit()
    flash("Estudio eliminado.", "info")
    return redirect(url_for("admin.estudios"))


# ---------------------------------------------------------------------------
# Experiencias
# ---------------------------------------------------------------------------
@bp.get("/experiencias")
def experiencias():
    return _listar(
        Experiencia,
        "Experiencia laboral",
        "Puestos y proyectos profesionales.",
        "fa-solid fa-briefcase",
        [
            {"campo": "puesto", "label": "Puesto"},
            {"campo": "empresa", "label": "Empresa"},
            {"campo": "periodo", "label": "Período"},
            {"campo": "modalidad", "label": "Modalidad"},
            {"campo": "activo", "label": "Visible", "tipo": "bool"},
        ],
        "experiencia", "experiencias",
    )


@bp.route("/experiencias/nuevo", methods=["GET", "POST"])
def experiencia_nuevo():
    return _formulario(
        Experiencia, ExperienciaForm, "Nueva experiencia",
        "Registrá un trabajo, pasantía o proyecto profesional.",
        "fa-solid fa-briefcase", "experiencia", "experiencias",
    )


@bp.route("/experiencias/<int:item_id>/editar", methods=["GET", "POST"])
def experiencia_editar(item_id):
    item = db.get_or_404(Experiencia, item_id)
    return _formulario(
        Experiencia, ExperienciaForm, "Editar experiencia",
        "Actualizá las tareas y logros del puesto.",
        "fa-solid fa-briefcase", "experiencia", "experiencias", item,
    )


@bp.post("/experiencias/<int:item_id>/eliminar")
def experiencia_eliminar(item_id):
    item = db.get_or_404(Experiencia, item_id)
    db.session.delete(item)
    db.session.commit()
    flash("Experiencia eliminada.", "info")
    return redirect(url_for("admin.experiencias"))


# ---------------------------------------------------------------------------
# Tecnologías
# ---------------------------------------------------------------------------
@bp.get("/tecnologias")
def tecnologias():
    return _listar(
        Tecnologia,
        "Tecnologías",
        "Herramientas y nivel de conocimiento mostrado en el sitio.",
        "fa-solid fa-layer-group",
        [
            {"campo": "nombre", "label": "Tecnología"},
            {"campo": "categoria", "label": "Categoría"},
            {"campo": "nivel", "label": "Nivel", "tipo": "nivel"},
            {"campo": "activo", "label": "Visible", "tipo": "bool"},
        ],
        "tecnologia", "tecnologias",
    )


@bp.route("/tecnologias/nueva", methods=["GET", "POST"])
def tecnologia_nuevo():
    return _formulario(
        Tecnologia, TecnologiaForm, "Nueva tecnología",
        "Agregá una herramienta con su ícono y nivel.",
        "fa-solid fa-layer-group", "tecnologia", "tecnologias",
    )


@bp.route("/tecnologias/<int:item_id>/editar", methods=["GET", "POST"])
def tecnologia_editar(item_id):
    item = db.get_or_404(Tecnologia, item_id)
    return _formulario(
        Tecnologia, TecnologiaForm, "Editar tecnología",
        "Ajustá el nivel, el color o el ícono.",
        "fa-solid fa-layer-group", "tecnologia", "tecnologias", item,
    )


@bp.post("/tecnologias/<int:item_id>/eliminar")
def tecnologia_eliminar(item_id):
    item = db.get_or_404(Tecnologia, item_id)
    db.session.delete(item)
    db.session.commit()
    flash("Tecnología eliminada.", "info")
    return redirect(url_for("admin.tecnologias"))


# ---------------------------------------------------------------------------
# Proyectos
# ---------------------------------------------------------------------------
def _cargar_choices_proyecto(form: ProyectoForm) -> None:
    form.tecnologias.choices = opciones_select([
        (t.id, t.nombre)
        for t in Tecnologia.query.order_by(Tecnologia.orden.asc(), Tecnologia.nombre.asc())
    ])


@bp.get("/proyectos")
def proyectos():
    return _listar(
        Proyecto,
        "Proyectos",
        "Trabajos destacados con sus tecnologías y enlaces.",
        "fa-solid fa-diagram-project",
        [
            {"campo": "titulo", "label": "Proyecto"},
            {"campo": "tecnologias", "label": "Tecnologías", "tipo": "tecnologias"},
            {"campo": "destacado", "label": "Destacado", "tipo": "bool"},
            {"campo": "activo", "label": "Visible", "tipo": "bool"},
        ],
        "proyecto", "proyectos",
    )


@bp.route("/proyectos/nuevo", methods=["GET", "POST"])
def proyecto_nuevo():
    form = ProyectoForm()
    _cargar_choices_proyecto(form)
    if form.validate_on_submit():
        proyecto = Proyecto()
        _aplicar_campos(form, proyecto)
        proyecto.tecnologias = (
            Tecnologia.query.filter(Tecnologia.id.in_(form.tecnologias.data)).all()
            if form.tecnologias.data
            else []
        )
        db.session.add(proyecto)
        db.session.commit()
        flash("Proyecto creado correctamente.", "success")
        return redirect(url_for("admin.proyectos"))
    return render_template(
        "admin/contenido_form.html",
        form=form,
        titulo="Nuevo proyecto",
        descripcion="Mostrá un trabajo con su descripción, tecnologías y enlaces.",
        icono="fa-solid fa-diagram-project",
        item=None,
        prefijo="proyecto",
        cancelar_endpoint="admin.proyectos",
    )


@bp.route("/proyectos/<int:item_id>/editar", methods=["GET", "POST"])
def proyecto_editar(item_id):
    proyecto = db.get_or_404(Proyecto, item_id)
    form = ProyectoForm(obj=proyecto)
    _cargar_choices_proyecto(form)
    if request.method == "GET":
        form.tecnologias.data = [t.id for t in proyecto.tecnologias]
    if form.validate_on_submit():
        _aplicar_campos(form, proyecto)
        proyecto.tecnologias = (
            Tecnologia.query.filter(Tecnologia.id.in_(form.tecnologias.data)).all()
            if form.tecnologias.data
            else []
        )
        db.session.commit()
        flash("Proyecto actualizado correctamente.", "success")
        return redirect(url_for("admin.proyectos"))
    return render_template(
        "admin/contenido_form.html",
        form=form,
        titulo="Editar proyecto",
        descripcion="Actualizá la descripción, las tecnologías o los enlaces.",
        icono="fa-solid fa-diagram-project",
        item=proyecto,
        prefijo="proyecto",
        cancelar_endpoint="admin.proyectos",
    )


@bp.post("/proyectos/<int:item_id>/eliminar")
def proyecto_eliminar(item_id):
    proyecto = db.get_or_404(Proyecto, item_id)
    db.session.delete(proyecto)
    db.session.commit()
    flash("Proyecto eliminado.", "info")
    return redirect(url_for("admin.proyectos"))


# ---------------------------------------------------------------------------
# Mensajes de contacto
# ---------------------------------------------------------------------------
@bp.get("/mensajes")
def mensajes():
    return render_template(
        "admin/mensajes.html",
        mensajes=Mensaje.query.order_by(Mensaje.creado_en.desc()).all(),
        sin_leer=Mensaje.query.filter_by(leido=False).count(),
    )


@bp.get("/mensajes/<int:item_id>")
def mensaje_detalle(item_id):
    mensaje = db.get_or_404(Mensaje, item_id)
    if not mensaje.leido:
        mensaje.leido = True
        db.session.commit()
    return render_template("admin/mensaje_detalle.html", mensaje=mensaje)


@bp.post("/mensajes/<int:item_id>/leido")
def mensaje_leido(item_id):
    mensaje = db.get_or_404(Mensaje, item_id)
    mensaje.leido = not mensaje.leido
    db.session.commit()
    flash("Estado del mensaje actualizado.", "info")
    return redirect(request.referrer or url_for("admin.mensajes"))


@bp.post("/mensajes/<int:item_id>/eliminar")
def mensaje_eliminar(item_id):
    mensaje = db.get_or_404(Mensaje, item_id)
    db.session.delete(mensaje)
    db.session.commit()
    flash("Mensaje eliminado.", "info")
    return redirect(url_for("admin.mensajes"))


# ---------------------------------------------------------------------------
# Cuenta
# ---------------------------------------------------------------------------
@bp.route("/cuenta", methods=["GET", "POST"])
def cuenta():
    form = CambiarPasswordForm(obj=current_user)
    if form.validate_on_submit():
        username = (form.username.data or "").strip().lower()
        ocupado = Usuario.query.filter(
            Usuario.username == username, Usuario.id != current_user.id
        ).first()
        if ocupado:
            flash("Ese nombre de usuario ya está en uso.", "danger")
        elif form.nueva_password.data:
            if not form.actual_password.data or not current_user.check_password(
                form.actual_password.data
            ):
                flash("La contraseña actual no es correcta.", "danger")
            elif form.nueva_password.data != form.confirmar_password.data:
                flash("Las contraseñas nuevas no coinciden.", "danger")
            else:
                current_user.username = username
                current_user.set_password(form.nueva_password.data)
                db.session.commit()
                flash("Cuenta actualizada correctamente.", "success")
                return redirect(url_for("admin.cuenta"))
        else:
            current_user.username = username
            db.session.commit()
            flash("Nombre de usuario actualizado.", "success")
            return redirect(url_for("admin.cuenta"))

    return render_template("admin/cuenta.html", form=form)
