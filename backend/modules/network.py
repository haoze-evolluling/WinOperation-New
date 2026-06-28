from utils.wmi import query as wmi_query


_STATUS_TEXT = [
    "未连接", "已连接", "已连接", "媒体断开",
    "已禁用", "未初始化", "硬件未就绪", "媒体断开",
    "未知", "正在握手", "已断开", "正在隔离",
]


def _format_speed(raw):
    if raw and int(raw) > 0:
        return f"{int(raw) // 1_000_000} Mbps"
    return "—"


def _format_list(values):
    if not values:
        return "—"
    return ", ".join(values)


def get_network_info():
    configs = wmi_query("""
        SELECT Description, Index, IPAddress, MACAddress, IPSubnet, DefaultIPGateway,
               DNSServerSearchOrder, DHCPEnabled
        FROM Win32_NetworkAdapterConfiguration
        WHERE IPEnabled = TRUE
    """.strip())

    adapters_raw = wmi_query("""
        SELECT DeviceID, Speed, NetConnectionStatus
        FROM Win32_NetworkAdapter
        WHERE NetEnabled = TRUE
    """.strip())

    adapter_map = {}
    for a in adapters_raw:
        try:
            adapter_map[int(a.get("DeviceID", -1))] = a
        except (ValueError, TypeError):
            pass

    result = []
    for c in configs:
        idx = c.get("Index")
        extra = adapter_map.get(idx, {}) if idx is not None else {}

        ips = c.get("IPAddress") or []
        ipv4_list = [ip for ip in ips if ":" not in ip]
        ipv6_list = [ip for ip in ips if ":" in ip]
        ip = ipv4_list[0] if ipv4_list else (ips[0] if ips else "—")
        extra_ips = [ipv4_list[1:], ipv6_list]
        extra_ips = [i for sub in extra_ips for i in sub]
        subnets = c.get("IPSubnet") or []
        subnet = subnets[0] if subnets else "—"
        gateways = c.get("DefaultIPGateway") or []
        gateway = gateways[0] if gateways else "—"
        dns = c.get("DNSServerSearchOrder") or []
        dns_str = _format_list(dns)
        mac = c.get("MACAddress") or "—"
        dhcp = c.get("DHCPEnabled")
        status_code = extra.get("NetConnectionStatus")
        status = _STATUS_TEXT[status_code] if status_code is not None and 0 <= status_code < len(_STATUS_TEXT) else (f"未知({status_code})" if status_code is not None else "—")
        speed = _format_speed(extra.get("Speed"))

        result.append({
            "name": c.get("Description", ""),
            "ip": ip,
            "extra_ips": extra_ips,
            "mac": mac,
            "subnet": subnet,
            "gateway": gateway,
            "dns": dns_str,
            "dhcp": "是" if dhcp else "否",
            "status": status,
            "speed": speed,
        })
    return {"adapters": result}
