import os
import shutil
import tempfile
import glob
import ctypes
from ctypes import wintypes


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


def _scan_dir(path):
    file_count = 0
    size_bytes = 0
    for entry in os.scandir(path):
        try:
            if entry.is_file() or entry.is_symlink():
                size_bytes += entry.stat().st_size
                file_count += 1
            elif entry.is_dir():
                size_bytes += _dir_size(entry.path)
                file_count += 1
        except (PermissionError, OSError):
            continue
    return file_count, size_bytes


def _get_recycle_bin_info():
    class SHQUERYRBINFO(ctypes.Structure):
        _fields_ = [
            ("cbSize", wintypes.DWORD),
            ("i64Size", ctypes.c_longlong),
            ("i64NumItems", ctypes.c_longlong),
        ]

    rb_info = SHQUERYRBINFO()
    rb_info.cbSize = ctypes.sizeof(SHQUERYRBINFO)
    ctypes.windll.shell32.SHQueryRecycleBinW(None, ctypes.byref(rb_info))
    return rb_info.i64Size, rb_info.i64NumItems


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


def scan_cleanup_categories():
    categories = [
        {
            "id": "temp_files",
            "name": "临时文件",
            "description": "系统临时文件和缓存",
            "paths": [
                tempfile.gettempdir(),
                os.path.expandvars(r"%LOCALAPPDATA%\Temp"),
            ],
        },
        {
            "id": "browser_cache",
            "name": "浏览器缓存",
            "description": "Chrome、Edge、Firefox 缓存",
            "paths": [
                os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data\Default\Cache"),
                os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\Cache"),
            ],
        },
        {
            "id": "thumbnail_cache",
            "name": "缩略图缓存",
            "description": "Windows 资源管理器缩略图缓存",
            "paths": [
                os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Windows\Explorer"),
            ],
        },
        {
            "id": "windows_update",
            "name": "Windows 更新缓存",
            "description": "Windows 更新下载文件",
            "paths": [
                os.path.expandvars(r"%WINDIR%\SoftwareDistribution\Download"),
            ],
        },
        {
            "id": "recycle_bin",
            "name": "回收站",
            "description": "回收站中的文件",
            "paths": [],
        },
    ]

    result = []
    for cat in categories:
        file_count = 0
        size_bytes = 0
        scan_paths = list(cat["paths"])

        if cat["id"] == "browser_cache":
            firefox_profile = os.path.expandvars(r"%LOCALAPPDATA%\Mozilla\Firefox\Profiles")
            if os.path.isdir(firefox_profile):
                for profile_dir in glob.glob(os.path.join(firefox_profile, "*", "cache2")):
                    scan_paths.append(profile_dir)
        elif cat["id"] == "thumbnail_cache":
            explorer_dir = cat["paths"][0]
            if os.path.isdir(explorer_dir):
                for thumb_file in glob.glob(os.path.join(explorer_dir, "thumbcache_*")):
                    try:
                        size = os.path.getsize(thumb_file)
                        file_count += 1
                        size_bytes += size
                    except OSError:
                        continue
        elif cat["id"] == "recycle_bin":
            try:
                rb_size, rb_count = _get_recycle_bin_info()
                file_count = rb_count
                size_bytes = rb_size
                scan_paths = [cat["name"]]
            except Exception:
                file_count = 0
                size_bytes = 0
                scan_paths = [cat["name"]]
            result.append({
                "id": cat["id"],
                "name": cat["name"],
                "description": cat["description"],
                "file_count": file_count,
                "size_bytes": size_bytes,
                "size_mb": round(size_bytes / (1024 * 1024), 1),
                "paths": scan_paths,
            })
            continue

        for path in scan_paths:
            if not os.path.isdir(path):
                continue
            fc, sb = _scan_dir(path)
            file_count += fc
            size_bytes += sb

        result.append({
            "id": cat["id"],
            "name": cat["name"],
            "description": cat["description"],
            "file_count": file_count,
            "size_bytes": size_bytes,
            "size_mb": round(size_bytes / (1024 * 1024), 1),
            "paths": scan_paths,
        })

    return result


