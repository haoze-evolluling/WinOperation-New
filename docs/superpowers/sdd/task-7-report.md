Status: DONE
Commits: c5d8b8111cad05bdae06b74f033379f34b60ef39
Test: python -c "from modules.network import get_network_info; import json; print(json.dumps(get_network_info(), indent=2, ensure_ascii=False))"
  Output:
{
  "adapters": [
    {
      "name": "Intel(R) Wi-Fi 6 AX200 160MHz",
      "ip": "192.168.1.101",
      "dns": [],
      "speed": ""
    }
  ]
}
Concerns: None
