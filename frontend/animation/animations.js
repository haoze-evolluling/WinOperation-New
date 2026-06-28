(function () {
  "use strict";

  const ANIM_CONFIG = window.ANIM_CONFIG || {};
  const DEFAULTS = {
    pressScale: 0.94,
    pressEasing: "cubic-bezier(0.34, 1.56, 0.64, 1)",
    pressDuration: 300,
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
      .anim-press {
        transition: transform ${cfg.pressDuration}ms ${cfg.pressEasing};
      }

      .anim-press.card, .anim-press.service-card, .anim-press.cleanup-category {
        transform: scale(0.97);
      }
      .anim-press.btn {
        transform: scale(${cfg.pressScale});
      }
      .anim-press.nav-item {
        transform: scale(0.95);
      }
      .anim-press.reg-tree-node {
        transform: scale(0.97);
      }
      .anim-press.form-group input {
        transform: scale(0.98);
      }
      .anim-press.theme-toggle {
        transform: scale(0.93);
      }
      .anim-press.reg-actions button {
        transform: scale(0.94);
      }
    `;
    document.head.appendChild(style);
  }

  function buildCombinedSelector(selectors) {
    return Object.values(selectors).join(", ");
  }

  class AnimationsEngine {
    constructor() {
      this.selectors = cfg.selectors || {};
      this.combinedSelector = buildCombinedSelector(this.selectors);
      this.handlers = {
        mousedown: this.onMouseDown.bind(this),
        mouseup: this.onMouseUp.bind(this),
      };
    }

    init() {
      if (prefersReducedMotion()) {
        console.log("[AnimationsEngine] Reduced motion preferred — animations disabled.");
        return;
      }
      if (!this.combinedSelector) return;

      injectStyles();

      document.addEventListener("mousedown", this.handlers.mousedown);
      document.addEventListener("mouseup", this.handlers.mouseup);
    }

    findAnimatedElement(target) {
      if (!target) return null;
      return target.closest(this.combinedSelector);
    }

    onMouseDown(e) {
      const el = this.findAnimatedElement(e.target);
      if (el) {
        el.classList.add("anim-press");
      }
    }

    onMouseUp() {
      document.querySelectorAll(".anim-press").forEach((el) => {
        el.classList.remove("anim-press");
      });
    }

    destroy() {
      document.removeEventListener("mousedown", this.handlers.mousedown);
      document.removeEventListener("mouseup", this.handlers.mouseup);
      const style = document.getElementById("animations-injected");
      if (style) style.remove();
    }
  }

  window.AnimationsEngine = AnimationsEngine;
  window.animationsEngine = new AnimationsEngine();
  window.animationsEngine.init();
})();
