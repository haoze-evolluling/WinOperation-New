from utils.wmi import query as wmi_query


def get_network_info():
    adapters = wmi_query("""
        SELECT Description, IPAddress 
        FROM Win32_NetworkAdapterConfiguration 
        WHERE IPEnabled = TRUE
    """)
    result = []
    for a in adapters:
        ips = a.get("IPAddress") or []
        ip = ips[0] if ips else ""
        result.append({
            "name": a.get("Description", ""),
            "ip": ip,
            "dns": [],  # ponytail: DNS via separate query adds complexity for little value
            "speed": "",
        })
    return {"adapters": result}
