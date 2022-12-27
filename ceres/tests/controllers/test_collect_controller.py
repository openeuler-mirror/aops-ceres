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
from __future__ import absolute_import

import json
from unittest import mock
import os

from ceres.conf.constant import HOST_COLLECT_INFO_SUPPORT
from ceres.function.status import TOKEN_ERROR, PARAM_ERROR
from ceres.manages.collect_manage import Collect
from ceres.manages.plugin_manage import GalaGopher, Plugin
from ceres.manages.resource_manage import Resource
from ceres.manages.token_manage import TokenManage
from ceres.tests import BaseTestCase


class TestCeresController(BaseTestCase):
    headers = {'Content-Type': 'application/json'}
    headers_with_token = {'Content-Type': 'application/json', 'access_token': 'hdahdahiudahud'}
    headers_with_incorrect_token = {'Content-Type': 'application/json',
                                    'access_token': '213965d8302b5246a13352680d7c8e602'}

    def setUp(self) -> None:
        TokenManage.set_value('hdahdahiudahud')

    @mock.patch.object(Collect, 'get_host_info')
    def test_get_host_info_should_return_os_info_when_input_all_is_correct(self, mock_host_info):
        mock_host_info.return_value = {
            "resp": {
                "cpu": {},
                "disk": {},
                "os": {},
                "memory": {}
            }
        }
        url = "v1/ceres/host/info"
        response = self.client.post(url, headers=self.headers_with_token, data=json.dumps(["cpu", "disk", "os", "memory"]))
        expect_info_type = HOST_COLLECT_INFO_SUPPORT
        self.assertEqual(expect_info_type, list(response.json.get('resp').keys()))

    @mock.patch.object(Collect, 'get_host_info')
    def test_get_host_info_should_return_corresponding_os_info_when_input_partial_info_type(self, mock_host_info):
        mock_host_info.return_value = {
            "resp": {
                "cpu": {},
                "os": {},
                "memory": {}
            }
        }
        url = "v1/ceres/host/info"
        response = self.client.post(url, headers=self.headers_with_token, data=json.dumps(["cpu", "memory", "os"]))
        expect_info_type = ['cpu', 'os', 'memory']
        self.assertEqual(expect_info_type, list(response.json.get('resp').keys()))

    @mock.patch.object(Collect, 'get_host_info')
    def test_get_host_info_should_return_all_os_info_when_input_info_type_is_empty_list(self, mock_host_info):
        mock_host_info.return_value = {
            "resp": {
                "cpu": {},
                "disk": {},
                "os": {},
                "memory": {}
            }
        }
        url = "v1/ceres/host/info"
        response = self.client.post(url, headers=self.headers_with_token, data=json.dumps([]))
        expect_info_type = HOST_COLLECT_INFO_SUPPORT
        self.assertEqual(expect_info_type, list(response.json.get('resp').keys()))

    def test_get_host_info_should_return_400_when_with_no_token(self):
        url = "v1/ceres/host/info"
        response = self.client.post(url, headers=self.headers, data=json.dumps([]))
        self.assert400(response, response.json)

    def test_get_host_info_should_return_param_error_when_input_info_type_is_error(self):
        url = "v1/ceres/host/info"
        response = self.client.post(url, headers=self.headers, data=json.dumps(['mock']))
        self.assert400(response, response.json)

    def test_get_host_info_should_return_token_error_when_input_incorrect_token(self):
        url = "v1/ceres/host/info"
        response = self.client.post(url, headers=self.headers_with_incorrect_token,
                                    data=json.dumps([]))
        self.assertEqual(TOKEN_ERROR, response.json.get('code'), response.json)

    def test_get_host_info_should_return_param_error_when_input_info_type_is_not_support(self):
        url = "v1/ceres/host/info"
        response = self.client.post(url, headers=self.headers_with_token,
                                    data=json.dumps(['system']))
        self.assertEqual(PARAM_ERROR, response.json.get('code'), response.json)

    def test_get_host_info_should_return_param_error_when_no_input(self):
        url = "v1/ceres/host/info"
        response = self.client.post(url, headers=self.headers_with_token)
        self.assert400(response)

    def test_get_host_info_should_return_405_when_request_by_other_method(self):
        url = "v1/ceres/host/info"
        response = self.client.get(url, headers=self.headers_with_token, data=json.dumps([]))
        self.assert405(response)

    def test_change_collect_items_should_only_return_change_success_when_input_correct(self):
        url = "http://localhost:12000/v1/ceres/collect/items/change"
        data = {
            "gopher": {
                "redis": "on",
                "system_inode": "on",
            }
        }
        response = self.client.post(url, headers=self.headers_with_token, data=json.dumps(data))
        self.assert200(response, response.json)

    def test_change_collect_items_should_return_change_success_and_failure_when_input_unsupported_items(
            self):
        url = "http://localhost:12000/v1/ceres/collect/items/change"
        data = {
            "gopher": {
                "redis": "on",
                "system_inode": "on",
                'dd': 'off'
            }
        }
        response = self.client.post(url, headers=self.headers_with_token, data=json.dumps(data))
        self.assert200(response, response.json)

    def test_change_collect_items_should_return_not_support_when_input_unsupported_plugin(self):
        url = "http://localhost:12000/v1/ceres/collect/items/change"
        data = {
            "gopher2": {
                "redis": "on",
                "system_inode": "on",
                'dd': 'off'
            }
        }
        response = self.client.post(url, headers=self.headers_with_token, data=json.dumps(data))
        self.assert200(response, response.json)

    def test_change_collect_items_should_return_all_result_when_input_installed_plugin_and_unsupported_plugin(
            self):
        url = "http://localhost:12000/v1/ceres/collect/items/change"
        data = {
            "gopher": {
                "redis": "on",
                "system_inode": "on",
                'dd': 'off'
            },
            "gopher2": {
                "redis": "on",
                "system_inode": "on",
                'dd': 'off'
            }
        }
        response = self.client.post(url, headers=self.headers_with_token, data=json.dumps(data))
        self.assert200(response, response.json)

    def test_change_collect_items_should_return_param_error_when_input_incorrect(self):
        url = "http://localhost:12000/v1/ceres/collect/items/change"
        data = {
            "gopher": {
                "redis": 1,
                "system_inode": "on",
            }
        }
        response = self.client.post(url, headers=self.headers_with_token, data=json.dumps(data))
        self.assertEqual(PARAM_ERROR, response.json.get('code'), response.json)

    def test_change_collect_items_should_return_param_error_when_with_no_input(self):
        url = "http://localhost:12000/v1/ceres/collect/items/change"
        response = self.client.post(url, headers=self.headers_with_token)
        self.assertEqual(PARAM_ERROR, response.json.get('code'), response.json)

    def test_get_application_info_should_return_target_app_running_info_when_with_correct_token(
            self):
        with mock.patch(
                'ceres.controllers.collect_controller.plugin_status_judge') as mock_plugin_status:
            mock_plugin_status.return_value = 'Active: active (running)'
            response = self.client.get('/v1/ceres/application/info',
                                       headers=self.headers_with_token)
            self.assert200(response, response.json)

    def test_get_application_info_should_return_token_error_when_with_incorrect_token(self, ):
        response = self.client.get('/v1/ceres/application/info',
                                   headers=self.headers_with_incorrect_token)
        self.assertEqual(TOKEN_ERROR, response.json.get('code'), response.json)

    def test_get_application_info_should_return_400_when_with_no_token(self):
        response = self.client.get('/v1/ceres/application/info')
        self.assert400(response, response.json)

    def test_get_application_info_should_return_405_when_request_by_incorrect_method(self):
        response = self.client.post('/v1/ceres/application/info')
        self.assert405(response, response.json)

    @mock.patch("ceres.controllers.collect_controller.validate_data")
    def test_collect_file_should_return_param_error_when_input_file_list_is_not_str(self, validate_data):
        validate_data.return_value = False
        response = self.client.post('/v1/ceres/file/collect',
                                    data=json.dumps([]),
                                    headers=self.headers_with_token)
        self.assertEqual(PARAM_ERROR, response.json.get("code"))

    @mock.patch.object(os.path, 'exists')
    @mock.patch.object(os.path, 'isfile')
    @mock.patch.object(Collect, 'get_file_info')
    def test_collect_file_should_return_file_content_when_input_correct_file_path_with_token(self,
                                                                                             mock_file_info,
                                                                                             mock_isfile,
                                                                                             mock_exists
                                                                                             ):
        mock_file_info.return_value = {"path": "file_path",
                                       "file_attr": {
                                           "mode": "0755",
                                           "owner": "owner",
                                           "group": "group"
                                       },
                                       "content": "content"
                                       }
        mock_isfile.return_value = True
        mock_exists.return_value = True
        data = ['test1', 'test2']
        response = self.client.post('/v1/ceres/file/collect',
                                    data=json.dumps(data),
                                    headers=self.headers_with_token)
        self.assertTrue(response.json.get('infos')[0].get('content'), response.json)

    @mock.patch.object(Collect, 'get_file_info')
    @mock.patch.object(os.path, 'exists')
    @mock.patch.object(os.path, 'isfile')
    def test_collect_file_should_return_fail_list_when_input_file_path_is_not_exist(self,
                                                                                    mock_isfile,
                                                                                    mock_exists,
                                                                                    mock_file_info
                                                                                    ):
        mock_isfile.side_effect = [True, True]
        mock_exists.side_effect = [True, False]
        data = ['test1', 'test2']
        mock_file_info.return_value = {"path": "file_path",
                                       "file_attr": {
                                           "mode": "0755",
                                           "owner": "owner",
                                           "group": "group"
                                       },
                                       "content": "content"
                                       }
        response = self.client.post('/v1/ceres/file/collect',
                                    data=json.dumps(data),
                                    headers=self.headers_with_token)
        self.assertEqual(response.json.get('fail_files'), ['test2'], response.json)

    @mock.patch.object(Collect, 'get_file_info')
    @mock.patch.object(os.path, 'exists')
    @mock.patch.object(os.path, 'isfile')
    def test_collect_file_should_return_fail_list_when_input_partial_file_path_is_not_exist(self,
                                                                                    mock_isfile,
                                                                                    mock_exists,
                                                                                    mock_file_info
                                                                                    ):
        mock_isfile.side_effect = [True, True]
        mock_exists.side_effect = [True, True]
        data = ['test1', 'test2']
        mock_file_info.side_effect = [{"path": "file_path",
                                       "file_attr": {
                                           "mode": "0755",
                                           "owner": "owner",
                                           "group": "group"
                                       },
                                       "content": "content"
                                       }, {}]
        response = self.client.post('/v1/ceres/file/collect',
                                    data=json.dumps(data),
                                    headers=self.headers_with_token)
        self.assertEqual(response.json.get('fail_files'), ['test2'], response.json)

    @mock.patch.object(os.path, 'isfile')
    @mock.patch.object(os.path, 'exists')
    def test_collect_file_should_return_fail_list_when_input_file_path_is_not_a_file(self,
                                                                                     mock_exists,
                                                                                     mock_isfile
                                                                                     ):
        mock_exists.return_value = True
        mock_isfile.side_effect = [False, False]
        data = ['test1', 'test2']
        response = self.client.post('/v1/ceres/file/collect',
                                    data=json.dumps(data),
                                    headers=self.headers_with_token)
        self.assertEqual(['test1', 'test2'], response.json.get('fail_files'),
                         response.json)

    def test_collect_file_should_return_token_error_when_input_correct_file_path_with_incorrect_token(
            self):
        data = ['test1']
        response = self.client.post('/v1/ceres/file/collect',
                                    data=json.dumps(data),
                                    headers=self.headers_with_incorrect_token)
        self.assertEqual(TOKEN_ERROR, response.json.get('code'), response.json)

    def test_collect_file_should_return_400_when_input_correct_file_path_with_no_token(self):
        data = ['test1']
        response = self.client.post('/v1/ceres/file/collect', data=json.dumps(data),
                                    headers=self.headers)
        self.assert400(response, response.json)

    def test_collect_file_should_return_400_when_no_input_with_token(self):
        response = self.client.post('/v1/ceres/file/collect', headers=self.headers)
        self.assert400(response, response.json)

    def test_collect_file_should_return_400_when_input_incorrect_data_with_token(self):
        data = [2333]
        response = self.client.post('/v1/ceres/file/collect', data=json.dumps(data),
                                    headers=self.headers)
        self.assert400(response, response.json)

    def test_collect_file_should_return_405_when_request_by_incorrect_method(self):
        data = ['test1']
        response = self.client.get('/v1/ceres/file/collect', data=json.dumps(data),
                                   headers=self.headers)
        self.assert405(response, response.json)

    @mock.patch.object(GalaGopher, 'get_collect_status')
    @mock.patch.object(Resource, 'get_memory_limit')
    @mock.patch.object(Resource, 'get_current_memory')
    @mock.patch.object(Resource, 'get_cpu_limit')
    @mock.patch.object(Resource, 'get_current_cpu')
    @mock.patch.object(Plugin, 'get_pid')
    @mock.patch.object(Plugin, 'get_plugin_status')
    @mock.patch("ceres.controllers.collect_controller.plugin_status_judge")
    @mock.patch("ceres.controllers.collect_controller.INSTALLABLE_PLUGIN", ['gala-gopher'])
    def test_ceres_plugin_info_should_return_plugin_info_when_all_is_right(
            self, mock_judge_result, mock_plugin_status, mock_pid, mock_current_cpu, mock_cpu_limit,
            mock_current_memory, mock_memory_limit, mock_collect_items):
        mock_judge_result.return_value = True
        mock_plugin_status.return_value = 'active'
        mock_pid.return_value = ''
        mock_current_cpu.return_value = 'current_cpu'
        mock_cpu_limit.return_value = 'limit_cpu'
        mock_current_memory.return_value = 'current_memory'
        mock_memory_limit.return_value = 'limit_memory'
        mock_collect_items.return_value = [{
                "probe_name": "mock_probe",
                "probe_status": "off",
                "support_auto": False
            }]
        response = self.client.get('/v1/ceres/plugin/info', headers=self.headers_with_token)
        expect_res = [{
            "collect_items": [{
                "probe_name": "mock_probe",
                "probe_status": "off",
                "support_auto": False
            }],
            "is_installed": True,
            "plugin_name": "gala-gopher",
            "resource": [
                {
                    "current_value": 'current_cpu',
                    "limit_value": 'limit_cpu',
                    "name": "cpu"
                },
                {
                    "current_value": 'current_memory',
                    "limit_value": 'limit_memory',
                    "name": "memory"
                }
            ],
            "status": "active"
        }]
        self.assertEqual(expect_res, response.json.get('resp'))

    @mock.patch("ceres.controllers.collect_controller.INSTALLABLE_PLUGIN", [])
    def test_ceres_plugin_info_should_return_empty_list_when_host_has_no_available_plugin(self):
        response = self.client.get('/v1/ceres/plugin/info', headers=self.headers_with_token)
        self.assertEqual([], response.json.get('resp'))

    def test_ceres_plugin_info_should_return_token_error_when_request_with_incorrect_token(self):
        response = self.client.get('/v1/ceres/plugin/info',
                                   headers=self.headers_with_incorrect_token)
        self.assertEqual(TOKEN_ERROR, response.json.get('code'))

    @mock.patch("ceres.controllers.collect_controller.plugin_status_judge")
    @mock.patch("ceres.controllers.collect_controller.INSTALLABLE_PLUGIN", ['gala-gopher'])
    def test_ceres_plugin_info_should_return_no_install_when_plugin_is_not_installed(
            self, mock_judge_result):
        mock_judge_result.return_value = False
        expect_res = [{
            "collect_items": [],
            "is_installed": False,
            "plugin_name": "gala-gopher",
            "resource": [],
            "status": None
        }]
        response = self.client.get('/v1/ceres/plugin/info', headers=self.headers_with_token)
        self.assertEqual(expect_res, response.json.get('resp'))

    @mock.patch.object(GalaGopher, 'get_collect_status')
    @mock.patch.object(Resource, 'get_memory_limit')
    @mock.patch.object(Resource, 'get_current_memory')
    @mock.patch.object(Resource, 'get_cpu_limit')
    @mock.patch.object(Resource, 'get_current_cpu')
    @mock.patch.object(Plugin, 'get_plugin_status')
    @mock.patch("ceres.controllers.collect_controller.plugin_status_judge")
    @mock.patch("ceres.controllers.collect_controller.INSTALLABLE_PLUGIN", ['gala-gopher'])
    def test_ceres_plugin_info_should_return_current_resource_is_null_when_plugin_is_not_running(
            self, mock_judge_result, mock_plugin_status, mock_current_cpu, mock_cpu_limit,
            mock_current_memory,mock_memory_limit, mock_collect_items):
        mock_judge_result.return_value = True
        mock_plugin_status.return_value = "inactive"
        mock_current_cpu.return_value = 'current_cpu'
        mock_cpu_limit.return_value = 'limit_cpu'
        mock_current_memory.return_value = 'current_memory'
        mock_memory_limit.return_value = 'limit_memory'
        mock_collect_items.return_value = [{
                "probe_name": "mock_probe",
                "probe_status": "off",
                "support_auto": False
            }]
        expect_res = [{
            "collect_items": [{
                "probe_name": "mock_probe",
                "probe_status": "off",
                "support_auto": False
            }],
            "is_installed": True,
            "plugin_name": "gala-gopher",
            "resource": [
                {
                    "current_value": None,
                    "limit_value": 'limit_cpu',
                    "name": "cpu"
                },
                {
                    "current_value": None,
                    "limit_value": 'limit_memory',
                    "name": "memory"
                }
            ],
            "status": "inactive"
        }]
        response = self.client.get('/v1/ceres/plugin/info', headers=self.headers_with_token)
        self.assertEqual(expect_res, response.json.get('resp'))

    @mock.patch.object(GalaGopher, 'get_collect_status')
    @mock.patch.object(Resource, 'get_memory_limit')
    @mock.patch.object(Resource, 'get_current_memory')
    @mock.patch.object(Resource, 'get_cpu_limit')
    @mock.patch.object(Resource, 'get_current_cpu')
    @mock.patch.object(Plugin, 'get_pid')
    @mock.patch.object(Plugin, 'get_plugin_status')
    @mock.patch("ceres.controllers.collect_controller.plugin_status_judge")
    @mock.patch("ceres.controllers.collect_controller.INSTALLABLE_PLUGIN", ['gala-gopher'])
    def test_ceres_plugin_info_should_return_plugin_collect_items_is_null_when_plugin_is_not_supported_get_collect_items_info(
            self, mock_judge_result, mock_plugin_status, mock_pid, mock_current_cpu, mock_cpu_limit,
            mock_current_memory,mock_memory_limit, mock_collect_items):
        mock_judge_result.return_value = True
        mock_plugin_status.return_value = 'active'
        mock_pid.return_value = ''
        mock_current_cpu.return_value = 'current_cpu'
        mock_cpu_limit.return_value = 'limit_cpu'
        mock_current_memory.return_value = 'current_memory'
        mock_memory_limit.return_value = 'limit_memory'
        mock_collect_items.return_value = []
        expect_res = [{
            "collect_items": [],
            "is_installed": True,
            "plugin_name": "gala-gopher",
            "resource": [
                {
                    "current_value": 'current_cpu',
                    "limit_value": 'limit_cpu',
                    "name": "cpu"
                },
                {
                    "current_value": 'current_memory',
                    "limit_value": 'limit_memory',
                    "name": "memory"
                }
            ],
            "status": "active"
        }]
        response = self.client.get('/v1/ceres/plugin/info', headers=self.headers_with_token)
        self.assertEqual(expect_res, response.json.get('resp'))
