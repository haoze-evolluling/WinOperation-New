async function loadNetwork() {
    const data = await api("/api/network/info");
    const container = document.getElementById("network-content");
    if (data.status !== "ok") { container.textContent = JSON.stringify(data); return; }
    let html = '<div class="cards">';
    data.data.adapters.forEach(a => {
        html += `
            <div class="card glass span-2">
                <div class="card-title">${a.name}</div>
                <div class="card-value">${a.ip}</div>
                ${a.extra_ips.length ? `<div class="extra-ips">${a.extra_ips.join("、")}</div>` : ""}
            </div>
            <div class="card glass">
                <div class="card-title">MAC 地址</div>
                <div class="card-value" style="font-size:1.1em">${a.mac}</div>
            </div>
            <div class="card glass">
                <div class="card-title">子网掩码</div>
                <div class="card-value" style="font-size:1.1em">${a.subnet}</div>
            </div>
            <div class="card glass">
                <div class="card-title">默认网关</div>
                <div class="card-value" style="font-size:1.1em">${a.gateway}</div>
            </div>
            <div class="card glass">
                <div class="card-title">DNS 服务器</div>
                <div class="card-value" style="font-size:1.1em">${a.dns}</div>
            </div>
            <div class="card glass">
                <div class="card-title">DHCP</div>
                <div class="card-value" style="font-size:1.1em">${a.dhcp}</div>
            </div>
            <div class="card glass">
                <div class="card-title">连接状态</div>
                <div class="card-value" style="font-size:1.1em">${a.status}</div>
            </div>
            <div class="card glass">
                <div class="card-title">网卡速度</div>
                <div class="card-value" style="font-size:1.1em">${a.speed}</div>
            </div>
        `;
    });
    html += "</div>";
    container.innerHTML = html;
}
