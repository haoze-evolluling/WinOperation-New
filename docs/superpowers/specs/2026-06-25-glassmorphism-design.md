# Glassmorphism UI — Design Spec

**Date:** 2026-06-25  
**Scope:** Apply full glassmorphism across all frontend panels (scope A — full page).

---

## 1. Goal

Transform the existing flat UI into a cohesive glassmorphism design while preserving readability, preserving all existing functionality, and supporting both light and dark themes.

---

## 2. Approach

Pure CSS approach: extend existing `:root` and `[data-theme="dark"]` custom property blocks with a new `glass` variable family. Replace surface-level `background` and `border` declarations on every major component with the glass variants. Decorative background blobs on `body` via `::before` / `::after` pseudo-elements. No JS changes.

---

## 3. New CSS Variables

### Light theme (`:root`)

```css
--glass-bg: rgba(255, 255, 255, 0.62);
--glass-bg-strong: rgba(255, 255, 255, 0.82);
--glass-border: rgba(255, 255, 255, 0.35);
--glass-border-subtle: rgba(255, 255, 255, 0.18);
--glass-blur: 22px;
--glass-shadow: 0 4px 24px rgba(0, 0, 0, 0.06), 0 0 1px rgba(0, 0, 0, 0.08);
--glass-shadow-hover: 0 8px 32px rgba(0, 0, 0, 0.10), 0 0 1px rgba(0, 0, 0, 0.12);
```

### Dark theme (`[data-theme="dark"]`)

```css
--glass-bg: rgba(48, 48, 48, 0.62);
--glass-bg-strong: rgba(48, 48, 48, 0.82);
--glass-border: rgba(255, 255, 255, 0.10);
--glass-border-subtle: rgba(255, 255, 255, 0.05);
--glass-blur: 22px;
--glass-shadow: 0 4px 24px rgba(0, 0, 0, 0.25), 0 0 1px rgba(0, 0, 0, 0.30);
--glass-shadow-hover: 0 8px 32px rgba(0, 0, 0, 0.35), 0 0 1px rgba(0, 0, 0, 0.40);
```

Notes:
- Glass variables use real color values (not `backdrop-filter` references) to keep the property system simple.
- `backdrop-filter: blur(var(--glass-blur))` is applied inline per component that needs it (cards, sidebar, tables). The `body` background itself does not need blur.

---

## 4. Body & Decorative Background

```css
body {
    background: linear-gradient(135deg, #E8EDF5 0%, #F0F4FA 40%, #E3E8F1 100%);
    position: relative;
    overflow-x: hidden;
}
body::before,
body::after {
    content: "";
    position: fixed;
    border-radius: 50%;
    filter: blur(80px);
    opacity: 0.55;
    pointer-events: none;
    z-index: -1;
}
body::before {
    width: 600px; height: 600px;
    top: -120px; right: -80px;
    background: radial-gradient(circle, rgba(0,120,212,0.18), transparent 70%);
}
body::after {
    width: 500px; height: 500px;
    bottom: -100px; left: 10%;
    background: radial-gradient(circle, rgba(120,180,255,0.14), transparent 70%);
}
```

Dark theme overrides:
- gradient → `linear-gradient(135deg, #1A1D23 0%, #22252B 40%, #1E2128 100%)`
- blobs → slightly higher opacity, cooler tones

---

## 5. Component Map

### Sidebar (`.sidebar`)
- `background: var(--glass-bg-strong)`
- `backdrop-filter: blur(30px) saturate(140%)`
- `border-right: 1px solid var(--glass-border)`

### Content area (`.content`)
- No background change (transparent, shows body gradient)

### Panel titles (`h2`)
- No change (text stays crisp)

### Dashboard cards (`.card`)
- `background: var(--glass-bg)`
- `backdrop-filter: blur(var(--glass-blur))`
- `border: 1px solid var(--glass-border)`
- `box-shadow: var(--glass-shadow)`
- hover: `box-shadow: var(--glass-shadow-hover); transform: translateY(-2px)`

