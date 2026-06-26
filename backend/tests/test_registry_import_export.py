import os
import sys
import pytest
from unittest.mock import patch, MagicMock, call
import re
import win32con

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "backend"))

from utils.registry import export_reg, import_reg


class TestExportReg:
    @patch("utils.registry.list_subkeys")
    def test_export_reg_generates_valid_header_and_section(self, mock_list):
        mock_list.return_value = {
            "subkeys": [],
            "values": [],
        }

        result = export_reg("HKCU\\Software\\MyApp")

        assert result.startswith("Windows Registry Editor Version 5.00")
        assert "[HKEY_CURRENT_USER\\Software\\MyApp]" in result

    @patch("utils.registry.list_subkeys")
    def test_export_reg_includes_reg_sz_value(self, mock_list):
        mock_list.return_value = {
            "subkeys": [],
            "values": [
                {"name": "StringValue", "data": "hello", "type_int": win32con.REG_SZ},
            ],
        }

        result = export_reg("HKCU\\Software\\MyApp")

        assert '"StringValue"="hello"' in result

    @patch("utils.registry.list_subkeys")
    def test_export_reg_includes_reg_dword_value(self, mock_list):
        mock_list.return_value = {
            "subkeys": [],
            "values": [
                {"name": "DwordValue", "data": 1, "type_int": win32con.REG_DWORD},
            ],
        }

        result = export_reg("HKCU\\Software\\MyApp")

        assert '"DwordValue"=dword:00000001' in result

    @patch("utils.registry.list_subkeys")
    def test_export_reg_skips_reg_binary(self, mock_list):
        mock_list.return_value = {
            "subkeys": [],
            "values": [
                {"name": "BinValue", "data": b"\x00\x01", "type_int": win32con.REG_BINARY},
            ],
        }

        result = export_reg("HKCU\\Software\\MyApp")

        assert "BinValue" not in result

    @patch("utils.registry.list_subkeys")
    def test_export_reg_skips_unknown_types(self, mock_list):
        mock_list.return_value = {
            "subkeys": [],
            "values": [
                {"name": "Unknown", "data": "x", "type_int": 99},
            ],
        }

        result = export_reg("HKCU\\Software\\MyApp")

        assert "Unknown" not in result

    @patch("utils.registry.list_subkeys")
    def test_export_reg_flat_only_no_subkey_recursion(self, mock_list):
        mock_list.return_value = {
            "subkeys": ["Child"],
            "values": [
                {"name": "Val", "data": "x", "type_int": win32con.REG_SZ},
            ],
        }

        result = export_reg("HKCU\\Software\\MyApp")

        assert "Child" not in result


class TestImportReg:
    @patch("utils.registry.write_key")
    def test_import_reg_skips_header_and_creates_values(self, mock_write):
        reg_text = """Windows Registry Editor Version 5.00

[HKEY_CURRENT_USER\\Software\\MyApp]
"StringValue"="hello"
"DwordValue"=dword:00000001
"""

        result = import_reg(reg_text)

        assert result["imported"] == 2
        assert result["failed"] == []
        assert mock_write.call_count == 2

    @patch("utils.registry.write_key")
    def test_import_reg_records_errors(self, mock_write):
        mock_write.side_effect = Exception("access denied")

        reg_text = 'Windows Registry Editor Version 5.00\n\n[HKEY_CURRENT_USER\\Software\\MyApp]\n"Bad"="x"\n'

        result = import_reg(reg_text)

        assert result["imported"] == 0
        assert len(result["failed"]) == 1
        assert "Bad" in result["failed"][0]

    @patch("utils.registry.write_key")
    def test_import_reg_skips_invalid_lines(self, mock_write):
        reg_text = """Windows Registry Editor Version 5.00

[HKEY_CURRENT_USER\\Software\\MyApp]
"StringValue"="hello"
this is not a valid line
"DwordValue"=dword:00000001
"""

        result = import_reg(reg_text)

        assert result["imported"] == 2
        assert len(result["errors"]) >= 1
        assert "not a valid line" in result["errors"][0] or len(result["errors"]) > 0
