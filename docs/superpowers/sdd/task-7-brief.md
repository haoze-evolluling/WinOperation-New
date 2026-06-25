# Task 7 Brief: 实现 network.py（真实网络信息）

**Goal:** 将 `backend/modules/network.py` 从模拟数据替换为 WMI 真实网络适配器查询。

**Files:**
- Modify: `backend/modules/network.py`

**Interfaces:**
- Consumes: `utils.wmi.query(wql)`
- Produces: `get_network_info() -> dict`

**Return Structure (must match existing frontend expectations):**
```python
{
    "adapters": [
        {
            "name": str,
            "ip": str,
            "dns": [str, ...],
            "speed": str,  # ponytail: leave empty, speed via WMI is unreliable
        },
        ...
    ]
}
```

**Implementation:**

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
            "dns": [],  # ponytail: DNS via separate query adds complexity for little value
            "speed": "",
        })
    return {"adapters": result}
```

**Validation:**
- Run: `python -c "from modules.network import get_network_info; import json; print(json.dumps(get_network_info(), indent=2, ensure_ascii=False))"`

**Report file:** `docs/superpowers/sdd/task-7-report.md`

**Report contract:** Return status, commits, test results, and any concerns.