def execute_cleanup(category_ids):
    cleaned = []
    failed = []
    total_freed_bytes = 0

    for cat_id in category_ids:
        if cat_id == "temp_files":
            temp_dirs = [
                tempfile.gettempdir(),
                os.path.expandvars(r"%LOCALAPPDATA%\Temp"),
            ]
            for temp_dir in temp_dirs:
                if not os.path.isdir(temp_dir):
                    continue
                for entry in os.scandir(temp_dir):
                    try:
                        if entry.is_file() or entry.is_symlink():
                            size = entry.stat().st_size
                            os.remove(entry.path)
                            total_freed_bytes += size
                            cleaned.append({"category": "temp_files", "path": entry.path, "size_mb": round(size / (1024 * 1024), 1)})
                        elif entry.is_dir():
                            dir_size = _dir_size(entry.path)
                            shutil.rmtree(entry.path)
                            total_freed_bytes += dir_size
                            cleaned.append({"category": "temp_files", "path": entry.path, "size_mb": round(dir_size / (1024 * 1024), 1)})
                    except (PermissionError, OSError) as e:
                        failed.append({"category": "temp_files", "path": entry.path, "error": str(e)})
                        continue

        elif cat_id == "browser_cache":
            cache_dirs = [
                os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data\Default\Cache"),
                os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\Cache"),
            ]
            firefox_profile = os.path.expandvars(r"%LOCALAPPDATA%\Mozilla\Firefox\Profiles")
            if os.path.isdir(firefox_profile):
                for profile_dir in glob.glob(os.path.join(firefox_profile, "*", "cache2")):
                    cache_dirs.append(profile_dir)

            for cache_dir in cache_dirs:
                if not os.path.isdir(cache_dir):
                    continue
                for entry in os.scandir(cache_dir):
                    try:
                        if entry.is_file() or entry.is_symlink():
                            size = entry.stat().st_size
                            os.remove(entry.path)
                            total_freed_bytes += size
                            cleaned.append({"category": "browser_cache", "path": entry.path, "size_mb": round(size / (1024 * 1024), 1)})
                        elif entry.is_dir():
                            dir_size = _dir_size(entry.path)
                            shutil.rmtree(entry.path)
                            total_freed_bytes += dir_size
                            cleaned.append({"category": "browser_cache", "path": entry.path, "size_mb": round(dir_size / (1024 * 1024), 1)})
                    except (PermissionError, OSError) as e:
                        failed.append({"category": "browser_cache", "path": entry.path, "error": str(e)})
                        continue

        elif cat_id == "thumbnail_cache":
            explorer_dir = os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Windows\Explorer")
            if os.path.isdir(explorer_dir):
                for thumb_file in glob.glob(os.path.join(explorer_dir, "thumbcache_*")):
                    try:
                        size = os.path.getsize(thumb_file)
                        os.remove(thumb_file)
                        total_freed_bytes += size
                        cleaned.append({"category": "thumbnail_cache", "path": thumb_file, "size_mb": round(size / (1024 * 1024), 1)})
                    except (PermissionError, OSError) as e:
                        failed.append({"category": "thumbnail_cache", "path": thumb_file, "error": str(e)})
                        continue

        elif cat_id == "windows_update":
            wu_dir = os.path.expandvars(r"%WINDIR%\SoftwareDistribution\Download")
            if os.path.isdir(wu_dir):
                for entry in os.scandir(wu_dir):
                    try:
                        if entry.is_file() or entry.is_symlink():
                            size = entry.stat().st_size
                            os.remove(entry.path)
                            total_freed_bytes += size
                            cleaned.append({"category": "windows_update", "path": entry.path, "size_mb": round(size / (1024 * 1024), 1)})
                        elif entry.is_dir():
                            dir_size = _dir_size(entry.path)
                            shutil.rmtree(entry.path)
                            total_freed_bytes += dir_size
                            cleaned.append({"category": "windows_update", "path": entry.path, "size_mb": round(dir_size / (1024 * 1024), 1)})
                    except (PermissionError, OSError) as e:
                        failed.append({"category": "windows_update", "path": entry.path, "error": str(e)})
                        continue

        elif cat_id == "recycle_bin":
            try:
                rb_size, rb_count = _get_recycle_bin_info()
                ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, 0)
                total_freed_bytes += rb_size
                cleaned.append({"category": "recycle_bin", "path": "回收站", "size_mb": round(rb_size / (1024 * 1024), 1)})
            except Exception as e:
                failed.append({"category": "recycle_bin", "path": "回收站", "error": str(e)})

    total_freed_mb = round(total_freed_bytes / (1024 * 1024), 1)

    return {
        "cleaned": cleaned,
        "failed": failed,
        "total_freed_mb": total_freed_mb,
    }
