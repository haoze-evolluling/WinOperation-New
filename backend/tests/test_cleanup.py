import os
import sys
import pytest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "backend"))

from modules.cleanup import scan_cleanup_categories, execute_cleanup


def _make_entry(name, size=1024, is_file=True, is_dir=False):
    entry = MagicMock()
    entry.path = f"C:\\fake\\{name}"
    entry.is_file.return_value = is_file
    entry.is_symlink.return_value = False
    entry.is_dir.return_value = is_dir
    entry.stat.return_value = MagicMock(st_size=size)
    return entry


class TestScanCleanupCategories:
    @patch("modules.cleanup.os.path.isdir", return_value=True)
    @patch("modules.cleanup.glob.glob")
    @patch("modules.cleanup.ctypes.windll.shell32.SHQueryRecycleBinW")
    def test_returns_five_categories(
        self, mock_recycle_bin, mock_glob, mock_isdir
    ):
        mock_recycle_bin.return_value = 0
        mock_glob.return_value = []

        fake_entry = _make_entry("file.tmp", size=1024)

        def fake_scandir(path):
            return [fake_entry]

        with patch("modules.cleanup.os.scandir", side_effect=fake_scandir):
            result = scan_cleanup_categories()
        
        assert len(result) == 5
        
        required_fields = {"id", "name", "description", "file_count", "size_bytes", "size_mb", "paths"}
        for cat in result:
            assert required_fields.issubset(cat.keys()), f"Missing fields in {cat}"
            assert isinstance(cat["file_count"], int)
            assert isinstance(cat["size_bytes"], int)
            assert isinstance(cat["size_mb"], float)
            assert isinstance(cat["paths"], list)
        
        ids = [cat["id"] for cat in result]
        assert ids == [
            "temp_files",
            "browser_cache",
            "thumbnail_cache",
            "windows_update",
            "recycle_bin",
        ]


class TestExecuteCleanup:
    @patch("modules.cleanup.os.path.isdir", return_value=True)
    @patch("modules.cleanup.shutil.rmtree")
    @patch("modules.cleanup.os.remove")
    @patch("modules.cleanup.os.scandir")
    def test_temp_files_returns_cleaned_failed_freed(
        self, mock_scandir, mock_remove, mock_rmtree, mock_isdir
    ):
        fake_entry = _make_entry("file.tmp", size=1024 * 1024)
        mock_scandir.return_value = [fake_entry]
        
        result = execute_cleanup(["temp_files"])
        
        assert "cleaned" in result
        assert "failed" in result
        assert "total_freed_mb" in result
        assert isinstance(result["cleaned"], list)
        assert isinstance(result["failed"], list)
        assert isinstance(result["total_freed_mb"], float)
        assert result["total_freed_mb"] >= 0


class TestExecuteCleanupEmpty:
    def test_empty_categories_returns_empty_results(self):
        result = execute_cleanup([])
        
        assert result["cleaned"] == []
        assert result["failed"] == []
        assert result["total_freed_mb"] == 0.0


class TestScanThumbnailCache:
    @patch("modules.cleanup.os.path.isdir")
    @patch("modules.cleanup.glob.glob")
    def test_thumbnail_cache_counts_thumbcache_files(self, mock_glob, mock_isdir):
        mock_isdir.return_value = True
        thumb_files = [
            r"C:\fake\Explorer\thumbcache_256.db",
            r"C:\fake\Explorer\thumbcache_1024.db",
            r"C:\fake\Explorer\thumbcache_critical.db",
        ]
        mock_glob.return_value = thumb_files
        
        def fake_getsize(path):
            if path in thumb_files:
                return 2048
            return 0
        
        with patch("modules.cleanup.os.path.getsize", side_effect=fake_getsize):
            with patch("modules.cleanup.os.scandir", return_value=[]):
                result = scan_cleanup_categories()
        
        thumb_cat = next(c for c in result if c["id"] == "thumbnail_cache")
        assert thumb_cat["file_count"] == 3
        assert thumb_cat["size_bytes"] == 2048 * 3


class TestExecuteRecycleBin:
    @patch("modules.cleanup.os.path.isdir", return_value=True)
    @patch("modules.cleanup._get_recycle_bin_info")
    @patch("modules.cleanup.ctypes.windll.shell32.SHEmptyRecycleBinW")
    def test_recycle_bin_reports_freed_bytes(self, mock_empty, mock_get_info, mock_isdir):
        mock_get_info.return_value = (5 * 1024 * 1024, 10)
        
        result = execute_cleanup(["recycle_bin"])
        
        assert result["total_freed_mb"] == 5.0
