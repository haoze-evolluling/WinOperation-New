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
    try:
        result = toggle_service(name, action)
        return ok(result)
    except Exception as e:
        return error(str(e))


# ---- 注册表 ----
@app.route("/api/registry/read/<path:reg_path>", methods=["GET"])
def registry_read(reg_path):
    from utils.registry import read_key, TYPE_MAP
    reg_path = reg_path.replace("/", "\\")
    key_name = request.args.get("key", "")
    try:
        data, reg_type = read_key(reg_path, key_name)
        return ok({"value": data, "type": TYPE_MAP.get(reg_type, f"REG_UNKNOWN({reg_type})")})
    except Exception as e:
        return error(str(e))


@app.route("/api/registry/write/<path:reg_path>", methods=["POST"])
def registry_write(reg_path):
    import win32con
    from utils.registry import write_key, REVERSE_TYPE_MAP
    reg_path = reg_path.replace("/", "\\")
    payload = request.json or {}
    type_int = REVERSE_TYPE_MAP.get(payload.get("type", "REG_SZ"), win32con.REG_SZ)
    try:
        write_key(reg_path, payload.get("key", ""), payload.get("value", ""), type_int)
        return ok({"message": "写入成功"})
    except Exception as e:
        return error(str(e))


@app.route("/api/registry/list/<path:reg_path>", methods=["GET"])
def registry_list(reg_path):
    from utils.registry import list_subkeys, TYPE_MAP
    reg_path = reg_path.replace("/", "\\")
    try:
        raw = list_subkeys(reg_path)
        values = [{"name": v["name"], "data": v["data"], "type": TYPE_MAP.get(v["type_int"], f"REG_UNKNOWN({v['type_int']})")} for v in raw["values"]]
        return ok({"status": "ok", "subkeys": raw["subkeys"], "values": values})
    except Exception as e:
        return error(str(e))


@app.route("/api/registry/tree/<path:reg_path>", methods=["GET"])
def registry_tree(reg_path):
    from utils.registry import tree_subkeys
    reg_path = reg_path.replace("/", "\\")
    depth = int(request.args.get("depth", 2))
    try:
        tree = tree_subkeys(reg_path, max_depth=min(depth, 10))
        return ok({"status": "ok", "path": reg_path, "tree": tree})
    except Exception as e:
        return error(str(e))


@app.route("/api/registry/batch-read", methods=["POST"])
def registry_batch_read():
    from utils.registry import read_key, TYPE_MAP
    payload = request.json or {}
    entries = payload.get("entries", [])
    results = []
    for entry in entries:
        try:
            data, reg_type = read_key(entry["path"], entry.get("key", ""))
            results.append({
                "path": entry["path"],
                "key": entry.get("key", ""),
                "value": data,
                "type": TYPE_MAP.get(reg_type, f"REG_UNKNOWN({reg_type})"),
                "status": "ok",
            })
        except Exception as e:
            results.append({
                "path": entry["path"],
                "key": entry.get("key", ""),
                "value": None,
                "type": None,
                "status": "error",
                "error": str(e),
            })
    return ok({"results": results})


@app.route("/api/registry/batch-write", methods=["POST"])
def registry_batch_write():
    import win32con
    from utils.registry import write_key, REVERSE_TYPE_MAP
    payload = request.json or {}
    entries = payload.get("entries", [])
    results = []
    for entry in entries:
        try:
            type_int = REVERSE_TYPE_MAP.get(entry.get("type", "REG_SZ"), win32con.REG_SZ)
            write_key(entry["path"], entry.get("key", ""), entry.get("value", ""), type_int)
            results.append({
                "path": entry["path"],
                "key": entry.get("key", ""),
                "value": entry.get("value", ""),
                "type": entry.get("type", "REG_SZ"),
                "status": "ok",
            })
        except Exception as e:
            results.append({
                "path": entry["path"],
                "key": entry.get("key", ""),
                "value": entry.get("value", ""),
                "type": entry.get("type", "REG_SZ"),
                "status": "error",
                "error": str(e),
            })
    return ok({"results": results})


@app.route("/api/registry/export", methods=["POST"])
def registry_export():
    from utils.registry import export_reg
    payload = request.json or {}
    reg_path = payload.get("path", "")
    try:
        content = export_reg(reg_path)
        return ok({"content": content})
    except Exception as e:
        return error(str(e))


@app.route("/api/registry/import", methods=["POST"])
def registry_import():
    from utils.registry import import_reg
    reg_text = request.data.decode("utf-8") if request.data else ""
    try:
        result = import_reg(reg_text)
        return ok(result)
    except Exception as e:
        return error(str(e))


# ---- 网络 ----
@app.route("/api/network/info", methods=["GET"])
def network_info():
    from modules.network import get_network_info
    return ok(get_network_info())


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
