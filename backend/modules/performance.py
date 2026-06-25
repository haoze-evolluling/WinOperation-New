import win32service
import win32serviceutil


SERVICE_STATES = {
    win32service.SERVICE_STOPPED: "stopped",
    win32service.SERVICE_START_PENDING: "starting",
    win32service.SERVICE_RUNNING: "running",
    win32service.SERVICE_STOP_PENDING: "stopping",
    win32service.SERVICE_PAUSED: "paused",
}


def _get_service_status(name):
    scm = win32service.OpenSCManager(None, None, win32service.SC_MANAGER_CONNECT)
    try:
        handle = win32service.OpenService(scm, name, win32service.SERVICE_QUERY_STATUS)
        try:
            status = win32service.QueryServiceStatus(handle)
            return status[1]
        finally:
            win32service.CloseServiceHandle(handle)
    finally:
        win32service.CloseServiceHandle(scm)


def get_services():
    scm = win32service.OpenSCManager(None, None, win32service.SC_MANAGER_ENUMERATE_SERVICE)
    try:
        services = win32service.EnumServicesStatus(scm, win32service.SERVICE_WIN32, win32service.SERVICE_STATE_ALL)
        result = []
        for svc in services:
            name = svc[0]
            display = svc[1]
            status_code = svc[2][1]
            status = SERVICE_STATES.get(status_code, "unknown")
            result.append({"name": name, "display_name": display, "status": status})
        return {"services": result}
    finally:
        win32service.CloseServiceHandle(scm)


def toggle_service(name, action):
    current_state = _get_service_status(name)

    if action == "start":
        if current_state == win32service.SERVICE_RUNNING:
            return {"name": name, "action": action, "message": f"服务 {name} 已在运行中，无需启动"}
        win32serviceutil.StartService(name)
        msg = f"已启动服务 {name}"
    else:
        if current_state == win32service.SERVICE_STOPPED:
            return {"name": name, "action": action, "message": f"服务 {name} 已处于停止状态，无需停止"}
        win32serviceutil.StopService(name)
        msg = f"已停止服务 {name}"
    return {"name": name, "action": action, "message": msg}
