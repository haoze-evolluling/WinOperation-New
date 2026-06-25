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
