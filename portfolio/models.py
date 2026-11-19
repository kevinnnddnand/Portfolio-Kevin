"""Modelo de dominio del portfolio.

Aquí se aplican los cuatro pilares de la Programación Orientada a Objetos:

* ABSTRACCIÓN: `Persona` y `ContenidoPortfolio` son clases abstractas que
  definen el contrato común (nombre completo / resumen) sin implementar los
  detalles de cada entidad.
* HERENCIA: `Perfil` hereda de `Persona`; `Estudio`, `Experiencia`,
  `Tecnologia` y `Proyecto` heredan de `ContenidoPortfolio`; todas heredan de
  `ModeloBase`, que aporta comportamiento común de persistencia.
* ENCAPSULAMIENTO: `Usuario` y `Perfil` protegen datos sensibles (contraseña,
  email, teléfono) detrás de atributos privados, propiedades y métodos.
* POLIMORFISMO: cada subclase de `ContenidoPortfolio` (incluida `TextoSitio`)
  sobrescribe `resumen()` y responde de forma distinta ante el mismo mensaje.
"""
from __future__ import annotations

from abc import ABC, ABCMeta, abstractmethod
from datetime import UTC, date, datetime

from flask_login import UserMixin
from flask_sqlalchemy.model import DefaultMeta
from werkzeug.security import check_password_hash, generate_password_hash

from .extensions import db


class MetaModelo(DefaultMeta, ABCMeta):
    """Metaclase que combina el modelo declarativo de SQLAlchemy con ABC.

    Permite que las clases de la base de datos también sean clases abstractas
    de Python, sin conflictos de metaclases.
    """


def ahora() -> datetime:
    """Fecha/hora UTC sin zona, compatible con MySQL DATETIME."""
    return datetime.now(UTC).replace(tzinfo=None)


MESES_CORTOS = (
    "ene", "feb", "mar", "abr", "may", "jun",
    "jul", "ago", "sep", "oct", "nov", "dic",
)


def formatear_mes(valor: date | None) -> str:
    """Convierte una fecha en 'mar 2024' para mostrarla en las plantillas."""
    if not valor:
        return ""
    return f"{MESES_CORTOS[valor.month - 1]} {valor.year}"


def formatear_periodo(inicio: date | None, fin: date | None, vigente: bool) -> str:
    """Devuelve un período legible, por ejemplo 'mar 2022 — Actualidad'."""
    desde = formatear_mes(inicio)
    if vigente or not fin:
        return f"{desde} — Actualidad" if desde else "Actualidad"
    return f"{desde} — {formatear_mes(fin)}" if desde else formatear_mes(fin)


class ModeloBase(db.Model, ABC, metaclass=MetaModelo):
    """Base abstracta de todos los modelos persistentes.

    Centraliza la serialización a JSON que utiliza la API pública y el
    `__repr__` de depuración. Es también un ejemplo de herencia reutilizable.
    """

    __abstract__ = True

    def to_dict(self) -> dict:
        """Serializa únicamente las columnas reales de la tabla."""
        datos = {}
        for columna in self.__table__.columns:
            valor = getattr(self, columna.name)
            if isinstance(valor, (date, datetime)):
                valor = valor.isoformat()
            datos[columna.name] = valor
        return datos

    def __repr__(self) -> str:  # pragma: no cover - solo ayuda al depurar
        return f"<{self.__class__.__name__} id={getattr(self, 'id', None)}>"


# ---------------------------------------------------------------------------
# ABSTRACCIÓN: contratos de dominio
# ---------------------------------------------------------------------------
class Persona(ABC):
    """Contrato abstracto para una persona del portfolio."""

    @property
    @abstractmethod
    def nombre_completo(self) -> str:
        """Nombre y apellido listos para mostrar."""

    @abstractmethod
    def resumen(self) -> str:
        """Descripción breve de la persona."""


class ContenidoPortfolio(ModeloBase):
    """Contrato abstracto para todo contenido que se muestra en el sitio.

    No representa una tabla: define el mensaje `resumen()` que cada subclase
    implementa (polimorfismo).
    """

    __abstract__ = True

    @abstractmethod
    def resumen(self) -> str:
        """Texto breve que resume el contenido."""


# ---------------------------------------------------------------------------
# Usuarios y perfil
# ---------------------------------------------------------------------------
class Usuario(UserMixin, ModeloBase):
    """Cuenta con acceso al panel de edición.

    ENCAPSULAMIENTO: el hash de la contraseña se guarda en `_password_hash`
    (atributo protegido) y solo se puede establecer o verificar mediante
    `set_password()` y `check_password()`. Nunca se expone en plantillas ni
    en la API.
    """

    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(60), unique=True, nullable=False, index=True)
    _password_hash = db.Column("password_hash", db.String(255), nullable=False)
    nombre = db.Column(db.String(120), nullable=False, default="Administrador")
    activo = db.Column(db.Boolean, nullable=False, default=True)
    creado_en = db.Column(db.DateTime, nullable=False, default=ahora)
    ultimo_acceso = db.Column(db.DateTime, nullable=True)

    def set_password(self, password_plano: str) -> None:
        """Genera y almacena un hash seguro (Werkzeug PBKDF2)."""
        if not password_plano or len(password_plano) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres.")
        self._password_hash = generate_password_hash(password_plano)

    def check_password(self, password_plano: str) -> bool:
        """Compara una contraseña en texto plano contra el hash almacenado."""
        return bool(password_plano) and check_password_hash(
            self._password_hash, password_plano
        )

    @property
    def is_active(self) -> bool:  # type: ignore[override]  # Flask-Login consulta esta propiedad
        """Solo las cuentas activas pueden iniciar sesión."""
        return bool(self.activo)

    def __repr__(self) -> str:
        # No se incluye el hash a propósito.
        return f"<Usuario {self.username}>"


