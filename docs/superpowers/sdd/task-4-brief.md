# Task 4 Brief: 实现 cleanup.py（真实文件系统清理）

**Goal:** 将 `backend/modules/cleanup.py` 从模拟数据替换为真实文件系统清理实现。

**Files:**
- Modify: `backend/modules/cleanup.py`

**Interfaces:**
- Consumes: stdlib `os`, `shutil`, `tempfile`
- Produces: `do_cleanup_temp(payload) -> dict`

**Return Structure (must match existing frontend expectations):**
```python
{
    "cleaned_paths": [str, ...],  # 已清理的文件/目录路径列表
    "freed_mb": float,            # 释放的空间（MB）
    "message": str,               # 结果消息
}
```

**Implementation:**

```python
import os
import shutil
import tempfile


def do_cleanup_temp(payload):
    temp_dirs = [
        tempfile.gettempdir(),
        os.path.expandvars(r"%LOCALAPPDATA%\Temp"),
    ]
    cleaned_paths = []
    freed_bytes = 0

    for temp_dir in temp_dirs:
        if not os.path.isdir(temp_dir):
            continue
        for entry in os.scandir(temp_dir):
            try:
                path = entry.path
                if entry.is_file() or entry.is_symlink():
                    size = entry.stat().st_size
                    os.remove(path)
                    freed_bytes += size
                    cleaned_paths.append(path)
                elif entry.is_dir():
                    dir_size = _dir_size(path)
                    shutil.rmtree(path)
                    freed_bytes += dir_size
                    cleaned_paths.append(path)
            except (PermissionError, OSError):
                continue

    freed_mb = round(freed_bytes / (1024 * 1024), 1)
    return {
        "cleaned_paths": cleaned_paths,
        "freed_mb": freed_mb,
        "message": f"清理完成，释放 {freed_mb} MB",
    }


def _dir_size(path):
    total = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            try:
                total += os.path.getsize(fp)
            except OSError:
                pass
    return total
```

**Validation:**
- Run: `python -c "from modules.cleanup import do_cleanup_temp; import json; print(json.dumps(do_cleanup_temp({}), indent=2, ensure_ascii=False))"`

**Report file:** `docs/superpowers/sdd/task-4-report.md`

**Report contract:** Return status, commits, test results, and any concerns.
