# Task 2: 创建 Flask 入口 app.py

## Context
这是 Windows 系统优化工具项目的 Task 2。你需要创建 Flask 后端入口文件，注册所有 API 路由，并托管前端静态文件。

## 需求

创建 `backend/app.py`，内容如下（**逐字使用，不要修改**）：

```python
from flask import Flask, jsonify, request, send_from_directory
import os

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

## 验证
写入文件后，运行：
```powershell
cd backend; python -c "import ast; ast.parse(open('app.py').read()); print('syntax ok')"
```

## 报告
完成后写入报告文件 `docs/superpowers/sdd/task-2-report.md`，包含：
- 文件路径和行数
- 语法验证结果
- 任何问题

## 注意
- 不要修改其他文件
- 只做这个任务
- 提交：`git add backend/app.py && git commit -m "feat: Task 2 - Flask 入口 app.py"`
