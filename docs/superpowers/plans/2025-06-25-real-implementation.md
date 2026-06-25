# Pywin32 真实功能实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 5 个模块从模拟数据替换为 pywin32 真实 Windows API 实现，应用强制管理员权限启动

**Architecture:** 抽 `utils/registry.py` 和 `utils/wmi.py` 避免重复，各模块直接调用。app.py 启动时检查管理员权限，非管理员直接报错退出。

**Tech Stack:** Python 3, Flask, pywin32, 原生 HTML/CSS/JS

## Global Constraints

- 启动时检测管理员权限，非管理员直接报错退出，不降级运行
- 所有写操作默认有管理员权限，移除所有 `requires_admin` 字段
- 注册表读写统一走 `utils/registry.py`，WMI 查询统一走 `utils/wmi.py`
- 统一 JSON 响应格式：`{"status": "ok|error", "data": ..., "error": ...}`
- 写操作全部走 POST，前端保留确认弹窗
- 依赖只加 stdlib + 已安装的 pywin32，不新增第三方包

---

### Task 1: app.py 添加管理员权限检测

**Files:**
- Modify: `backend/app.py:1-83`

**Interfaces:**
- Consumes: `ctypes.windll.shell32.IsUserAnAdmin()` (stdlib)
- Produces: 非管理员时 Flask 不会启动，直接 sys.exit 输出错误信息

- [ ] **Step 1: 添加管理员检测并修改 app.py**

```python
from flask import Flask, jsonify, request, send_from_directory
import ctypes
import os
import sys

def require_admin():
    if not ctypes.windll.shell32.IsUserAnAdmin():
        print("错误: 此应用需要管理员权限运行，请右键以管理员身份启动。", file=sys.stderr)
        sys.exit(1)

require_admin()

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")


@app.route("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/<path:path>")
def static_files(path):
    return send_from_directory(FRONTEND_DIR, path)


def ok(data=None):
    return jsonify({"status": "ok", "data": data})


def error(message):
    return jsonify({"status": "error", "error": message})


# ---- 系统信息 ----
@app.route("/api/system-info", methods=["GET"])
def system_info():
    from modules.system_info import get_system_info
    return ok(get_system_info())


# ---- 系统清理 ----
@app.route("/api/cleanup/temp-files", methods=["POST"])
def cleanup_temp_files():
    from modules.cleanup import do_cleanup_temp
    result = do_cleanup_temp(request.json or {})
    return ok(result)


# ---- 性能调优 ----
@app.route("/api/performance/services", methods=["GET"])
def get_services():
    from modules.performance import get_services
    return ok(get_services())


@app.route("/api/performance/services/<name>", methods=["POST"])
def toggle_service(name):
    from modules.performance import toggle_service
    action = (request.json or {}).get("action", "start")
    result = toggle_service(name, action)
    return ok(result)


# ---- 注册表 ----
@app.route("/api/registry/read/<path:reg_path>", methods=["GET"])
def registry_read(reg_path):
    from modules.registry import read_registry
    key_name = request.args.get("key", "")
    value = read_registry(reg_path, key_name)
    return ok(value)


@app.route("/api/registry/write/<path:reg_path>", methods=["POST"])
def registry_write(reg_path):
    from modules.registry import write_registry
    payload = request.json or {}
    result = write_registry(reg_path, payload.get("key", ""), payload.get("value", ""))
    return ok(result)


# ---- 网络 ----
@app.route("/api/network/info", methods=["GET"])
def network_info():
    from modules.network import get_network_info
    return ok(get_network_info())


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
```

- [ ] **Step 2: 验证语法正确**

```bash
cd backend
python -c "import ast; ast.parse(open('app.py', encoding='utf-8').read()); print('ok')"
```

- [ ] **Step 3: Commit**

```bash
git add backend/app.py
git commit -m "feat: 启动时强制管理员权限检测"
```

---

### Task 2: 创建工具层 utils/registry.py 和 utils/wmi.py

**Files:**
- Create: `backend/utils/registry.py`
- Create: `backend/utils/wmi.py`

