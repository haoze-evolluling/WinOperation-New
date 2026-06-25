# Task 2: Registry List/Tree/Batch API (Backend) — Report

## Status: DONE

## What Was Implemented

### `backend/utils/registry.py`
- **`list_subkeys(reg_path)`** — Enumerates subkeys via `RegEnumKeyEx` and values via `RegEnumValue`. Returns `{"subkeys": [...], "values": [...]}`.
- **`tree_subkeys(reg_path, max_depth=2)`** — Recursively builds a tree structure. Each node has `path`, `subkeys` (child nodes), `children` (alias), `values_count`.

### `backend/modules/registry.py`
- **`list_registry(reg_path)`** — Wraps `list_subkeys`, maps `type_int` to string via `TYPE_MAP`. Returns `{"status": "ok", "path": ..., "subkeys": [...], "values": [...]}`.
- **`tree_registry(reg_path, max_depth=2)`** — Wraps `tree_subkeys`.
- **`batch_read_registry(entries)`** — Processes `[{path, key}]` entries, returns `{results: [{path, key, value, type, status}]}`. Errors per-entry don't abort the batch.
- **`batch_write_registry(entries)`** — Processes `[{path, key, value, type}]` entries, returns `{results: [...]}`. Same per-entry error handling.

### `backend/app.py`
- `GET /api/registry/list/<path:reg_path>` → `list_registry()`
- `GET /api/registry/tree/<path:reg_path>?depth=2` → `tree_registry()`
- `POST /api/registry/batch-read` → `batch_read_registry()`
- `POST /api/registry/batch-write` → `batch_write_registry()`

## Tests
- `backend/tests/test_registry_extended.py` — 5 tests, all passing
- Tests: `list_subkeys` enumeration, `tree_subkeys` depth-0/depth-1, `batch_read_registry`, `batch_write_registry`

## Skipped
- Per-entry error type propagation in batch functions (returns generic error string; sufficient for initial API).
- Circular reference protection in `tree_subkeys` (registry trees don't have cycles in practice).

## Commit
(To be created: feature/cleanup-registry task 2)
