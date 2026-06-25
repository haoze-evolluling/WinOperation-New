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


@app.route("/api/cleanup/scan", methods=["POST"])
def scan_cleanup():
    from modules.cleanup import scan_cleanup_categories
    return ok(scan_cleanup_categories())


@app.route("/api/cleanup/execute", methods=["POST"])
def execute_cleanup():
    from modules.cleanup import execute_cleanup
    payload = request.json or {}
    categories = payload.get("categories", [])
    return ok(execute_cleanup(categories))


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
    reg_path = reg_path.replace("/", "\\")
    key_name = request.args.get("key", "")
    value = read_registry(reg_path, key_name)
    return ok(value)


@app.route("/api/registry/write/<path:reg_path>", methods=["POST"])
def registry_write(reg_path):
    from modules.registry import write_registry
    reg_path = reg_path.replace("/", "\\")
    payload = request.json or {}
    result = write_registry(reg_path, payload.get("key", ""), payload.get("value", ""))
    return ok(result)


@app.route("/api/registry/list/<path:reg_path>", methods=["GET"])
def registry_list(reg_path):
    from modules.registry import list_registry
    reg_path = reg_path.replace("/", "\\")
    result = list_registry(reg_path)
    return ok(result)


@app.route("/api/registry/tree/<path:reg_path>", methods=["GET"])
def registry_tree(reg_path):
    from modules.registry import tree_registry
    reg_path = reg_path.replace("/", "\\")
    depth = int(request.args.get("depth", 2))
    result = tree_registry(reg_path, max_depth=depth)
    return ok(result)


@app.route("/api/registry/batch-read", methods=["POST"])
def registry_batch_read():
    from modules.registry import batch_read_registry
    payload = request.json or {}
    entries = payload.get("entries", [])
    result = batch_read_registry(entries)
    return ok(result)


@app.route("/api/registry/batch-write", methods=["POST"])
def registry_batch_write():
    from modules.registry import batch_write_registry
    payload = request.json or {}
    entries = payload.get("entries", [])
    result = batch_write_registry(entries)
    return ok(result)


@app.route("/api/registry/export", methods=["POST"])
def registry_export():
    from modules.registry import export_registry
    payload = request.json or {}
    reg_path = payload.get("path", "")
    result = export_registry(reg_path)
    if result.get("status") == "error":
        return ok(result)
    from flask import Response
    return Response(result["content"], mimetype="text/plain")


@app.route("/api/registry/import", methods=["POST"])
def registry_import():
    from modules.registry import import_registry
    reg_text = request.data.decode("utf-8") if request.data else ""
    result = import_registry(reg_text)
    return ok(result)


# ---- 网络 ----
@app.route("/api/network/info", methods=["GET"])
def network_info():
    from modules.network import get_network_info
    return ok(get_network_info())


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
