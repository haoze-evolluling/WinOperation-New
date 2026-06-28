# Animation System Design

## Overview

Reintroduce interactive animations (hover lift, click press) across all interactive elements in the application, using a JS-driven injection approach. All animation logic lives in a new `animation/` folder.

## Architecture

```
animation/
  ├── animations.js   ← AnimationsEngine class (event listeners, class toggling, style injection)
  └── config.js       ← Central animation parameters (duration, distance, scale, easing)

index.html            ← <script src="/animation/animations.js">
frontend/js/main.js   ← new AnimationsEngine().init()
```

## Core Mechanism

1. `animations.js` exports `AnimationsEngine` class
2. `main.js` instantiates and calls `.init()` on DOMContentLoaded
3. Engine scans the page for registered selectors and attaches event listeners:
   - `mouseenter` / `mouseleave` → toggle hover class
   - `mousedown` / `mouseup` / `click` → toggle press class
4. Animation styles are injected as a single `<style>` tag into `<head>` by the engine
5. Engine reads `window.matchMedia('(prefers-reduced-motion: reduce)')` and disables all animations if true

## Animation Config (`config.js`)

```js
export const ANIM_CONFIG = {
  liftDistance: 4,
  pressScale: 0.94,
  duration: 180,
  easing: "cubic-bezier(0.4, 0, 0.2, 1)",
};
```

## Element Animations

| Selector | Hover Effect | Press Effect |
|----------|-------------|-------------|
| `.card` | `translateY(-4px)` + shadow deepen | `scale(0.97)` |
| `.btn` | existing color hover + `translateY(-2px)` | `scale(0.94)` |
| `.nav-item` | `translateX(4px)` | `scale(0.95)` |
| `.service-card` | `translateY(-3px)` + shadow deepen | `scale(0.97)` |
| `.cleanup-category` | `translateY(-3px)` + shadow deepen | `scale(0.97)` |
| `.reg-tree-node` | background highlight + `translateX(3px)` | `scale(0.97)` |
| `.form-group input` | border highlight + `translateY(-1px)` | `scale(0.98)` |
| `.theme-toggle` | `translateY(-2px)` | `scale(0.93)` |
| `.reg-actions button` | `translateY(-2px)` | `scale(0.94)` |

## Accessibility

- Respects `prefers-reduced-motion: reduce` — all animations disabled automatically
- No JS-only visual information; animations are purely decorative

## Registration API

Components can opt in by calling:
```js
AnimationsEngine.register('.card', { lift: 4, pressScale: 0.97 });
```

Defaults are pulled from `ANIM_CONFIG` unless overridden per-element.

## Dependencies

- None. Pure vanilla JS, no external libraries.
