# Task 3: 填充 5 个模块（模拟数据）

## Context
这是 Windows 系统优化工具项目的 Task 3。你需要创建 5 个后端模块文件，每个暴露被 app.py 导入的接口函数，返回模拟数据。

## 需求

按以下内容逐字创建 5 个文件：

### 3a: `backend/modules/system_info.py`

```python
def get_system_info():
    return {
        "cpu": {"name": "Intel Core i7-10700K", "cores": 8, "usage": 45},
        "memory": {"total_gb": 32, "used_gb": 12.5, "percent": 39.1},
        "disk": [
            {"drive": "C:", "total_gb": 512, "free_gb": 234, "percent": 54.3},
            {"drive": "D:", "total_gb": 1024, "free_gb": 800, "percent": 21.9},
        ],
        "uptime": "3 days, 14:22:05",
    }
```

### 3b: `backend/modules/cleanup.py`

```python
def do_cleanup_temp(payload):
    return {
        "cleaned_paths": ["C:\\Users\\Acer\\AppData\\Local\\Temp"],
        "freed_mb": 128,
        "message": "模拟清理完成",
        "requires_admin": False,
    }
```

### 3c: `backend/modules/performance.py`

```python
def get_services():
    return {
        "services": [
            {"name": "wuauserv", "display_name": "Windows Update", "status": "running"},
            {"name": "WinDefend", "display_name": "Windows Defender", "status": "running"},
            {"name": "Schedule", "display_name": "Task Scheduler", "status": "running"},
        ]
    }


def toggle_service(name, action):
    return {
        "name": name,
        "action": action,
        "message": f"模拟{'启动' if action == 'start' else '停止'}服务 {name}",
        "requires_admin": True,
    }
```

### 3d: `backend/modules/registry.py`

```python
def read_registry(reg_path, key_name=""):
    return {
        "path": reg_path,
        "key": key_name,
        "value": "模拟注册表值",
        "type": "REG_SZ",
        "requires_admin": False,
    }


def write_registry(reg_path, key_name, value):
    return {
        "path": reg_path,
        "key": key_name,
        "value": value,
        "message": "模拟写入注册表",
        "requires_admin": True,
    }
```

### 3e: `backend/modules/network.py`

```python
def get_network_info():
    return {
        "adapters": [
            {
                "name": "Wi-Fi",
                "ip": "192.168.1.100",
                "dns": ["223.5.5.5", "114.114.114.114"],
                "speed": "867 Mbps",
            },
            {
                "name": "Ethernet",
                "ip": "192.168.1.101",
                "dns": ["223.5.5.5"],
                "speed": "1 Gbps",
            },
        ]
    }
```

## 验证
写入文件后，运行：
```powershell
cd backend; python -c "
import modules.system_info, modules.cleanup, modules.performance, modules.registry, modules.network
print('all modules import ok')
"
```

## 报告
完成后写入报告文件 `docs/superpowers/sdd/task-3-report.md`，包含：
- 5 个文件路径
- 导入验证结果
- 任何问题

## 注意
- 不要修改 app.py 或其他文件
- 骨架阶段用模拟数据，pywin32 实现在后续迭代
- 提交：`git add backend/modules/*.py && git commit -m "feat: Task 3 - 5 个模块模拟数据"`
