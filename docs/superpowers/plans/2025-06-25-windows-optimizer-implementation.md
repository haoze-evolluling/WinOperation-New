# Windows 系统优化工具 — 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 搭建一个可运行的骨架：Flask 后端 + 原生 HTML/CSS/JS 前端，覆盖 5 个模块，用模拟数据先跑通流程。

**Architecture:** Flask 单文件入口 + 5 个模块文件，统一 JSON 响应。前端单页应用，左侧导航右侧面板，fetch 调用 API。

**Tech Stack:** Python 3, Flask, pywin32, 原生 HTML/CSS/JS

## Global Constraints

- 骨架阶段用模拟数据，pywin32 实现在后续迭代
- 写操作全部走 POST + 确认弹窗
- 需要管理员权限的操作返回 `requires_admin: true`
- 统一 JSON 响应格式：`{"status": "ok|error", "data": ..., "error": ...}`
- 零前端框架，原生实现

---

### Task 1: 搭建目录结构 + requirements.txt

**Files:**
- Create: `backend/requirements.txt`
- Create: `backend/app.py`
- Create: `backend/modules/__init__.py`
- Create: `backend/utils/__init__.py`
- Create: `backend/modules/system_info.py`
- Create: `backend/modules/cleanup.py`
- Create: `backend/modules/performance.py`
- Create: `backend/modules/registry.py`
- Create: `backend/modules/network.py`
- Create: `frontend/index.html`
- Create: `frontend/css/style.css`
- Create: `frontend/js/main.js`

- [ ] **Step 1: 创建 requirements.txt**

内容：
```
Flask>=2.0
pywin32>=305
```

- [ ] **Step 2: 创建目录结构**

运行：
```powershell
New-Item -ItemType Directory -Path "backend\modules" -Force
New-Item -ItemType Directory -Path "backend\utils" -Force
New-Item -ItemType Directory -Path "frontend\css" -Force
New-Item -ItemType Directory -Path "frontend\js" -Force
```

- [ ] **Step 3: 创建 `backend/modules/__init__.py`**

```python
# modules 包初始化
```

- [ ] **Step 4: 创建 `backend/utils/__init__.py`**

```python
# utils 包初始化
```

---

### Task 2: 创建 Flask 入口 app.py

**Files:**
- Create: `backend/app.py`

- [ ] **Step 1: 写入 app.py**

```python
from flask import Flask, jsonify, request, render_template_string, send_from_directory
import os

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

---

### Task 3: 填充 5 个模块（模拟数据）

**Files:**
- Modify: `backend/modules/system_info.py`
- Modify: `backend/modules/cleanup.py`
- Modify: `backend/modules/performance.py`
- Modify: `backend/modules/registry.py`
- Modify: `backend/modules/network.py`

每个模块统一返回格式 `{"status": "ok|error", "data": ..., "error": ..., "requires_admin": bool}`。

#### 3a: system_info.py

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

#### 3b: cleanup.py

```python
def do_cleanup_temp(payload):
    return {
        "cleaned_paths": ["C:\\Users\\Acer\\AppData\\Local\\Temp"],
        "freed_mb": 128,
        "message": "模拟清理完成",
        "requires_admin": False,
    }
```

#### 3c: performance.py

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

#### 3d: registry.py

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

#### 3e: network.py

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

---

### Task 4: 编写前端单页应用

**Files:**
- Modify: `frontend/index.html`
- Modify: `frontend/css/style.css`
- Modify: `frontend/js/main.js`

#### 4a: index.html

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Windows 系统优化工具</title>
    <link rel="stylesheet" href="/css/style.css">
</head>
<body>
    <div class="container">
        <nav class="sidebar">
            <div class="logo">WinOptimizer</div>
            <ul class="nav-menu">
                <li class="nav-item active" data-panel="dashboard">概览</li>
                <li class="nav-item" data-panel="system-info">系统信息</li>
                <li class="nav-item" data-panel="cleanup">系统清理</li>
                <li class="nav-item" data-panel="performance">性能调优</li>
                <li class="nav-item" data-panel="registry">注册表</li>
                <li class="nav-item" data-panel="network">网络优化</li>
            </ul>
        </nav>
        <main class="content">
            <!-- 概览 -->
            <section id="panel-dashboard" class="panel active">
                <h2>系统概览</h2>
                <div class="cards" id="dashboard-cards"></div>
            </section>

            <!-- 系统信息 -->
            <section id="panel-system-info" class="panel">
                <h2>系统信息</h2>
                <div id="system-info-content"></div>
            </section>

            <!-- 系统清理 -->
            <section id="panel-cleanup" class="panel">
                <h2>系统清理</h2>
                <button class="btn btn-primary" onclick="doCleanup()">清理临时文件</button>
                <div id="cleanup-result"></div>
            </section>

            <!-- 性能调优 -->
            <section id="panel-performance" class="panel">
                <h2>服务管理</h2>
                <div id="performance-content"></div>
            </section>

            <!-- 注册表 -->
            <section id="panel-registry" class="panel">
                <h2>注册表操作</h2>
                <div class="form-group">
                    <input type="text" id="reg-path" placeholder="注册表路径 (如 SOFTWARE\Microsoft)">
                    <input type="text" id="reg-key" placeholder="键名 (可选)">
                    <button class="btn btn-primary" onclick="readReg()">读取</button>
                </div>
                <div class="form-group">
                    <input type="text" id="reg-write-path" placeholder="注册表路径">
                    <input type="text" id="reg-write-key" placeholder="键名">
                    <input type="text" id="reg-write-value" placeholder="值">
                    <button class="btn btn-danger" onclick="writeReg()">写入</button>
                </div>
                <div id="registry-result"></div>
            </section>

            <!-- 网络优化 -->
            <section id="panel-network" class="panel">
                <h2>网络信息</h2>
                <div id="network-content"></div>
            </section>
        </main>
    </div>
    <script src="/js/main.js"></script>
</body>
</html>
```

