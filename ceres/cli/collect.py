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
from ceres.function.schema import HOST_INFO_SCHEMA, STRING_ARRAY
from ceres.function.util import validate_data
from ceres.manages.collect_manage import Collect


class HostCommand(BaseCommand):
    """
    Collection command support

    """

    def __init__(self):
        super().__init__()
        self._sub_command = "collect"
        self.parser = BaseCommand.subparsers.add_parser("collect")
        self._add_arguments()
        self.command_handlers = {
            'host': self.host_info_collect_handle,
            'file': self.file_content_collect_handle,
            'application': self.application_info_collect_handle,
        }

    def get_command_name(self):
        return self._sub_command

    def _add_arguments(self):
        command_group = self.parser.add_mutually_exclusive_group(required=True)
        command_group.add_argument("--host", type=str)
        command_group.add_argument("--file", type=str)
        command_group.add_argument("--application", action="store_true")

    def execute(self, args):
        """
        Command execution entry
        """
        if args.host:
            self.command_handlers["host"](args.host)
        elif args.application:
            self.command_handlers["application"]()
        elif args.file:
            self.command_handlers["file"](args.file)
        else:
            print("Please check the input parameters!")
            sys.exit(1)

    @staticmethod
    def file_content_collect_handle(arguments):
        """
        Text file reading method
        """
        result, data = validate_data(arguments, STRING_ARRAY)
        if not result:
            sys.exit(1)
        print(json.dumps(Collect.collect_file(data)))

    @staticmethod
    def host_info_collect_handle(arguments):
        """
        System information collection method
        """
        result, data = validate_data(arguments, HOST_INFO_SCHEMA)
        if not result:
            sys.exit(1)
        print(json.dumps(Collect().get_host_info(data)))

    @staticmethod
    def application_info_collect_handle():
        """
        Get the running applications in the target list
        """
        print(json.dumps(Collect.get_application_info()))
