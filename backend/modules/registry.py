from utils.registry import read_key, write_key
import win32con


TYPE_MAP = {
    win32con.REG_SZ: "REG_SZ",
    win32con.REG_DWORD: "REG_DWORD",
    win32con.REG_BINARY: "REG_BINARY",
    win32con.REG_MULTI_SZ: "REG_MULTI_STRING",
}


def read_registry(reg_path, key_name=""):
    data, reg_type = read_key(reg_path, key_name)
    return {
        "path": reg_path,
        "key": key_name,
        "value": data,
        "type": TYPE_MAP.get(reg_type, f"REG_UNKNOWN({reg_type})"),
    }


def write_registry(reg_path, key_name, value):
    write_key(reg_path, key_name, value)
    return {
        "path": reg_path,
        "key": key_name,
        "value": value,
        "message": "写入成功",
    }
