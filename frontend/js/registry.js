async function loadRegTree() {
    const basePath = document.getElementById("reg-tree-path").value || "HKCU";
    const data = await api(`/api/registry/tree/${encodeURIComponent(basePath)}?depth=2`);
    const container = document.getElementById("reg-tree");
    if (data.status !== "ok") { container.innerHTML = `<div class="result-card glass error"><strong>错误</strong> — 加载失败</div>`; return; }
    if (data.data.status === "error") { container.innerHTML = `<div class="result-card glass error"><strong>错误</strong> — ${data.data.error}</div>`; return; }
    const tree = data.data.tree;
    if (!tree || !tree.children) { container.innerHTML = `<div class="result-card warning"><strong>提示</strong> — 该路径下没有子项</div>`; return; }
    container.innerHTML = "";
    renderRegTree(tree.children, 0, basePath, container);
}

function renderRegTree(tree, depth, parentPath, container) {
    tree.forEach(node => {
        const wrapper = document.createElement("div");
        wrapper.className = "reg-tree-wrapper";
        const hasChildren = node.children && node.children.length > 0;
        const nodeDiv = document.createElement("div");
        nodeDiv.className = "reg-tree-node glass";
        nodeDiv.style.paddingLeft = `${depth * 20 + (hasChildren ? 4 : 4)}px`;
        nodeDiv.title = node.path || parentPath + "\\" + node.name;
        const toggle = document.createElement("span");
        toggle.className = "toggle";
        toggle.textContent = hasChildren ? "▼" : "•";
        nodeDiv.appendChild(toggle);
        const text = document.createElement("span");
        text.className = "reg-tree-name";
        text.textContent = node.name;
        nodeDiv.appendChild(text);
        if (hasChildren) {
            nodeDiv.addEventListener("click", (e) => {
                if (e.target === toggle || e.target === text) {
                    wrapper.classList.toggle("collapsed");
                    e.stopImmediatePropagation();
                }
            });
        }
        nodeDiv.addEventListener("click", () => {
            document.getElementById("reg-tree").querySelectorAll(".reg-tree-node").forEach(n => n.classList.remove("active"));
            nodeDiv.classList.add("active");
            loadRegValues(node.path || parentPath + "\\" + node.name);
        });
        nodeDiv.addEventListener("contextmenu", (e) => {
            e.preventDefault();
            if (confirm(`删除注册表项 "${node.path || parentPath + "\\" + node.name}" 及其所有子项？`)) {
                deleteRegKey(node.path || parentPath + "\\" + node.name);
            }
        });
        wrapper.appendChild(nodeDiv);
        if (hasChildren) {
            const childContainer = document.createElement("div");
            childContainer.className = "children";
            renderRegTree(node.children, depth + 1, node.path || parentPath + "\\" + node.name, childContainer);
            wrapper.appendChild(childContainer);
        }
        container.appendChild(wrapper);
    });
}

async function loadRegValues(path) {
    window._currentRegPath = path;
    document.getElementById("reg-path-display").textContent = path;
    const data = await api(`/api/registry/list/${encodeURIComponent(path)}`);
    const tbody = document.getElementById("reg-values-body");
    if (data.status !== "ok") { tbody.innerHTML = `<tr><td colspan="4">加载失败</td></tr>`; return; }
    if (data.data.status === "error") { tbody.innerHTML = `<tr><td colspan="4">${data.data.error}</td></tr>`; return; }
    tbody.innerHTML = "";
    if ((data.data.values || []).length === 0) {
        tbody.innerHTML = `<tr><td colspan="4" class="empty-hint">暂无值</td></tr>`;
        return;
    }
    (data.data.values || []).forEach(item => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td>${item.name}</td>
            <td><span class="reg-type-badge">${item.type}</span></td>
            <td class="reg-value-data">${item.data}</td>
            <td class="reg-actions">
                <button class="btn-copy" onclick="copyRegValue('${item.data.replace(/'/g, "\\'")}')" title="复制">复制</button>
                <button class="btn-del" onclick="deleteRegValue('${item.name.replace(/'/g, "\\'")}')" title="删除">删除</button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