class Perfil(Persona, ModeloBase):
    """Datos personales y de contacto que se muestran en el portfolio.

    ENCAPSULAMIENTO: email y teléfono se almacenan en atributos privados y se
    acceden mediante propiedades con validación/normalización.
    """

    __tablename__ = "perfil"

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(
        db.Integer, db.ForeignKey("usuarios.id", ondelete="SET NULL"), unique=True
    )
    nombre = db.Column(db.String(80), nullable=False)
    apellido = db.Column(db.String(80), nullable=False, default="")
    titulo = db.Column(db.String(150), nullable=False)
    subtitulo = db.Column(db.String(180), nullable=False, default="")
    bio = db.Column(db.Text, nullable=False, default="")
    _email = db.Column("email", db.String(120), nullable=False, default="")
    _telefono = db.Column("telefono", db.String(40), nullable=True)
    ubicacion = db.Column(db.String(120), nullable=False, default="")
    linkedin = db.Column(db.String(255), nullable=True)
    github = db.Column(db.String(255), nullable=True)
    sitio_web = db.Column(db.String(255), nullable=True)
    disponibilidad = db.Column(db.String(120), nullable=False, default="")
    cv_resumen = db.Column(db.Text, nullable=False, default="")
    avatar_url = db.Column(db.String(255), nullable=False, default="img/avatar.svg")
    actualizado_en = db.Column(db.DateTime, nullable=False, default=ahora, onupdate=ahora)

    usuario = db.relationship("Usuario", backref=db.backref("perfil", uselist=False))

    # Propiedades con encapsulamiento ------------------------------------
    @property
    def email(self) -> str:
        return self._email or ""

    @email.setter
    def email(self, valor: str) -> None:
        valor = (valor or "").strip().lower()
        if valor and ("@" not in valor or "." not in valor.split("@")[-1]):
            raise ValueError("El email no tiene un formato válido.")
        self._email = valor

    @property
    def telefono(self) -> str:
        return self._telefono or ""

    @telefono.setter
    def telefono(self, valor: str) -> None:
        self._telefono = "".join((valor or "").strip().split())

    @property
    def nombre_completo(self) -> str:
        return f"{self.nombre} {self.apellido}".strip()

    @property
    def iniciales(self) -> str:
        partes = [p for p in (self.nombre, self.apellido) if p]
        return "".join(p[0].upper() for p in partes)[:2] or "K"

    def resumen(self) -> str:
        return self.bio or self.subtitulo or self.titulo

    def __repr__(self) -> str:
        return f"<Perfil {self.nombre_completo}>"


# ---------------------------------------------------------------------------
# Contenido del portfolio (HERENCIA de ContenidoPortfolio)
# ---------------------------------------------------------------------------
class Estudio(ContenidoPortfolio):
    """Formación académica cursada."""

    __tablename__ = "estudios"

    id = db.Column(db.Integer, primary_key=True)
    institucion = db.Column(db.String(160), nullable=False)
    titulo = db.Column(db.String(160), nullable=False)
    area = db.Column(db.String(120), nullable=False, default="")
    nivel = db.Column(db.String(60), nullable=False, default="Terciario")
    fecha_inicio = db.Column(db.Date, nullable=False)
    fecha_fin = db.Column(db.Date, nullable=True)
    en_curso = db.Column(db.Boolean, nullable=False, default=False)
    descripcion = db.Column(db.Text, nullable=False, default="")
    orden = db.Column(db.Integer, nullable=False, default=0)
    activo = db.Column(db.Boolean, nullable=False, default=True)
    creado_en = db.Column(db.DateTime, nullable=False, default=ahora)

    @property
    def periodo(self) -> str:
        return formatear_periodo(self.fecha_inicio, self.fecha_fin, self.en_curso)

    def resumen(self) -> str:  # POLIMORFISMO
        return f"{self.titulo} en {self.institucion} ({self.periodo})."

    def __repr__(self) -> str:
        return f"<Estudio {self.titulo}>"


