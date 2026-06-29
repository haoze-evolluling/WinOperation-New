let _allServices = [];

async function loadPerformance() {
    const data = await api("/api/performance/services");
    const container = document.getElementById("performance-content");
    if (data.status !== "ok") { container.textContent = JSON.stringify(data); return; }

    _allServices = data.data.services || [];

    container.innerHTML = `
        <div class="service-toolbar">
            <input type="text" class="service-search" id="service-search" placeholder="搜索服务名称..." oninput="filterServices()">
            <span class="service-count" id="service-count">${_allServices.length} 个服务</span>
        </div>
        <div class="service-table-wrap">
            <table>
                <thead>
                    <tr>
                        <th></th>
                        <th>服务名称</th>
                        <th>显示名称</th>
                        <th>状态</th>
                        <th>操作</th>
                    </tr>
                </thead>
                <tbody id="service-tbody"></tbody>
            </table>
        </div>
    `;

    filterServices();
}

function filterServices() {
    const keyword = (document.getElementById("service-search")?.value || "").toLowerCase();
    const filtered = keyword
        ? _allServices.filter(s => s.name.toLowerCase().includes(keyword) || s.display_name.toLowerCase().includes(keyword))
        : _allServices;

    const countEl = document.getElementById("service-count");
    if (countEl) countEl.textContent = keyword
        ? `${filtered.length} / ${_allServices.length} 个服务`
        : `${_allServices.length} 个服务`;

    const tbody = document.getElementById("service-tbody");
    if (!tbody) return;
    tbody.innerHTML = "";

    if (filtered.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5" class="empty-hint">没有匹配的服务</td></tr>`;
        return;
    }

    filtered.forEach(s => {
        const dotClass = s.status === "running" ? "running" : s.status === "stopped" ? "stopped" : "other";
        const action = s.status === "running"
            ? `<button class="btn btn-danger" onclick="toggleService('${s.name.replace(/'/g, "\\'")}', 'stop')">停止</button>`
            : `<button class="btn btn-primary" onclick="toggleService('${s.name.replace(/'/g, "\\'")}', 'start')">启动</button>`;
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td><span class="service-status-dot ${dotClass}" title="${s.status}"></span></td>
            <td>${s.name}</td>
            <td>${s.display_name}</td>
            <td>${s.status}</td>
            <td class="service-row-actions">${action}</td>
        `;
        tbody.appendChild(tr);
    });
}

async function toggleService(name, action) {
    const result = await api(`/api/performance/services/${name}`, {
        method: "POST",
        body: JSON.stringify({ action }),
    });
    const resultContainer = document.getElementById("performance-result");
    if (result.status === "ok") {
        resultContainer.innerHTML = `<div class="result-card glass success"><strong>${result.data.message}</strong></div>`;
    } else {
        resultContainer.innerHTML = `<div class="result-card glass error"><strong>错误</strong> — ${result.error || '操作失败'}</div>`;
    }
    loadPerformance();
}
