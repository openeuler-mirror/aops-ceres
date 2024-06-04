import unittest
import json
from unittest import mock
from io import StringIO
from ceres.cli.plugin import PluginCommand
from ceres.manages.collect_manage import Collect
from ceres.manages.plugin_manage import Plugin, GalaGopher
from ceres.function.status import SUCCESS


class TestPluginCommand(unittest.TestCase):
    def setUp(self):
        self.command = PluginCommand()

    @mock.patch("sys.exit")
    def test_plugin_start_handle_should_return_system_exit_when_input_plugin_not_in_supported_plugins(self, mock_exit):
        # Simulate command line parameters: "--start gopher"
        namespace = self.command.parser.parse_args(["--start", "gopher"])
        self.command.execute(namespace)
        mock_exit.assert_called_once_with(1)

    @mock.patch('sys.stdout', new_callable=StringIO)
    @mock.patch.object(Plugin, "start_service")
    def test_plugin_start_handle_should_return_start_succeed_when_plugin_in_supported_plugins(
        self, mock_start_plugin, mock_stdout
    ):
        mock_start_plugin.return_value = SUCCESS
        # Simulate command line parameters: "--start gala-gopher"
        namespace = self.command.parser.parse_args(["--start", "gala-gopher"])
        self.command.execute(namespace)
        output = mock_stdout.getvalue().strip()
        self.assertEqual(output, SUCCESS)

    @mock.patch("sys.exit")
    def test_plugin_stop_handle_should_return_system_exit_when_input_plugin_not_in_supported_plugins(self, mock_exit):
        # Simulate command line parameters: "--start gopher"
        namespace = self.command.parser.parse_args(["--stop", "gopher"])
        self.command.execute(namespace)
        mock_exit.assert_called_once_with(1)

    @mock.patch('sys.stdout', new_callable=StringIO)
    @mock.patch.object(Plugin, "stop_service")
    def test_plugin_stop_handle_should_return_start_succeed_when_plugin_in_supported_plugins(
        self, mock_stop_plugin, mock_stdout
    ):
        mock_stop_plugin.return_value = SUCCESS
        # Simulate command line parameters: "--start gala-gopher"
        namespace = self.command.parser.parse_args(["--stop", "gala-gopher"])
        self.command.execute(namespace)
        output = mock_stdout.getvalue().strip()
        self.assertEqual(output, SUCCESS)

    @mock.patch('sys.stdout', new_callable=StringIO)
    @mock.patch.object(GalaGopher, "change_items_status")
    def test_change_collect_items_handle_should_return_change_result_when_entered_data_is_correct(
        self, mock_change_items, mock_stdout
    ):
        mock_modify_result = '{"resp": {"plugin1": {"success": [], "failure": ["item1", "item2"]}}}'
        mock_change_items.return_value = mock_modify_result
        # Simulate command line parameters: "--change-collect-items {"plugin1": {"item1": "on", "item2": "off"}}"
        namespace = self.command.parser.parse_args(
            ["--change-collect-items", '{"plugin1": {"item1": "on", "item2": "off"}}']
        )
        self.command.execute(namespace)
        output = mock_stdout.getvalue().strip()
        self.assertEqual(output, mock_modify_result)

    @mock.patch('sys.exit')
    def test_change_collect_items_handle_should_return_system_exit_when_entered_data_is_incorrect(self, mock_exit):
        # Simulate command line parameters: "--change-collect-items {"plugin1": {"item1": "on", "item2": "off"}}"
        namespace = self.command.parser.parse_args(
            ["--change-collect-items", '{"plugin1": {"item1": "error", "item2": "off"}}']
        )
        self.command.execute(namespace)
        mock_exit.assert_called_once_with(1)

    @mock.patch('sys.stdout', new_callable=StringIO)
    @mock.patch.object(Collect, "get_plugin_info")
    def test_plugin_info_handle_should_return_info_when_all_is_ok(self, mock_query_plugin_info, mock_stdout):
        mock_plugin_info = [
            {
                "plugin_name": "gala-gopher",
                "collect_items": [],
                "status": "inactive",
                "resource": [
                    {"name": "cpu", "current_value": None, "limit_value": None},
                    {"name": "memory", "current_value": None, "limit_value": None},
                ],
                "is_installed": True,
            }
        ]
        mock_query_plugin_info.return_value = mock_plugin_info
        # Simulate command line parameters: "--info"
        namespace = self.command.parser.parse_args(["--info"])
        self.command.execute(namespace)
        output = mock_stdout.getvalue().strip()
        self.assertEqual(output, json.dumps(mock_plugin_info))


if __name__ == '__main__':
    unittest.main()
