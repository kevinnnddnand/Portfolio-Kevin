-- =============================================================================
-- Proyecto Integrador — Portfolio Full Stack
-- Diseño físico de la base de datos para MySQL 8.x
-- Motor: InnoDB · Charset: utf8mb4 · Collation: utf8mb4_unicode_ci
--
-- Uso:
--   mysql -u usuario -p < database/schema_mysql.sql
--
-- El modelo lógico se documenta en docs/Documentacion_Preliminar_Portfolio.pdf
-- y las relaciones se implementan con SQLAlchemy en portfolio/models.py.
-- =============================================================================

CREATE DATABASE IF NOT EXISTS portfolio
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE portfolio;

-- Orden de creación: primero las tablas independientes y luego las que
-- contienen claves foráneas.
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS proyecto_tecnologia;
DROP TABLE IF EXISTS mensajes;
DROP TABLE IF EXISTS textos_sitio;
DROP TABLE IF EXISTS proyectos;
DROP TABLE IF EXISTS tecnologias;
DROP TABLE IF EXISTS experiencias;
DROP TABLE IF EXISTS estudios;
DROP TABLE IF EXISTS perfil;
DROP TABLE IF EXISTS usuarios;
SET FOREIGN_KEY_CHECKS = 1;

-- -----------------------------------------------------------------------------
-- usuarios: cuentas con acceso al panel de edición (1 usuario : 0..1 perfil)
-- -----------------------------------------------------------------------------
CREATE TABLE usuarios (
  id            INT UNSIGNED NOT NULL AUTO_INCREMENT,
  username      VARCHAR(60)  NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  nombre        VARCHAR(120) NOT NULL DEFAULT 'Administrador',
  activo        TINYINT(1)   NOT NULL DEFAULT 1,
  creado_en     DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  ultimo_acceso DATETIME     NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uq_usuarios_username (username)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- perfil: datos personales del autor (1 fila para el portfolio)
-- La FK usuario_id es única: un usuario administra un perfil.
-- -----------------------------------------------------------------------------
CREATE TABLE perfil (
  id             INT UNSIGNED NOT NULL AUTO_INCREMENT,
  usuario_id     INT UNSIGNED NULL,
  nombre         VARCHAR(80)  NOT NULL,
  apellido       VARCHAR(80)  NOT NULL DEFAULT '',
  titulo         VARCHAR(150) NOT NULL,
  subtitulo      VARCHAR(180) NOT NULL DEFAULT '',
  bio            TEXT         NOT NULL,
  email          VARCHAR(120) NOT NULL DEFAULT '',
  telefono       VARCHAR(40)  NULL,
  ubicacion      VARCHAR(120) NOT NULL DEFAULT '',
  linkedin       VARCHAR(255) NULL,
  github         VARCHAR(255) NULL,
  sitio_web      VARCHAR(255) NULL,
  disponibilidad VARCHAR(120) NOT NULL DEFAULT '',
  cv_resumen     TEXT         NOT NULL,
  avatar_url     VARCHAR(255) NOT NULL DEFAULT 'img/avatar.svg',
  actualizado_en DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
                 ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uq_perfil_usuario (usuario_id),
  CONSTRAINT fk_perfil_usuario
    FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
    ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- estudios: formación académica (1 perfil : N estudios)
-- -----------------------------------------------------------------------------
CREATE TABLE estudios (
  id            INT UNSIGNED NOT NULL AUTO_INCREMENT,
  institucion   VARCHAR(160) NOT NULL,
  titulo        VARCHAR(160) NOT NULL,
  area          VARCHAR(120) NOT NULL DEFAULT '',
  nivel         VARCHAR(60)  NOT NULL DEFAULT 'Terciario',
  fecha_inicio  DATE         NOT NULL,
  fecha_fin     DATE         NULL,
  en_curso      TINYINT(1)   NOT NULL DEFAULT 0,
  descripcion   TEXT         NOT NULL,
  orden         INT          NOT NULL DEFAULT 0,
  activo        TINYINT(1)   NOT NULL DEFAULT 1,
  creado_en     DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_estudios_orden (orden),
  KEY idx_estudios_activo (activo)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- experiencias: trayectoria laboral (1 perfil : N experiencias)
-- -----------------------------------------------------------------------------
CREATE TABLE experiencias (
  id           INT UNSIGNED NOT NULL AUTO_INCREMENT,
  empresa      VARCHAR(160) NOT NULL,
  puesto       VARCHAR(160) NOT NULL,
  ubicacion    VARCHAR(120) NOT NULL DEFAULT '',
  modalidad    VARCHAR(40)  NOT NULL DEFAULT 'Remoto',
  fecha_inicio DATE         NOT NULL,
  fecha_fin    DATE         NULL,
  actual       TINYINT(1)   NOT NULL DEFAULT 0,
  descripcion  TEXT         NOT NULL,
  logros       TEXT         NOT NULL,
  orden        INT          NOT NULL DEFAULT 0,
  activo       TINYINT(1)   NOT NULL DEFAULT 1,
  creado_en    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_experiencias_orden (orden),
  KEY idx_experiencias_activo (activo)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- tecnologias: stack técnico y nivel de dominio
-- -----------------------------------------------------------------------------
CREATE TABLE tecnologias (
  id        INT UNSIGNED NOT NULL AUTO_INCREMENT,
  nombre    VARCHAR(80)  NOT NULL,
  categoria VARCHAR(60)  NOT NULL DEFAULT 'Backend',
  nivel     INT          NOT NULL DEFAULT 70,
  icono     VARCHAR(80)  NOT NULL DEFAULT 'fa-solid fa-code',
  color     VARCHAR(20)  NOT NULL DEFAULT '#38e0c8',
  orden     INT          NOT NULL DEFAULT 0,
  activo    TINYINT(1)   NOT NULL DEFAULT 1,
  PRIMARY KEY (id),
  KEY idx_tecnologias_categoria (categoria),
  KEY idx_tecnologias_orden (orden),
  CONSTRAINT ck_tecnologias_nivel CHECK (nivel BETWEEN 0 AND 100)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- proyectos: trabajos destacados del portfolio
-- -----------------------------------------------------------------------------
CREATE TABLE proyectos (
  id          INT UNSIGNED NOT NULL AUTO_INCREMENT,
  titulo      VARCHAR(160) NOT NULL,
  descripcion TEXT         NOT NULL,
  repo_url    VARCHAR(255) NULL,
  demo_url    VARCHAR(255) NULL,
  imagen_url  VARCHAR(255) NOT NULL DEFAULT 'img/proyecto-portfolio.svg',
  destacado   TINYINT(1)   NOT NULL DEFAULT 0,
  orden       INT          NOT NULL DEFAULT 0,
  activo      TINYINT(1)   NOT NULL DEFAULT 1,
  creado_en   DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_proyectos_destacado (destacado),
  KEY idx_proyectos_orden (orden)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- proyecto_tecnologia: tabla intermedia N:M
-- Un proyecto usa muchas tecnologías y una tecnología aparece en N proyectos.
-- -----------------------------------------------------------------------------
CREATE TABLE proyecto_tecnologia (
  proyecto_id   INT UNSIGNED NOT NULL,
  tecnologia_id INT UNSIGNED NOT NULL,
  PRIMARY KEY (proyecto_id, tecnologia_id),
  KEY idx_pt_tecnologia (tecnologia_id),
  CONSTRAINT fk_pt_proyecto
    FOREIGN KEY (proyecto_id) REFERENCES proyectos (id)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_pt_tecnologia
    FOREIGN KEY (tecnologia_id) REFERENCES tecnologias (id)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- textos_sitio: frases editables desde /admin/contenido
-- La clave es estable y la usa Jinja2 como textos.get('clave', 'valor por defecto').
-- -----------------------------------------------------------------------------
CREATE TABLE textos_sitio (
  id       INT UNSIGNED NOT NULL AUTO_INCREMENT,
  clave    VARCHAR(100) NOT NULL,
  etiqueta VARCHAR(160) NOT NULL,
  valor    TEXT         NOT NULL,
  orden    INT          NOT NULL DEFAULT 0,
  seccion  VARCHAR(40)  NOT NULL DEFAULT 'General',
  PRIMARY KEY (id),
  UNIQUE KEY uq_textos_clave (clave),
  KEY idx_textos_orden (orden)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- mensajes: consultas recibidas desde el formulario público de contacto
-- -----------------------------------------------------------------------------
CREATE TABLE mensajes (
  id        INT UNSIGNED NOT NULL AUTO_INCREMENT,
  nombre    VARCHAR(120) NOT NULL,
  email     VARCHAR(120) NOT NULL,
  asunto    VARCHAR(160) NOT NULL,
  mensaje   TEXT         NOT NULL,
  leido     TINYINT(1)   NOT NULL DEFAULT 0,
  creado_en DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_mensajes_leido (leido),
  KEY idx_mensajes_creado (creado_en)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;
