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
