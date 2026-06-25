# Task 5 Brief: 实现 performance.py（真实服务管理）

**Goal:** 将 `backend/modules/performance.py` 从模拟数据替换为 win32service 真实服务管理。

**Files:**
- Modify: `backend/modules/performance.py`

**Interfaces:**
- Consumes: `win32service`, `win32serviceutil` (pywin32)
- Produces: `get_services() -> dict` 和 `toggle_service(name, action) -> dict`

**Return Structures:**
```python
# get_services()
{"services": [{"name": str, "display_name": str, "status": str}, ...]}

# toggle_service()
{"name": str, "action": str, "message": str}
```

**Status mapping:**
- SERVICE_STOPPED → "stopped"
- SERVICE_START_PENDING → "starting"
- SERVICE_RUNNING → "running"
- SERVICE_STOP_PENDING → "stopping"
- SERVICE_PAUSED → "paused"
- default → "unknown"

**Implementation:**

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

**Validation:**
- Run: `python -c "from modules.performance import get_services; import json; svcs = get_services()['services']; print(f'found {len(svcs)} services'); print(json.dumps(svcs[:3], indent=2, ensure_ascii=False))"`

**Report file:** `docs/superpowers/sdd/task-5-report.md`

**Report contract:** Return status, commits, test results, and any concerns.
