const HEALTH_LEVELS = [
    { threshold: 50, label: "正常", color: "#0F7B0F", bg: "rgba(15,123,15,0.08)" },
    { threshold: 80, label: "较高", color: "#CA5010", bg: "rgba(202,80,16,0.08)" },
    { threshold: Infinity, label: "高负载", color: "#D13438", bg: "rgba(209,52,56,0.08)" },
];

function getHealthLevel(pct) {
    return HEALTH_LEVELS.find(l => pct < l.threshold) || HEALTH_LEVELS[HEALTH_LEVELS.length - 1];
}

function getOverallStatus(cpu, mem, disk) {
    const max = Math.max(cpu, mem, disk);
    if (max < 50) return { label: "系统运行正常", color: "#0F7B0F", bg: "rgba(15,123,15,0.06)" };
    if (max < 80) return { label: "部分资源使用率较高", color: "#CA5010", bg: "rgba(202,80,16,0.06)" };
    return { label: "系统负载较高，建议关注", color: "#D13438", bg: "rgba(209,52,56,0.06)" };
}

async function loadDashboard() {
    const container = document.getElementById("dashboard-content");
    const sysContainer = document.getElementById("system-info-content");
    container.innerHTML = '<p style="color:var(--text-tertiary)">加载中...</p>';
    sysContainer.innerHTML = '<p style="color:var(--text-tertiary)">加载中...</p>';
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
        const adapters = netData.data?.adapters || [];

        const diskTotal = d.disk.reduce((s, x) => s + x.total_gb, 0);
        const diskFree = d.disk.reduce((s, x) => s + x.free_gb, 0);
        const diskUsedPct = diskTotal > 0 ? ((diskTotal - diskFree) / diskTotal * 100) : 0;

        const cpuPct = d.cpu.usage;
        const memPct = d.memory.percent;
        const cpuLevel = getHealthLevel(cpuPct);
        const memLevel = getHealthLevel(memPct);
        const diskLevel = getHealthLevel(diskUsedPct);
        const overall = getOverallStatus(cpuPct, memPct, diskUsedPct);

        let html = "";

        // Health summary banner
        html += `<div class="health-banner" style="background:${overall.bg};border:1px solid ${overall.color}22;color:${overall.color}">`;
        html += `<div class="health-banner-label">${overall.label}</div>`;
        html += `<div class="health-banner-detail"><span>CPU ${cpuLevel.label}</span><span class="banner-sep">·</span><span>内存 ${memLevel.label}</span><span class="banner-sep">·</span><span>磁盘 ${diskLevel.label}</span></div>`;
        html += "</div>";

        // Health metrics
        html += '<div class="dash-section-title">资源使用率</div>';
        html += '<div class="health-metrics">';

        html += renderHealthCard("cpu", "CPU", `${cpuPct}%`, d.cpu.name, cpuLevel, [
            { label: "核心", value: `${d.cpu.cores} 核` },
        ]);

        html += renderHealthCard("memory", "内存", `${memPct}%`, `${d.memory.used_gb} / ${d.memory.total_gb} GB 已用`, memLevel, [
            { label: "总量", value: `${d.memory.total_gb} GB` },
        ]);

        html += renderHealthCard("disk", "磁盘", `${diskUsedPct.toFixed(1)}%`, `${diskTotal.toFixed(1)} GB 总计`, diskLevel, [
            { label: "可用", value: `${diskFree.toFixed(1)} GB` },
        ]);

        html += "</div>";

        // Network adapters
        if (adapters.length > 0) {
            html += '<div class="dash-section-title">网络适配器</div>';
            html += '<div class="network-section">';
            adapters.forEach(a => {
                const connClass = a.status === "已连接" ? "connected" : "disconnected";
                const statusLabel = a.status === "已连接" ? "已连接" : "未连接";
                html += `<div class="adapter-card ${connClass}">`;
                html += `<div class="adapter-header">
                    <div class="adapter-name">${a.name}</div>
                    <span class="status-badge status-${connClass}"><span class="status-dot"></span>${statusLabel}</span>
                </div>`;
                html += `<div class="adapter-primary-ip">${a.ip || "无 IP"}`;
                if (a.ip) {
                    html += `<span class="ip-tag ${a.ip.includes(":") ? "ipv6" : ""}">${a.ip.includes(":") ? "IPv6" : "IPv4"}</span>`;
                }
                html += "</div>";
                if (a.extra_ips.length) {
                    html += '<div class="extra-ips">';
                    a.extra_ips.forEach(ip => {
                        const isV6 = ip.includes(":");
                        html += `<div class="extra-ip-row"><span class="ip-tag ${isV6 ? "ipv6" : ""}">${isV6 ? "IPv6" : "IPv4"}</span>${ip}</div>`;
                    });
                    html += "</div>";
                }
                html += '<div class="adapter-grid">';
                if (a.mac && a.mac !== "—") html += adapterRow("MAC 地址", a.mac);
                if (a.subnet && a.subnet !== "—") html += adapterRow("子网掩码", a.subnet);
                if (a.gateway && a.gateway !== "—") html += adapterRow("默认网关", a.gateway);
                if (a.dns && a.dns !== "—") html += adapterRow("DNS 服务器", a.dns);
                html += adapterRow("DHCP", a.dhcp ? "已启用" : "禁用");
                if (a.speed && a.speed !== "—") html += adapterRow("网卡速度", a.speed);
                html += "</div>";
                html += "</div>";
            });
            html += "</div>";
        }

        // Per-disk breakdown (per-drive granularity, not duplicate of aggregate card)
        let sysHtml = '<div class="disk-detail-section"><div class="dash-section-title">磁盘详情</div><div class="resource-card"><table><thead><tr><th>盘符</th><th>总容量</th><th>可用</th><th>使用率</th></tr></thead><tbody>';
        d.disk.forEach(disk => {
            sysHtml += '<tr><td>' + disk.drive + '</td><td>' + disk.total_gb + ' GB</td><td>' + disk.free_gb + ' GB</td><td>' + disk.percent + '%</td></tr>';
        });
        sysHtml += '</tbody></table></div></div>';
        sysContainer.innerHTML = sysHtml;

        container.innerHTML = html;

        // Animate progress bars (double rAF ensures browser paints 0% first)
        requestAnimationFrame(() => {
            requestAnimationFrame(() => {
                container.querySelectorAll(".health-bar-fill").forEach(bar => {
                    bar.style.width = bar.dataset.width;
                });
            });
        });
    } catch (e) {
        container.textContent = "加载失败: " + e.message;
    }
}

function renderHealthCard(type, name, value, sub, level, details) {
    let bar = "";
    let detailsHtml = "";
    details.forEach(d => {
        if (!bar) {
            bar = `<div class="health-bar-track"><div class="health-bar-fill" style="width:0%" data-width="${Math.min(parseFloat(value) || 0, 100)}%"></div></div>`;
        }
        detailsHtml += `<div class="health-detail"><span class="health-detail-label">${d.label}</span><span class="health-detail-value">${d.value}</span></div>`;
    });

    return `<div class="health-card" data-type="${type}" style="--level-color:${level.color};--level-bg:${level.bg}">
        <div class="health-header">
            <div class="health-name">${name}</div>
            <div class="health-value" style="color:${level.color}">${value}</div>
        </div>
        <div class="health-sub">${sub}</div>
        ${bar}
        <div class="health-details">${detailsHtml}</div>
        <div class="health-level">${level.label}</div>
    </div>`;
}

function adapterRow(label, value) {
    return `<div class="adapter-detail"><span class="adapter-detail-label">${label}</span><span class="adapter-detail-value">${value}</span></div>`;
}