#### 4b: style.css

```css
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: "Segoe UI", sans-serif; background: #1a1a2e; color: #e0e0e0; }
.container { display: flex; min-height: 100vh; }
.sidebar { width: 220px; background: #16213e; padding: 20px; }
.logo { font-size: 1.4em; font-weight: bold; margin-bottom: 30px; color: #e94560; }
.nav-menu { list-style: none; }
.nav-item { padding: 12px 16px; cursor: pointer; border-radius: 6px; margin-bottom: 4px; transition: background 0.2s; }
.nav-item:hover, .nav-item.active { background: #e94560; }
.content { flex: 1; padding: 30px; overflow-y: auto; }
.panel { display: none; }
.panel.active { display: block; }
h2 { margin-bottom: 20px; border-bottom: 1px solid #333; padding-bottom: 10px; }
.cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; }
.card { background: #16213e; padding: 20px; border-radius: 8px; border-left: 3px solid #e94560; }
.card-title { font-size: 0.9em; color: #888; margin-bottom: 8px; }
.card-value { font-size: 1.8em; font-weight: bold; }
.btn { padding: 8px 16px; border: none; border-radius: 4px; cursor: pointer; margin-right: 8px; margin-top: 10px; }
.btn-primary { background: #e94560; color: white; }
.btn-danger { background: #c0392b; color: white; }
.form-group { margin-bottom: 16px; }
.form-group input { padding: 8px; margin-right: 8px; border-radius: 4px; border: 1px solid #333; background: #16213e; color: white; }
.result { margin-top: 16px; padding: 12px; background: #16213e; border-radius: 6px; white-space: pre-wrap; }
table { width: 100%; border-collapse: collapse; margin-top: 16px; }
th, td { padding: 10px; text-align: left; border-bottom: 1px solid #333; }
th { background: #16213e; color: #e94560; }
```

#### 4c: main.js

