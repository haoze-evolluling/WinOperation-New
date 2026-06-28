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

  function buildCombinedSelector(selectors) {
    return Object.values(selectors).join(", ");
  }

  class AnimationsEngine {
    constructor() {
      this.selectors = cfg.selectors || {};
      this.combinedSelector = buildCombinedSelector(this.selectors);
      this.currentHover = null;
      this.handlers = {
        mouseover: this.onMouseOver.bind(this),
        mouseout: this.onMouseOut.bind(this),
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

      document.addEventListener("mouseover", this.handlers.mouseover);
      document.addEventListener("mouseout", this.handlers.mouseout);
      document.addEventListener("mousedown", this.handlers.mousedown);
      document.addEventListener("mouseup", this.handlers.mouseup);
    }

    findAnimatedElement(target) {
      if (!target) return null;
      return target.closest(this.combinedSelector);
    }

    onMouseOver(e) {
      const el = this.findAnimatedElement(e.target);
      if (el && el !== this.currentHover) {
        if (this.currentHover) {
          this.currentHover.classList.remove("anim-lift");
        }
        el.classList.add("anim-lift");
        this.currentHover = el;
      }
    }

    onMouseOut(e) {
      const el = this.findAnimatedElement(e.target);
      if (el && el === this.currentHover && !el.contains(e.relatedTarget)) {
        el.classList.remove("anim-lift");
        this.currentHover = null;
      }
    }

    onMouseDown(e) {
      const el = this.findAnimatedElement(e.target);
      if (el) {
        el.classList.add("anim-press");
        el.classList.remove("anim-lift");
      }
    }

    onMouseUp() {
      if (this.currentHover) {
        this.currentHover.classList.remove("anim-press");
      }
    }

    destroy() {
      document.removeEventListener("mouseover", this.handlers.mouseover);
      document.removeEventListener("mouseout", this.handlers.mouseout);
      document.removeEventListener("mousedown", this.handlers.mousedown);
      document.removeEventListener("mouseup", this.handlers.mouseup);
      if (this.currentHover) {
        this.currentHover.classList.remove("anim-lift");
        this.currentHover.classList.remove("anim-press");
        this.currentHover = null;
      }
      const style = document.getElementById("animations-injected");
      if (style) style.remove();
    }
  }

  window.AnimationsEngine = AnimationsEngine;
  window.animationsEngine = new AnimationsEngine();
  window.animationsEngine.init();
})();
