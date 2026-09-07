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
            "data_or_reason": '{\n  "SPApplicationsDataType" : [\n    {\n      "_name" : "App Store",\n      "arch_kind" : "arch_arm_i64",\n      "lastModified" : "2026-08-13T02:51:55Z",\n      "obtained_from" : "apple",\n      "path" : "/System/Applications/App Store.app",\n      "signed_by" : [\n        "macOS Software Signing",\n        "Apple Code Signing Certification Authority",\n        "Apple Root CA"\n      ],\n      "version" : "3.0"\n    },\n    {\n      "_name" : "Apps",\n      "arch_kind" : "arch_arm_i64",\n      "lastModified" : "2026-08-13T02:51:55Z",\n      "obtained_from" : "apple",\n      "path" : "/System/Applications/Apps.app",\n      "signed_by" : [\n        "macOS Software Signing",\n        "Apple Code Signing Certification Authority",\n        "Apple Root CA"\n      ],\n      "version" : "1.0"\n    }',
        }
        result: dict = detect_software("Darwin")
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


if __name__ == "__main__":
    unittest.main()
