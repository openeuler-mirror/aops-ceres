#!/usr/bin/python3
# ******************************************************************************
# Copyright (c) Huawei Technologies Co., Ltd. 2022-2022. All rights reserved.
# licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN 'AS IS' BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# ******************************************************************************/
import unittest

from ceres.function.register import register, register_info_to_dict
from ceres.function.status import PARAM_ERROR


class TestRegister(unittest.TestCase):
    def test_register_should_return_param_error_when_input_username_is_null(self):
        input_data = {
            "password": "changeme",
            "host_name": "host01",
            "host_group_name": "2333",
            "management": False,
            "zeus_ip": "127.0.0.1",
            "zeus_port": "11111",
        }
        data = register(input_data)
        self.assertEqual(PARAM_ERROR, data)

    def test_register_should_return_param_error_when_input_username_is_not_string(self):
        input_data = {
            "username": 12345,
            "password": "changeme",
            "host_name": "host01",
            "host_group_name": "2333",
            "management": False,
            "zeus_ip": "127.0.0.1",
            "zeus_port": "11111",
        }
        data = register(input_data)
        self.assertEqual(PARAM_ERROR, data)

    def test_register_should_return_param_error_when_input_password_is_null(self):
        input_data = {
            "username": "admin",
            "host_name": "host01",
            "host_group_name": "2333",
            "management": False,
            "zeus_ip": "127.0.0.1",
            "zeus_port": "11111",
        }
        data = register(input_data)
        self.assertEqual(PARAM_ERROR, data)

    def test_register_should_return_param_error_when_input_password_is_not_string(self):
        input_data = {
            "username": "admin",
            "password": 123456,
            "host_name": "host01",
            "host_group_name": "2333",
            "management": False,
            "zeus_ip": "127.0.0.1",
            "zeus_port": "11111",
        }
        data = register(input_data)
        self.assertEqual(PARAM_ERROR, data)

    def test_register_should_return_param_error_when_input_host_name_is_null(self):
        input_data = {
            "username": "admin",
            "password": "changeme",
            "host_group_name": "2333",
            "management": False,
            "zeus_ip": "127.0.0.1",
            "zeus_port": "11111",
        }
        data = register(input_data)
        self.assertEqual(PARAM_ERROR, data)

    def test_register_should_return_param_error_when_input_host_name_is_not_string(self):
        input_data = {
            "username": "admin",
            "password": "changeme",
            "host_name": 12345,
            "host_group_name": "2333",
            "management": False,
            "zeus_ip": "127.0.0.1",
            "zeus_port": "11111",
        }
        data = register(input_data)
        self.assertEqual(PARAM_ERROR, data)

    def test_register_should_return_param_error_when_input_host_group_name_is_null(self):
        input_data = {
            "username": "admin",
            "password": "changeme",
            "host_name": "host01",
            "management": False,
            "zeus_ip": "127.0.0.1",
            "zeus_port": "11111",
        }
        data = register(input_data)
        self.assertEqual(PARAM_ERROR, data)

    def test_register_should_return_param_error_when_input_host_group_name_is_not_string(self):
        input_data = {
            "username": "admin",
            "password": "changeme",
            "host_name": "host01",
            "host_group_name": True,
            "management": False,
            "zeus_ip": "127.0.0.1",
            "zeus_port": "11111",
        }
        data = register(input_data)
        self.assertEqual(PARAM_ERROR, data)

    def test_register_should_return_param_error_when_input_management_is_null(self):
        input_data = {
            "username": "admin",
            "password": "changeme",
            "host_name": "host01",
            "host_group_name": "2333",
            "zeus_ip": "127.0.0.1",
            "zeus_port": "11111",
        }
        data = register(input_data)
        self.assertEqual(PARAM_ERROR, data)

    def test_register_should_return_param_error_when_input_management_is_not_boolean(self):
        input_data = {
            "username": "admin",
            "password": "changeme",
            "host_name": "host01",
            "host_group_name": "2333",
            "management": "string",
            "zeus_ip": "127.0.0.1",
            "zeus_port": "11111",
        }
        data = register(input_data)
        self.assertEqual(PARAM_ERROR, data)

    def test_register_should_return_param_error_when_input_zeus_ip_is_null(self):
        input_data = {
            "username": "admin",
            "password": "changeme",
            "host_name": "host01",
            "host_group_name": "2333",
            "management": False,
            "zeus_port": "11111",
        }
        data = register(input_data)
        self.assertEqual(PARAM_ERROR, data)

    def test_register_should_return_param_error_when_input_zeus_ip_is_not_string(self):
        input_data = {
            "username": "admin",
            "password": "changeme",
            "host_name": "host01",
            "host_group_name": "2333",
            "management": False,
            "zeus_port": "11111",
        }
        data = register(input_data)
        self.assertEqual(PARAM_ERROR, data)

    def test_register_should_return_param_error_when_input_zeus_port_is_null(self):
        input_data = {
            "web_username": "admin",
            "web_password": "changeme",
            "host_name": "host01",
            "host_group_name": "2333",
            "management": False,
            "zeus_ip": "127.0.0.1",
        }
        data = register(input_data)
        self.assertEqual(PARAM_ERROR, data)

    def test_register_should_return_param_error_when_input_zeus_port_is_not_string(self):
        input_data = {
            "username": "admin",
            "password": "changeme",
            "host_name": "host01",
            "host_group_name": "2333",
            "management": False,
            "zeus_ip": "127.0.0.1",
            "zeus_port": 80,
        }
        data = register(input_data)
        self.assertEqual(PARAM_ERROR, data)

    def test_register_should_return_param_error_when_input_ceres_port_is_not_string(self):
        input_data = {
            "username": "admin",
            "password": "changeme",
            "host_name": "host01",
            "host_group_name": "2333",
            "management": False,
            "zeus_ip": "127.0.0.1",
            "zeus_port": "11111",
            "ceres_port": 11000,
        }
        data = register(input_data)
        self.assertEqual(data, PARAM_ERROR)

    def test_register_info_to_dict_should_return_dict_info_when_input_is_correct(self):
        mock_string = '{"mock": "mock"}'
        res = register_info_to_dict(mock_string)
        self.assertEqual({'mock': 'mock'}, res)

    def test_register_info_to_dict_should_return_empty_dict_when_input_is_incorrect(self):
        mock_string = '["mock"]'
        res = register_info_to_dict(mock_string)
        self.assertEqual({}, res)

    def test_register_info_to_dict_should_return_empty_dict_when_input_is_not_json_string(self):
        mock_string = '{mock'
        res = register_info_to_dict(mock_string)
        self.assertEqual({}, res)
