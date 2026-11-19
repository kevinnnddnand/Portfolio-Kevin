/* ==========================================================================
   Portfolio — interacciones del front end
   Animaciones:
   1) typewriter del rol en el hero.
   2) reveal on scroll con IntersectionObserver.
   3) barras de tecnologías que se completan al entrar en pantalla.
   4) navbar que cambia al hacer scroll y menú mobile.
   ========================================================================== */
(function () {
  "use strict";

  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const nav = document.getElementById("nav");
  const navToggle = document.getElementById("navToggle");
  const navLinks = document.getElementById("navLinks");

  /* ------------------------------ Navbar --------------------------------- */
  const onScroll = () => {
    if (nav) nav.classList.toggle("is-scrolled", window.scrollY > 24);
  };
  onScroll();
  window.addEventListener("scroll", onScroll, { passive: true });

  function cerrarMenu() {
    if (!nav) return;
    nav.classList.remove("menu-open");
    document.body.style.overflow = "";
    if (navToggle) navToggle.setAttribute("aria-expanded", "false");
  }

  if (navToggle) {
    navToggle.addEventListener("click", () => {
      const abierto = nav.classList.toggle("menu-open");
      navToggle.setAttribute("aria-expanded", String(abierto));
      document.body.style.overflow = abierto ? "hidden" : "";
    });
  }

  if (navLinks) {
    navLinks.querySelectorAll("a").forEach((link) => {
      link.addEventListener("click", cerrarMenu);
    });
  }

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") cerrarMenu();
  });

  document.addEventListener("click", (event) => {
    if (!nav || !nav.classList.contains("menu-open")) return;
    if (!nav.contains(event.target)) cerrarMenu();
  });

  window.addEventListener("resize", () => {
    if (window.innerWidth > 820) cerrarMenu();
  });

  /* ------------------------ Enlace activo (scroll spy) ------------------- */
  const enlaces = Array.from(document.querySelectorAll("[data-nav]"));
  const secciones = enlaces
    .map((enlace) => document.getElementById(enlace.dataset.nav))
    .filter(Boolean);

  if (secciones.length) {
    let ticking = false;
    const marcarActivo = () => {
      const y = window.scrollY + 130;
      let actual = secciones[0].id;
      secciones.forEach((seccion) => {
        if (seccion.offsetTop <= y) actual = seccion.id;
      });
      enlaces.forEach((enlace) => {
        enlace.classList.toggle("active", enlace.dataset.nav === actual);
      });
      ticking = false;
    };
    window.addEventListener(
      "scroll",
      () => {
        if (!ticking) {
          ticking = true;
          window.requestAnimationFrame(marcarActivo);
        }
      },
      { passive: true }
    );
    marcarActivo();
  }

  /* ------------------- Animación 2: reveal al hacer scroll -------------- */
  const revelables = document.querySelectorAll("[data-reveal]");
  if ("IntersectionObserver" in window && !reduceMotion) {
    const observer = new IntersectionObserver(
      (entradas) => {
        entradas.forEach((entrada) => {
          if (entrada.isIntersecting) {
            entrada.target.classList.add("is-visible");
            observer.unobserve(entrada.target);
          }
        });
      },
      { threshold: 0.12, rootMargin: "0px 0px -40px 0px" }
    );
    revelables.forEach((elemento) => observer.observe(elemento));
  } else {
    revelables.forEach((elemento) => elemento.classList.add("is-visible"));
  }

  /* ---------------- Animación 1: typewriter del hero -------------------- */
  const typed = document.getElementById("typedRole");
  if (typed && !reduceMotion) {
    let roles = [];
    try {
      roles = JSON.parse(typed.dataset.roles || "[]");
    } catch (error) {
      roles = [typed.textContent.trim()];
    }
    if (roles.length) {
      typed.setAttribute("aria-live", "off");
      let indiceRol = 0;
      let indiceChar = 0;
      let borrando = false;

      const escribir = () => {
        const rol = roles[indiceRol];
        if (!borrando) {
          typed.textContent = rol.slice(0, indiceChar + 1);
          indiceChar += 1;
          if (indiceChar === rol.length) {
            borrando = true;
            window.setTimeout(escribir, 2200);
            return;
          }
          window.setTimeout(escribir, 65);
        } else {
          typed.textContent = rol.slice(0, indiceChar - 1);
          indiceChar -= 1;
          if (indiceChar === 0) {
            borrando = false;
            indiceRol = (indiceRol + 1) % roles.length;
            window.setTimeout(escribir, 320);
            return;
          }
          window.setTimeout(escribir, 32);
        }
      };
      typed.textContent = "";
      window.setTimeout(escribir, 700);
    }
  }

  /* ---------------------- Notificaciones flash -------------------------- */
  document.querySelectorAll(".flash").forEach((flash) => {
    const cerrar = flash.querySelector(".flash-close");
    const quitar = () => {
      flash.style.opacity = "0";
      flash.style.transform = "translateX(18px)";
      window.setTimeout(() => flash.remove(), 220);
    };
    if (cerrar) cerrar.addEventListener("click", quitar);
    const demora = flash.classList.contains("flash-danger") ? 9000 : 6000;
    window.setTimeout(quitar, demora);
  });

  /* ---------------------- Mostrar/ocultar contraseña -------------------- */
  document.querySelectorAll("[data-password-toggle]").forEach((boton) => {
    boton.addEventListener("click", () => {
      const input = boton.parentElement.querySelector("input");
      if (!input) return;
      const mostrando = input.type === "text";
      input.type = mostrando ? "password" : "text";
      const icono = boton.querySelector("i");
      if (icono) {
        icono.classList.toggle("fa-eye", mostrando);
        icono.classList.toggle("fa-eye-slash", !mostrando);
      }
      boton.setAttribute("aria-label", mostrando ? "Mostrar contraseña" : "Ocultar contraseña");
      input.focus();
    });
  });

  /* ------------------ Animar números de las estadísticas ---------------- */
  const contadores = document.querySelectorAll(".hero-stats dt");
  if ("IntersectionObserver" in window && !reduceMotion && contadores.length) {
    const animar = (elemento) => {
      const texto = elemento.textContent.trim();
      const numero = parseInt(texto, 10);
      if (Number.isNaN(numero)) return;
      const sufijo = texto.replace(/[0-9]/g, "");
      const duracion = 1100;
      const inicio = performance.now();
      const paso = (ahora) => {
        const progreso = Math.min((ahora - inicio) / duracion, 1);
        const suavizado = 1 - Math.pow(1 - progreso, 3);
        elemento.textContent = Math.round(numero * suavizado) + sufijo;
        if (progreso < 1) window.requestAnimationFrame(paso);
      };
      window.requestAnimationFrame(paso);
    };
    const obs = new IntersectionObserver(
      (entradas) => {
        entradas.forEach((entrada) => {
          if (entrada.isIntersecting) {
            animar(entrada.target);
            obs.unobserve(entrada.target);
          }
        });
      },
      { threshold: 0.8 }
    );
    contadores.forEach((contador) => obs.observe(contador));
  }
})();
