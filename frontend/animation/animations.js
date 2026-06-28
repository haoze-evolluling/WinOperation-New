(function () {
  "use strict";

  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

  const style = document.createElement("style");
  style.id = "animations-injected";
  style.textContent = `
    .anim-press { transition: transform .3s cubic-bezier(0.34,1.56,0.64,1); }
    .anim-press.card, .anim-press.service-card, .anim-press.cleanup-category { transform: scale(0.97); }
    .anim-press.btn { transform: scale(0.94); }
    .anim-press.nav-item { transform: scale(0.95); }
    .anim-press.reg-tree-node { transform: scale(0.97); }
    .anim-press.form-group input { transform: scale(0.98); }
    .anim-press.theme-toggle { transform: scale(0.93); }
    .anim-press.reg-actions button { transform: scale(0.94); }
  `;
  document.head.appendChild(style);

  const selector = ".card, .btn, .nav-item, .service-card, .cleanup-category, .reg-tree-node, .form-group input, .theme-toggle, .reg-actions button";

  function findEl(target) {
    return target.closest(selector);
  }

  document.addEventListener("mousedown", function (e) {
    const el = findEl(e.target);
    if (el) el.classList.add("anim-press");
  });

  document.addEventListener("mouseup", function () {
    document.querySelectorAll(".anim-press").forEach(function (el) {
      el.classList.remove("anim-press");
    });
  });
})();