**Interfaces:**
- Produces: `utils.registry.read_key(root, path, value_name) -> (data, type)` 和 `utils.registry.write_key(root, path, value_name, data, reg_type)`
- Produces: `utils.wmi.query(wql) -> list[dict]`

#### 2a: utils/registry.py

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

#### 2b: utils/wmi.py

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

- [ ] **Step 1: 创建 utils/registry.py**

```python
# (use content above)
```

- [ ] **Step 2: 创建 utils/wmi.py**

```python
# (use content above)
```

- [ ] **Step 3: 验证语法**

```bash
cd backend
python -c "import ast; ast.parse(open('utils/registry.py', encoding='utf-8').read()); print('registry ok')"
python -c "import ast; ast.parse(open('utils/wmi.py', encoding='utf-8').read()); print('wmi ok')"
```

- [ ] **Step 4: Commit**

```bash
git add backend/utils/registry.py backend/utils/wmi.py
git commit -m "feat: 抽 registry 和 wmi 工具层"
```

---

### Task 3: 实现 system_info.py（真实系统信息）

**Files:**
- Modify: `backend/modules/system_info.py`

**Interfaces:**
- Consumes: `utils.wmi.query(wql)`
- Produces: `get_system_info() -> dict` 包含 cpu, memory, disk, uptime

```python
from utils.wmi import query as wmi_query


def get_system_info():
    cpu_rows = wmi_query("SELECT Name, NumberOfCores, LoadPercentage FROM Win32_Processor")
    cpu = {
        "name": cpu_rows[0]["Name"] if cpu_rows else "Unknown",
        "cores": int(cpu_rows[0]["NumberOfCores"]) if cpu_rows else 0,
        "usage": int(cpu_rows[0]["LoadPercentage"]) if cpu_rows else 0,
    }

    os_rows = wmi_query("SELECT TotalVisibleMemorySize, FreePhysicalMemory FROM Win32_OperatingSystem")
    if os_rows:
        total_kb = int(os_rows[0]["TotalVisibleMemorySize"])
        free_kb = int(os_rows[0]["FreePhysicalMemory"])
        total_gb = round(total_kb / (1024 * 1024), 1)
        used_gb = round((total_kb - free_kb) / (1024 * 1024), 1)
        percent = round((total_kb - free_kb) / total_kb * 100, 1)
    else:
        total_gb = used_gb = percent = 0

    disk_rows = wmi_query("SELECT DeviceID, Size, FreeSpace FROM Win32_LogicalDisk WHERE DriveType=3")
    disk = []
    for row in disk_rows:
        total_gb_disk = round(int(row["Size"]) / (1024 ** 3), 1)
        free_gb_disk = round(int(row["FreeSpace"]) / (1024 ** 3), 1)
        disk.append({
            "drive": row["DeviceID"],
            "total_gb": total_gb_disk,
            "free_gb": free_gb_disk,
            "percent": round((1 - int(row["FreeSpace"]) / int(row["Size"])) * 100, 1),
        })

    import ctypes
    uptime_ms = ctypes.windll.kernel32.GetTickCount64()
    uptime_sec = uptime_ms / 1000
    days = int(uptime_sec // 86400)
    hours = int((uptime_sec % 86400) // 3600)
    minutes = int((uptime_sec % 3600) // 60)
    seconds = int(uptime_sec % 60)
    uptime = f"{days} days, {hours:02d}:{minutes:02d}:{seconds:02d}"

    return {
        "cpu": cpu,
        "memory": {"total_gb": total_gb, "used_gb": used_gb, "percent": percent},
        "disk": disk,
        "uptime": uptime,
    }
```

- [ ] **Step 1: 验证当前模拟数据返回结构**

```bash
cd backend
python -c "from modules.system_info import get_system_info; import json; print(json.dumps(get_system_info(), indent=2))"
```

- [ ] **Step 2: 替换为真实实现**

```python
# (use content above)
```

- [ ] **Step 3: 验证真实数据返回正常**

```bash
cd backend
python -c "from modules.system_info import get_system_info; import json; print(json.dumps(get_system_info(), indent=2))"
```

