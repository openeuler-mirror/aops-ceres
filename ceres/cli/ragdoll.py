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
from ceres.function.schema import CONF_SYNC_SCHEMA
from ceres.function.status import StatusCode
from ceres.function.util import validate_data
from ceres.manages.list_file_manage import ListFileManage
from ceres.manages.sync_manage import SyncManage


class RagdollCommand(BaseCommand):
    def __init__(self):
        super().__init__()
        self._sub_command = "ragdoll"
        self.parser = BaseCommand.subparsers.add_parser("ragdoll")
        self._add_arguments()
        self.command_handlers = {
            'sync': self.sync_config_handle,
            'list': self.query_file_list_handle,
        }

    def get_command_name(self):
        return self._sub_command

    def _add_arguments(self):
        self.parser.add_argument("--sync", type=str, required=False)
        self.parser.add_argument("--list", type=str, required=False)

    def execute(self, namespace):
        """
        Command execution entry
        """
        data = vars(namespace)
        if not data.get("sync") and not data.get("list"):
            print("No command provided. Please enter a valid command.", file=sys.stderr)
            sys.exit(1)

        for option, arguments in data.items():
            if option in self.command_handlers and arguments:
                self.command_handlers[option](arguments)

    @staticmethod
    def sync_config_handle(arguments):
        """
        Write conf into file

        Args:
            config(dict): filepath and content for file sync,  only. eg:
            {
                "file_path" = "/tmp/test"
                "content" = "contents for this file"
            }

        Returns:
            None
        """
        result, data = validate_data(arguments, CONF_SYNC_SCHEMA)
        if not result:
            sys.exit(1)
        res = StatusCode.make_response_body(SyncManage.sync_contents_to_conf(data))
        print(json.dumps(res))

    @staticmethod
    def query_file_list_handle(directory_path):
        """
        Read the file list from the specified directory

        Args:
            directory_path: the path of directory

        """
        status, response = ListFileManage.list_file(directory_path)
        res = StatusCode.make_response_body((status, response))
        print(json.dumps(res))
