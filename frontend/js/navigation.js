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
