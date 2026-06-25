const API = window.location.origin;

function initTheme() {
    const saved = localStorage.getItem("theme");
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    const theme = saved || (prefersDark ? "dark" : "light");
    document.documentElement.setAttribute("data-theme", theme);
}

document.getElementById("themeToggle").addEventListener("click", () => {
    const current = document.documentElement.getAttribute("data-theme");
    const next = current === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", next);
    localStorage.setItem("theme", next);
});

initTheme();

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
        case "registry":
            loadRegTree();
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

async function doScanCleanup() {
    const result = await api("/api/cleanup/scan", { method: "POST", body: JSON.stringify({}) });
    const container = document.getElementById("cleanup-result");
    if (result.status !== "ok") { container.innerHTML = `<div class="result-card error"><strong>错误</strong> — ${result.error || '操作失败'}</div>`; return; }
    renderCleanupCategories(result.data);
}

function renderCleanupCategories(categories) {
    const container = document.getElementById("cleanup-categories");
    container.innerHTML = "";
    categories.forEach(cat => {
        const card = document.createElement("div");
        card.className = "cleanup-category";
        card.innerHTML = `
            <div class="cleanup-category-header">
                <input type="checkbox" id="cat-${cat.id}" value="${cat.id}" onchange="updateCleanupBtn()">
                <label for="cat-${cat.id}" class="cleanup-category-name">${cat.name}</label>
            </div>
            <div class="cleanup-category-desc">${cat.description}</div>
            <div class="cleanup-category-meta">${cat.file_count} 个文件 · ${cat.size_mb} MB</div>
        `;
        container.appendChild(card);
    });
}

function updateCleanupBtn() {
    const checked = document.querySelectorAll("#cleanup-categories input[type='checkbox']:checked");
    document.getElementById("cleanup-execute-btn").disabled = checked.length === 0;
}

async function doCleanupSelected() {
    const checked = document.querySelectorAll("#cleanup-categories input[type='checkbox']:checked");
    const ids = Array.from(checked).map(cb => cb.value);
    if (ids.length === 0) return;
    const result = await api("/api/cleanup/execute", { method: "POST", body: JSON.stringify({ categories: ids }) });
    const container = document.getElementById("cleanup-result");
    if (result.status !== "ok") { container.innerHTML = `<div class="result-card error"><strong>错误</strong> — ${result.error || '操作失败'}</div>`; return; }
    renderCleanupResult(result.data);
}

