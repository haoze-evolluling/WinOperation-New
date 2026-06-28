async function activatePanel(panelName) {
    document.querySelectorAll(".nav-item").forEach(i => i.classList.remove("active"));
    document.querySelectorAll(".panel").forEach(p => p.classList.remove("active"));
    document.querySelector(`.nav-item[data-panel="${panelName}"]`)?.classList.add("active");
    const panel = document.getElementById("panel-" + panelName);
    if (panel) panel.classList.add("active");
    await loadPanel(panelName);
    if (window.animationsEngine) {
        window.animationsEngine.animateEntrance(panel);
    }
}

function restoreNavigation() {
    const saved = localStorage.getItem("activePanel");
    if (saved && document.querySelector(`.nav-item[data-panel="${saved}"]`)) {
        activatePanel(saved);
        return true;
    }
    return false;
}

document.querySelectorAll(".nav-item").forEach(item => {
    item.addEventListener("click", () => {
        activatePanel(item.dataset.panel);
        localStorage.setItem("activePanel", item.dataset.panel);
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
