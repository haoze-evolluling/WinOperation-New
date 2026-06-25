import win32com.client
import pywintypes


def query(wql):
    try:
        obj = win32com.client.GetObject("winmgmts:\\\\.\\root\\cimv2")
    except pywintypes.com_error as e:
        raise RuntimeError(str(e)) from None
    cols = None
    results = []
    try:
        for item in obj.ExecQuery(wql):
            if cols is None:
                cols = [p.name for p in item.Properties_]
            row = {c: getattr(item, c, None) for c in cols}
            results.append(row)
    except pywintypes.com_error as e:
        raise RuntimeError(str(e)) from None
    return results
