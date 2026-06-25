# Task 1: Cleanup Scan API (Backend)

## What to Build

Extend the cleanup module with scan-and-select functionality.

## Files to Modify

- `backend/modules/cleanup.py` — extend
- `backend/app.py` — add routes

## Requirements

### 1. `scan_cleanup_categories()` in `backend/modules/cleanup.py`

Returns array of cleanup categories, each with:
- `id`: string identifier (e.g. "temp_files")
- `name`: display name in Chinese
- `description`: brief description
- `file_count`: number of items
- `size_bytes`: total size in bytes
- `size_mb`: total size in MB (rounded to 1 decimal)
- `paths`: array of paths scanned

Categories to include:
1. **temp_files** — `%TEMP%` and `%LOCALAPPDATA%\Temp`
2. **browser_cache** — Chrome/Edge/Firefox default cache dirs:
   - `%LOCALAPPDATA%\Google\Chrome\User Data\Default\Cache`
   - `%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\Cache`
   - `%LOCALAPPDATA%\Mozilla\Firefox\Profiles\*\cache2` (ponytail: glob with `glob` module)
3. **thumbnail_cache** — `%LOCALAPPDATA%\Microsoft\Windows\Explorer\thumbcache_*` files
4. **windows_update** — `%WINDIR%\SoftwareDistribution\Download`
5. **recycle_bin** — use `ctypes.windll.shell32.SHQueryRecycleBinW(None, byref(shell_script))` to get total size

For each category, count items and sum sizes. Skip inaccessible paths gracefully.

### 2. `execute_cleanup(category_ids)` in `backend/modules/cleanup.py`

Takes array of category ID strings. For each:
- `temp_files`: reuse existing `do_cleanup_temp()` logic (inline it or refactor)
- `browser_cache`: delete files in cache dirs
- `thumbnail_cache`: delete `thumbcache_*` files
- `windows_update`: delete contents of `SoftwareDistribution\Download`
- `recycle_bin`: use `send2trash` or ctypes to empty

Returns:
```python
{
    "cleaned": [{"category": "temp_files", "path": "...", "size_mb": 1.2}, ...],
    "failed": [{"category": "xxx", "path": "...", "error": "..."}],
    "total_freed_mb": 42.5
}
```

### 3. New routes in `backend/app.py`

- `POST /api/cleanup/scan` → calls `scan_cleanup_categories()`
- `POST /api/cleanup/execute` → body: `{"categories": ["temp_files", "browser_cache"]}`, calls `execute_cleanup()`

## Patterns to Follow

- Use `ok(data)` / `error(msg)` from `app.py`
- Lazy import inside route handlers
- Skip on `PermissionError` / `OSError` (existing pattern)
- Chinese UI strings

## Acceptance Criteria

- `POST /api/cleanup/scan` returns 5 categories with file counts and sizes
- `POST /api/cleanup/execute` with `["temp_files"]` cleans temp files and reports freed MB
- Inaccessible paths are silently skipped (no crash)
- Recycle bin size is returned without emptying it
