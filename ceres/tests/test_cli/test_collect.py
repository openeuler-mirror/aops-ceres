import unittest
import json
from unittest import mock
from io import StringIO
from ceres.cli.collect import HostCommand
from ceres.manages.collect_manage import Collect
from ceres.manages.plugin_manage import Plugin, GalaGopher
from ceres.function.status import SUCCESS


class TestPluginCommand(unittest.TestCase):
    def setUp(self):
        self.command = HostCommand()

    @mock.patch("sys.exit")
    def test_collect_host_info_handle_should_return_system_exit_when_input_info_type_is_not_supported(self, mock_exit):
        # Simulate command line parameters: "--host <args>"
        namespace = self.command.parser.parse_args(["--host", "[2]"])
        self.command.execute(namespace)
        mock_exit.assert_called_once_with(1)

    @mock.patch('sys.stdout', new_callable=StringIO)
    @mock.patch.object(Collect, "get_host_info")
    def test_collect_host_info_handle_should_return_system_exit_when_input_info_type_is_supported(
        self, mock_host_info, mock_stdout
    ):
        host_info = {
            "cpu": {
                "architecture": "x86_64",
                "core_count": "4",
                "model_name": "Intel(R) N100",
                "vendor_id": "GenuineIntel",
                "l1d_cache": "128 KiB (4 instances)",
                "l1i_cache": "256 KiB (4 instances)",
                "l2_cache": "8 MiB (4 instances)",
                "l3_cache": "24 MiB (4 instances)",
            },
            "disk": [{"model": "VBOX HARDDISK", "capacity": "40.0 GB"}],
            "memory": {"size": "11G", "total": None, "info": []},
            "os": {
                "os_version": "openEuler-22.03-LTS",
                "bios_version": "VirtualBox",
                "kernel": "5.10.0-60.106.0.133",
            },
        }
        mock_host_info.return_value = host_info
        # Simulate command line parameters: "--host <args>"
        namespace = self.command.parser.parse_args(["--host", "[]"])
        self.command.execute(namespace)
        output = mock_stdout.getvalue().strip()
        self.assertEqual(output, json.dumps(host_info))

    @mock.patch("sys.exit")
    def test_collect_file_content_should_return_system_exit_when_input_empty_string(self, mock_exit):
        # Simulate command line parameters: "--file <args>"
        namespace = self.command.parser.parse_args(["--file", '[]'])
        self.command.execute(namespace)
        mock_exit.assert_called_once_with(1)

    @mock.patch('sys.stdout', new_callable=StringIO)
    @mock.patch.object(Collect, "collect_file")
    def test_collect_file_content_should_return_file_content_when_input_correct_text_file_path(
        self, mock_file_collect, mock_stdout
    ):
        file_info = {"success_files": [], "fail_files": ["/tmp/97sdad8a7dadsa"], "infos": []}
        # Simulate command line parameters: "--file <args>"
        mock_file_collect.return_value = file_info
        namespace = self.command.parser.parse_args(["--file", '["/tmp/97sdad8a7dadsa"]'])
        self.command.execute(namespace)
        output = mock_stdout.getvalue().strip()
        self.assertEqual(output, json.dumps(file_info))

    @mock.patch('sys.stdout', new_callable=StringIO)
    @mock.patch.object(Collect, "get_application_info")
    def test_collect_running_applications_handle_should_return_running_apps_when_all_is_correct(
        self, mock_running_apps, mock_stdout
    ):
        mock_running_apps.return_value = ["mysql"]
        # Simulate command line parameters: "--application"
        namespace = self.command.parser.parse_args(["--application"])
        self.command.execute(namespace)
        output = mock_stdout.getvalue().strip()
        self.assertEqual(output, '["mysql"]')


if __name__ == '__main__':
    unittest.main()
