def get_services():
    return {
        "services": [
            {"name": "wuauserv", "display_name": "Windows Update", "status": "running"},
            {"name": "WinDefend", "display_name": "Windows Defender", "status": "running"},
            {"name": "Schedule", "display_name": "Task Scheduler", "status": "running"},
        ]
    }


def toggle_service(name, action):
    return {
        "name": name,
        "action": action,
        "message": f"模拟{'启动' if action == 'start' else '停止'}服务 {name}",
        "requires_admin": True,
    }
