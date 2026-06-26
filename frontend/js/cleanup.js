async function doScanCleanup() {
    const result = await api("/api/cleanup/scan", { method: "POST", body: JSON.stringify({}) });
    const container = document.getElementById("cleanup-result");
    if (result.status !== "ok") { container.innerHTML = `<div class="result-card glass error"><strong>错误</strong> — ${result.error || '操作失败'}</div>`; return; }
    renderCleanupCategories(result.data);
}

function renderCleanupCategories(categories) {
    const container = document.getElementById("cleanup-categories");
    container.innerHTML = "";
    categories.forEach(cat => {
        const card = document.createElement("div");
        card.className = "cleanup-category";
        card.innerHTML = `
            <div class="cleanup-category-header">
                <input type="checkbox" id="cat-${cat.id}" value="${cat.id}" onchange="updateCleanupBtn()">
                <label for="cat-${cat.id}" class="cleanup-category-name">${cat.name}</label>
            </div>
            <div class="cleanup-category-desc">${cat.description}</div>
            <div class="cleanup-category-meta">${cat.file_count} 个文件 · ${cat.size_mb} MB</div>
        `;
        container.appendChild(card);
    });
}

function updateCleanupBtn() {
    const checked = document.querySelectorAll("#cleanup-categories input[type='checkbox']:checked");
    document.getElementById("cleanup-execute-btn").disabled = checked.length === 0;
}

async function doCleanupSelected() {
    const checked = document.querySelectorAll("#cleanup-categories input[type='checkbox']:checked");
    const ids = Array.from(checked).map(cb => cb.value);
    if (ids.length === 0) return;
    const result = await api("/api/cleanup/execute", { method: "POST", body: JSON.stringify({ categories: ids }) });
    const container = document.getElementById("cleanup-result");
    if (result.status !== "ok") { container.innerHTML = `<div class="result-card glass error"><strong>错误</strong> — ${result.error || '操作失败'}</div>`; return; }
    renderCleanupResult(result.data);
}

function renderCleanupResult(data) {
    const container = document.getElementById("cleanup-result");
    let html = `<div class="result-card glass success"><strong>清理完成</strong> — 共释放 ${data.total_freed_mb} MB</div>`;
    if (data.cleaned && data.cleaned.length > 0) {
        html += `<div class="result-card glass"><strong>已清理项目 (${data.cleaned.length})</strong>
            <ul class="result-list">
                ${data.cleaned.map(c => `<li class="result-list-item">${c.path} (${c.size_mb} MB)</li>`).join("")}
            </ul></div>`;
    }
    if (data.failed && data.failed.length > 0) {
        html += `<div class="result-card glass error"><strong>失败项目 (${data.failed.length})</strong>
            <ul class="result-list">
                ${data.failed.map(f => `<li class="result-list-item">${f.path}: ${f.error}</li>`).join("")}
            </ul></div>`;
    }
    container.innerHTML = html;
}