```javascript
const API = "http://localhost:5000";

document.querySelectorAll(".nav-item").forEach(item => {
    item.addEventListener("click", () => {
        document.querySelectorAll(".nav-item").forEach(i => i.classList.remove("active"));
        document.querySelectorAll(".panel").forEach(p => p.classList.remove("active"));
        item.classList.add("active");
        document.getElementById("panel-" + item.dataset.panel).classList.add("active");
        loadPanel(item.dataset.panel);
    });
});

async function loadPanel(panel) {
    switch (panel) {
        case "dashboard":
            await loadDashboard();
            break;
        case "system-info":
            await loadSystemInfo();
            break;
        case "performance":
            await loadPerformance();
            break;
        case "network":
            await loadNetwork();
            break;
    }
}

async function api(path, options = {}) {
    const res = await fetch(`${API}${path}`, {
        headers: { "Content-Type": "application/json" },
        ...options,
    });
    return res.json();
}

async function loadDashboard() {
    const data = await api("/api/system-info");
    const container = document.getElementById("dashboard-cards");
    if (data.status !== "ok") { container.textContent = JSON.stringify(data); return; }
    const d = data.data;
    container.innerHTML = `
        <div class="card"><div class="card-title">CPU</div><div class="card-value">${d.cpu.usage}%</div><div>${d.cpu.name}</div></div>
        <div class="card"><div class="card-title">内存</div><div class="card-value">${d.memory.percent}%</div><div>${d.memory.used_gb} / ${d.memory.total_gb} GB</div></div>
        <div class="card"><div class="card-title">运行时间</div><div class="card-value" style="font-size:1.2em">${d.uptime}</div></div>
    `;
}

async function loadSystemInfo() {
    const data = await api("/api/system-info");
    const container = document.getElementById("system-info-content");
    if (data.status !== "ok") { container.textContent = JSON.stringify(data, null, 2); return; }
    const d = data.data;
    let html = `<h3>CPU</h3><p>${d.cpu.name} - ${d.cpu.cores} 核 - 使用率 ${d.cpu.usage}%</p>`;
    html += `<h3>内存</h3><p>已用 ${d.memory.used_gb} GB / ${d.memory.total_gb} GB (${d.memory.percent}%)</p>`;
    html += `<h3>磁盘</h3><table><tr><th>盘符</th><th>总容量</th><th>可用</th><th>使用率</th></tr>`;
    d.disk.forEach(disk => {
        html += `<tr><td>${disk.drive}</td><td>${disk.total_gb} GB</td><td>${disk.free_gb} GB</td><td>${disk.percent}%</td></tr>`;
    });
    html += "</table>";
    container.innerHTML = html;
}

async function doCleanup() {
    const result = await api("/api/cleanup/temp-files", { method: "POST", body: JSON.stringify({}) });
    const container = document.getElementById("cleanup-result");
    container.innerHTML = `<div class="result">${JSON.stringify(result, null, 2)}</div>`;
}

async function loadPerformance() {
    const data = await api("/api/performance/services");
    const container = document.getElementById("performance-content");
    if (data.status !== "ok") { container.textContent = JSON.stringify(data); return; }
    let html = `<table><tr><th>服务名</th><th>显示名称</th><th>状态</th><th>操作</th></tr>`;
    data.data.services.forEach(s => {
        html += `<tr><td>${s.name}</td><td>${s.display_name}</td><td>${s.status}</td>
            <td><button class="btn btn-primary" onclick="toggleService('${s.name}', 'start')">启动</button>
            <button class="btn btn-danger" onclick="toggleService('${s.name}', 'stop')">停止</button></td></tr>`;
    });
    html += "</table>";
    container.innerHTML = html;
}

async function toggleService(name, action) {
    const result = await api(`/api/performance/services/${name}`, {
        method: "POST",
        body: JSON.stringify({ action }),
    });
    alert(JSON.stringify(result, null, 2));
    loadPerformance();
}

async function readReg() {
    const path = document.getElementById("reg-path").value;
    const key = document.getElementById("reg-key").value;
    const data = await api(`/api/registry/read/${encodeURIComponent(path)}?key=${encodeURIComponent(key)}`);
    document.getElementById("registry-result").innerHTML = `<div class="result">${JSON.stringify(data, null, 2)}</div>`;
}

async function writeReg() {
    const path = document.getElementById("reg-write-path").value;
    const key = document.getElementById("reg-write-key").value;
    const value = document.getElementById("reg-write-value").value;
    if (!confirm("确定要写入注册表吗？")) return;
    const data = await api(`/api/registry/write/${encodeURIComponent(path)}`, {
        method: "POST",
        body: JSON.stringify({ key, value }),
    });
    document.getElementById("registry-result").innerHTML = `<div class="result">${JSON.stringify(data, null, 2)}</div>`;
}

async function loadNetwork() {
    const data = await api("/api/network/info");
    const container = document.getElementById("network-content");
    if (data.status !== "ok") { container.textContent = JSON.stringify(data); return; }
    let html = `<table><tr><th>名称</th><th>IP</th><th>DNS</th><th>速度</th></tr>`;
    data.data.adapters.forEach(a => {
        html += `<tr><td>${a.name}</td><td>${a.ip}</td><td>${a.dns.join(", ")}</td><td>${a.speed}</td></tr>`;
    });
    html += "</table>";
    container.innerHTML = html;
}

loadDashboard();
```

---

### Task 5: 验证可运行

- [ ] **Step 1: 安装依赖**

```bash
cd backend
pip install -r requirements.txt
```

- [ ] **Step 2: 启动服务**

```bash
cd backend
python app.py
```

- [ ] **Step 3: 浏览器访问 `http://localhost:5000`**

确认：
- 左侧导航可切换 6 个面板
- 概览显示系统信息卡片
- 系统信息面板显示完整信息
- 系统清理按钮触发模拟清理
- 服务列表渲染并可点击启停
- 注册表读写功能可用
- 网络信息表格渲染正常

---

### Task 6: Git 初始化与提交

- [ ] **Step 1: git add 并提交**

```bash
git add .
git commit -m "feat: 初始骨架，Flask 后端 + 前端，5 个模块模拟数据"
```
