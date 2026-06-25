def read_registry(reg_path, key_name=""):
    return {
        "path": reg_path,
        "key": key_name,
        "value": "模拟注册表值",
        "type": "REG_SZ",
        "requires_admin": False,
    }


def write_registry(reg_path, key_name, value):
    return {
        "path": reg_path,
        "key": key_name,
        "value": value,
        "message": "模拟写入注册表",
        "requires_admin": True,
    }
