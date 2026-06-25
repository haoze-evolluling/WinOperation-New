# Task 4: Cleanup Panel UI + CSS (Frontend)

## What to Build

Rewrite the cleanup panel with scan-and-select UI.

## Files to Modify

- `frontend/index.html` — rewrite cleanup panel section
- `frontend/js/main.js` — add cleanup functions
- `frontend/css/style.css` — add styles

## Requirements

### 1. HTML (`frontend/index.html`)

Replace the existing cleanup panel (`#panel-cleanup`) with:
```html
<section id="panel-cleanup" class="panel">
    <h2>系统清理</h2>
    <div class="cleanup-actions">
        <button class="btn btn-primary" onclick="doScanCleanup()">扫描可清理项</button>
        <button class="btn btn-danger" onclick="doCleanupSelected()" id="cleanup-execute-btn" disabled>清理选中项</button>
    </div>
    <div id="cleanup-categories" class="cleanup-categories"></div>
    <div id="cleanup-result" class="result-area"></div>
</section>
```

### 2. JavaScript (`frontend/js/main.js`)

Add these functions:

- `doScanCleanup()`:
  - Calls `POST /api/cleanup/scan`
  - On success, calls `renderCleanupCategories(result.data.categories)`
  - On error, shows error in `#cleanup-result`

- `renderCleanupCategories(categories)`:
  - Clears `#cleanup-categories`
  - For each category, creates a `.cleanup-category` card with:
    - Checkbox (name matches category `id`)
    - Category name
    - Description
    - File count
    - Size (MB)
  - Checkbox change → update `#cleanup-execute-btn` disabled state (disabled when none checked)

- `doCleanupSelected()`:
  - Collects checked category IDs
  - Calls `POST /api/cleanup/execute` with body `{"categories": ids}`
  - Calls `renderCleanupResult(result.data)`

- `renderCleanupResult(data)`:
  - Shows result cards in `#cleanup-result`
  - Display: total freed MB, list of cleaned items, any failed items
  - Format: card-style, not raw JSON

### 3. CSS (`frontend/css/style.css`)

Add styles:
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
.result-area {
    margin-top: 20px;
}
.result-card {
    padding: 16px 20px;
    background: var(--bg-layer2);
    border-radius: var(--radius-lg);
    border: 1px solid var(--border-subtle);
    margin-bottom: 12px;
}
.result-card.success {
    border-left: 4px solid var(--success);
}
.result-card.error {
    border-left: 4px solid var(--danger);
}
.result-card.warning {
    border-left: 4px solid #F0A030;
}
```

## Patterns to Follow

- Use existing `api()` helper for requests
- Use existing `ok()` / `error()` pattern from backend
- Chinese UI text
- No raw JSON dumps — use formatted cards

## Acceptance Criteria

- Clicking "扫描可清理项" shows 5 category cards
- Each card shows name, description, file count, size
- Selecting categories enables "清理选中项" button
- Clicking cleanup shows result cards with freed space
- Empty/unchecked state disables cleanup button