- [ ] **Step 4: Commit**

```bash
git add backend/modules/system_info.py
git commit -m "feat: system_info 使用 WMI 获取真实系统信息"
```

---

### Task 4: 实现 cleanup.py（真实清理）

**Files:**
- Modify: `backend/modules/cleanup.py`

**Interfaces:**
- Consumes: `os`, `shutil`, `tempfile` (stdlib)
- Produces: `do_cleanup_temp(payload) -> dict`

```python
import os
import shutil
import tempfile


def do_cleanup_temp(payload):
    temp_dirs = [
        tempfile.gettempdir(),
        os.path.expandvars(r"%LOCALAPPDATA%\Temp"),
    ]
    cleaned_paths = []
    freed_bytes = 0

    for temp_dir in temp_dirs:
        if not os.path.isdir(temp_dir):
            continue
        for entry in os.scandir(temp_dir):
            try:
                path = entry.path
                if entry.is_file() or entry.is_symlink():
                    size = entry.stat().st_size
                    os.remove(path)
                    freed_bytes += size
                    cleaned_paths.append(path)
                elif entry.is_dir():
                    dir_size = _dir_size(path)
                    shutil.rmtree(path)
                    freed_bytes += dir_size
                    cleaned_paths.append(path)
            except (PermissionError, OSError):
                continue

    freed_mb = round(freed_bytes / (1024 * 1024), 1)
    return {
        "cleaned_paths": cleaned_paths,
        "freed_mb": freed_mb,
        "message": f"清理完成，释放 {freed_mb} MB",
    }


def _dir_size(path):
    total = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            try:
                total += os.path.getsize(fp)
            except OSError:
                pass
    return total
```

- [ ] **Step 1: 替换 cleanup.py 为真实实现**

```python
# (use content above)
```

- [ ] **Step 2: 验证语法和导入**

```bash
cd backend
python -c "from modules.cleanup import do_cleanup_temp; import json; print(json.dumps(do_cleanup_temp({}), indent=2))"
```

- [ ] **Step 3: Commit**

```bash
git add backend/modules/cleanup.py
git commit -m "feat: cleanup 使用真实文件系统清理"
```

---

### Task 5: 实现 performance.py（真实服务管理）

**Files:**
- Modify: `backend/modules/performance.py`

**Interfaces:**
- Consumes: `win32service` (pywin32)
- Produces: `get_services() -> dict` 和 `toggle_service(name, action) -> dict`

```python
import win32service
import win32serviceutil


SERVICE_STATES = {
    win32service.SERVICE_STOPPED: "stopped",
    win32service.SERVICE_START_PENDING: "starting",
    win32service.SERVICE_RUNNING: "running",
    win32service.SERVICE_STOP_PENDING: "stopping",
    win32service.SERVICE_PAUSED: "paused",
}


def get_services():
    scm = win32service.OpenSCManager(None, None, win32service.SC_MANAGER_ENUMERATE_SERVICE)
    try:
        services = win32service.EnumServicesStatus(scm, win32service.SERVICE_WIN32, win32service.SERVICE_STATE_ALL)
        result = []
        for svc in services:
            name = svc[0]
            display = svc[1]
            status_code = svc[2][1]
            status = SERVICE_STATES.get(status_code, "unknown")
            result.append({"name": name, "display_name": display, "status": status})
        return {"services": result}
    finally:
        win32service.CloseServiceHandle(scm)


def toggle_service(name, action):
    if action == "start":
        win32serviceutil.StartService(name)
        msg = f"已启动服务 {name}"
    else:
        win32serviceutil.StopService(name)
        msg = f"已停止服务 {name}"
    return {"name": name, "action": action, "message": msg}
```

- [ ] **Step 1: 替换 performance.py**

```python
# (use content above)
```

- [ ] **Step 2: 验证语法和导入**

```bash
cd backend
python -c "from modules.performance import get_services; import json; svcs = get_services()['services']; print(f'found {len(svcs)} services'); print(json.dumps(svcs[:3], indent=2, ensure_ascii=False))"
```

