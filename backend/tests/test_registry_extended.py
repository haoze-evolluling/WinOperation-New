import os
import sys
import pytest
from unittest.mock import patch, MagicMock, call

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "backend"))

from utils.registry import list_subkeys, tree_subkeys
from modules.registry import list_registry, tree_registry, batch_read_registry, batch_write_registry
import win32api


class TestListSubkeys:
    @patch("utils.registry.win32api.RegOpenKeyEx")
    @patch("utils.registry.win32api.RegEnumKeyEx")
    @patch("utils.registry.win32api.RegEnumValue")
    @patch("utils.registry.win32api.RegCloseKey")
    def test_list_subkeys_returns_subkeys_and_values(
        self, mock_close, mock_enum_value, mock_enum_key, mock_open
    ):
        mock_key = MagicMock()
        mock_open.return_value = mock_key
        mock_enum_key.side_effect = [("SubKey1", "", 0), ("SubKey2", "", 0), win32api.error("no more")]
        mock_enum_value.side_effect = [("ValName", "test_data", 1), win32api.error("no more")]

        result = list_subkeys("HKCU\\Software")

        mock_open.assert_called_once()
        mock_close.assert_called_once_with(mock_key)
        assert result["subkeys"] == ["SubKey1", "SubKey2"]
        assert len(result["values"]) == 1
        assert result["values"][0]["name"] == "ValName"


class TestTreeSubkeys:
    @patch("utils.registry.list_subkeys")
    def test_tree_subkeys_depth_1_no_children(self, mock_list):
        mock_list.return_value = {
            "subkeys": ["Microsoft"],
            "values": [],
        }

        result = tree_subkeys("HKCU\\Software", max_depth=1)

        assert result["path"] == "HKCU\\Software"
        assert len(result["subkeys"]) == 1
        assert result["subkeys"][0]["subkeys"] == []
        assert result["values_count"] == 0

    @patch("utils.registry.list_subkeys")
    def test_tree_subkeys_depth_0_returns_no_subkeys(self, mock_list):
        mock_list.return_value = {
            "subkeys": ["Microsoft"],
            "values": [],
        }

        result = tree_subkeys("HKCU\\Software", max_depth=0)

        assert result["subkeys"] == []

    @patch("utils.registry.list_subkeys")
    def test_tree_subkeys_error_returns_error_status(self, mock_list):
        mock_list.side_effect = Exception("access denied")

        result = tree_registry("HKCU\\Software\\Bad", max_depth=2)

        assert result["status"] == "error"


class TestBatchReadRegistry:
    def test_batch_read_multiple_entries(self):
        entries = [
            {"path": "HKCU\\Software\\Test", "key": "Val1"},
            {"path": "HKCU\\Software\\Test", "key": "Val2"},
            {"path": "HKCU\\Software\\Test", "key": "Val3"},
        ]

        with patch("modules.registry.read_key") as mock_read:
            mock_read.side_effect = [
                ("data1", 1),
                ("data2", 2),
                ("data3", 1),
            ]
            result = batch_read_registry(entries)

        assert "results" in result
        assert len(result["results"]) == 3
        for item in result["results"]:
            assert "path" in item
            assert "key" in item
            assert "value" in item
            assert "type" in item
            assert "status" in item


class TestBatchWriteRegistry:
    def test_batch_write_returns_status(self):
        entries = [
            {"path": "HKCU\\Software\\Test", "key": "Val1", "value": "x", "type": "REG_SZ"},
            {"path": "HKCU\\Software\\Test", "key": "Val2", "value": "y", "type": "REG_SZ"},
        ]

        with patch("modules.registry.write_key") as mock_write:
            result = batch_write_registry(entries)

        assert "results" in result
        assert len(result["results"]) == 2
        for item in result["results"]:
            assert item["status"] == "ok"
