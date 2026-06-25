# Task 6: CSS Global Styles for New Components

## What to Build

Add all CSS styles needed by the new cleanup and registry panels.

## Files to Modify

- `frontend/css/style.css` — append new styles

## Requirements

Add these style blocks to the end of `frontend/css/style.css`:

### Button Variants (add to existing .btn styles)
```css
.btn-sm {
    padding: 4px 12px;
    font-size: 0.8em;
}
.btn-secondary {
    background: var(--bg-layer3);
    color: var(--text-primary);
}
.btn-secondary:hover {
    background: var(--border-standard);
}
.btn-success {
    background: var(--success);
    color: white;
}
.btn-success:hover {
    background: #148A14;
    box-shadow: 0 4px 12px rgba(15, 123, 15, 0.25);
}
```

### Cleanup Panel Styles
```css
.cleanup-actions {
    display: flex;
    gap: 12px;
    margin-bottom: 20px;
}
.cleanup-categories {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 12px;
}
.cleanup-category {
    background: var(--bg-layer1);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-lg);
    padding: 16px;
    box-shadow: var(--shadow-card);
    transition: all var(--transition-fast);
    cursor: pointer;
}
.cleanup-category:hover {
    box-shadow: var(--shadow-hover);
    transform: translateY(-1px);
}
.cleanup-category-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 8px;
}
.cleanup-category-name {
    font-weight: 500;
    color: var(--text-primary);
}
.cleanup-category-meta {
    color: var(--text-secondary);
    font-size: 0.85em;
}
.cleanup-category-desc {
    color: var(--text-tertiary);
    font-size: 0.8em;
    margin-top: 4px;
}
```

### Registry Panel Styles
```css
.reg-layout {
    display: flex;
    gap: 16px;
    min-height: 400px;
}
.reg-sidebar {
    width: 260px;
    flex-shrink: 0;
    border-right: 1px solid var(--border-subtle);
    padding-right: 16px;
}
.reg-sidebar input {
    width: 100%;
    margin-bottom: 8px;
}
.reg-tree {
    margin-top: 8px;
}
.reg-tree-node {
    padding: 6px 8px;
    cursor: pointer;
    border-radius: var(--radius-sm);
    font-size: 0.9em;
    color: var(--text-secondary);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.reg-tree-node:hover {
    background: var(--accent-light);
    color: var(--accent);
}
.reg-tree-node.active {
    background: var(--accent-light);
    color: var(--accent);
    font-weight: 500;
}
.reg-main {
    flex: 1;
    min-width: 0;
}
.reg-toolbar {
    display: flex;
    gap: 8px;
    margin-bottom: 12px;
    flex-wrap: wrap;
}
.reg-path-display {
    font-family: "Cascadia Code", "Fira Code", Consolas, monospace;
    font-size: 0.95em;
    padding: 8px 12px;
    background: var(--bg-layer2);
    border-radius: var(--radius-sm);
    margin-bottom: 12px;
    color: var(--accent);
}
.reg-write-form {
    display: flex;
    gap: 8px;
    align-items: center;
    margin-top: 16px;
    padding: 16px;
    background: var(--bg-layer2);
    border-radius: var(--radius-lg);
}
.reg-write-form input,
.reg-write-form select {
    padding: 8px 12px;
    border-radius: var(--radius-sm);
    border: 1px solid var(--border-standard);
    background: var(--bg-input);
    color: var(--text-primary);
    font-family: inherit;
    font-size: 0.9em;
}
.reg-type-badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: var(--radius-sm);
    font-size: 0.75em;
    font-weight: 600;
    text-transform: uppercase;
    background: var(--accent-light);
    color: var(--accent);
}
```

### Result Display Styles (shared)
```css
.result-area {
    margin-top: 20px;
}
.result-card {
    padding: 16px 20px;
    background: var(--bg-layer2);
    border-radius: var(--radius-lg);
    border: 1px solid var(--border-subtle);
    border-left: 4px solid var(--accent);
    margin-bottom: 12px;
}
.result-card.success {
    border-left-color: var(--success);
}
.result-card.error {
    border-left-color: var(--danger);
}
.result-card.warning {
    border-left-color: #F0A030;
}
```

## Patterns to Follow

- Use existing CSS custom properties (var(--...))
- Match existing border-radius, shadow, and spacing values
- Dark theme support via existing `[data-theme="dark"]` block (no changes needed if using CSS vars)

## Acceptance Criteria

- All new classes defined in style.css
- Uses existing CSS custom properties
- Dark theme works automatically via existing variables
- No hardcoded colors
