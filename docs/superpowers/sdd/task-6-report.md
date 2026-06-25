# Task 6 Report: 实现 registry.py（真实注册表读写）

- Status: DONE
- Commits: 6950523
- Test: `python -c "import sys; sys.path.insert(0, 'backend'); from modules.registry import read_registry; import json; print(json.dumps(read_registry(r'HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion', 'ProductName'), indent=2))"`
  - Output:
    ```json
    {
      "path": "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion",
      "key": "ProductName",
      "value": "Windows 10 IoT Enterprise LTSC 2021",
      "type": "REG_SZ"
    }
    ```
- Concerns: brief 中 `win32con.REG_MULTI_STRING` 应为 `win32con.REG_MULTI_SZ`，已修正。