class Experiencia(ContenidoPortfolio):
    """Experiencia laboral o profesional."""

    __tablename__ = "experiencias"

    id = db.Column(db.Integer, primary_key=True)
    empresa = db.Column(db.String(160), nullable=False)
    puesto = db.Column(db.String(160), nullable=False)
    ubicacion = db.Column(db.String(120), nullable=False, default="")
    modalidad = db.Column(db.String(40), nullable=False, default="Remoto")
    fecha_inicio = db.Column(db.Date, nullable=False)
    fecha_fin = db.Column(db.Date, nullable=True)
    actual = db.Column(db.Boolean, nullable=False, default=False)
    descripcion = db.Column(db.Text, nullable=False, default="")
    logros = db.Column(db.Text, nullable=False, default="")
    orden = db.Column(db.Integer, nullable=False, default=0)
    activo = db.Column(db.Boolean, nullable=False, default=True)
    creado_en = db.Column(db.DateTime, nullable=False, default=ahora)

    @property
    def periodo(self) -> str:
        return formatear_periodo(self.fecha_inicio, self.fecha_fin, self.actual)

    @property
    def lista_logros(self) -> list[str]:
        return [linea.strip(" -•\t") for linea in (self.logros or "").splitlines() if linea.strip()]

    def resumen(self) -> str:  # POLIMORFISMO
        return f"{self.puesto} en {self.empresa} ({self.periodo})."

    def __repr__(self) -> str:
        return f"<Experiencia {self.puesto}>"


class Tecnologia(ContenidoPortfolio):
    """Tecnología o herramienta que maneja el autor."""

    __tablename__ = "tecnologias"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), nullable=False)
    categoria = db.Column(db.String(60), nullable=False, default="Backend")
    nivel = db.Column(db.Integer, nullable=False, default=70)
    icono = db.Column(db.String(80), nullable=False, default="fa-solid fa-code")
    color = db.Column(db.String(20), nullable=False, default="#38e0c8")
    orden = db.Column(db.Integer, nullable=False, default=0)
    activo = db.Column(db.Boolean, nullable=False, default=True)

    def resumen(self) -> str:  # POLIMORFISMO
        return f"{self.nombre}: nivel {self.nivel}% ({self.categoria})."

    def __repr__(self) -> str:
        return f"<Tecnologia {self.nombre}>"


# Tabla intermedia del modelo relacional: un proyecto usa muchas tecnologías
# y una tecnología puede aparecer en muchos proyectos (N:M).
proyecto_tecnologia = db.Table(
    "proyecto_tecnologia",
    db.Column(
        "proyecto_id", db.Integer,
        db.ForeignKey("proyectos.id", ondelete="CASCADE"), primary_key=True,
    ),
    db.Column(
        "tecnologia_id", db.Integer,
        db.ForeignKey("tecnologias.id", ondelete="CASCADE"), primary_key=True,
    ),
)


class Proyecto(ContenidoPortfolio):
    """Proyecto destacado del portfolio."""

    __tablename__ = "proyectos"

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(160), nullable=False)
    descripcion = db.Column(db.Text, nullable=False, default="")
    repo_url = db.Column(db.String(255), nullable=True)
    demo_url = db.Column(db.String(255), nullable=True)
    imagen_url = db.Column(db.String(255), nullable=False, default="img/proyecto-portfolio.svg")
    destacado = db.Column(db.Boolean, nullable=False, default=False)
    orden = db.Column(db.Integer, nullable=False, default=0)
    activo = db.Column(db.Boolean, nullable=False, default=True)
    creado_en = db.Column(db.DateTime, nullable=False, default=ahora)

    tecnologias = db.relationship(
        "Tecnologia",
        secondary=proyecto_tecnologia,
        backref=db.backref("proyectos", lazy="select"),
        order_by="Tecnologia.orden",
    )

    def resumen(self) -> str:  # POLIMORFISMO
        return self.descripcion or f"Proyecto {self.titulo}."

    def __repr__(self) -> str:
        return f"<Proyecto {self.titulo}>"


class TextoSitio(ContenidoPortfolio):
    """Texto editable del sitio (HERENCIA + POLIMORFISMO).

    Cada fila guarda una clave estable (por ejemplo ``mapa.titulo``), una
    etiqueta legible para el panel y el valor que se muestra en las plantillas.
    Así el administrador puede cambiar frases completas sin tocar Jinja2.
    """

    __tablename__ = "textos_sitio"

    id = db.Column(db.Integer, primary_key=True)
    clave = db.Column(db.String(100), nullable=False, unique=True, index=True)
    etiqueta = db.Column(db.String(160), nullable=False)
    valor = db.Column(db.Text, nullable=False, default="")
    orden = db.Column(db.Integer, nullable=False, default=0)
    seccion = db.Column(db.String(40), nullable=False, default="General")

    def resumen(self) -> str:  # POLIMORFISMO
        return f"{self.etiqueta}: {self.valor}"

    def __repr__(self) -> str:
        return f"<TextoSitio {self.clave}>"


class Mensaje(ModeloBase):
    """Mensaje recibido desde el formulario de contacto."""

    __tablename__ = "mensajes"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    asunto = db.Column(db.String(160), nullable=False)
    mensaje = db.Column(db.Text, nullable=False)
    leido = db.Column(db.Boolean, nullable=False, default=False)
    creado_en = db.Column(db.DateTime, nullable=False, default=ahora)

    def resumen(self) -> str:
        return f"{self.asunto} — {self.nombre}"

    def __repr__(self) -> str:
        return f"<Mensaje {self.asunto!r}>"
