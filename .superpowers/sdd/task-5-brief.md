# Task 5: Registry Panel UI + CSS (Frontend)

## What to Build

Rewrite the registry panel with tree navigation and value table.

## Files to Modify

- `frontend/index.html` — rewrite registry panel section
- `frontend/js/main.js` — add registry functions
- `frontend/css/style.css` — add styles

## Requirements

### 1. HTML (`frontend/index.html`)

Replace the existing registry panel (`#panel-registry`) with:
```html
<section id="panel-registry" class="panel">
    <h2>注册表操作</h2>
    <div class="reg-layout">
        <div class="reg-sidebar">
            <input type="text" id="reg-tree-path" placeholder="路径 (如 HKCU\Software)" value="HKCU">
            <button class="btn btn-sm" onclick="loadRegTree()">加载</button>
            <div id="reg-tree" class="reg-tree"></div>
        </div>
        <div class="reg-main">
            <div class="reg-toolbar">
                <button class="btn btn-primary" onclick="refreshRegValues()">刷新</button>
                <button class="btn btn-success" onclick="showRegWriteForm()">新建/修改值</button>
                <button class="btn btn-secondary" onclick="exportCurrentReg()">导出 .reg</button>
                <button class="btn btn-secondary" onclick="importRegFile()">导入 .reg</button>
                <input type="file" id="reg-import-file" accept=".reg" style="display:none" onchange="doImportReg(event)">
            </div>
            <div id="reg-path-display" class="reg-path-display">HKCU</div>
            <table class="reg-values-table">
                <thead><tr><th>名称</th><th>类型</th><th>数据</th><th>操作</th></tr></thead>
                <tbody id="reg-values-body"></tbody>
            </table>
            <div id="reg-write-form" class="reg-write-form" style="display:none">
                <input type="text" id="reg-write-key" placeholder="键名">
                <select id="reg-write-type">
                    <option value="REG_SZ">REG_SZ</option>
                    <option value="REG_DWORD">REG_DWORD</option>
                    <option value="REG_BINARY">REG_BINARY</option>
                </select>
                <input type="text" id="reg-write-value" placeholder="值">
                <button class="btn btn-primary" onclick="writeReg()">写入</button>
                <button class="btn btn-sm" onclick="hideRegWriteForm()">取消</button>
            </div>
        </div>
    </div>
    <div id="registry-result" class="result-area"></div>
</section>
```

### 2. JavaScript (`frontend/js/main.js`)

Replace existing `readReg()`, `writeReg()` with:

- `loadRegTree()`:
  - Reads `#reg-tree-path` value
  - Calls `GET /api/registry/tree/<path>?depth=2`
  - Renders tree nodes in `#reg-tree`

- `loadRegValues(path)`:
  - Calls `GET /api/registry/list/<path>`
  - Renders value rows in `#reg-values-body`
  - Updates `#reg-path-display`
  - Stores current path in `window._currentRegPath`

- `renderRegTree(tree, depth=0)`:
  - Recursive function to render tree nodes with indentation
  - Each node is clickable → calls `loadRegValues(node.path)`

- `refreshRegValues()`:
  - Calls `loadRegValues(window._currentRegPath)`

- `showRegWriteForm()` / `hideRegWriteForm()`:
  - Toggle `#reg-write-form` visibility

- `writeReg()`:
  - Reads path from `#reg-tree-path`, key, value, type from form
  - Calls `POST /api/registry/write/<path>` with body `{key, value, type}`
  - On success, refreshes values and hides form

- `exportCurrentReg()`:
  - Reads current path
  - Calls `POST /api/registry/export` with body `{path}`
  - Creates download link for `.reg` file

- `importRegFile()`:
  - Triggers `#reg-import-file` click

- `doImportReg(event)`:
  - Reads file content
  - Calls `POST /api/registry/import` with body = file text
  - Shows result in `#registry-result`

### 3. CSS (`frontend/css/style.css`)

Add styles:
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
.reg-values-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    margin-top: 0;
    border-radius: var(--radius-lg);
    overflow: hidden;
    box-shadow: var(--shadow-card);
    border: 1px solid var(--border-subtle);
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

## Patterns to Follow

- Use existing `api()` helper
- Chinese UI text
- No raw JSON dumps in final display
- Tree nodes use monospace font for paths

## Acceptance Criteria

- Tree loads and displays registry structure
- Clicking tree node loads values in right panel
- Values shown in table with name, type badge, data
- Write form allows entering key, type, value
- Export creates downloadable .reg file
- Import reads .reg file and shows result
