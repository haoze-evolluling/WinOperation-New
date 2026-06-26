async function loadDashboard() {
    const data = await api("/api/system-info");
    const container = document.getElementById("dashboard-cards");
    if (data.status !== "ok") { container.textContent = JSON.stringify(data); return; }
    const d = data.data;
    container.innerHTML = `
        <div class="card glass"><div class="card-title">CPU</div><div class="card-value">${d.cpu.usage}%</div><div>${d.cpu.name}</div></div>
        <div class="card glass"><div class="card-title">内存</div><div class="card-value">${d.memory.percent}%</div><div>${d.memory.used_gb} / ${d.memory.total_gb} GB</div></div>
        <div class="card glass"><div class="card-title">运行时间</div><div class="card-value" style="font-size:1.2em">${d.uptime}</div></div>
    `;
}
