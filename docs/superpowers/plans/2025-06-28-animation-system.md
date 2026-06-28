# Animation System Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add interactive hover-lift and click-press animations across all elements via a JS-driven CSS injection system, with animation logic centralized in a new `frontend/animation/` folder.

**Architecture:** AnimationsEngine scans registered selectors, listens for mouse events, toggles CSS classes, and injects all animation styles as a single `<style>` tag into `<head>. Config is a plain JS object exported from `config.js`. Respects `prefers-reduced-motion`.

**Tech Stack:** Vanilla JS, no dependencies. Flask serves `animation/` folder as static files automatically since it lives under `frontend/`.

## Global Constraints

- No external libraries; pure vanilla JS
- Animation logic must live under `frontend/animation/`
- Must respect `prefers-reduced-motion: reduce` — disable all animations when true
- No changes to backend routes or existing CSS files
- Existing hover color changes in CSS must be preserved (animations are additive)
- All new files must use LF line endings

---

### Task 1: Create animation config file

**Files:**
- Create: `frontend/animation/config.js`

**Interfaces:**
- Consumes: nothing
- Produces: `window.ANIM_CONFIG` — global config object consumed by AnimationsEngine

- [ ] **Step 1: Create config.js**

Create `frontend/animation/config.js` with the following content:

```js
window.ANIM_CONFIG = {
  liftDistance: 4,
  pressScale: 0.94,
  duration: 180,
  easing: "cubic-bezier(0.4, 0, 0.2, 1)",
  selectors: {
    card: ".card",
    btn: ".btn",
    navItem: ".nav-item",
    serviceCard: ".service-card",
    cleanupCategory: ".cleanup-category",
    regTreeNode: ".reg-tree-node",
    formInput: ".form-group input",
    themeToggle: ".theme-toggle",
    regActionBtn: ".reg-actions button",
  },
};
```

- [ ] **Step 2: Verify file exists**

Run: `dir frontend\animation\config.js`
Expected: file listed

- [ ] **Step 3: Commit**

```bash
git add frontend/animation/config.js
git commit -m "feat: add animation config with global parameters"
```

---

### Task 2: Create AnimationsEngine

**Files:**
- Create: `frontend/animation/animations.js`

**Interfaces:**
- Consumes: `window.ANIM_CONFIG` from config.js
- Produces: `window.AnimationsEngine` class with `.init()` method

- [ ] **Step 1: Create animations.js**

Create `frontend/animation/animations.js` with the following content:

```js
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
```

- [ ] **Step 2: Verify file exists**

Run: `dir frontend\animation\animations.js`
Expected: file listed

- [ ] **Step 3: Commit**

```bash
git add frontend/animation/animations.js
git commit -m "feat: add AnimationsEngine with hover lift and click press"
```

---

### Task 3: Wire animation system into the app

**Files:**
- Modify: `frontend/index.html` — add script tag
- Modify: `frontend/js/main.js` — initialize AnimationsEngine

**Interfaces:**
- Consumes: `window.AnimationsEngine` from animations.js
- Produces: animations initialized on page load

- [ ] **Step 1: Add script tag to index.html**

Edit `frontend/index.html`:

Add the line `<script src="/animation/animations.js"></script>` before `</body>`, right after the existing `<script src="/js/main.js"></script>`.

Resulting end of body should look like:
```html
    <script src="/js/main.js"></script>
    <script src="/animation/animations.js"></script>
</body>
```

- [ ] **Step 2: Initialize in main.js**

Edit `frontend/js/main.js`:

Current content:
```js
if (!restoreNavigation()) {
    activatePanel("dashboard");
}
```

New content:
```js
if (!restoreNavigation()) {
    activatePanel("dashboard");
}

if (window.AnimationsEngine) {
    window.animationsEngine = new AnimationsEngine();
    window.animationsEngine.init();
}
```

- [ ] **Step 3: Verify both files**

Run:
```bash
findstr "animation" frontend\index.html
findstr "AnimationsEngine" frontend\js\main.js
```
Expected: both show the new code

- [ ] **Step 4: Commit**

```bash
git add frontend/index.html frontend/js/main.js
git commit -m "feat: wire AnimationsEngine into app bootstrap"
```

---

### Task 4: Manual verification

**Files:**
- Test: run Flask server and verify in browser

- [ ] **Step 1: Start Flask server**

```bash
python backend/app.py
```

- [ ] **Step 2: Open browser**

Navigate to `http://localhost:5000`

- [ ] **Step 3: Verify animations**

Check the following:
1. Hover over a card → it lifts up slightly (`translateY(-4px)`)
2. Click a card → it compresses (`scale(0.97)`) then bounces back on release
3. Hover over a nav item → it slides right (`translateX(4px)`)
4. Click a button → it compresses (`scale(0.94)`)
5. Hover over a theme toggle button → it lifts up
6. Hover over reg-tree-node → it slides right and highlights

- [ ] **Step 4: Verify reduced motion**

In browser DevTools, toggle `prefers-reduced-motion: reduce` in the Rendering tab and refresh. All animations should be absent.

- [ ] **Step 5: Commit** (no code changes needed, just verification)

```bash
echo "Manual verification complete"
```
