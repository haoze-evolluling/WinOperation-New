# Task 6 Brief: 实现 registry.py（真实注册表读写）

**Goal:** 将 `backend/modules/registry.py` 从模拟数据替换为真实注册表读写实现。

**Files:**
- Modify: `backend/modules/registry.py`

**Interfaces:**
- Consumes: `utils.registry.read_key(reg_path, value_name) -> (data, reg_type)` 和 `utils.registry.write_key(reg_path, value_name, data, reg_type)`
- Produces: `read_registry(path, key_name) -> dict` 和 `write_registry(path, key_name, value) -> dict`

**Return Structures:**
```python
# read_registry()
{"path": str, "key": str, "value": any, "type": str}

# write_registry()
{"path": str, "key": str, "value": any, "message": str}
```

**Type mapping:**
```python
TYPE_MAP = {
    win32con.REG_SZ: "REG_SZ",
    win32con.REG_DWORD: "REG_DWORD",
    win32con.REG_BINARY: "REG_BINARY",
    win32con.REG_MULTI_STRING: "REG_MULTI_STRING",
}
```

**Implementation:**

```python
from utils.registry import read_key, write_key
import win32con


TYPE_MAP = {
    win32con.REG_SZ: "REG_SZ",
    win32con.REG_DWORD: "REG_DWORD",
    win32con.REG_BINARY: "REG_BINARY",
    win32con.REG_MULTI_STRING: "REG_MULTI_STRING",
}


def read_registry(reg_path, key_name=""):
    data, reg_type = read_key(reg_path, key_name)
    return {
        "path": reg_path,
        "key": key_name,
        "value": data,
        "type": TYPE_MAP.get(reg_type, f"REG_UNKNOWN({reg_type})"),
    }


def write_registry(reg_path, key_name, value):
    write_key(reg_path, key_name, value)
    return {
        "path": reg_path,
        "key": key_name,
        "value": value,
        "message": "写入成功",
    }
```

**Validation:**
- Run: `python -c "from modules.registry import read_registry; import json; print(json.dumps(read_registry(r'HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion', 'ProductName'), indent=2))"`

**Report file:** `docs/superpowers/sdd/task-6-report.md`

**Report contract:** Return status, commits, test results, and any concerns.
