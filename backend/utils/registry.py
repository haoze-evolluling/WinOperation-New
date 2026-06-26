import win32api
import win32con
import winreg
import re

_ABBREV_TO_FULL = {
    "HKLM": "HKEY_LOCAL_MACHINE",
    "HKCU": "HKEY_CURRENT_USER",
    "HKCR": "HKEY_CLASSES_ROOT",
    "HKU": "HKEY_USERS",
    "HKCC": "HKEY_CURRENT_CONFIG",
}
_ROOT_TO_ABBREV = {v: k for k, v in _ABBREV_TO_FULL.items()}


def _parse_root(reg_path):
    parts = reg_path.split("\\", 1)
    root_str = parts[0].upper()
    sub_path = parts[1] if len(parts) > 1 else ""
    root = _ABBREV_TO_FULL.get(root_str)
    if root is None:
        raise ValueError(f"不支持的注册表根: {root_str}")
    # map full name back to win32 constant
    root_map = {
        "HKEY_LOCAL_MACHINE": win32con.HKEY_LOCAL_MACHINE,
        "HKEY_CURRENT_USER": win32con.HKEY_CURRENT_USER,
        "HKEY_CLASSES_ROOT": win32con.HKEY_CLASSES_ROOT,
        "HKEY_USERS": win32con.HKEY_USERS,
        "HKEY_CURRENT_CONFIG": win32con.HKEY_CURRENT_CONFIG,
    }
    return root_map[root], sub_path


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
        key = winreg.OpenKey(root, sub_path, 0, winreg.KEY_READ)
        subkeys = []
        i = 0
        while True:
            try:
                name = winreg.EnumKey(key, i)
                subkeys.append(name)
                i += 1
            except OSError:
                break
        values = []
        i = 0
        while True:
            try:
                name, data, reg_type = winreg.EnumValue(key, i)
                values.append({"name": name, "data": data, "type_int": reg_type})
                i += 1
            except OSError:
                break
        return {"subkeys": subkeys, "values": values}
    finally:
        if key:
            winreg.CloseKey(key)


def tree_subkeys(reg_path, max_depth=2):
    max_depth = min(max_depth, 10)
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
            "children": children,
            "values_count": len(info["values"]),
        }

    return _build(node_path, max_depth)


def export_reg(reg_path):
    info = list_subkeys(reg_path)
    lines = ["Windows Registry Editor Version 5.00", ""]
    section = f"[{_reg_path_to_string(reg_path)}]"
    lines.append(section)
    for v in info["values"]:
        name = v["name"]
        data = v["data"]
        reg_type = v["type_int"]
        if reg_type == win32con.REG_SZ:
            lines.append(f'"{name}"="{data}"')
        elif reg_type == win32con.REG_DWORD:
            lines.append(f'"{name}"=dword:{data:08X}')
        # ponytail: skip REG_BINARY and unknown types per brief; add when needed
    return "\n".join(lines)


def _reg_path_to_string(reg_path):
    parts = reg_path.split("\\", 1)
    root_str = parts[0].upper()
    rest = parts[1] if len(parts) > 1 else ""
    root_name = _ABBREV_TO_FULL.get(root_str, root_str)
    if rest:
        return f"{root_name}\\{rest}"
    return root_name


def import_reg(reg_text):
    imported = 0
    failed = []
    errors = []
    current_path = None

    for line in reg_text.splitlines():
        line = line.strip()
        if not line or line.startswith("Windows Registry Editor"):
            continue
        section_match = re.match(r'^\[(.+)\]$', line)
        if section_match:
            full_path = section_match.group(1)
            parts = full_path.split("\\", 1)
            root_str = parts[0].upper()
            abbrev = _ROOT_TO_ABBREV.get(root_str)
            if abbrev is None:
                errors.append(f"不支持的注册表根: {root_str}")
                current_path = None
                continue
            rest = parts[1] if len(parts) > 1 else ""
            current_path = f"{abbrev}\\{rest}" if rest else abbrev
            continue

        if current_path is None:
            continue

        val_match = re.match(r'^"([^"]+)"="(.+)"$', line)
        if val_match:
            name = val_match.group(1)
            data = val_match.group(2)
            try:
                write_key(current_path, name, data, win32con.REG_SZ)
                imported += 1
            except Exception as e:
                failed.append(name)
                errors.append(str(e))
            continue

        dword_match = re.match(r'^"([^"]+)"=dword:([0-9a-fA-F]+)$', line)
        if dword_match:
            name = dword_match.group(1)
            hex_str = dword_match.group(2)
            try:
                data = int(hex_str, 16)
                write_key(current_path, name, data, win32con.REG_DWORD)
                imported += 1
            except Exception as e:
                failed.append(name)
                errors.append(str(e))
            continue

        errors.append(f"无法解析行: {line}")

    return {"imported": imported, "failed": failed, "errors": errors}
