import os
import shutil
import tempfile
import glob
import ctypes
from ctypes import wintypes


def _scan_dir(path):
    file_count = 0
    size_bytes = 0
    for entry in os.scandir(path):
        try:
            if entry.is_file() or entry.is_symlink():
                size_bytes += entry.stat().st_size
                file_count += 1
            elif entry.is_dir():
                fc, sb = _scan_dir(entry.path)
                file_count += fc
                size_bytes += sb
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
    ret = ctypes.windll.shell32.SHQueryRecycleBinW(None, ctypes.byref(rb_info))
    if ret != 0:
        return 0, 0
    return rb_info.i64Size, rb_info.i64NumItems


# ponytail: single source of truth for category paths; scan and execute both reference this
CATEGORIES = [
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


def _browser_cache_paths():
    paths = list(CATEGORIES[1]["paths"])
    firefox_profile = os.path.expandvars(r"%LOCALAPPDATA%\Mozilla\Firefox\Profiles")
    if os.path.isdir(firefox_profile):
        for profile_dir in glob.glob(os.path.join(firefox_profile, "*", "cache2")):
            paths.append(profile_dir)
    return paths


def _thumbnail_paths():
    explorer_dir = CATEGORIES[2]["paths"][0]
    if os.path.isdir(explorer_dir):
        return glob.glob(os.path.join(explorer_dir, "thumbcache_*"))
    return []


def scan_cleanup_categories():
    result = []
    for cat in CATEGORIES:
        file_count = 0
        size_bytes = 0

        if cat["id"] == "browser_cache":
            scan_paths = _browser_cache_paths()
        elif cat["id"] == "thumbnail_cache":
            scan_paths = _thumbnail_paths()
            for thumb_file in scan_paths:
                try:
                    size = os.path.getsize(thumb_file)
                    file_count += 1
                    size_bytes += size
                except OSError:
                    continue
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
        else:
            scan_paths = list(cat["paths"])

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


def _cleanup_dirs(dirs, category, cleaned, failed, total_freed_bytes):
    for d in dirs:
        if not os.path.isdir(d):
            continue
        for entry in os.scandir(d):
            try:
                if entry.is_file() or entry.is_symlink():
                    size = entry.stat().st_size
                    os.remove(entry.path)
                    total_freed_bytes[0] += size
                    cleaned.append({"category": category, "path": entry.path, "size_mb": round(size / (1024 * 1024), 1)})
                elif entry.is_dir():
                    shutil.rmtree(entry.path)
            except (PermissionError, OSError) as e:
                failed.append({"category": category, "path": entry.path, "error": str(e)})


def execute_cleanup(category_ids):
    cleaned = []
    failed = []
    total_freed_bytes = [0]

    for cat_id in category_ids:
        cat = next((c for c in CATEGORIES if c["id"] == cat_id), None)
        if cat is None:
            continue

        if cat_id == "browser_cache":
            _cleanup_dirs(_browser_cache_paths(), cat_id, cleaned, failed, total_freed_bytes)

        elif cat_id == "thumbnail_cache":
            for thumb_file in _thumbnail_paths():
                try:
                    size = os.path.getsize(thumb_file)
                    os.remove(thumb_file)
                    total_freed_bytes[0] += size
                    cleaned.append({"category": cat_id, "path": thumb_file, "size_mb": round(size / (1024 * 1024), 1)})
                except (PermissionError, OSError) as e:
                    failed.append({"category": cat_id, "path": thumb_file, "error": str(e)})

        elif cat_id == "recycle_bin":
            try:
                rb_size, rb_count = _get_recycle_bin_info()
                ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, 0)
                total_freed_bytes[0] += rb_size
                cleaned.append({"category": cat_id, "path": "回收站", "size_mb": round(rb_size / (1024 * 1024), 1)})
            except Exception as e:
                failed.append({"category": cat_id, "path": "回收站", "error": str(e)})

        else:
            _cleanup_dirs(cat["paths"], cat_id, cleaned, failed, total_freed_bytes)

    total_freed_mb = round(total_freed_bytes[0] / (1024 * 1024), 1)

    return {
        "cleaned": cleaned,
        "failed": failed,
        "total_freed_mb": total_freed_mb,
    }
