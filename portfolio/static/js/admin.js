/* Panel de administración: menú lateral, confirmaciones y notificaciones. */
(function () {
  "use strict";

  const sidebar = document.getElementById("sidebar");
  const overlay = document.getElementById("sidebarOverlay");
  const menuBtn = document.getElementById("menuBtn");
  const closeBtn = document.getElementById("sidebarClose");

  function abrir() {
    if (!sidebar) return;
    sidebar.classList.add("is-open");
    if (menuBtn) menuBtn.setAttribute("aria-expanded", "true");
  }

  function cerrar() {
    if (!sidebar) return;
    sidebar.classList.remove("is-open");
    if (menuBtn) menuBtn.setAttribute("aria-expanded", "false");
  }

  if (menuBtn) menuBtn.addEventListener("click", abrir);
  if (closeBtn) closeBtn.addEventListener("click", cerrar);
  if (overlay) overlay.addEventListener("click", cerrar);

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") cerrar();
  });

  document.querySelectorAll("[data-confirm]").forEach((form) => {
    form.addEventListener("submit", (event) => {
      if (!window.confirm(form.dataset.confirm)) {
        event.preventDefault();
      }
    });
  });

  document.querySelectorAll(".flash").forEach((flash) => {
    const cerrarFlash = () => {
      flash.style.opacity = "0";
      flash.style.transform = "translateY(-6px)";
      window.setTimeout(() => flash.remove(), 200);
    };
    const boton = flash.querySelector(".flash-close");
    if (boton) boton.addEventListener("click", cerrarFlash);
    window.setTimeout(cerrarFlash, 6000);
  });

  // Cierra el menú mobile al navegar.
  if (sidebar) {
    sidebar.querySelectorAll("nav a").forEach((enlace) => {
      enlace.addEventListener("click", () => {
        if (window.innerWidth <= 1024) cerrar();
      });
    });
  }
})();