### Cleanup categories (`.cleanup-category`)
- Same as `.card`

### Service cards (`.service-card`)
- Same as `.card`

### Result cards / result area (`.result`, `.result-card`, `.result-area`)
- `background: var(--glass-bg)`
- `backdrop-filter: blur(var(--glass-blur))`
- `border: 1px solid var(--glass-border)`

### Tables (`table`)
- `border-collapse: separate; border-spacing: 0;`
- `border-radius: var(--radius-lg); overflow: hidden;`
- `border: 1px solid var(--glass-border);`
- `box-shadow: var(--glass-shadow);`
- `thead th`: `background: var(--glass-bg-strong); backdrop-filter: blur(var(--glass-blur));`
- `tbody td`: alternating `background: var(--glass-bg)` / `rgba(...)` (or use `tr:nth-child(even)`)

### Forms / inputs (`.form-group input`, `.reg-sidebar input`, `.reg-write-form input/select`)
- `background: var(--glass-bg-strong)`
- `backdrop-filter: blur(16px)`
- `border: 1px solid var(--glass-border)`
- `color: var(--text-primary)`

### Registry write form (`.reg-write-form`)
- Same as `.card`

### Registry toolbar / cleanup-actions (`.reg-toolbar`, `.cleanup-actions`)
- These are action bars, not cards. Apply light glass:
  - `background: rgba(255,255,255,0.35)` (light) / `rgba(48,48,48,0.35)` (dark)
  - `backdrop-filter: blur(12px)`
  - `border: 1px solid var(--glass-border-subtle)`
  - `border-radius: var(--radius-lg)`
  - `padding: 12px`

### Buttons (`.btn-*`)
- Keep existing solid colors.
- Optional: add subtle glass to secondary buttons (`rgba(0,0,0,0.05)` base + border).
- Primary / danger / success remain fully opaque for contrast.

---

## 6. Readability Safeguards

1. **Inputs and table cells** use `--glass-bg-strong` (higher opacity) so text is never washed out.
2. **Buttons** remain opaque or use high-opacity glass + strong border to preserve click affordance.
3. **Borders are mandatory** on every glass component — without a border the blur effect collapses visually.
4. **Text colors unchanged** — existing `--text-primary/secondary/tertiary` remain, ensuring contrast ratios are preserved.
5. **Blur values capped** — max `30px` on sidebar, `22px` on cards, `16px` on inputs to limit GPU load.

---

## 7. Performance Considerations

- `backdrop-filter` is GPU-accelerated on modern browsers but can be expensive on large surfaces.
- Apply `backdrop-filter` only to containers (cards, sidebar, table header), NOT to `body` or full-width rows.
- Keep blur radii ≤ 30px.
- On low-end hardware or older GPUs the effect degrades gracefully to flat backgrounds (browser fallback).

---

## 8. Files Changed

| File | Changes |
|------|---------|
| `frontend/css/style.css` | Add glass variables in `:root` + `[data-theme="dark"]`; add body gradient + blobs; update selectors listed in §5 |
| `frontend/index.html` | No changes |
| `frontend/js/main.js` | No changes |
| `backend/**/*` | No changes |

---

## 9. Rollout Plan

1. Add glass variables.
2. Update `body` background and pseudo-elements.
3. Update sidebar.
4. Update `.card`, `.cleanup-category`, `.service-card`.
5. Update `.result`, `.result-card`.
6. Update `table`, `th`, `td`.
7. Update inputs and `.reg-write-form`.
8. Update `.reg-toolbar`, `.cleanup-actions`.
9. Verify in both light and dark themes.
10. Visual regression check: all text must remain readable, all controls clickable.

---

## 10. Success Criteria

- Every panel surfaces a glass effect (transparency + blur + border + shadow).
- Dark theme renders correctly with no washed-out text.
- Dashboard cards, cleanup categories, service cards, tables, forms, result areas all visually cohesive.
- No JS behavior changes; all existing functionality preserved.
- No layout shifts or overflow issues caused by pseudo-element blobs.
