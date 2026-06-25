# Implementation Plan: Full-Featured Cleanup & Registry

## Global Constraints

- No new dependencies (use stdlib only: os, shutil, tempfile, win32api, win32con)
- Follow existing patterns: `ok(data)` / `error(msg)` JSON envelope, lazy imports in routes
- Vanilla HTML/CSS/JS — no framework
- All responses use the existing JSON envelope pattern
- Chinese UI text for all user-facing strings
- Registry paths use `HKLM`, `HKCU`, `HKCR`, `HKU`, `HKCC` root notation
- ponytail: simplest solution that works; no speculative abstractions

---

## Task 1: Cleanup Scan API (Backend)

**Files to create/modify:**
- `backend/modules/cleanup.py` — extend with scan logic
- `backend/app.py` — add new routes

**What to implement:**

Extend `backend/modules/cleanup.py`:

1. Add `scan_cleanup_categories()` function that returns an array of categories:
   - `temp_files`: scans `%TEMP%` and `%LOCALAPPDATA%\Temp`, counts files + total size
   - `browser_cache`: scans Chrome/Edge/Firefox default cache dirs
   - `thumbnail_cache`: scans `%LOCALAPPDATA%\Microsoft\Windows\Explorer\thumbcache_*`
   - `windows_update`: scans `%WINDIR%\SoftwareDistribution\Download`
   - `recycle_bin`: uses `send2trash` or shell to get recycle bin size (ponytail: use ctypes SHQueryRecycleBin)
   - Each category: `{id, name, description, file_count, size_bytes, size_mb, paths: [...]}`

2. Add `execute_cleanup(category_ids)` function that takes an array of category IDs and cleans only those:
   - Reuse existing `do_cleanup_temp()` for `temp_files`
   - Add new cleaners for each category
   - Return `{cleaned: [...], failed: [...], total_freed_mb}`

3. Helper `_dir_size(path)` already exists, reuse it.

**New routes in `backend/app.py`:**
- `POST /api/cleanup/scan` → calls `scan_cleanup_categories()`
- `POST /api/cleanup/execute` → body: `{categories: ["temp_files", "browser_cache"]}`, calls `execute_cleanup()`

** ponyitail notes:**
- Use `ctypes.windll.shell32.SHQueryRecycleBinW` for recycle bin size — no pip dependency
- Browser cache paths: use common defaults, skip if dir doesn't exist
- `_dir_size` is O(n) scan, acceptable for a cleanup tool (ponytail: this exists)

---

## Task 2: Registry List/Tree/Batch API (Backend)

**Files to modify:**
- `backend/utils/registry.py` — add new low-level functions
- `backend/modules/registry.py` — add high-level wrappers
- `backend/app.py` — add new routes

**What to implement:**

In `backend/utils/registry.py`, add:
- `list_subkeys(reg_path)` → `{subkeys: [str], values: [{name, data, type_int}]}` using `RegEnumKeyEx` and `RegEnumValue`
- `tree_subkeys(reg_path, max_depth=2)` → recursively build tree `{path, subkeys: [{name, path, children: [...]}], values_count}`

In `backend/modules/registry.py`, add:
- `list_registry(reg_path)` → wraps `list_subkeys`, maps type_int to string
- `tree_registry(reg_path, max_depth=2)` → wraps `tree_subkeys`
- `batch_read_registry(entries)` → `{results: [{path, key, value, type, status}]}`
- `batch_write_registry(entries)` → `{results: [{path, key, value, type, status}]}`

**New routes in `backend/app.py`:**
- `GET /api/registry/list/<path:reg_path>` → `list_registry()`
- `GET /api/registry/tree/<path:reg_path>?depth=2` → `tree_registry()`
- `POST /api/registry/batch-read` → body: `{entries: [{path, key}]}`
- `POST /api/registry/batch-write` → body: `{entries: [{path, key, value, type}]}`

** ponytail notes:**
- `max_depth` default 2, prevent runaway recursion
- Type mapping already exists in TYPE_MAP, reuse it

---

## Task 3: Registry Import/Export API (Backend)

**Files to modify:**
- `backend/utils/registry.py` — add export/import
- `backend/modules/registry.py` — add wrappers
- `backend/app.py` — add routes

**What to implement:**

In `backend/utils/registry.py`, add:
- `export_reg(reg_path)` → generates standard `.reg` file format text:
  ```
  Windows Registry Editor Version 5.00
  
  [HKEY_CURRENT_USER\Path]
  "KeyName"="value"
  "DwordKey"=dword:00000001
  ```
  - Handles REG_SZ (quoted string), REG_DWORD (hex), REG_BINARY (hex bytes)
  - Returns string content

- `import_reg(reg_text)` → parses `.reg` format and writes values:
  - Parse sections `[HKEY_...]`
  - Parse value lines `"name"="value"` and `"name"=dword:XXXX`
  - Skip `Windows Registry Editor Version` header line
  - Use existing `write_key` for each value

