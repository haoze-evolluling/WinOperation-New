# Task 2: Registry List/Tree/Batch API (Backend)

## What to Build

Add registry enumeration and batch read/write APIs.

## Files to Modify

- `backend/utils/registry.py` — add low-level functions
- `backend/modules/registry.py` — add wrappers
- `backend/app.py` — add routes

## Requirements

### 1. `list_subkeys(reg_path)` in `backend/utils/registry.py`

Returns:
```python
{
    "subkeys": ["SubKey1", "SubKey2"],
    "values": [{"name": "ValueName", "data": ..., "type_int": 1}]
}
```

Use `win32api.RegEnumKeyEx` for subkeys, `win32api.RegEnumValue` for values.

### 2. `tree_subkeys(reg_path, max_depth=2)` in `backend/utils/registry.py`

Recursively builds tree:
```python
{
    "path": "HKCU\\Software",
    "subkeys": [
        {"name": "Microsoft", "path": "HKCU\\Software\\Microsoft", "children": [...], "values_count": 3}
    ],
    "values_count": 2
}
```

Stop recursion at `max_depth`.

### 3. High-level wrappers in `backend/modules/registry.py`

- `list_registry(reg_path)` — wraps `list_subkeys`, maps `type_int` to string using existing `TYPE_MAP`
- `tree_registry(reg_path, max_depth=2)` — wraps `tree_subkeys`
- `batch_read_registry(entries)` — `entries: [{path, key}]`, returns `{results: [{path, key, value, type, status}]}`
- `batch_write_registry(entries)` — `entries: [{path, key, value, type}]`, returns `{results: [{path, key, value, type, status}]}`

### 4. New routes in `backend/app.py`

- `GET /api/registry/list/<path:reg_path>` → `list_registry()`
- `GET /api/registry/tree/<path:reg_path>?depth=2` → `tree_registry()`
- `POST /api/registry/batch-read` → body: `{"entries": [{"path": "HKCU\\...", "key": "Name"}]}`
- `POST /api/registry/batch-write` → body: `{"entries": [{"path": "HKCU\\...", "key": "Name", "value": "x", "type": "REG_SZ"}]}`

## Patterns to Follow

- Existing `read_registry()` and `write_registry()` are the pattern
- `TYPE_MAP` already exists, reuse it
- `HKEY_MAP` already exists, reuse it

## Acceptance Criteria

- `GET /api/registry/list/HKCU` returns subkeys and values of HKCU root
- `GET /api/registry/tree/HKCU\Software?depth=1` returns one level of tree
- `POST /api/registry/batch-read` processes multiple entries
- All errors return `{"status": "error", "error": "..."}`
