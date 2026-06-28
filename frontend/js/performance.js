async function loadPerformance() {
    const data = await api("/api/performance/services");
    const container = document.getElementById("performance-content");
    if (data.status !== "ok") { container.textContent = JSON.stringify(data); return; }
    container.innerHTML = '<div class="service-cards"></div>';
    const grid = container.querySelector(".service-cards");
    data.data.services.forEach(s => {
        const card = document.createElement("div");
        card.className = "service-card glass";
        card.innerHTML = `
            <div class="service-card-header">
                <span class="service-card-name" title="${s.name}">${s.name}</span>
                <span class="service-card-status">${s.status}</span>
            </div>
            <div class="service-card-meta">${s.display_name}</div>
            <div class="service-card-actions">
                <button class="btn btn-primary" onclick="toggleService('${s.name}', 'start')">启动</button>
                <button class="btn btn-danger" onclick="toggleService('${s.name}', 'stop')">停止</button>
            </div>
        `;
        grid.appendChild(card);
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