- [ ] **Step 3: Commit**

```bash
git add backend/modules/performance.py
git commit -m "feat: performance 使用 win32service 管理真实服务"
```

---

### Task 6: 实现 registry.py（真实注册表读写）

**Files:**
- Modify: `backend/modules/registry.py`

**Interfaces:**
- Consumes: `utils.registry.read_key()` 和 `utils.registry.write_key()`
- Produces: `read_registry(path, key_name) -> dict` 和 `write_registry(path, key_name, value) -> dict`

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

- [ ] **Step 1: 替换 registry.py**

```python
# (use content above)
```

- [ ] **Step 2: 验证语法**

```bash
cd backend
python -c "from modules.registry import read_registry; import json; print(json.dumps(read_registry(r'HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion', 'ProductName'), indent=2))"
```

- [ ] **Step 3: Commit**

```bash
git add backend/modules/registry.py
git commit -m "feat: registry 使用真实注册表读写"
```

---

### Task 7: 实现 network.py（真实网络信息）

**Files:**
- Modify: `backend/modules/network.py`

**Interfaces:**
- Consumes: `utils.wmi.query(wql)`
- Produces: `get_network_info() -> dict`

```python
from utils.wmi import query as wmi_query


def get_network_info():
    adapters = wmi_query("""
        SELECT Description, IPAddress, DNSHostName 
        FROM Win32_NetworkAdapterConfiguration 
        WHERE IPEnabled = TRUE
    """)
    result = []
    for a in adapters:
        ips = a.get("IPAddress") or []
        ip = ips[0] if ips else ""
        result.append({
            "name": a.get("Description", ""),
            "ip": ip,
            "dns": [],  # DNS via separate query if needed
            "speed": "",
        })
    return {"adapters": result}
```

- [ ] **Step 1: 替换 network.py**

```python
# (use content above)
```

- [ ] **Step 2: 验证语法和数据**

```bash
cd backend
python -c "from modules.network import get_network_info; import json; print(json.dumps(get_network_info(), indent=2, ensure_ascii=False))"
```

- [ ] **Step 3: Commit**

```bash
git add backend/modules/network.py
git commit -m "feat: network 使用 WMI 获取真实网络适配器信息"
```

---

### Task 8: 前端微调：移除 requires_admin 相关提示

**Files:**
- Modify: `frontend/js/main.js`

**Interfaces:**
- Consumes: 当前 JS 逻辑
- Produces: 移除对 `requires_admin` 的检查（已不存在于后端响应）

- [ ] **Step 1: 检查 main.js 是否有 requires_admin 引用**

```bash
cd frontend/js
Select-String -Pattern "requires_admin" main.js
```

- [ ] **Step 2: 如无引用则跳过，有则移除相关代码**

- [ ] **Step 3: Commit**

```bash
git add frontend/js/main.js
git commit -m "chore: 移除前端 requires_admin 相关逻辑"
```

---

### Task 9: 全量验证

- [ ] **Step 1: 安装依赖（如未装）**

```bash
cd backend
pip install -r requirements.txt
```

- [ ] **Step 2: 以管理员权限启动并验证所有 API**

```bash
cd backend
python app.py
```

在另一个终端验证：
```bash
curl http://localhost:5000/api/system-info | python -m json.tool
curl -X POST http://localhost:5000/api/cleanup/temp-files -H "Content-Type: application/json" -d "{}" | python -m json.tool
curl http://localhost:5000/api/performance/services | python -m json.tool
curl http://localhost:5000/api/network/info | python -m json.tool
# 注册表读写测试（修改为实际存在的路径）
curl "http://localhost:5000/api/registry/read/HKLM/SOFTWARE/Microsoft/Windows%20NT/CurrentVersion?key=ProductName" | python -m json.tool
```

- [ ] **Step 3: 浏览器打开 http://localhost:5000 确认 5 个面板正常渲染**

- [ ] **Step 4: Commit（如修复了问题）**

```bash
git add -A
git commit -m "fix: 修复 pywin32 实现中的问题"
```
