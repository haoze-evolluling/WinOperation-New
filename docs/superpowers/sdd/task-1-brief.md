# Task 1 Brief: app.py 添加管理员权限检测

**Goal:** 在 app.py 启动时检测管理员权限，非管理员直接报错退出，不允许降级运行。

**Files:**
- Modify: `backend/app.py`

**Implementation:**

在 `backend/app.py` 文件开头添加管理员权限检测代码。具体修改：
1. 在顶部添加 `import ctypes` 和 `import sys`
2. 添加 `require_admin()` 函数，使用 `ctypes.windll.shell32.IsUserAnAdmin()` 检测
3. 在 `app = Flask(__name__)` 之前调用 `require_admin()`
4. 非管理员时输出错误信息到 stderr 并 `sys.exit(1)`

完整代码结构：

```python
from flask import Flask, jsonify, request, send_from_directory
import ctypes
import os
import sys

def require_admin():
    if not ctypes.windll.shell32.IsUserAnAdmin():
        print("错误: 此应用需要管理员权限运行，请右键以管理员身份启动。", file=sys.stderr)
        sys.exit(1)

require_admin()

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")


@app.route("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/<path:path>")
def static_files(path):
    return send_from_directory(FRONTEND_DIR, path)


def ok(data=None):
    return jsonify({"status": "ok", "data": data})


def error(message):
    return jsonify({"status": "error", "error": message})


# ---- 系统信息 ----
@app.route("/api/system-info", methods=["GET"])
def system_info():
    from modules.system_info import get_system_info
    return ok(get_system_info())


# ---- 系统清理 ----
@app.route("/api/cleanup/temp-files", methods=["POST"])
def cleanup_temp_files():
    from modules.cleanup import do_cleanup_temp
    result = do_cleanup_temp(request.json or {})
    return ok(result)


# ---- 性能调优 ----
@app.route("/api/performance/services", methods=["GET"])
def get_services():
    from modules.performance import get_services
    return ok(get_services())


@app.route("/api/performance/services/<name>", methods=["POST"])
def toggle_service(name):
    from modules.performance import toggle_service
    action = (request.json or {}).get("action", "start")
    result = toggle_service(name, action)
    return ok(result)


# ---- 注册表 ----
@app.route("/api/registry/read/<path:reg_path>", methods=["GET"])
def registry_read(reg_path):
    from modules.registry import read_registry
    key_name = request.args.get("key", "")
    value = read_registry(reg_path, key_name)
    return ok(value)


@app.route("/api/registry/write/<path:reg_path>", methods=["POST"])
def registry_write(reg_path):
    from modules.registry import write_registry
    payload = request.json or {}
    result = write_registry(reg_path, payload.get("key", ""), payload.get("value", ""))
    return ok(result)


# ---- 网络 ----
@app.route("/api/network/info", methods=["GET"])
def network_info():
    from modules.network import get_network_info
    return ok(get_network_info())


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
```

**Validation:**
- Run: `cd backend && python -c "import ast; ast.parse(open('app.py', encoding='utf-8').read()); print('ok')"`

**Report file:** `docs/superpowers/sdd/task-1-report.md`

**Report contract:** Return status (DONE/DONE_WITH_CONCERNS/NEEDS_CONTEXT/BLOCKED), commits made, test results, and any concerns.
