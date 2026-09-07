import sys
import unittest
from unittest import TestCase
from unittest.mock import patch

from sysinv.software import detect_software


# Test assertations for detect_software function
class TestDetectSoftware(TestCase):
    # Patches the run_command function in when detect_software is called
    @patch("sysinv.software.run_command")
    def test_linux_detect_software(self, mock_run_command):
        # Mocks dict of success and data returned from command
        mock_run_command.return_value = {
            "success": True,
            "data_or_reason": "adduser\t3.153ubuntu1\tUbuntu Developers <ubuntu-devel-discuss@lists.ubuntu.com>\nadwaita-icon-theme\t50.0-1\tUbuntu Developers <ubuntu-devel-discuss@lists.ubuntu.com>\n",
        }
        result: dict = detect_software("Linux")
        expected: dict = {
            "success": True,
            "data_or_reason": [
                {
                    "name": "adduser",
                    "version": "3.153ubuntu1",
                    "publisher": "Ubuntu Developers <ubuntu-devel-discuss@lists.ubuntu.com>",
                },
                {
                    "name": "adwaita-icon-theme",
                    "version": "50.0-1",
                    "publisher": "Ubuntu Developers <ubuntu-devel-discuss@lists.ubuntu.com>",
                },
            ],
        }
        self.assertEqual(result, expected)

    # Patches the run_command function in when detect_software is called
    @patch("sysinv.software.run_command")
    def test_mac_detect_software(self, mock_run_command):
        # Mocks dict of success and data returned from command
        mock_run_command.return_value = {
            "success": True,
            "data_or_reason": '{\n  "SPApplicationsDataType" : [\n    {\n      "_name" : "App Store",\n      "arch_kind" : "arch_arm_i64",\n      "lastModified" : "2026-08-13T02:51:55Z",\n      "obtained_from" : "apple",\n      "path" : "/System/Applications/App Store.app",\n      "signed_by" : [\n        "macOS Software Signing",\n        "Apple Code Signing Certification Authority",\n        "Apple Root CA"\n      ],\n      "version" : "3.0"\n    },\n    {\n      "_name" : "Python",\n      "arch_kind" : "arch_arm_i64",\n      "lastModified" : "2026-08-31T11:17:37Z",\n      "obtained_from" : "identified_developer",\n      "path" : "/Library/Frameworks/Python.framework/Versions/3.14/Resources/Python.app",\n      "signed_by" : [\n        "Developer ID Application: Python Software Foundation (BMM5U3QVKW)",\n        "Developer ID Certification Authority",\n        "Apple Root CA"\n      ],\n      "version" : "3.14.7"\n    }\n  ]\n}',
        }
        result: dict = detect_software("Darwin")
        expected: dict = {
            "success": True,
            "data_or_reason": [
                {"name": "App Store", "version": "3.0", "publisher": "apple"},
                {
                    "name": "Python",
                    "version": "3.14.7",
                    "publisher": "identified_developer",
                },
            ],
        }
        self.assertEqual(result, expected)

    @unittest.skipUnless(sys.platform.startswith("win"), "Requires Windows")
    @patch("winreg.CloseKey")
    @patch("winreg.EnumKey")
    @patch("winreg.QueryValueEx")
    @patch("winreg.OpenKey")
    def test_windows_detect_software(
        self, mock_OpenKey, mock_QueryValueEx, mock_EnumKey, mock_CloseKey
    ):
        def fake_OpenKey(hive, subkey_name):
            return subkey_name

        def fake_QueryValueEx(handle, field):
            data = {
                "7-Zip": {
                    "DisplayName": "7-Zip 26.02 (x64)",
                    "DisplayVersion": "26.02",
                    "Publisher": "Igor Pavlov",
                },
                "AddressBook": {
                    "DisplayName": "Missing Name",
                    "DisplayVersion": "Missing Version",
                    "Publisher": "Missing Publisher",
                },
            }
            return (data[handle][field], 1)

        def fake_CloseKey(handle):
            return None

        # Mocks dict of success and data returned from command
        mock_OpenKey.side_effect = fake_OpenKey
        mock_CloseKey.side_effect = fake_CloseKey
        mock_EnumKey.side_effect = ["7-Zip", "AddressBook", OSError()]
        mock_QueryValueEx.side_effect = fake_QueryValueEx
        result: dict = detect_software("Windows")
        expected: dict = {
            "success": True,
            "data_or_reason": [
                {
                    "name": "7-Zip 26.02 (x64)",
                    "version": "26.02",
                    "publisher": "Igor Pavlov",
                },
                {
                    "name": "Missing Name",
                    "version": "Missing Version",
                    "publisher": "Missing Publisher",
                },
            ],
        }
        self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
