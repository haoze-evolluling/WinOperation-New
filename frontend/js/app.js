const API = window.location.origin;

async function api(path, options = {}) {
    const res = await fetch(`${API}${path}`, {
        headers: { "Content-Type": "application/json" },
        ...options,
    });
    return res.json();
}

function initTheme() {
    const saved = localStorage.getItem("theme");
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    const theme = saved || (prefersDark ? "dark" : "light");
    document.documentElement.setAttribute("data-theme", theme);
}

document.getElementById("themeToggle").addEventListener("click", () => {
    const current = document.documentElement.getAttribute("data-theme");
    const next = current === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", next);
    localStorage.setItem("theme", next);
});

function animateProgress(thumb, from, to, duration) {
    const handle = {};
    const p = new Promise(resolve => {
        let cancelled = false;
        let rafId;
        const tick = (now) => {
            if (cancelled) { resolve(); return; }
            const elapsed = now - startTime;
            const t = Math.min(elapsed / duration, 1);
            const eased = 1 - Math.pow(1 - t, 3);
            thumb.style.width = (from + (to - from) * eased) + '%';
            if (t < 1) {
                rafId = requestAnimationFrame(tick);
            } else {
                resolve();
            }
        };
        const startTime = performance.now();
        rafId = requestAnimationFrame(tick);
        handle._cancel = () => {
            cancelled = true;
            if (rafId) cancelAnimationFrame(rafId);
        };
    });
    p._cancel = handle._cancel;
    return p;
}

async function activatePanel(panelName) {
    if (activatePanel._loading) return;
    activatePanel._loading = true;

    document.querySelectorAll(".nav-item").forEach(i => i.classList.remove("active"));
    document.querySelectorAll(".panel").forEach(p => p.classList.remove("active"));
    document.querySelector(`.nav-item[data-panel="${panelName}"]`)?.classList.add("active");

    const bar = document.getElementById("loading-bar");
    const thumb = bar.querySelector(".loading-bar-thumb");

    bar.classList.remove("done", "stall");
    bar.classList.add("active");
    thumb.style.transition = "none";
    thumb.style.width = "0%";

    const phase1 = animateProgress(thumb, 0, 85, 600);

    const dataPromise = loadPanel(panelName);

    const stallTimer = new Promise(resolve => {
        setTimeout(() => {
            if (bar.classList.contains("active")) {
                bar.classList.add("stall");
                phase1._cancel();
                thumb.style.transition = "none";
                thumb.style.width = "99%";
            }
            resolve();
        }, 800);
    });

    await Promise.race([dataPromise, stallTimer]);

    bar.classList.remove("stall");
    thumb.style.transition = "none";
    thumb.style.width = "99%";

    await new Promise(r => setTimeout(r, 80));

    thumb.style.transition = "width 0.15s ease";
    thumb.style.width = "100%";
    await new Promise(r => setTimeout(r, 150));

    bar.classList.add("done");
    await new Promise(r => setTimeout(r, 250));

    const panel = document.getElementById("panel-" + panelName);
    if (panel) panel.classList.add("active");

    thumb.style.transition = "none";
    thumb.style.width = "0%";
    bar.classList.remove("active", "done", "stall");

    activatePanel._loading = false;
}

async function restoreNavigation() {
    const saved = localStorage.getItem("activePanel");
    if (saved && document.querySelector(`.nav-item[data-panel="${saved}"]`)) {
        await activatePanel(saved);
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
        case "dashboard": await loadDashboard(); break;
        case "cleanup": await loadCleanup(); break;
        case "performance": await loadPerformance(); break;
        case "registry": await loadRegTree(); break;
    }
}

(async () => {
    initTheme();
    if (!(await restoreNavigation())) {
        activatePanel("dashboard");
    }
})();
