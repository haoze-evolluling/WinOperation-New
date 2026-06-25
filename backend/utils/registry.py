import win32api
import win32con

HKEY_MAP = {
    "HKLM": win32con.HKEY_LOCAL_MACHINE,
    "HKCU": win32con.HKEY_CURRENT_USER,
    "HKCR": win32con.HKEY_CLASSES_ROOT,
    "HKU": win32con.HKEY_USERS,
    "HKCC": win32con.HKEY_CURRENT_CONFIG,
}


def _parse_root(reg_path):
    parts = reg_path.split("\\", 1)
    root_str = parts[0].upper()
    sub_path = parts[1] if len(parts) > 1 else ""
    root = HKEY_MAP.get(root_str)
    if root is None:
        raise ValueError(f"不支持的注册表根: {root_str}")
    return root, sub_path


def read_key(reg_path, value_name=""):
    root, sub_path = _parse_root(reg_path)
    key = None
    try:
        key = win32api.RegOpenKeyEx(root, sub_path, 0, win32con.KEY_READ)
        data, reg_type = win32api.RegQueryValueEx(key, value_name)
        return data, reg_type
    finally:
        if key:
            win32api.RegCloseKey(key)


def write_key(reg_path, value_name, data, reg_type=win32con.REG_SZ):
    root, sub_path = _parse_root(reg_path)
    key = None
    try:
        key = win32api.RegCreateKey(root, sub_path)
        win32api.RegSetValueEx(key, value_name, 0, reg_type, data)
    finally:
        if key:
            win32api.RegCloseKey(key)
