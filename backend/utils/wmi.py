import win32com.client
import pywintypes
import pythoncom


def query(wql):
    pythoncom.CoInitialize()
    try:
        obj = win32com.client.Dispatch("WbemScripting.SWbemLocator").ConnectServer(".", "root\\cimv2")
    except pywintypes.com_error as e:
        raise RuntimeError(f"WMI connect failed: {e}") from None
    cols = None
    results = []
    try:
        for item in obj.ExecQuery(wql):
            if cols is None:
                cols = [p.name for p in item.Properties_]
            row = {c: getattr(item, c, None) for c in cols}
            results.append(row)
    except pywintypes.com_error as e:
        raise RuntimeError(f"WMI query failed: {e}") from None
    finally:
        pythoncom.CoUninitialize()
    return results
