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
import configparser
import json
import os
import unittest
from unittest import mock

import libconf

from ceres.function.util import load_gopher_config, plugin_status_judge, get_dict_from_file, update_ini_data_value
from ceres.models.custom_exception import InputError


class TestUtil(unittest.TestCase):
    MOCK_GOPHER_CONFIG = '''
        mock_key =
    (
    {
        name = "mock_value1";
        switch = "off";
        interval = 1;
    },
    {
        name = "mock_value2";
        switch = "off";
        interval = 1;
    },
    );'''

    @mock.patch.object(mock.Mock, 'stdout', create=True)
    @mock.patch('ceres.function.util.get_shell_data')
    @mock.patch('ceres.function.util.INFORMATION_ABOUT_RPM_SERVICE', {"mock": {"service_name": "mock"}})
    def test_plugin_status_judge_should_return_plugin_status_when_all_is_right(self, mock_shell, mock_stdout):
        mock_status_string = 'Active: active (running)'
        mock_shell.side_effect = (mock.Mock, mock_status_string)
        mock_stdout.return_value = None
        mock_shell.stdout.return_value = ''
        res = plugin_status_judge('mock')
        self.assertEqual(mock_status_string, res)

    @mock.patch('ceres.function.util.INFORMATION_ABOUT_RPM_SERVICE', {})
    def test_plugin_status_judge_should_return_empty_string_when_input_plugin_is_not_support(self):
        res = plugin_status_judge('mock')
        self.assertEqual('', res)

    @mock.patch('ceres.function.util.INFORMATION_ABOUT_RPM_SERVICE', {'mock': {}})
    def test_plugin_status_judge_should_return_empty_string_when_get_plugin_service_name_failed(self):
        res = plugin_status_judge('mock')
        self.assertEqual('', res)

    @mock.patch('ceres.function.util.get_shell_data')
    @mock.patch('ceres.function.util.INFORMATION_ABOUT_RPM_SERVICE', {"mock": {"service_name": "mock"}})
    def test_plugin_status_judge_should_return_empty_string_when_command_execution_failed(self, mock_shell):
        mock_shell.side_effect = InputError('')
        res = plugin_status_judge('mock')
        self.assertEqual('', res)

    @mock.patch('builtins.open', mock.mock_open(read_data='{"mock":"info"}'))
    def test_get_dict_from_file_should_return_dict_info_when_all_is_right(self):
        res = get_dict_from_file('')
        self.assertEqual({"mock": "info"}, res)

    @mock.patch('builtins.open', mock.mock_open(read_data='["mock"]'))
    def test_get_dict_from_file_should_return_empty_dict_when_file_content_is_not_key_value(self):
        res = get_dict_from_file('')
        self.assertEqual({}, res)

    @mock.patch.object(json, 'load')
    @mock.patch('builtins.open', mock.mock_open(read_data='{"mock":"info"}'))
    def test_get_dict_from_file_should_return_empty_dict_when_file_content_is_not_json_string(self, mock_json_load):
        mock_json_load.side_effect = json.decoder.JSONDecodeError('err', 'mock_dic', int())
        res = get_dict_from_file('')
        self.assertEqual({}, res)

    @mock.patch('builtins.open')
    def test_get_dict_from_file_should_return_empty_dict_when_file_path_is_wrong(self, mock_open):
        mock_open.side_effect = FileNotFoundError()
        res = get_dict_from_file('')
        self.assertEqual({}, res)

    @mock.patch.object(os, 'makedirs')
    @mock.patch('ceres.function.util.load_conf')
    @mock.patch('builtins.open', mock.mock_open())
    def test_update_ini_data_value_should_return_update_success_when_input_data_is_in_target_file(
        self, mock_configparser, mock_mkdir
    ):
        mock_mkdir.return_value = None

        mock_parser = configparser.RawConfigParser()
        mock_parser.read_dict({"section": {"option": "value"}})
        mock_configparser.return_value = mock_parser
        mock_configparser.write.return_value = mock.Mock()

        update_ini_data_value('file_path', 'section', 'option', 'mock_value')
        self.assertEqual('mock_value', mock_parser.get('section', 'option'))

    @mock.patch.object(os, 'makedirs')
    @mock.patch('ceres.function.util.load_conf')
    @mock.patch('builtins.open', mock.mock_open())
    def test_update_ini_data_value_should_return_update_success_configparser_when_file_path_is_wrong(
        self, mock_configparser, mock_mkdir
    ):
        mock_mkdir.return_value = None

        mock_parser = configparser.RawConfigParser()
        mock_configparser.return_value = mock_parser
        mock_configparser.write.return_value = mock.Mock()

        update_ini_data_value('file_path', 'section', 'option', 'mock_value')
        self.assertEqual('mock_value', mock_parser.get('section', 'option'))

    @mock.patch.object(os, 'makedirs')
    @mock.patch('ceres.function.util.load_conf')
    @mock.patch('builtins.open', mock.mock_open())
    def test_update_ini_data_value_should_return_update_success_when_input_data_is_not_in_target_file(
        self, mock_configparser, mock_mkdir
    ):
        mock_mkdir.return_value = None

        mock_parser = configparser.RawConfigParser()
        mock_parser.read_dict({"mock": {"option": "value"}})
        mock_configparser.return_value = mock_parser
        mock_configparser.write.return_value = mock.Mock()

        update_ini_data_value('file_path', 'section', 'option', 'mock_value')
        self.assertEqual('mock_value', mock_parser.get('section', 'option'))

    @mock.patch("builtins.open", mock.mock_open(read_data=MOCK_GOPHER_CONFIG))
    def test_load_gopher_config_should_return_gopher_config_when_load_succeed(self):
        mock_config = load_gopher_config('mock')
        self.assertTrue("mock_key" in mock_config.keys())

    @mock.patch("builtins.open")
    def test_load_gopher_config_should_return_empty_config_object_when_file_is_not_found(self, mock_open):
        mock_open.side_effect = FileNotFoundError()
        mock_config = load_gopher_config('mock')
        self.assertEqual(libconf.AttrDict(), mock_config)

    @mock.patch("ceres.function.util.load")
    @mock.patch("builtins.open", mock.mock_open(read_data=MOCK_GOPHER_CONFIG))
    def test_load_gopher_config_should_return_empty_config_object_when_file_is_exist_but_load_fail(self, mock_load):
        mock_load.side_effect = libconf.ConfigParseError()
        mock_config = load_gopher_config('mock')
        self.assertEqual(libconf.AttrDict(), mock_config)
