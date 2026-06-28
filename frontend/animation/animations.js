(function () {
  "use strict";

  const ANIM_CONFIG = window.ANIM_CONFIG || {};
  const DEFAULTS = {
    liftDistance: 4,
    pressScale: 0.94,
    duration: 180,
    easing: "cubic-bezier(0.4, 0, 0.2, 1)",
  };

  const cfg = { ...DEFAULTS, ...ANIM_CONFIG };

  function prefersReducedMotion() {
    return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  }

  function injectStyles() {
    if (prefersReducedMotion()) return;
    const style = document.createElement("style");
    style.id = "animations-injected";
    style.textContent = `
      .anim-lift { transition: transform ${cfg.duration}ms ${cfg.easing}, box-shadow ${cfg.duration}ms ${cfg.easing}; }
      .anim-press { transition: transform ${cfg.duration}ms ${cfg.easing}; }

      .anim-lift.card, .anim-lift.service-card, .anim-lift.cleanup-category {
        transform: translateY(-${cfg.liftDistance}px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
      }
      .anim-press.card, .anim-press.service-card, .anim-press.cleanup-category {
        transform: scale(0.97);
      }

      .anim-lift.btn { transform: translateY(-2px); }
      .anim-press.btn { transform: scale(${cfg.pressScale}); }

      .anim-lift.nav-item { transform: translateX(4px); }
      .anim-press.nav-item { transform: scale(0.95); }

      .anim-lift.reg-tree-node { transform: translateX(3px); }
      .anim-press.reg-tree-node { transform: scale(0.97); }

      .anim-lift.form-group input { transform: translateY(-1px); }
      .anim-press.form-group input { transform: scale(0.98); }

      .anim-lift.theme-toggle { transform: translateY(-2px); }
      .anim-press.theme-toggle { transform: scale(0.93); }

      .anim-lift.reg-actions button { transform: translateY(-2px); }
      .anim-press.reg-actions button { transform: scale(0.94); }
    `;
    document.head.appendChild(style);
  }

  class AnimationsEngine {
    constructor() {
      this.selectors = cfg.selectors || {};
      this.boundHandlers = [];
    }

    init() {
      if (prefersReducedMotion()) {
        console.log("[AnimationsEngine] Reduced motion preferred — animations disabled.");
        return;
      }
      injectStyles();
      Object.entries(this.selectors).forEach(([, sel]) => {
        document.querySelectorAll(sel).forEach((el) => this.attach(el));
      });
    }

    attach(el) {
      const onEnter = () => el.classList.add("anim-lift");
      const onLeave = () => { el.classList.remove("anim-lift"); el.classList.remove("anim-press"); };
      const onDown = () => { el.classList.add("anim-press"); el.classList.remove("anim-lift"); };
      const onUp = () => { el.classList.remove("anim-press"); };

      el.addEventListener("mouseenter", onEnter);
      el.addEventListener("mouseleave", onLeave);
      el.addEventListener("mousedown", onDown);
      el.addEventListener("mouseup", onUp);
      el.addEventListener("mouseleave", onLeave);

      this.boundHandlers.push({ el, onEnter, onLeave, onDown, onUp });
    }

    destroy() {
      this.boundHandlers.forEach(({ el, onEnter, onLeave, onDown, onUp }) => {
        el.removeEventListener("mouseenter", onEnter);
        el.removeEventListener("mouseleave", onLeave);
        el.removeEventListener("mousedown", onDown);
        el.removeEventListener("mouseup", onUp);
      });
      const style = document.getElementById("animations-injected");
      if (style) style.remove();
      this.boundHandlers = [];
    }
  }

  window.AnimationsEngine = AnimationsEngine;
})();
