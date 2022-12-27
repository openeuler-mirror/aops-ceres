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
import json
from unittest import mock

from ceres.function.status import SERVER_ERROR, SUCCESS, SERVICE_NOT_EXIST, TOKEN_ERROR, PARAM_ERROR
from ceres.tests import BaseTestCase
from ceres.manages.token_manage import TokenManage
from ceres.manages.plugin_manage import Plugin, GalaGopher

header = {
    "Content-Type": "application/json; charset=UTF-8"
}

header_with_token = {
    "Content-Type": "application/json; charset=UTF-8",
    "access_token": "13965d8302b5246a13352680d7c8e602"
}

header_with_incorrect_token = {
    "Content-Type": "application/json; charset=UTF-8",
    "access_token": "13965d8302b5246a13352680d7c8e602Ss"
}


class TestPluginController(BaseTestCase):
    def setUp(self) -> None:
        TokenManage.set_value('13965d8302b5246a13352680d7c8e602')

    @mock.patch.object(Plugin, 'start_service')
    def test_start_plugin_should_return_200_when_input_installed_plugin_name_with_correct_token(
            self,
            mock_start_service):
        plugin_name = "gala-gopher"
        mock_start_service.return_value = SUCCESS
        response = self.client.post(f'/v1/ceres/plugin/start?plugin_name={plugin_name}',
                                    headers=header_with_token)
        self.assert200(response, response.json)

    @mock.patch.object(Plugin, 'start_service')
    def test_start_plugin_should_return_service_not_exist_when_input_plugin_name_is_not_installed_with_correct_token(
            self, mock_start_service):
        plugin_name = "gala-gopher"
        mock_start_service.return_value = SERVICE_NOT_EXIST
        response = self.client.post(f'/v1/ceres/plugin/start?plugin_name={plugin_name}',
                                    headers=header_with_token)
        self.assertEqual(SERVICE_NOT_EXIST, response.json.get('code'))

    def test_start_plugin_should_return_param_error_when_input_plugin_name_is_not_supported_with_correct_token(
            self):
        plugin_name = "nginx"
        response = self.client.post(f'/v1/ceres/plugin/start?plugin_name={plugin_name}',
                                    headers=header_with_token)
        self.assertEqual(PARAM_ERROR, response.json.get('code'))

    def test_start_plugin_should_return_param_error_when_input_plugin_name_is_none_with_correct_token(
            self):
        response = self.client.post('/v1/ceres/plugin/start?plugin_name=',
                                    headers=header_with_token)
        self.assertEqual(PARAM_ERROR, response.json.get('code'))

    def test_start_plugin_should_return_400_when_input_none_with_correct_token(self):
        response = self.client.post('/v1/ceres/plugin/start', headers=header_with_token)
        self.assert400(response, response.json)

    def test_start_plugin_should_return_token_error_when_input_installed_plugin_name_with_incorrect_token(
            self):
        response = self.client.post('/v1/ceres/plugin/start?plugin_name=gala-gopher',
                                    headers=header_with_incorrect_token)
        self.assertEqual(TOKEN_ERROR, response.json.get('code'))

    def test_start_plugin_should_return_token_error_when_input_installed_plugin_name_with_no_token(
            self):
        response = self.client.post('/v1/ceres/plugin/start?plugin_name=gala-gopher')
        self.assert400(response)

    def test_start_plugin_should_return_405_when_request_by_other_method(self):
        response = self.client.get('/v1/ceres/plugin/start?plugin_name=gala-gopher')
        self.assert405(response, response.json)

    @mock.patch('ceres.controllers.plugin_controller.INSTALLABLE_PLUGIN', ['mock_plugin'])
    @mock.patch('ceres.controllers.plugin_controller.INFORMATION_ABOUT_RPM_SERVICE', {})
    def test_start_plugin_should_return_server_error_when_input_plugin_not_in_rpm_info(self):
        response = self.client.post('/v1/ceres/plugin/start?plugin_name=mock_plugin',
                                    headers=header_with_token)
        self.assertEqual(SERVER_ERROR, response.json.get("code"))

    @mock.patch.object(Plugin, 'stop_service')
    def test_stop_plugin_should_return_200_when_input_installed_plugin_name_with_correct_token(
            self, mock_stop_service):
        mock_stop_service.return_value = SUCCESS
        plugin_name = "gala-gopher"
        response = self.client.post(f'/v1/ceres/plugin/stop?plugin_name={plugin_name}',
                                    headers=header_with_token)
        self.assert200(response, response.json)

    @mock.patch.object(Plugin, 'stop_service')
    def test_stop_plugin_should_return_service_not_exist_when_input_plugin_name_is_not_installed_with_correct_token(
            self,
            mock_stop_service):
        mock_stop_service.return_value = SERVICE_NOT_EXIST
        plugin_name = "gala-gopher"
        response = self.client.post(f'/v1/ceres/plugin/stop?plugin_name={plugin_name}',
                                    headers=header_with_token)
        self.assertEqual(SERVICE_NOT_EXIST, response.json.get('code'))

    def test_stop_plugin_should_return_param_error_when_input_plugin_name_is_not_supported_with_correct_token(
            self):
        plugin_name = "nginx"
        response = self.client.post(f'/v1/ceres/plugin/stop?plugin_name={plugin_name}',
                                    headers=header_with_token)
        self.assertEqual(PARAM_ERROR, response.json.get('code'))

    def test_stop_plugin_should_return_param_error_when_input_plugin_name_is_none_with_correct_token(
            self):
        response = self.client.post('/v1/ceres/plugin/stop?plugin_name=', headers=header_with_token)
        self.assertEqual(PARAM_ERROR, response.json.get('code'))

    def test_stop_plugin_should_return_400_when_input_none_with_correct_token(self):
        response = self.client.post('/v1/ceres/plugin/stop', headers=header_with_token)
        self.assert400(response, response.json)

    def test_stop_plugin_should_return_token_error_when_input_installed_plugin_name_with_incorrect_token(
            self):
        response = self.client.post('/v1/ceres/plugin/stop?plugin_name=gala-gopher',
                                    headers=header_with_incorrect_token)
        self.assertEqual(TOKEN_ERROR, response.json.get('code'))

    def test_stop_plugin_should_return_400_when_input_installed_plugin_name_with_no_token(self):
        response = self.client.post('/v1/ceres/plugin/stop?plugin_name=gala-gopher')
        self.assert400(response)

    def test_stop_plugin_should_return_405_when_request_by_other_method(self):
        response = self.client.get('/v1/ceres/plugin/stop?plugin_name=gala-gopher')
        self.assert405(response, response.json)

    @mock.patch('ceres.controllers.plugin_controller.INSTALLABLE_PLUGIN', ['mock_plugin'])
    @mock.patch('ceres.controllers.plugin_controller.INFORMATION_ABOUT_RPM_SERVICE', {})
    def test_stop_plugin_should_return_server_error_when_input_plugin_not_in_rpm_info(self):
        response = self.client.post('/v1/ceres/plugin/stop?plugin_name=mock_plugin',
                                    headers=header_with_token)
        self.assertEqual(SERVER_ERROR, response.json.get("code"))

    @mock.patch('ceres.controllers.plugin_controller.plugin_status_judge')
    @mock.patch.object(GalaGopher, 'change_items_status')
    @mock.patch('ceres.controllers.plugin_controller.INSTALLABLE_PLUGIN', ['gala-gopher'])
    @mock.patch('ceres.controllers.plugin_controller.PLUGIN_WITH_CLASS',
                {'gala-gopher': "GalaGopher"})
    def test_change_collect_items_should_return_change_result_when_all_input_is_correct(
            self, mock_plugin_change, mock_judge_res):
        mock_args = {
            "gala-gopher": {
                "mock_probe1": "auto",
                "mock_probe2": "on",
                "mock_probe3": "on",
                "mock_probe4": "auto",
                "mock_probe5": "auto"
            }
        }

        mock_plugin_change.return_value = {
            "failure": [
                "mock_probe1",
                "mock_probe2",
                "mock_probe3"
            ],
            "success": [
                "mock_probe4",
                "mock_probe5"
            ]
        }
        mock_judge_res.return_value = True

        response = self.client.post('/v1/ceres/collect/items/change',
                                    data=json.dumps(mock_args), headers=header_with_token)
        self.assertEqual(['mock_probe4', 'mock_probe5'],
                         response.json.get('resp').get('gala-gopher').get('success'))

    def test_change_collect_items_should_return_param_error_when_input_args_is_incorrect(
            self):
        mock_args = {
            "gala-gopher": {
                "mock_probe1": "mock"
            }
        }

        response = self.client.post('/v1/ceres/collect/items/change',
                                    data=json.dumps(mock_args), headers=header_with_token)
        self.assertEqual(PARAM_ERROR, response.json.get('code'))

    @mock.patch('ceres.controllers.plugin_controller.INSTALLABLE_PLUGIN', ['mock-test'])
    def test_change_collect_items_should_return_change_fail_when_input_plugin_name_is_not_supported(
            self):
        mock_args = {
            "mock1": {
                "mock_probe1": "auto"
            }
        }

        response = self.client.post('/v1/ceres/collect/items/change',
                                    data=json.dumps(mock_args), headers=header_with_token)
        self.assertEqual(['mock_probe1'], response.json.get('resp').get('mock1').get('failure'))

    @mock.patch('ceres.controllers.plugin_controller.plugin_status_judge')
    @mock.patch('ceres.controllers.plugin_controller.INSTALLABLE_PLUGIN', ['mock'])
    def test_change_collect_items_should_return_change_fail_when_input_plugin_is_not_installed(
            self, mock_judge_res):
        mock_args = {
            "mock": {
                "mock_probe1": "auto"
            }
        }
        mock_judge_res.return_value = False

        response = self.client.post('/v1/ceres/collect/items/change',
                                    data=json.dumps(mock_args), headers=header_with_token)
        self.assertEqual(['mock_probe1'], response.json.get('resp').get('mock').get('failure'))

    @mock.patch('ceres.controllers.plugin_controller.plugin_status_judge')
    @mock.patch('ceres.controllers.plugin_controller.INSTALLABLE_PLUGIN', ['mock'])
    @mock.patch('ceres.controllers.plugin_controller.PLUGIN_WITH_CLASS', {})
    def test_change_collect_items_should_return_change_fail_when_input_plugin_is_not_supported(
            self, mock_judge_res):
        mock_args = {
            "mock": {
                "mock_probe1": "auto"
            }
        }
        mock_judge_res.return_value = True

        response = self.client.post('/v1/ceres/collect/items/change',
                                    data=json.dumps(mock_args), headers=header_with_token)
        self.assertEqual(['mock_probe1'], response.json.get('resp').get('mock').get('failure'))

    def test_change_collect_items_should_return_change_fail_when_token_is_incorrect(self):
        mock_args = {
            "mock": {
                "mock_probe1": "auto"
            }
        }
        response = self.client.post('/v1/ceres/collect/items/change',
                                    data=json.dumps(mock_args), headers=header_with_incorrect_token)
        self.assertEqual(TOKEN_ERROR, response.json.get('code'))

    def test_change_collect_items_should_return_empty_when_input_is_null(self):
        mock_args = {}
        response = self.client.post('/v1/ceres/collect/items/change',
                                    data=json.dumps(mock_args), headers=header_with_token)
        self.assertEqual({}, response.json.get('resp'), response.json)

    def test_change_collect_items_should_return_param_error_when_no_input(self):
        response = self.client.post('/v1/ceres/collect/items/change', headers=header_with_token)
        self.assertEqual(PARAM_ERROR, response.json.get('code'))
