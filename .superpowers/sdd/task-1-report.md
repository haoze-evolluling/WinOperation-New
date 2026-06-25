# Task 1: Cleanup Scan API (Backend) — Report

## Status: DONE

## Changes

### `backend/modules/cleanup.py`
- Added `_scan_dir(path)` — helper to count files and sum sizes in a directory
- Added `_get_recycle_bin_info()` — uses `ctypes.windll.shell32.SHQueryRecycleBinW` to get recycle bin size/item count
- Added `scan_cleanup_categories()` — returns 5 categories (temp_files, browser_cache, thumbnail_cache, windows_update, recycle_bin) with id, name, description, file_count, size_bytes, size_mb, paths
- Added `execute_cleanup(category_ids)` — deletes files for each requested category, returns cleaned/failed/total_freed_mb
- Kept existing `do_cleanup_temp()` and `_dir_size()` untouched
- Removed dead `_clean_path()` helper (never called)

### `backend/app.py`
- Added `POST /api/cleanup/scan` — calls `scan_cleanup_categories()`
- Added `POST /api/cleanup/execute` — body: `{"categories": ["temp_files", ...]}`, calls `execute_cleanup()`

### `backend/tests/test_cleanup.py` (new)
- `TestScanCleanupCategories::test_returns_five_categories` — mocks filesystem + ctypes, asserts 5 categories with all required fields and correct IDs
- `TestExecuteCleanup::test_temp_files_returns_cleaned_failed_freed` — mocks `os.scandir`, asserts cleaned/failed/total_freed_mb keys exist with correct types
- `TestExecuteCleanupEmpty::test_empty_categories_returns_empty_results` — asserts empty input returns empty cleaned/failed and 0.0 total_freed_mb

## Test Results
```
3 passed in 0.02s
```

## Skipped (YAGNI)
- No validation for unknown category IDs — unknown IDs silently ignored
- No batch-size limits — caller controls what to clean
- No progress callbacks — one-shot response, add when frontend needs streaming
- No `send2trash` dependency — used ctypes `SHEmptyRecycleBinW` (already available via pywin32)

## Concerns
- `execute_cleanup` has per-category scan+delete loops that are structurally identical — could extract a shared helper if more categories are added later
- No explicit test for `browser_cache` Firefox glob or `thumbnail_cache` thumbcache patterns — covered indirectly through the scan test's mocked glob
