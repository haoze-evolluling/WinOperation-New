# Task 3: Registry Import/Export API (Backend)

## What to Build

Add .reg file export and import functionality.

## Files to Modify

- `backend/utils/registry.py` — add export/import functions
- `backend/modules/registry.py` — add wrappers
- `backend/app.py` — add routes

## Requirements

### 1. `export_reg(reg_path)` in `backend/utils/registry.py`

Generates standard Windows .reg file format text:
```
Windows Registry Editor Version 5.00

[HKEY_CURRENT_USER\Software\MyApp]
"StringValue"="hello"
"DwordValue"=dword:00000001
```

- Header: `Windows Registry Editor Version 5.00\n\n`
- Section header: `[<root>\<path>]`
- REG_SZ values: `"Name"="Value"`
- REG_DWORD values: `"Name"=dword:XXXXXXXX`
- Skip REG_BINARY and unknown types (YAGNI)
- Enumerate all values at the given path (use `list_subkeys`'s values list)
- Do NOT recurse into subkeys (flat export only)

### 2. `import_reg(reg_text)` in `backend/utils/registry.py`

Parses .reg format text and writes values:
- Skip the header line (`Windows Registry Editor Version ...`)
- Parse section headers `[HKEY_...]` to determine current path
- Parse value lines:
  - `"Name"="Value"` → REG_SZ
  - `"Name"=dword:XXXXXXXX` → REG_DWORD (convert hex string to int)
- Use existing `write_key()` for each parsed value
- Return: `{"imported": N, "failed": [...], "errors": [...]}`

### 3. High-level wrappers in `backend/modules/registry.py`

- `export_registry(reg_path)` → wraps `export_reg()`, returns `{content: str, path: str}`
- `import_registry(reg_text)` → wraps `import_reg()`

### 4. New routes in `backend/app.py`

- `POST /api/registry/export` → body: `{"path": "HKCU\\Software\\MyApp"}`, returns text/plain with `Windows Registry Editor Version 5.00` header
- `POST /api/registry/import` → body: raw `.reg` text string, calls `import_registry()`

## Patterns to Follow

- `write_key()` in utils/registry.py already handles type parameter
- Existing error handling pattern: try/except, return error dict

## Acceptance Criteria

- Export produces valid .reg format with header
- Import of a simple .reg file creates the values
- Invalid lines are skipped with error recorded
- Header line is ignored during import
