import win32com.client


def query(wql):
    obj = win32com.client.GetObject("winmgmts:\\\\.\\root\\cimv2")
    cols = None
    results = []
    for item in obj.ExecQuery(wql):
        if cols is None:
            cols = [p.name for p in item.Properties_]
        row = {c: getattr(item, c, None) for c in cols}
        results.append(row)
    return results
