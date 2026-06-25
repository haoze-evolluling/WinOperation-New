# Task 4: 编写前端单页应用

## Context
这是 Windows 系统优化工具项目的 Task 4。你需要创建前端单页应用，包含 index.html、style.css 和 main.js 三个文件。

## 需求

### 4a: `frontend/index.html`

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

### 4b: `frontend/css/style.css`

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

### 4c: `frontend/js/main.js`

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

## 验证
写入文件后，确认文件存在：
```powershell
Test-Path frontend/index.html; Test-Path frontend/css/style.css; Test-Path frontend/js/main.js
```

## 报告
完成后写入报告文件 `docs/superpowers/sdd/task-4-report.md`，包含：
- 3 个文件路径和行数
- 文件存在性验证结果
- 任何问题

## 注意
- 不要修改后端文件
- 只做这个任务
- 提交：`git add frontend/ && git commit -m "feat: Task 4 - 前端单页应用"`