**In `backend/modules/registry.py`, add:**
- `export_registry(reg_path)` → wraps `export_reg()`
- `import_registry(reg_text)` → wraps `import_reg()`, returns `{imported: N, failed: [...], errors: [...]}`

**New routes in `backend/app.py`:**
- `POST /api/registry/export` → body: `{path}`, returns `text/plain` with `.reg` content type
- `POST /api/registry/import` → body: raw `.reg` text, calls `import_registry()`

** ponytail notes:**
- Parser is simple line-by-line, not a full grammar (YAGNI)
- Handle only the most common formats: REG_SZ, REG_DWORD
- Skip unknown formats silently

---

## Task 4: Cleanup Panel UI + CSS (Frontend)

**Files to modify:**
- `frontend/index.html` — rewrite cleanup panel
- `frontend/js/main.js` — add cleanup functions
- `frontend/css/style.css` — add styles

**What to implement:**

Rewrite the cleanup panel in `index.html`:
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

In `main.js`, add:
- `doScanCleanup()` — calls `/api/cleanup/scan`, renders category cards with checkboxes
- `doCleanupSelected()` — collects checked categories, calls `/api/cleanup/execute`
- `renderCleanupCategories(categories)` — renders cards, each showing: name, description, file count, size, checkbox
- `renderCleanupResult(result)` — shows result cards with freed MB, cleaned count, errors

CSS additions:
- `.cleanup-actions` — button group
- `.cleanup-categories` — grid of category cards
- `.cleanup-category` — individual card with checkbox
- `.cleanup-category-header` — checkbox + name + size
- `.cleanup-category-desc` — description text
- `.result-area` — container for results
- `.result-card` — success/warning/error result display

---

## Task 5: Registry Panel UI + CSS (Frontend)

**Files to modify:**
- `frontend/index.html` — rewrite registry panel
- `frontend/js/main.js` — add registry functions
- `frontend/css/style.css` — add styles

**What to implement:**

Rewrite the registry panel in `index.html`:
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

In `main.js`, add:
- `loadRegTree()` — calls `/api/registry/tree/HKCU?depth=2`, renders tree
- `loadRegValues(path)` — calls `/api/registry/list/<path>`, renders table rows
- `refreshRegValues()` — reloads current path's values
- `showRegWriteForm()` / `hideRegWriteForm()` — toggle write form
- `writeReg()` — calls `/api/registry/write/<path>` with type support
- `exportCurrentReg()` — calls `/api/registry/export`, triggers download
- `importRegFile()` — triggers file input
- `doImportReg(event)` — reads file, calls `/api/registry/import`

CSS additions:
- `.reg-layout` — flex row: sidebar + main
- `.reg-sidebar` — left panel with tree
- `.reg-tree` — tree node list with indent
- `.reg-tree-node` — clickable path segment
- `.reg-tree-node:hover` — highlight
- `.reg-main` — right panel
- `.reg-toolbar` — button group
- `.reg-path-display` — current path breadcrumb
- `.reg-values-table` — values list table
- `.reg-write-form` — inline write form
- `.reg-type-badge` — colored type label

---

## Task 6: CSS Global Styles for New Components

**Files to modify:**
- `frontend/css/style.css` — add all new component styles

**What to add:**

Add these CSS rules to `style.css`:

```css
/* Cleanup panel */
.cleanup-actions { display: flex; gap: 12px; margin-bottom: 20px; }
.cleanup-categories { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 12px; }
.cleanup-category { ... card-like styles ... }
.cleanup-category-header { display: flex; align-items: center; gap: 10px; }
.cleanup-category-desc { color: var(--text-secondary); font-size: 0.85em; }

/* Registry panel */
.reg-layout { display: flex; gap: 16px; min-height: 400px; }
.reg-sidebar { width: 260px; flex-shrink: 0; }
.reg-tree { margin-top: 12px; }
.reg-tree-node { padding: 6px 8px; cursor: pointer; border-radius: var(--radius-sm); }
.reg-tree-node:hover { background: var(--accent-light); }
.reg-main { flex: 1; }
.reg-toolbar { display: flex; gap: 8px; margin-bottom: 12px; flex-wrap: wrap; }
.reg-path-display { ... }

/* Shared */
.btn-sm { padding: 4px 12px; font-size: 0.8em; }
.btn-secondary { background: var(--bg-layer3); color: var(--text-primary); }
.btn-secondary:hover { background: var(--border-standard); }
.btn-success { background: #0F7B0F; }
.btn-success:hover { background: #148A14; }
```

---

## Execution Order

1. Task 1 (cleanup backend) — standalone
2. Task 2 (registry list/tree/batch) — standalone
3. Task 3 (registry import/export) — depends on Task 2's utils
4. Task 4 (cleanup UI) — depends on Task 1
5. Task 5 (registry UI) — depends on Task 2 + 3
6. Task 6 (CSS) — depends on Task 4 + 5

Tasks 1, 2 can run in parallel. Task 3 after Task 2. Tasks 4, 5, 6 after their dependencies.
