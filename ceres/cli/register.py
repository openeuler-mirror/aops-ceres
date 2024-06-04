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

import requests

from ceres.cli.base import BaseCommand
from ceres.function.log import LOGGER
from ceres.function.schema import REGISTER_SCHEMA
from ceres.function.status import HTTP_CONNECT_ERROR, SUCCESS, PARAM_ERROR
from ceres.function.util import validate_data
from ceres.function.status import SUCCESS
from ceres.function.util import get_dict_from_file
from ceres.manages.collect_manage import Collect


class RegisterCommand(BaseCommand):
    """
    Registration command support
    """

    def __init__(self):
        super().__init__()
        self._sub_command = "register"
        self.parser = BaseCommand.subparsers.add_parser("register")
        self._add_arguments()
        self.command_handlers = {
            'path': self.register_with_file_data,
            'f': self.register_with_file_data,
            'data': self.register_with_json_data,
            'd': self.register_with_json_data,
        }

    def get_command_name(self):
        return self._sub_command

    def _add_arguments(self):
        register_group = self.parser.add_mutually_exclusive_group(required=True)
        register_group.add_argument('-f', '--path', type=str, help="file contains data which register need")
        register_group.add_argument('-d', '--data', type=str, help="json data which register need")

    def execute(self, namespace):
        """
        Command execution entry
        """
        namespace_json = vars(namespace)
        for option, arguments in namespace_json.items():
            if option in self.command_handlers and arguments:
                self.command_handlers[option](arguments)
        return

    def register_with_json_data(self, arguments):
        """
        get args from command-line and register on manager

        Args:
            args(argparse.Namespace): args parser

        Returns:
            NoReturn
        """
        self._register(self._register_info_to_dict(arguments))

    def register_with_file_data(self, arguments):
        """
        get args from command-line and register on manager

        Args:
            args(argparse.Namespace): args parser

        Returns:
            NoReturn
        """
        self._register(get_dict_from_file(arguments))

    def _register(self, register_info):
        if register_info and self._register_handle(register_info) == SUCCESS:
            print('Register Success')
        else:
            print('Register Fail')

    @staticmethod
    def _register_info_to_dict(string: str) -> dict:
        """
        Convert json string to dictionary
        Args:
            string(str)

        Returns:
            dict
        """
        try:
            res = json.loads(string)
        except json.decoder.JSONDecodeError:
            LOGGER.error('Json conversion error, the data entered is not' ' json format.')
            res = {}
        if not isinstance(res, dict):
            res = {}
        return res

    @staticmethod
    def _register_handle(register_info: dict) -> int:
        """
        register on manager
        Args:
            register_info(dict): It contains the necessary information to register an account
            for example:
                {
                "ssh_user": "root",
                "password": "password",
                "zeus_ip": "127.0.0.1",
                "zeus_port": 11111,
                "host_name": "host_name",
                "host_group_name": "aops",
                "management": true,
                "ssh_port":22,
                "access_token": "token-string"
                }

        Returns:
            str: status code
        """
        reuslt, _ = validate_data(register_info, REGISTER_SCHEMA)
        if not reuslt:
            return PARAM_ERROR

        headers = {'content-type': 'application/json', "access_token": register_info.pop('access_token')}
        register_info['host_ip'] = Collect.get_host_ip()
        url = f'http://{register_info.pop("zeus_ip")}:{register_info.pop("zeus_port")}/manage/host/add'
        try:
            ret = requests.post(url, data=json.dumps(register_info), headers=headers, timeout=5)
        except requests.exceptions.RequestException as e:
            LOGGER.error(e)
            return HTTP_CONNECT_ERROR

        if ret.status_code != requests.codes["ok"]:
            LOGGER.warning(ret.text)
            return ret.status_code

        if ret.json().get('label') != SUCCESS:
            LOGGER.error(ret.text)
        return ret.json().get('label')