function renderCleanupResult(data) {
    const container = document.getElementById("cleanup-result");
    let html = `<div class="result-card success"><strong>清理完成</strong> — 共释放 ${data.total_freed_mb} MB</div>`;
    if (data.cleaned && data.cleaned.length > 0) {
        html += `<div class="result-card"><strong>已清理项目 (${data.cleaned.length})</strong>
            <ul class="result-list">
                ${data.cleaned.map(c => `<li class="result-list-item">${c.path} (${c.size_mb} MB)</li>`).join("")}
            </ul></div>`;
    }
    if (data.failed && data.failed.length > 0) {
        html += `<div class="result-card error"><strong>失败项目 (${data.failed.length})</strong>
            <ul class="result-list">
                ${data.failed.map(f => `<li class="result-list-item">${f.path}: ${f.error}</li>`).join("")}
            </ul></div>`;
    }
    container.innerHTML = html;
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

async function loadRegTree() {
    const basePath = document.getElementById("reg-tree-path").value || "HKCU";
    const data = await api(`/api/registry/tree/${encodeURIComponent(basePath)}?depth=2`);
    const container = document.getElementById("reg-tree");
    if (data.status !== "ok") { container.innerHTML = `<div class="result-card error"><strong>错误</strong> — 加载失败</div>`; return; }
    if (data.data.status === "error") { container.innerHTML = `<div class="result-card error"><strong>错误</strong> — ${data.data.error}</div>`; return; }
    const tree = data.data.tree;
    if (!tree || !tree.children) { container.innerHTML = `<div class="result-card warning"><strong>提示</strong> — 该路径下没有子项</div>`; return; }
    container.innerHTML = "";
    renderRegTree(tree.children, 0, basePath, container);
}

function renderRegTree(tree, depth, parentPath, container) {
    tree.forEach(node => {
        const div = document.createElement("div");
        div.className = "reg-tree-node";
        div.style.paddingLeft = `${depth * 16 + 8}px`;
        div.textContent = node.name;
        div.title = node.path || parentPath + "\\" + node.name;
        div.addEventListener("click", () => {
            container.querySelectorAll(".reg-tree-node").forEach(n => n.classList.remove("active"));
            div.classList.add("active");
            loadRegValues(node.path || parentPath + "\\" + node.name);
        });
        container.appendChild(div);
        if (node.children && node.children.length > 0) {
            renderRegTree(node.children, depth + 1, node.path || parentPath + "\\" + node.name, container);
        }
    });
}

async function loadRegValues(path) {
    window._currentRegPath = path;
    document.getElementById("reg-path-display").textContent = path;
    const data = await api(`/api/registry/list/${encodeURIComponent(path)}`);
    const tbody = document.getElementById("reg-values-body");
    if (data.status !== "ok") { tbody.innerHTML = `<tr><td colspan="4">加载失败</td></tr>`; return; }
    if (data.data.status === "error") { tbody.innerHTML = `<tr><td colspan="4">${data.data.error}</td></tr>`; return; }
    tbody.innerHTML = "";
    (data.data.values || []).forEach(item => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td>${item.name}</td>
            <td><span class="reg-type-badge">${item.type}</span></td>
            <td>${item.data}</td>
            <td></td>
        `;
        tbody.appendChild(tr);
    });
}

async function refreshRegValues() {
    if (window._currentRegPath) await loadRegValues(window._currentRegPath);
}

function showRegWriteForm() {
    document.getElementById("reg-write-form").style.display = "flex";
}

function hideRegWriteForm() {
    document.getElementById("reg-write-form").style.display = "none";
}

async function writeReg() {
    const path = document.getElementById("reg-tree-path").value || "HKCU";
    const key = document.getElementById("reg-write-key").value;
    const type = document.getElementById("reg-write-type").value;
    const value = document.getElementById("reg-write-value").value;
    if (!key) { alert("请输入键名"); return; }
    const result = await api(`/api/registry/write/${encodeURIComponent(path)}`, {
        method: "POST",
        body: JSON.stringify({ key, value, type }),
    });
    const container = document.getElementById("registry-result");
    if (result.status !== "ok") {
        container.innerHTML = `<div class="result-card error"><strong>错误</strong> — ${result.error || '写入失败'}</div>`;
        hideRegWriteForm();
        return;
    }
    container.innerHTML = `<div class="result-card success">写入成功</div>`;
    hideRegWriteForm();
    refreshRegValues();
}

async function exportCurrentReg() {
    const path = window._currentRegPath || document.getElementById("reg-tree-path").value || "HKCU";
    const result = await api(`/api/registry/export`, {
        method: "POST",
        body: JSON.stringify({ path }),
    });
    if (result.status === "ok" && result.data && result.data.content) {
        const blob = new Blob([result.data.content], { type: "application/octet-stream" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "export.reg";
        a.click();
        URL.revokeObjectURL(url);
    } else {
        alert("导出失败");
    }
}

function importRegFile() {
    document.getElementById("reg-import-file").click();
}

async function doImportReg(event) {
    const file = event.target.files[0];
    if (!file) return;
    const text = await file.text();
    const res = await fetch(`${API}/api/registry/import`, {
        method: "POST",
        headers: { "Content-Type": "text/plain" },
        body: text,
    });
    const result = await res.json();
    const container = document.getElementById("registry-result");
    if (result.status === "ok") {
        container.innerHTML = `<div class="result-card success">导入成功</div>`;
    } else {
        container.innerHTML = `<div class="result-card error">导入失败</div>`;
    }
    event.target.value = "";
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
