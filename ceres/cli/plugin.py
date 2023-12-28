#!/usr/bin/python3
# ******************************************************************************
# Copyright (c) Huawei Technologies Co., Ltd. 2024-2024. All rights reserved.
# licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN 'AS IS' BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# ******************************************************************************/
import json
import sys

from ceres.cli.base import BaseCommand
from ceres.conf.constant import INSTALLABLE_PLUGIN, PLUGIN_WITH_CLASS
from ceres.function.log import LOGGER
from ceres.function.schema import CHANGE_COLLECT_ITEMS_SCHEMA
from ceres.function.util import plugin_status_judge, validate_data
from ceres.manages import plugin_manage
from ceres.manages.collect_manage import Collect


class PluginCommand(BaseCommand):
    """
    Plugin management command support
    """

    def __init__(self):
        super().__init__()
        self._sub_command = "plugin"
        self.parser = BaseCommand.subparsers.add_parser("plugin")
        self._add_arguments()
        self.command_handlers = {
            "start": self.plugin_start_handle,
            "stop": self.plugin_stop_handle,
            "change_collect_items": self.change_collect_items_handle,
            "info": self.plugin_info_handle,
        }

    def get_command_name(self):
        return self._sub_command

    def _add_arguments(self):
        cmd_group = self.parser.add_mutually_exclusive_group(required=False)
        cmd_group.add_argument("--start", type=str)
        cmd_group.add_argument("--stop", type=str)
        self.parser.add_argument('--change-collect-items', type=str)
        self.parser.add_argument('--info', action="store_true")

    def execute(self, namespace):
        """
        Command execution entry
        """
        for option, arguments in vars(namespace).items():
            if option in self.command_handlers and arguments:
                self.command_handlers[option](arguments)

    @staticmethod
    def plugin_start_handle(arguments):
        """
        start plugin method
        """
        if arguments not in INSTALLABLE_PLUGIN:
            LOGGER.error("Unsupported plugin, please check and try again")
            sys.exit(1)
        print(plugin_manage.Plugin(arguments).start_service())

    @staticmethod
    def plugin_stop_handle(arguments):
        """
        stop plugin method
        """
        if arguments not in INSTALLABLE_PLUGIN:
            LOGGER.error("Unsupported plugin, please check and try again")
            sys.exit(1)
        print(plugin_manage.Plugin(arguments).stop_service())

    def change_collect_items_handle(self, arguments):
        """
        Modify collection indicators in collection plugins
        """
        result, data = validate_data(arguments, CHANGE_COLLECT_ITEMS_SCHEMA)
        if not result:
            sys.exit(1)
        print(json.dumps(self._change_collect_items(data)))

    @staticmethod
    def _change_collect_items(collect_items_status: dict) -> dict:
        """
        change collect items about plugin

        Args:
            collect_items_status(dict): A dict which contains collect items and its status.
            e.g
                {
                    "gala-gopher": {
                        "redis": "on",
                        "system_inode": "on",
                        "tcp": "on",
                        "haproxy": "auto",
                        "lvs": "auto"
                    }
                }

        Returns:
            Response which contains update result or error info
        """

        def generate_failed_result(plugin_name: str) -> dict:
            """
            generate plugin items change result

            Returns:
                dict: e.g
                    {"success": [], "failure":[items1, items2, ...]}
            """
            return {'success': [], 'failure': list(collect_items_status.get(plugin_name).keys())}

        res = {}
        for plugin_name in collect_items_status.keys():
            if plugin_name not in INSTALLABLE_PLUGIN:
                LOGGER.warning(f'{plugin_name} is not supported by ceres')
                res[plugin_name] = generate_failed_result(plugin_name)
                continue

            if not plugin_status_judge(plugin_name):
                LOGGER.warning(f'{plugin_name} is not installed by ceres')
                res[plugin_name] = generate_failed_result(plugin_name)
                continue

            plugin_class_name = PLUGIN_WITH_CLASS.get(plugin_name, '')
            if hasattr(plugin_manage, plugin_class_name):
                plugin = getattr(plugin_manage, plugin_class_name)
                if hasattr(plugin, 'change_items_status'):
                    res[plugin_name] = plugin().change_items_status(collect_items_status[plugin_name])
            else:
                LOGGER.warning(f'{plugin_name} is not supported by collect items')
                res[plugin_name] = generate_failed_result(plugin_name)

        return {"resp": res}

    @staticmethod
    def plugin_info_handle(args):
        """
        Query plugin information managed by ceres
        """
        print(json.dumps(Collect.get_plugin_info()))
