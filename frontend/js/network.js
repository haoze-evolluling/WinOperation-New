async function loadNetwork() {
    const data = await api("/api/network/info");
    const container = document.getElementById("network-content");
    if (data.status !== "ok") { container.textContent = JSON.stringify(data); return; }
    let html = `<table><tr><th>名称</th><th>IP</th></tr>`;
    data.data.adapters.forEach(a => {
        html += `<tr><td>${a.name}</td><td>${a.ip}</td></tr>`;
    });
    html += "</table>";
    container.innerHTML = html;
}
