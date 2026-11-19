"""Formularios Flask-WTF.

Todos los formularios incluyen protección CSRF automática. Además, los
validadores del lado del servidor evitan datos inválidos aunque el usuario
manipule el HTML.
"""
from __future__ import annotations

from typing import ClassVar

from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import (
    BooleanField,
    DateField,
    EmailField,
    HiddenField,
    IntegerField,
    PasswordField,
    SelectField,
    SelectMultipleField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import (
    URL,
    DataRequired,
    Email,
    Length,
    NumberRange,
    Optional,
    ValidationError,
)

try:  # WTForms >= 3.3 recomienda SelectChoice en lugar de tuplas.
    from wtforms.fields.choices import SelectChoice
except ImportError:  # pragma: no cover - WTForms 3.2
    SelectChoice = None  # type: ignore[assignment]


def opciones_select(pares: list[tuple]) -> list:
    """Convierte pares (valor, etiqueta) al formato recomendado por WTForms."""
    if SelectChoice is None:  # pragma: no cover - WTForms 3.2
        return list(pares)
    return [SelectChoice(str(valor), str(etiqueta)) for valor, etiqueta in pares]


class LoginForm(FlaskForm):
    """Autenticación mediante usuario y contraseña (Flask-WTF)."""

    username = StringField(
        "Usuario",
        validators=[DataRequired("Ingresá tu usuario."), Length(max=60)],
        render_kw={"autocomplete": "username", "placeholder": "kevinAdmin"},
    )
    password = PasswordField(
        "Contraseña",
        validators=[DataRequired("Ingresá tu contraseña.")],
        render_kw={"autocomplete": "current-password", "placeholder": "••••••••"},
    )
    remember = BooleanField("Mantener sesión iniciada")
    submit = SubmitField("Ingresar")


class PerfilForm(FlaskForm):
    """Edición de los datos personales mostrados en el sitio."""

    nombre = StringField("Nombre", validators=[DataRequired(), Length(max=80)])
    apellido = StringField("Apellido", validators=[Optional(), Length(max=80)])
    titulo = StringField(
        "Título profesional", validators=[DataRequired(), Length(max=150)]
    )
    subtitulo = StringField("Subtítulo", validators=[Optional(), Length(max=180)])
    bio = TextAreaField(
        "Sobre mí", validators=[DataRequired(), Length(max=3000)],
        render_kw={"rows": 6},
    )
    email = EmailField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    telefono = StringField("Teléfono", validators=[Optional(), Length(max=40)])
    ubicacion = StringField("Ubicación", validators=[Optional(), Length(max=120)])
    linkedin = StringField(
        "LinkedIn", validators=[Optional(), URL(), Length(max=255)],
        render_kw={"placeholder": "https://linkedin.com/in/usuario"},
    )
    github = StringField(
        "GitHub", validators=[Optional(), URL(), Length(max=255)],
        render_kw={"placeholder": "https://github.com/usuario"},
    )
    sitio_web = StringField(
        "Sitio web", validators=[Optional(), URL(), Length(max=255)],
        render_kw={"placeholder": "https://tusitio.com"},
    )
    disponibilidad = StringField(
        "Disponibilidad", validators=[Optional(), Length(max=120)],
        render_kw={"placeholder": "Disponible para proyectos freelance"},
    )
    cv_resumen = TextAreaField(
        "Resumen para el CV", validators=[Optional(), Length(max=2000)],
        render_kw={"rows": 4},
    )
    avatar_url = StringField(
        "Avatar (ruta o URL)", validators=[Optional(), Length(max=255)],
        render_kw={"placeholder": "img/avatar.svg"},
    )
    submit = SubmitField("Guardar perfil")

    CAMPOS: ClassVar[list[str]] = [
        "nombre", "apellido", "titulo", "subtitulo", "bio", "email", "telefono",
        "ubicacion", "linkedin", "github", "sitio_web", "disponibilidad",
        "cv_resumen", "avatar_url",
    ]


class EstudioForm(FlaskForm):
    """Alta y edición de estudios cursados."""

    institucion = StringField(
        "Institución", validators=[DataRequired(), Length(max=160)]
    )
    titulo = StringField("Título / carrera", validators=[DataRequired(), Length(max=160)])
    area = StringField("Área de estudio", validators=[Optional(), Length(max=120)])
    nivel = SelectField(
        "Nivel",
        choices=[
            "Secundario",
            "Terciario",
            "Universitario",
            "Curso",
            "Posgrado",
        ],
        validators=[DataRequired()],
    )
    fecha_inicio = DateField(
        "Fecha de inicio", validators=[DataRequired("Indicá la fecha de inicio.")]
    )
    fecha_fin = DateField("Fecha de fin", validators=[Optional()])
    en_curso = BooleanField("Actualmente en curso")
    descripcion = TextAreaField(
        "Descripción", validators=[Optional(), Length(max=2000)],
        render_kw={"rows": 4},
    )
    orden = IntegerField("Orden", validators=[Optional()], default=0)
    activo = BooleanField("Visible en el portfolio", default=True)
    submit = SubmitField("Guardar estudio")

    CAMPOS: ClassVar[list[str]] = [
        "institucion", "titulo", "area", "nivel", "fecha_inicio", "fecha_fin",
        "en_curso", "descripcion", "orden", "activo",
    ]

    def validate_fecha_fin(self, campo):
        if self.en_curso.data:
            return
        if not campo.data:
            raise ValidationError("Indicá una fecha de fin o marcá 'en curso'.")
        if self.fecha_inicio.data and campo.data < self.fecha_inicio.data:
            raise ValidationError("La fecha de fin no puede ser anterior al inicio.")


class ExperienciaForm(FlaskForm):
    """Alta y edición de experiencia laboral."""

    empresa = StringField("Empresa / organización", validators=[DataRequired(), Length(max=160)])
    puesto = StringField("Puesto", validators=[DataRequired(), Length(max=160)])
    ubicacion = StringField("Ubicación", validators=[Optional(), Length(max=120)])
    modalidad = SelectField(
        "Modalidad",
        choices=[
            "Remoto",
            "Híbrido",
            "Presencial",
        ],
        validators=[DataRequired()],
    )
    fecha_inicio = DateField(
        "Fecha de inicio", validators=[DataRequired("Indicá la fecha de inicio.")]
    )
    fecha_fin = DateField("Fecha de fin", validators=[Optional()])
    actual = BooleanField("Trabajo actualmente aquí")
    descripcion = TextAreaField(
        "Descripción", validators=[Optional(), Length(max=3000)],
        render_kw={"rows": 4},
    )
    logros = TextAreaField(
        "Logros (uno por línea)", validators=[Optional(), Length(max=3000)],
        render_kw={"rows": 4, "placeholder": "• Desarrollé...\n• Automaticé..."},
    )
    orden = IntegerField("Orden", validators=[Optional()], default=0)
    activo = BooleanField("Visible en el portfolio", default=True)
    submit = SubmitField("Guardar experiencia")

    CAMPOS: ClassVar[list[str]] = [
        "empresa", "puesto", "ubicacion", "modalidad", "fecha_inicio", "fecha_fin",
        "actual", "descripcion", "logros", "orden", "activo",
    ]

    def validate_fecha_fin(self, campo):
        if self.actual.data:
            return
        if not campo.data:
            raise ValidationError("Indicá una fecha de fin o marcá 'trabajo actual'.")
        if self.fecha_inicio.data and campo.data < self.fecha_inicio.data:
            raise ValidationError("La fecha de fin no puede ser anterior al inicio.")


class TecnologiaForm(FlaskForm):
    """Alta y edición de tecnologías y su nivel."""

    nombre = StringField("Nombre", validators=[DataRequired(), Length(max=80)])
    categoria = SelectField(
        "Categoría",
        choices=[
            "Backend",
            "Frontend",
            "Base de datos",
            "Herramientas",
            "Otros",
        ],
        validators=[DataRequired()],
    )
    nivel = IntegerField(
        "Nivel (%)", validators=[DataRequired(), NumberRange(min=0, max=100)], default=70
    )
    icono = StringField(
        "Ícono FontAwesome", validators=[DataRequired(), Length(max=80)],
        render_kw={"placeholder": "fa-brands fa-python"},
    )
    color = StringField(
        "Color", validators=[DataRequired(), Length(max=20)],
        render_kw={"placeholder": "#38e0c8"},
    )
    orden = IntegerField("Orden", validators=[Optional()], default=0)
    activo = BooleanField("Visible en el portfolio", default=True)
    submit = SubmitField("Guardar tecnología")

    CAMPOS: ClassVar[list[str]] = [
        "nombre", "categoria", "nivel", "icono", "color", "orden", "activo"
    ]

    def validate_color(self, campo):
        valor = (campo.data or "").strip()
        if not (valor.startswith("#") and len(valor) in {4, 7}):
            raise ValidationError("Usá un color hexadecimal, por ejemplo #38e0c8.")


class ProyectoForm(FlaskForm):
    """Alta y edición de proyectos."""

    titulo = StringField("Título", validators=[DataRequired(), Length(max=160)])
    descripcion = TextAreaField(
        "Descripción", validators=[DataRequired(), Length(max=3000)],
        render_kw={"rows": 5},
    )
    tecnologias = SelectMultipleField(
        "Tecnologías", coerce=int, validators=[Optional()],
        render_kw={"size": 8},
    )
    repo_url = StringField(
        "Repositorio", validators=[Optional(), URL(), Length(max=255)],
        render_kw={"placeholder": "https://github.com/usuario/repo"},
    )
    demo_url = StringField(
        "Demo en vivo", validators=[Optional(), URL(), Length(max=255)],
        render_kw={"placeholder": "https://mi-proyecto.com"},
    )
    imagen_url = StringField(
        "Portada (ruta o URL)", validators=[Optional(), Length(max=255)],
        render_kw={"placeholder": "img/proyecto-portfolio.svg"},
    )
    destacado = BooleanField("Destacado")
    orden = IntegerField("Orden", validators=[Optional()], default=0)
    activo = BooleanField("Visible en el portfolio", default=True)
    submit = SubmitField("Guardar proyecto")

    CAMPOS: ClassVar[list[str]] = [
        "titulo", "descripcion", "repo_url", "demo_url", "imagen_url",
        "destacado", "orden", "activo",
    ]


class ContactoForm(FlaskForm):
    """Formulario público de contacto."""

    nombre = StringField(
        "Nombre", validators=[DataRequired("Contame tu nombre."), Length(max=120)]
    )
    email = EmailField("Email", validators=[DataRequired("Ingresá tu email."), Email()])
    asunto = StringField(
        "Asunto", validators=[DataRequired("Indicá un asunto."), Length(max=160)]
    )
    mensaje = TextAreaField(
        "Mensaje", validators=[DataRequired("Escribí tu mensaje."), Length(min=10, max=4000)],
        render_kw={"rows": 6, "placeholder": "Hola Kevin, me gustaría..."},
    )
    # Honeypot anti-spam: invisible para personas, tentador para bots.
    website = HiddenField("Sitio web", render_kw={"tabindex": "-1", "autocomplete": "off"})
    submit = SubmitField("Enviar mensaje")

    def validate_website(self, campo):
        if campo.data:
            raise ValidationError("Mensaje rechazado.")


class CambiarPasswordForm(FlaskForm):
    """Cambio de contraseña del administrador."""

    username = StringField("Usuario", validators=[DataRequired(), Length(max=60)])
    actual_password = PasswordField(
        "Contraseña actual", validators=[Optional()],
        render_kw={"autocomplete": "current-password"},
    )
    nueva_password = PasswordField(
        "Nueva contraseña", validators=[Optional(), Length(min=8, max=128)],
        render_kw={"autocomplete": "new-password"},
    )
    confirmar_password = PasswordField(
        "Repetir nueva contraseña", validators=[Optional(), Length(min=8, max=128)],
        render_kw={"autocomplete": "new-password"},
    )
    submit = SubmitField("Actualizar cuenta")


class TextosSitioForm(FlaskForm):
    """Formulario base del editor de textos; los campos se generan desde la BD.

    Los nombres de los campos son las claves de `textos_sitio`, por eso no se
    declaran aquí. El token CSRF sí se incluye con `hidden_tag()`.
    """

    submit = SubmitField("Guardar textos")


class CvForm(FlaskForm):
    """Reemplaza el PDF del CV que descarga el sitio."""

    archivo = FileField(
        "Archivo PDF",
        validators=[DataRequired("Elegí un archivo PDF.")],
        render_kw={"accept": "application/pdf,.pdf"},
    )
    submit = SubmitField("Subir CV")


class MensajeRespuestaForm(FlaskForm):
    """Formulario mínimo para operaciones POST sobre mensajes."""

    submit = SubmitField("Enviar")
