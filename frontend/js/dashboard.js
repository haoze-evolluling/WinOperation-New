async function loadDashboard() {
    const container = document.getElementById("dashboard-cards");
    try {
        const [sysData, svcData, netData] = await Promise.all([
            api("/api/system-info"),
            api("/api/performance/services"),
            api("/api/network/info"),
        ]);
        if (sysData.status !== "ok") {
            container.textContent = JSON.stringify(sysData);
            return;
        }
        const d = sysData.data;
        const running = (svcData.data?.services || []).filter(s => s.status === "running").length;
        const adapters = (netData.data?.adapters || []).length;

        const diskTotal = d.disk.reduce((s, x) => s + x.total_gb, 0);
        const diskFree = d.disk.reduce((s, x) => s + x.free_gb, 0);
        const diskUsedPct = diskTotal > 0 ? ((diskTotal - diskFree) / diskTotal * 100).toFixed(1) : 0;

        const cards = [
            { title: "CPU 使用率", value: `${d.cpu.usage}%`, sub: d.cpu.name },
            { title: "CPU 核心数", value: d.cpu.cores, sub: "核" },
            { title: "CPU 型号", value: d.cpu.name },
            { title: "内存使用率", value: `${d.memory.percent}%`, sub: `${d.memory.used_gb} / ${d.memory.total_gb} GB` },
            { title: "内存已用", value: `${d.memory.used_gb} GB`, sub: `总量 ${d.memory.total_gb} GB` },
            { title: "内存总量", value: `${d.memory.total_gb} GB` },
            { title: "磁盘总容量", value: `${diskTotal.toFixed(1)} GB` },
            { title: "磁盘可用", value: `${diskFree.toFixed(1)} GB` },
            { title: "磁盘使用率", value: `${diskUsedPct}%` },
            { title: "运行中服务", value: running, sub: `服务数量` },
            { title: "网络适配器", value: adapters, sub: "已启用" },
            { title: "运行时间", value: d.uptime },
        ];

        container.innerHTML = cards.map(c => {
            const truncated = c.value.length > 18
                ? `<div class="card-value-truncated" title="${c.value}">${c.value.slice(0, 16)}…</div>`
                : `<div class="card-value">${c.value}</div>`;
            const sub = c.sub ? `<div class="card-sub">${c.sub}</div>` : "";
            return `<div class="card glass"><div class="card-title">${c.title}</div>${truncated}${sub}</div>`;
        }).join("");
    } catch (e) {
        container.textContent = "加载失败: " + e.message;
    }
}
