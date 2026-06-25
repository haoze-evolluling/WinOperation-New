from utils.registry import read_key, write_key, list_subkeys, tree_subkeys
import win32con


TYPE_MAP = {
    win32con.REG_SZ: "REG_SZ",
    win32con.REG_DWORD: "REG_DWORD",
    win32con.REG_BINARY: "REG_BINARY",
    win32con.REG_MULTI_SZ: "REG_MULTI_STRING",
}


def read_registry(reg_path, key_name=""):
    try:
        data, reg_type = read_key(reg_path, key_name)
        return {
            "status": "ok",
            "path": reg_path,
            "key": key_name,
            "value": data,
            "type": TYPE_MAP.get(reg_type, f"REG_UNKNOWN({reg_type})"),
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


def write_registry(reg_path, key_name, value):
    try:
        write_key(reg_path, key_name, value)
        return {
            "status": "ok",
            "path": reg_path,
            "key": key_name,
            "value": value,
            "message": "写入成功",
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


def list_registry(reg_path):
    try:
        raw = list_subkeys(reg_path)
        values = []
        for v in raw["values"]:
            values.append({
                "name": v["name"],
                "data": v["data"],
                "type": TYPE_MAP.get(v["type_int"], f"REG_UNKNOWN({v['type_int']})"),
            })
        return {
            "status": "ok",
            "path": reg_path,
            "subkeys": raw["subkeys"],
            "values": values,
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


def tree_registry(reg_path, max_depth=2):
    try:
        tree = tree_subkeys(reg_path, max_depth=max_depth)
        return {
            "status": "ok",
            "path": reg_path,
            "tree": tree,
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


def batch_read_registry(entries):
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
    return {"results": results}


def batch_write_registry(entries):
    results = []
    for entry in entries:
        try:
            write_key(
                entry["path"],
                entry.get("key", ""),
                entry.get("value", ""),
            )
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
    return {"results": results}
