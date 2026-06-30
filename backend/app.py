from flask import Flask, request, send_from_directory, Response
import ctypes
import os
import sys
import json


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
    payload = json.dumps({"status": "ok", "data": data}, ensure_ascii=False)
    return Response(payload, mimetype="application/json; charset=utf-8")


def error(message):
    payload = json.dumps({"status": "error", "error": message}, ensure_ascii=False)
    return Response(payload, mimetype="application/json; charset=utf-8")


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



# ---- 网络 ----
@app.route("/api/network/info", methods=["GET"])
def network_info():
    from modules.network import get_network_info
    return ok(get_network_info())


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
