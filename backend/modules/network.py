def get_network_info():
    return {
        "adapters": [
            {
                "name": "Wi-Fi",
                "ip": "192.168.1.100",
                "dns": ["223.5.5.5", "114.114.114.114"],
                "speed": "867 Mbps",
            },
            {
                "name": "Ethernet",
                "ip": "192.168.1.101",
                "dns": ["223.5.5.5"],
                "speed": "1 Gbps",
            },
        ]
    }
