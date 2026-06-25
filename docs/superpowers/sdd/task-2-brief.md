# Task 2 Brief: 创建 utils/registry.py 和 utils/wmi.py

**Goal:** 抽取工具层，统一注册表读写和 WMI 查询，供后续模块复用。

**Files:**
- Create: `backend/utils/registry.py`
- Create: `backend/utils/wmi.py`

**Global Constraints:**
- 只使用 stdlib + pywin32，不新增第三方依赖
- 统一 JSON 响应格式：`{"status": "ok|error", "data": ..., "error": ...}`

---

### utils/registry.py

**Purpose:** 封装 win32api 注册表操作，提供简洁的 read/write 接口。

**Interfaces Produced:**
- `read_key(reg_path, value_name="") -> (data, reg_type)` — 读取注册表值，返回 (数据, 类型)
- `write_key(reg_path, value_name, data, reg_type=win32con.REG_SZ)` — 写入注册表值

**Implementation:**

```python
import win32api
import win32con

HKEY_MAP = {
    "HKLM": win32con.HKEY_LOCAL_MACHINE,
    "HKCU": win32con.HKEY_CURRENT_USER,
    "HKCR": win32con.HKEY_CLASSES_ROOT,
    "HKU": win32con.HKEY_USERS,
    "HKCC": win32con.HKEY_CURRENT_CONFIG,
}


def _parse_root(reg_path):
    parts = reg_path.split("\\", 1)
    root_str = parts[0].upper()
    sub_path = parts[1] if len(parts) > 1 else ""
    root = HKEY_MAP.get(root_str)
    if root is None:
        raise ValueError(f"不支持的注册表根: {root_str}")
    return root, sub_path


def read_key(reg_path, value_name=""):
    root, sub_path = _parse_root(reg_path)
    key = None
    try:
        key = win32api.RegOpenKeyEx(root, sub_path, 0, win32con.KEY_READ)
        data, reg_type = win32api.RegQueryValueEx(key, value_name)
        return data, reg_type
    finally:
        if key:
            win32api.RegCloseKey(key)


def write_key(reg_path, value_name, data, reg_type=win32con.REG_SZ):
    root, sub_path = _parse_root(reg_path)
    key = None
    try:
        key = win32api.RegCreateKey(root, sub_path)
        win32api.RegSetValueEx(key, value_name, 0, reg_type, data)
    finally:
        if key:
            win32api.RegCloseKey(key)
```

**Validation:**
- Run: `python -c "import ast; ast.parse(open('utils/registry.py', encoding='utf-8').read()); print('ok')"`

---

### utils/wmi.py

**Purpose:** 封装 WMI COM 查询，统一返回 list[dict]。

**Interfaces Produced:**
- `query(wql) -> list[dict]` — 执行 WQL 查询，返回字典列表

**Implementation:**

```python
import win32com.client


def query(wql):
    obj = win32com.client.GetObject("winmgmts:\\\\.\\root\\cimv2")
    cols = None
    results = []
    for item in obj.ExecQuery(wql):
        if cols is None:
            cols = [p.name for p in item.Properties_]
        row = {c: getattr(item, c, None) for c in cols}
        results.append(row)
    return results
```

**Validation:**
- Run: `python -c "import ast; ast.parse(open('utils/wmi.py', encoding='utf-8').read()); print('ok')"`

---

**Report file:** `docs/superpowers/sdd/task-2-report.md`

**Report contract:** Return status, commits, test results, and any concerns.