function copyRegValue(text) {
    navigator.clipboard.writeText(text).then(() => {
        showToast("已复制到剪贴板");
    });
}

async function deleteRegValue(name) {
    if (!confirm(`删除值 "${name}"？`)) return;
    const path = window._currentRegPath;
    const result = await api(`/api/registry/delete-value/${encodeURIComponent(path)}`, {
        method: "POST",
        body: JSON.stringify({ key: name }),
    });
    if (result.status === "ok") {
        showToast("删除成功");
        loadRegValues(path);
    } else {
        showToast(result.error || "删除失败", "error");
    }
}

async function deleteRegKey(path) {
    const result = await api(`/api/registry/delete-key/${encodeURIComponent(path)}`, {
        method: "POST",
        body: JSON.stringify({}),
    });
    if (result.status === "ok") {
        showToast("删除成功");
        window._currentRegPath = "";
        document.getElementById("reg-path-display").textContent = path.split("\\")[0];
        loadRegTree();
    } else {
        showToast(result.error || "删除失败", "error");
    }
}

function showToast(message, type) {
    let toast = document.getElementById("reg-toast");
    if (!toast) {
        toast = document.createElement("div");
        toast.id = "reg-toast";
        document.body.appendChild(toast);
    }
    toast.textContent = message;
    toast.className = "reg-toast " + (type === "error" ? "error" : "success");
    toast.style.display = "block";
    setTimeout(() => { toast.style.display = "none"; }, 2200);
}

function refreshRegValues() {
    if (window._currentRegPath) loadRegValues(window._currentRegPath);
}

function showRegWriteForm() {
    document.getElementById("reg-write-form").style.display = "flex";
}

function hideRegWriteForm() {
    document.getElementById("reg-write-form").style.display = "none";
}

async function writeReg() {
    const path = document.getElementById("reg-tree-path").value || "HKCU";
    const key = document.getElementById("reg-write-key").value;
    const type = document.getElementById("reg-write-type").value;
    const value = document.getElementById("reg-write-value").value;
    if (!key) { alert("请输入键名"); return; }
    const result = await api(`/api/registry/write/${encodeURIComponent(path)}`, {
        method: "POST",
        body: JSON.stringify({ key, value, type }),
    });
    const container = document.getElementById("registry-result");
    if (result.status !== "ok") {
        container.innerHTML = `<div class="result-card glass error"><strong>错误</strong> — ${result.error || '写入失败'}</div>`;
        hideRegWriteForm();
        return;
    }
    container.innerHTML = `<div class="result-card glass success">写入成功</div>`;
    hideRegWriteForm();
    refreshRegValues();
}

async function exportCurrentReg() {
    const path = window._currentRegPath || document.getElementById("reg-tree-path").value || "HKCU";
    const result = await api(`/api/registry/export`, {
        method: "POST",
        body: JSON.stringify({ path }),
    });
    if (result.status === "ok" && result.data && result.data.content) {
        const blob = new Blob([result.data.content], { type: "application/octet-stream" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "export.reg";
        a.click();
        URL.revokeObjectURL(url);
    } else {
        alert("导出失败");
    }
}

function importRegFile() {
    document.getElementById("reg-import-file").click();
}

async function doImportReg(event) {
    const file = event.target.files[0];
    if (!file) return;
    const text = await file.text();
    const res = await fetch(`${API}/api/registry/import`, {
        method: "POST",
        headers: { "Content-Type": "text/plain" },
        body: text,
    });
    const result = await res.json();
    const container = document.getElementById("registry-result");
    if (result.status === "ok") {
        container.innerHTML = `<div class="result-card glass success">导入成功</div>`;
    } else {
        container.innerHTML = `<div class="result-card glass error">导入失败</div>`;
    }
    event.target.value = "";
}
