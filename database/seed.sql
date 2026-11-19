-- =============================================================================
-- Datos iniciales REALES del portfolio (MySQL 8.x)
--
-- IMPORTANTE:
--   * Ejecutar únicamente sobre una base recién creada con schema_mysql.sql.
--   * La aplicación también puede cargar estos datos automáticamente con
--     `flask seed-db` (o al iniciar con SEED_ON_START=1). En ese caso NO es
--     necesario ejecutar este archivo.
--   * Si la base ya tiene datos de prueba, ejecutá antes schema_mysql.sql para
--     reconstruir las tablas. El perfil y los textos se restauran a los valores
--     del CV de Kevin Basualdo.
--   * Credenciales del administrador:
--       usuario: kevinAdmin
--       contraseña: kevin1504
--     Cambiarlas antes de publicar el sitio desde "Mi cuenta" en el panel.
-- =============================================================================

USE portfolio;

-- ---------------------------------------------------------------------------
-- Usuario administrador
-- El hash corresponde a kevin1504 (Werkzeug scrypt, nunca se guarda la clave).
-- ---------------------------------------------------------------------------
INSERT INTO usuarios (id, username, password_hash, nombre, activo, creado_en)
VALUES (1, 'kevinAdmin', 'scrypt:32768:8:1$1xKBAXMGkSVqER4K$b75bfc57e02c7cd65f0e99c3800eb06b3ca529f503e8bebdeb69c8f09c2a587e37c5ff6c49f87d7e7227461066723ac5eb2f1a7e6ee592c2e50b757128c17435', 'Kevin', 1, NOW());


-- ---------------------------------------------------------------------------
-- Perfil (datos del CV de RRHH)
-- ---------------------------------------------------------------------------
INSERT INTO perfil (
  id, usuario_id, nombre, apellido, titulo, subtitulo, bio, email, telefono,
  ubicacion, linkedin, github, sitio_web, disponibilidad, cv_resumen,
  avatar_url, actualizado_en
) VALUES (
  1, 1, 'Kevin', 'Basualdo',
  'Estudiante de carrera técnica · Programación y diseño web',
  'Python · Flask · MySQL · Diseño web · Contenido digital',
  'Soy estudiante de una carrera técnica, apasionado por la programación y con un perfil creativo. Me encantan deportes como el voleibol y el baloncesto; además, me interesa el diseño de videojuegos y otros elementos, como logotipos. Trabajo en diseño web, gestión de redes sociales, diseño de aplicaciones, creación de contenido y definición de estrategias.',
  'd48721257@alumnos.itr.ed.ar',
  '(351) 3 29-2406',
  'Villa San Nicolás, Malagueño, Córdoba, Argentina',
  NULL, NULL, NULL,
  'Disponible para proyectos de diseño web y desarrollo',
  'Estudiante de una carrera técnica, apasionado por la programación y con un perfil creativo. Diseño web, gestión de redes sociales, diseño de aplicaciones, creación de contenido y definición de estrategias. Español nativo, inglés B1 y japonés iniciante.',
  'img/avatar.svg', NOW()
);


-- ---------------------------------------------------------------------------
-- Estudios (ITR 2023-Present · IEC 2021-2023)
-- ---------------------------------------------------------------------------
INSERT INTO estudios (
  id, institucion, titulo, area, nivel, fecha_inicio, fecha_fin, en_curso,
  descripcion, orden, activo, creado_en
) VALUES
(
  1,
  'ITR — Instituto Técnico Renault',
  'Carrera técnica (ITR)',
  'Programación y diseño',
  'Terciario',
  '2023-03-01', NULL, 1,
  'Formación técnica en curso: diseño web, diseño de aplicaciones, gestión de redes sociales, creación de contenido y definición de estrategias.',
  1, 1, NOW()
),
(
  2,
  'IEC — Instituto de Educación Córdoba',
  'Secundario',
  'Formación general',
  'Secundario',
  '2021-03-01', '2023-12-01', 0,
  'Estudios secundarios completados en el IEC (2021-2023).',
  2, 1, NOW()
);


