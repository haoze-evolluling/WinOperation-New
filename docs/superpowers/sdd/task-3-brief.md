# Task 3 Brief: 实现 system_info.py（真实系统信息）

**Goal:** 将 `backend/modules/system_info.py` 从模拟数据替换为 WMI 真实查询，保持与前端兼容的返回结构。

**Files:**
- Modify: `backend/modules/system_info.py`

**Interfaces:**
- Consumes: `utils.wmi.query(wql)` — returns list[dict]
- Produces: `get_system_info() -> dict` with keys: `cpu`, `memory`, `disk`, `uptime`

**Return Structure (must match existing frontend expectations):**
```python
{
    "cpu": {"name": str, "cores": int, "usage": int},
    "memory": {"total_gb": float, "used_gb": float, "percent": float},
    "disk": [{"drive": str, "total_gb": float, "free_gb": float, "percent": float}, ...],
    "uptime": str,  # format: "X days, HH:MM:SS"
}
```

**Implementation:**

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

**Validation:**
- First verify current mock returns correct structure: `python -c "from modules.system_info import get_system_info; import json; print(json.dumps(get_system_info(), indent=2))"`
- Then verify real data: same command after modification

**Report file:** `docs/superpowers/sdd/task-3-report.md`

**Report contract:** Return status, commits, test results, and any concerns.
