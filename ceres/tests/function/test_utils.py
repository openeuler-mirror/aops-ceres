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

import responses

from ceres.function.register import register
from ceres.function.status import SUCCESS, PARAM_ERROR


class TestUtils(unittest.TestCase):

    @responses.activate
    def test_register_should_return_200_when_input_correct(self):
        input_data = {
            "web_username": "admin",
            "web_password": "changeme",
            "host_name": "host01",
            "host_group_name": "2333",
            "management": False,
            "manager_ip": "127.0.0.1",
            "manager_port": "11111",
            "client_port": "12000"
        }
        responses.add(responses.POST,
                      'http://127.0.0.1:11111/manage/host/add',
                      json={"token": "hdahdahiudahud", "code": SUCCESS},
                      status=SUCCESS,
                      content_type='application/json'
                      )
        data = register(input_data)
        self.assertEqual(SUCCESS, data)

    def test_register_should_return_param_error_when_input_web_username_is_null(self):
        input_data = {
            "web_password": "changeme",
            "host_name": "host01",
            "host_group_name": "2333",
            "management": False,
            "manager_ip": "127.0.0.1",
            "manager_port": "11111"
        }
        data = register(input_data)
        self.assertEqual(PARAM_ERROR, data)

    def test_register_should_return_param_error_when_input_web_username_is_not_string(self):
        input_data = {
            "web_username": 12345,
            "web_password": "changeme",
            "host_name": "host01",
            "host_group_name": "2333",
            "management": False,
            "manager_ip": "127.0.0.1",
            "manager_port": "11111"
        }
        data = register(input_data)
        self.assertEqual(PARAM_ERROR, data)

    def test_register_should_return_param_error_when_input_web_password_is_null(self):
        input_data = {
            "web_username": "admin",
            "host_name": "host01",
            "host_group_name": "2333",
            "management": False,
            "manager_ip": "127.0.0.1",
            "manager_port": "11111"
        }
        data = register(input_data)
        self.assertEqual(PARAM_ERROR, data)

    def test_register_should_return_param_error_when_input_web_password_is_not_string(self):
        input_data = {
            "web_username": "admin",
            "web_password": 123456,
            "host_name": "host01",
            "host_group_name": "2333",
            "management": False,
            "manager_ip": "127.0.0.1",
            "manager_port": "11111"
        }
        data = register(input_data)
        self.assertEqual(PARAM_ERROR, data)

    def test_register_should_return_param_error_when_input_host_name_is_null(self):
        input_data = {
            "web_username": "admin",
            "web_password": "changeme",
            "host_group_name": "2333",
            "management": False,
            "manager_ip": "127.0.0.1",
            "manager_port": "11111"
        }
        data = register(input_data)
        self.assertEqual(PARAM_ERROR, data)

    def test_register_should_return_param_error_when_input_host_name_is_not_string(self):
        input_data = {
            "web_username": "admin",
            "web_password": "changeme",
            "host_name": 12345,
            "host_group_name": "2333",
            "management": False,
            "manager_ip": "127.0.0.1",
            "manager_port": "11111"
        }
        data = register(input_data)
        self.assertEqual(PARAM_ERROR, data)

    def test_register_should_return_param_error_when_input_host_group_name_is_null(self):
        input_data = {
            "web_username": "admin",
            "web_password": "changeme",
            "host_name": "host01",
            "management": False,
            "manager_ip": "127.0.0.1",
            "manager_port": "11111"
        }
        data = register(input_data)
        self.assertEqual(PARAM_ERROR, data)

    def test_register_should_return_param_error_when_input_host_group_name_is_not_string(self):
        input_data = {
            "web_username": "admin",
            "web_password": "changeme",
            "host_name": "host01",
            "host_group_name": True,
            "management": False,
            "manager_ip": "127.0.0.1",
            "manager_port": "11111"
        }
        data = register(input_data)
        self.assertEqual(PARAM_ERROR, data)

    def test_register_should_return_param_error_when_input_management_is_null(self):
        input_data = {
            "web_username": "admin",
            "web_password": "changeme",
            "host_name": "host01",
            "host_group_name": "2333",
            "manager_ip": "127.0.0.1",
            "manager_port": "11111"
        }
        data = register(input_data)
        self.assertEqual(PARAM_ERROR, data)

    def test_register_should_return_param_error_when_input_management_is_not_boolean(self):
        input_data = {
            "web_username": "admin",
            "web_password": "changeme",
            "host_name": "host01",
            "host_group_name": "2333",
            "management": "string",
            "manager_ip": "127.0.0.1",
            "manager_port": "11111"
        }
        data = register(input_data)
        self.assertEqual(PARAM_ERROR, data)

    def test_register_should_return_param_error_when_input_manager_ip_is_null(self):
        input_data = {
            "web_username": "admin",
            "web_password": "changeme",
            "host_name": "host01",
            "host_group_name": "2333",
            "management": False,
            "manager_port": "11111"
        }
        data = register(input_data)
        self.assertEqual(PARAM_ERROR, data)

    def test_register_should_return_param_error_when_input_manager_ip_is_not_string(self):
        input_data = {
            "web_username": "admin",
            "web_password": "changeme",
            "host_name": "host01",
            "host_group_name": "2333",
            "management": False,
            "manager_port": "11111"
        }
        data = register(input_data)
        self.assertEqual(PARAM_ERROR, data)

    def test_register_should_return_param_error_when_input_manager_port_is_null(self):
        input_data = {
            "web_username": "admin",
            "web_password": "changeme",
            "host_name": "host01",
            "host_group_name": "2333",
            "management": False,
            "manager_ip": "127.0.0.1",
        }
        data = register(input_data)
        self.assertEqual(PARAM_ERROR, data)

    def test_register_should_return_param_error_when_input_manager_port_is_not_string(self):
        input_data = {
            "web_username": "admin",
            "web_password": "changeme",
            "host_name": "host01",
            "host_group_name": "2333",
            "management": False,
            "manager_ip": "127.0.0.1",
            "manager_port": 80
        }
        data = register(input_data)
        self.assertEqual(PARAM_ERROR, data)

    def test_register_should_return_param_error_when_input_client_port_is_not_string(self):
        input_data = {
            "web_username": "admin",
            "web_password": "changeme",
            "host_name": "host01",
            "host_group_name": "2333",
            "management": False,
            "manager_ip": "127.0.0.1",
            "manager_port": "11111",
            "client_port": 11000
        }
        data = register(input_data)
        self.assertEqual(data, PARAM_ERROR)

    @responses.activate
    def test_register_should_return_success_when_input_with_no_client_port(self):
        responses.add(responses.POST,
                      'http://127.0.0.1:11111/manage/host/add',
                      json={"token": "hdahdahiudahud", "code": SUCCESS},
                      status=SUCCESS,
                      content_type='application/json'
                      )
        input_data = {
            "web_username": "admin",
            "web_password": "changeme",
            "host_name": "host01",
            "host_group_name": "2333",
            "management": False,
            "manager_ip": "127.0.0.1",
            "manager_port": "11111",
        }
        data = register(input_data)
        self.assertEqual(SUCCESS, data)
