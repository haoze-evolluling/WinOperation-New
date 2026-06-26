async function loadSystemInfo() {
    const data = await api("/api/system-info");
    const container = document.getElementById("system-info-content");
    if (data.status !== "ok") { container.textContent = JSON.stringify(data, null, 2); return; }
    const d = data.data;
    let html = `<h3 class="glass">CPU</h3><p class="glass">${d.cpu.name} - ${d.cpu.cores} 核 - 使用率 ${d.cpu.usage}%</p>`;
    html += `<h3 class="glass">内存</h3><p class="glass">已用 ${d.memory.used_gb} GB / ${d.memory.total_gb} GB (${d.memory.percent}%)</p>`;
    html += `<h3>磁盘</h3><table><tr><th>盘符</th><th>总容量</th><th>可用</th><th>使用率</th></tr>`;
    d.disk.forEach(disk => {
        html += `<tr><td>${disk.drive}</td><td>${disk.total_gb} GB</td><td>${disk.free_gb} GB</td><td>${disk.percent}%</td></tr>`;
    });
    html += "</table>";
    container.innerHTML = html;
}