-- ---------------------------------------------------------------------------
-- Experiencia laboral (Portones Automáticos · 2025-2026)
-- ---------------------------------------------------------------------------
INSERT INTO experiencias (
  id, empresa, puesto, ubicacion, modalidad, fecha_inicio, fecha_fin, actual,
  descripcion, logros, orden, activo, creado_en
) VALUES
(
  1,
  'Portones Automáticos',
  'Reparador de puertas',
  'Villa San Nicolás, Malagueño, Córdoba, Argentina',
  'Presencial',
  '2025-01-01', NULL, 1,
  'Reparación y mantenimiento de puertas y portones automáticos (2025-2026).',
  '',
  1, 1, NOW()
),
(
  2,
  'Portones Automáticos',
  'Diseñador web',
  'Villa San Nicolás, Malagueño, Córdoba, Argentina',
  'Remoto',
  '2026-01-01', NULL, 1,
  'Diseño web para la empresa, combinado con la reparación de portones automáticos.',
  'Diseño web.\nGestión de redes sociales.\nDiseño de aplicaciones.\nCreación de contenido.\nDefinición de estrategia.',
  2, 1, NOW()
);


-- ---------------------------------------------------------------------------
-- Tecnologías (el mismo orden y niveles que `flask seed-db`)
-- ---------------------------------------------------------------------------
INSERT INTO tecnologias (id, nombre, categoria, nivel, icono, color, orden, activo) VALUES
(1, 'Python',         'Backend',       82, 'fa-brands fa-python',     '#3776ab', 1, 1),
(2, 'Flask',          'Backend',       78, 'fa-solid fa-flask',       '#0f766e', 2, 1),
(3, 'HTML5',          'Frontend',      86, 'fa-brands fa-html5',      '#e34f26', 3, 1),
(4, 'CSS3',           'Frontend',      82, 'fa-brands fa-css3-alt',   '#1572b6', 4, 1),
(5, 'JavaScript',     'Frontend',      70, 'fa-brands fa-js',         '#b58900', 5, 1),
(6, 'MySQL',          'Base de datos', 74, 'fa-solid fa-database',    '#00758f', 6, 1),
(7, 'Git',            'Herramientas',  68, 'fa-brands fa-git-alt',    '#f05032', 7, 1),
(8, 'Diseño web',     'Otros',         88, 'fa-solid fa-pen-ruler',   '#8b5cf6', 8, 1),
(9, 'Redes sociales', 'Otros',         80, 'fa-solid fa-share-nodes', '#e1306c', 9, 1);


-- ---------------------------------------------------------------------------
-- Proyectos
-- ---------------------------------------------------------------------------
INSERT INTO proyectos (
  id, titulo, descripcion, repo_url, demo_url, imagen_url, destacado, orden,
  activo, creado_en
) VALUES
(
  1,
  'Portfolio Web Full Stack',
  'Sitio personal administrable: perfil, formación, experiencia, tecnologías y proyectos se editan desde un panel protegido y se guardan en MySQL. Incluye CV descargable y diseño responsive.',
  NULL, NULL, 'img/proyecto-portfolio.svg', 1, 1, 1, NOW()
),
(
  2,
  'Sitio web para Portones Automáticos',
  'Diseño web para una empresa local de portones automáticos: presentación de servicios, contenido para redes sociales y estrategia digital.',
  NULL, NULL, 'img/proyecto-tareas.svg', 1, 2, 1, NOW()
),
(
  3,
  'Contenido y piezas gráficas',
  'Creación de contenido, logotipos y dibujos hiperrealistas. Interés por el diseño de videojuegos y otros elementos visuales.',
  NULL, NULL, 'img/proyecto-ventas.svg', 0, 3, 1, NOW()
);

