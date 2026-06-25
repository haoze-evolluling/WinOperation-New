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


def list_subkeys(reg_path):
    root, sub_path = _parse_root(reg_path)
    key = None
    try:
        key = win32api.RegOpenKeyEx(root, sub_path, 0, win32con.KEY_READ)
        subkeys = []
        i = 0
        while True:
            try:
                name, _, _ = win32api.RegEnumKeyEx(key, i)
                subkeys.append(name)
                i += 1
            except win32api.error:
                break
        values = []
        i = 0
        while True:
            try:
                name, data, reg_type = win32api.RegEnumValue(key, i)
                values.append({"name": name, "data": data, "type_int": reg_type})
                i += 1
            except win32api.error:
                break
        return {"subkeys": subkeys, "values": values}
    finally:
        if key:
            win32api.RegCloseKey(key)


def tree_subkeys(reg_path, max_depth=2):
    node_path = reg_path

    def _build(path, depth):
        if depth < 0:
            return None
        info = list_subkeys(path)
        children = []
        if depth > 0:
            for name in info["subkeys"]:
                child_path = f"{path}\\{name}"
                child = _build(child_path, depth - 1)
                if child is not None:
                    child["name"] = name
                    children.append(child)
        return {
            "path": path,
            "subkeys": children,
            "values_count": len(info["values"]),
        }

    return _build(node_path, max_depth)