-- ---------------------------------------------------------------------------
-- Relación N:M proyecto ↔ tecnología
-- ---------------------------------------------------------------------------
INSERT INTO proyecto_tecnologia (proyecto_id, tecnologia_id) VALUES
(1, 1), (1, 2), (1, 6), (1, 3), (1, 4), (1, 8),
(2, 3), (2, 4), (2, 8), (2, 9),
(3, 8), (3, 9), (3, 5);


-- ---------------------------------------------------------------------------
-- Textos editables del sitio
-- Los administra el panel en /admin/contenido y las plantillas los leen con
-- textos.get('clave', 'valor por defecto'). Generado desde portfolio/seed.py
-- para que el SQL y el seed de la app sean idénticos.
-- ---------------------------------------------------------------------------
INSERT INTO textos_sitio (id, clave, etiqueta, valor, orden, seccion) VALUES
(1, 'sitio.marca', 'Marca del sitio', 'kevin.dev', 1, 'General'),
(2, 'sitio.descripcion', 'Descripción para buscadores', 'Portfolio de Kevin Basualdo: programación, diseño web y contenido digital con Python, Flask y MySQL.', 2, 'General'),
(3, 'sitio.og_descripcion', 'Descripción para redes sociales', 'Portfolio full stack con Python, Flask y MySQL.', 3, 'General'),
(4, 'sitio.pie_descripcion', 'Texto del pie de página', 'Construyendo experiencias web con código limpio, datos bien modelados y atención al detalle.', 4, 'General'),
(5, 'sitio.copyright_nombre', 'Nombre en el copyright', 'Kevin Basualdo', 5, 'General'),
(6, 'sitio.estado', 'Estado en el pie', 'Disponible para proyectos', 6, 'General'),
(7, 'sitio.hecho_con', 'Tecnologías del pie', 'Flask y MySQL', 7, 'General'),
(8, 'sitio.saltar', 'Enlace saltar al contenido', 'Saltar al contenido principal', 8, 'General'),
(9, 'nav.sobre_mi', 'Menú: Sobre mí', 'Sobre mí', 9, 'Navegación'),
(10, 'nav.estudios', 'Menú: Estudios', 'Estudios', 10, 'Navegación'),
(11, 'nav.experiencia', 'Menú: Experiencia', 'Experiencia', 11, 'Navegación'),
(12, 'nav.tecnologias', 'Menú: Tecnologías', 'Tecnologías', 12, 'Navegación'),
(13, 'nav.proyectos', 'Menú: Proyectos', 'Proyectos', 13, 'Navegación'),
(14, 'nav.contacto', 'Menú: Contacto', 'Contacto', 14, 'Navegación'),
(15, 'nav.cv', 'Menú: CV', 'CV', 15, 'Navegación'),
(16, 'nav.acceso', 'Menú: Acceso', 'Acceso', 16, 'Navegación'),
(17, 'footer.navegacion', 'Pie: título Navegación', 'Navegación', 17, 'Navegación'),
(18, 'footer.stack', 'Pie: título Stack', 'Stack', 18, 'Navegación'),
(19, 'footer.stack_1', 'Pie: Stack línea 1', 'Python · Flask', 19, 'Navegación'),
(20, 'footer.stack_2', 'Pie: Stack línea 2', 'HTML · CSS', 20, 'Navegación'),
(21, 'footer.stack_3', 'Pie: Stack línea 3', 'JavaScript · MySQL', 21, 'Navegación'),
(22, 'footer.stack_4', 'Pie: Stack línea 4', 'Git', 22, 'Navegación'),
(23, 'footer.estado', 'Pie: título Estado', 'Estado', 23, 'Navegación'),
(24, 'footer.derechos', 'Pie: derechos', 'Todos los derechos reservados.', 24, 'Navegación'),
(25, 'hero.saludo', 'Saludo del hero', 'Hola, soy', 25, 'Hero'),
(26, 'hero.chip_python', 'Chip Python', 'Python', 26, 'Hero'),
(27, 'hero.chip_flask', 'Chip Flask', 'Flask', 27, 'Hero'),
(28, 'hero.chip_mysql', 'Chip MySQL', 'MySQL', 28, 'Hero'),
(29, 'hero.scroll', 'Indicador Scroll', 'Scroll', 29, 'Hero'),
(30, 'hero.rol_2', 'Rol animado 2', 'Python & Flask', 30, 'Hero'),
(31, 'hero.rol_3', 'Rol animado 3', 'Backend + MySQL', 31, 'Hero'),
(32, 'hero.rol_4', 'Rol animado 4', 'Diseño con detalle', 32, 'Hero'),
(33, 'hero.descripcion_extra', 'Texto extra bajo el subtítulo', 'Convierto ideas en aplicaciones web funcionales, cuidando el modelo de datos, la experiencia de uso y cada detalle del código.', 33, 'Hero'),
(34, 'hero.stat_proyectos', 'Etiqueta estadística proyectos', 'Proyectos', 34, 'Hero'),
(35, 'hero.stat_tecnologias', 'Etiqueta estadística tecnologías', 'Tecnologías', 35, 'Hero'),
(36, 'hero.stat_formaciones', 'Etiqueta estadística formaciones', 'Formaciones', 36, 'Hero'),
(37, 'boton.ver_proyectos', 'Botón Ver proyectos', 'Ver proyectos', 37, 'Botones'),
(38, 'boton.descargar_cv', 'Botón Descargar CV', 'Descargar CV', 38, 'Botones'),
(39, 'boton.descargar_cv_largo', 'Botón Descargar CV (contacto)', 'Descargar CV en PDF', 39, 'Botones'),
(40, 'sobre.kicker', 'Sobre mí: kicker', '01 — Sobre mí', 40, 'Sobre mí'),
(41, 'sobre.titulo_1', 'Sobre mí: título', 'Código con criterio,', 41, 'Sobre mí'),
(42, 'sobre.titulo_2', 'Sobre mí: título destacado', 'interfaces con intención.', 42, 'Sobre mí'),
(43, 'sobre.texto_extra', 'Sobre mí: segundo párrafo', 'Me interesa especialmente la intersección entre el backend y los datos: diseñar tablas coherentes, escribir APIs claras y construir pantallas que hagan simple lo complejo. Aprendo haciendo y documentando cada decisión.', 43, 'Sobre mí'),
(44, 'sobre.etiqueta_ubicacion', 'Etiqueta Ubicación', 'Ubicación', 44, 'Sobre mí'),
(45, 'sobre.etiqueta_email', 'Etiqueta Email', 'Email', 45, 'Sobre mí'),
(46, 'sobre.etiqueta_disponibilidad', 'Etiqueta Disponibilidad', 'Disponibilidad', 46, 'Sobre mí'),
(47, 'sobre.foco_backend_titulo', 'Tarjeta Backend: título', 'Backend', 47, 'Sobre mí'),
(48, 'sobre.foco_backend_texto', 'Tarjeta Backend: texto', 'APIs REST con Flask, autenticación, formularios seguros y lógica de negocio ordenada.', 48, 'Sobre mí'),
(49, 'sobre.foco_datos_titulo', 'Tarjeta Datos: título', 'Datos', 49, 'Sobre mí'),
(50, 'sobre.foco_datos_texto', 'Tarjeta Datos: texto', 'Modelado relacional en MySQL, consultas eficientes y persistencia con SQLAlchemy.', 50, 'Sobre mí'),
(51, 'sobre.foco_interfaz_titulo', 'Tarjeta Interfaz: título', 'Interfaz', 51, 'Sobre mí'),
(52, 'sobre.foco_interfaz_texto', 'Tarjeta Interfaz: texto', 'Jinja2, HTML semántico, CSS responsive y animaciones que acompañan sin distraer.', 52, 'Sobre mí'),
(53, 'estudios.kicker', 'Estudios: kicker', '02 — Formación', 53, 'Estudios'),
(54, 'estudios.titulo', 'Estudios: título', 'Estudios', 54, 'Estudios'),
(55, 'estudios.titulo_acento', 'Estudios: palabra destacada', 'cursados', 55, 'Estudios'),
(56, 'estudios.nota', 'Estudios: nota', 'La base técnica detrás de cada proyecto: formación formal, cursos y práctica constante.', 56, 'Estudios'),
(57, 'estudios.vacio', 'Estudios: sin datos', 'Todavía no hay estudios cargados.', 57, 'Estudios'),
(58, 'estudios.en_curso', 'Estudios: badge En curso', 'En curso', 58, 'Estudios'),
(59, 'experiencia.kicker', 'Experiencia: kicker', '03 — Trayectoria', 59, 'Experiencia'),
(60, 'experiencia.titulo', 'Experiencia: título', 'Experiencia', 60, 'Experiencia'),
(61, 'experiencia.titulo_acento', 'Experiencia: palabra destacada', 'laboral', 61, 'Experiencia'),
(62, 'experiencia.nota', 'Experiencia: nota', 'Trabajo real, problemas reales y aprendizajes que se traducen en mejores soluciones.', 62, 'Experiencia'),
(63, 'experiencia.vacio', 'Experiencia: sin datos', 'Todavía no hay experiencia cargada.', 63, 'Experiencia'),
(64, 'experiencia.actual', 'Experiencia: badge Actual', 'Actual', 64, 'Experiencia'),
(65, 'tecnologias.kicker', 'Tecnologías: kicker', '04 — Stack', 65, 'Tecnologías'),
(66, 'tecnologias.titulo', 'Tecnologías: título', 'Tecnologías que', 66, 'Tecnologías'),
(67, 'tecnologias.titulo_acento', 'Tecnologías: palabra destacada', 'uso', 67, 'Tecnologías'),
(68, 'tecnologias.nota', 'Tecnologías: nota', 'Herramientas con las que construyo, medido en nivel de dominio y experiencia práctica.', 68, 'Tecnologías'),
(69, 'tecnologias.vacio', 'Tecnologías: sin datos', 'Todavía no hay tecnologías cargadas.', 69, 'Tecnologías'),
(70, 'tecnologias.herramienta', 'Singular herramienta', 'herramienta', 70, 'Tecnologías'),
(71, 'tecnologias.herramientas', 'Plural herramientas', 'herramientas', 71, 'Tecnologías'),
(72, 'proyectos.kicker', 'Proyectos: kicker', '05 — Portfolio', 72, 'Proyectos'),
(73, 'proyectos.titulo', 'Proyectos: título', 'Proyectos', 73, 'Proyectos'),
(74, 'proyectos.titulo_acento', 'Proyectos: palabra destacada', 'destacados', 74, 'Proyectos'),
(75, 'proyectos.nota', 'Proyectos: nota', 'Una selección de trabajos donde aplico el stack completo, del modelo de datos a la interfaz.', 75, 'Proyectos'),
(76, 'proyectos.vacio', 'Proyectos: sin datos', 'Todavía no hay proyectos cargados.', 76, 'Proyectos'),
(77, 'proyectos.destacado', 'Etiqueta Destacado', 'Destacado', 77, 'Proyectos'),
(78, 'proyectos.repositorio', 'Enlace Repositorio', 'Repositorio', 78, 'Proyectos'),
(79, 'proyectos.demo', 'Enlace Demo', 'Demo', 79, 'Proyectos'),
(80, 'proyectos.academico', 'Proyecto sin enlaces', 'Proyecto académico', 80, 'Proyectos'),
(81, 'mapa.kicker', 'Mapa: kicker', 'Ubicación', 81, 'Ubicación'),
(82, 'mapa.titulo_1', 'Mapa: título', 'Desde Villa San Nicolás,', 82, 'Ubicación'),
(83, 'mapa.titulo_2', 'Mapa: título destacado', 'Córdoba, para el mundo.', 83, 'Ubicación'),
(84, 'mapa.texto', 'Mapa: párrafo', 'Desde Villa San Nicolás, a minutos de Carlos Paz, trabajo de forma remota con equipos y clientes de cualquier lugar. La distancia no es un límite cuando la comunicación y los procesos son claros.', 84, 'Ubicación'),
(85, 'mapa.dato_1', 'Mapa: dato 1', 'UTC−3 · Argentina', 85, 'Ubicación'),
(86, 'mapa.dato_2', 'Mapa: dato 2', 'Respuesta en menos de 24 h', 86, 'Ubicación'),
(87, 'mapa.dato_3', 'Mapa: dato 3', 'Español · Inglés técnico', 87, 'Ubicación'),
(88, 'mapa.titulo_iframe', 'Mapa: título del iframe', 'Mapa de Villa San Nicolás, Malagueño, Córdoba, Argentina', 88, 'Ubicación'),
(89, 'mapa.bbox', 'Mapa: bbox (lat/lon separados por coma)', '-64.50,-31.47,-64.41,-31.40', 89, 'Ubicación'),
(90, 'mapa.marker', 'Mapa: marcador lat,lon', '-31.4365,-64.4538', 90, 'Ubicación'),
(91, 'mapa.badge_titulo', 'Mapa: badge título', 'Villa San Nicolás', 91, 'Ubicación'),
(92, 'mapa.badge_subtitulo', 'Mapa: badge subtítulo', 'Malagueño, Córdoba', 92, 'Ubicación'),
(93, 'contacto.kicker', 'Contacto: kicker', '06 — Contacto', 93, 'Contacto'),
(94, 'contacto.titulo_1', 'Contacto: título', '¿Tenés una idea?', 94, 'Contacto'),
(95, 'contacto.titulo_2', 'Contacto: título destacado', 'Hagámosla realidad.', 95, 'Contacto'),
(96, 'contacto.texto', 'Contacto: párrafo', 'Estoy abierto a oportunidades laborales, proyectos freelance y colaboraciones. Contame qué necesitás y te respondo con una propuesta clara.', 96, 'Contacto'),
(97, 'contacto.etiqueta_email', 'Contacto: etiqueta email', 'Escribime', 97, 'Contacto'),
(98, 'contacto.etiqueta_telefono', 'Contacto: etiqueta teléfono', 'Teléfono', 98, 'Contacto'),
(99, 'contacto.form_titulo', 'Formulario: título', 'Mandame un mensaje', 99, 'Contacto'),
(100, 'contacto.form_seguro', 'Formulario: etiqueta seguridad', 'Formulario protegido', 100, 'Contacto'),
(101, 'contacto.form_nota', 'Formulario: nota', 'Tus datos solo se usan para responder tu mensaje.', 101, 'Contacto'),
(102, 'form.nombre', 'Formulario: etiqueta Nombre', 'Nombre', 102, 'Contacto'),
(103, 'form.nombre_placeholder', 'Formulario: placeholder Nombre', 'Tu nombre', 103, 'Contacto'),
(104, 'form.email', 'Formulario: etiqueta Email', 'Email', 104, 'Contacto'),
(105, 'form.asunto', 'Formulario: etiqueta Asunto', 'Asunto', 105, 'Contacto'),
(106, 'form.asunto_placeholder', 'Formulario: placeholder Asunto', 'Propuesta, consulta, colaboración...', 106, 'Contacto'),
(107, 'form.mensaje', 'Formulario: etiqueta Mensaje', 'Mensaje', 107, 'Contacto'),
(108, 'form.mensaje_placeholder', 'Formulario: placeholder Mensaje', 'Contame un poco más...', 108, 'Contacto'),
(109, 'form.enviar', 'Formulario: botón Enviar', 'Enviar mensaje', 109, 'Contacto');


-- Fin del script. No se cargan mensajes de ejemplo: el panel de mensajes se
-- completa con los contactos reales del formulario público.
