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
import unittest
from unittest import mock

from ceres.manages.resource_manage import Resource
from ceres.models.custom_exception import InputError


class TestResourceManage(unittest.TestCase):
    @mock.patch.object(mock.Mock, 'stdout', create=True)
    @mock.patch('ceres.manages.resource_manage.get_shell_data')
    def test_get_current_memory_should_return_current_value_when_all_is_right(
            self, mock_shell, mock_stdout):
        mock_shell.side_effect = (mock.Mock, 'VmRSS: 2333 kB')
        mock_stdout.return_value = None
        mock_shell.stdout.return_value = ''
        res = Resource.get_current_memory('')
        self.assertEqual('2333 kB', res)

    @mock.patch('ceres.manages.resource_manage.get_shell_data')
    def test_get_current_memory_should_return_empty_str_when_command_execution_failed(
            self, mock_shell):
        mock_shell.side_effect = InputError('')
        res = Resource.get_current_memory('')
        self.assertEqual('', res)

    @mock.patch.object(mock.Mock, 'stdout', create=True)
    @mock.patch('ceres.manages.resource_manage.get_shell_data')
    def test_get_current_cpu_should_return_current_value_when_all_is_right(
            self, mock_shell, mock_stdout):
        mock_shell.side_effect = (mock.Mock, mock.Mock, mock.Mock, '20')
        mock_stdout.return_value = None
        mock_shell.stdout.return_value = ''
        res = Resource.get_current_cpu('', '')
        self.assertEqual('20%', res)

    @mock.patch('ceres.manages.resource_manage.get_shell_data')
    def test_get_current_cpu_should_return_current_value_when_command_execution_failed(
            self, mock_shell):
        mock_shell.side_effect = InputError('')
        res = Resource.get_current_cpu('', '')
        self.assertEqual('', res)

    @mock.patch('ceres.manages.resource_manage.load_conf')
    def test_get_cpu_limit_should_return_cpu_limit_value_when_all_is_right(
            self, mock_load_conf):
        parser = configparser.RawConfigParser()
        parser.read_dict({"Service": {'CPUQuota': '20%'}})
        mock_load_conf.return_value = parser
        res = Resource.get_cpu_limit('')
        self.assertEqual('20%', res)

    @mock.patch('ceres.manages.resource_manage.load_conf')
    def test_get_cpu_limit_should_return_null_when_config_file_has_no_section_service(
            self, mock_load_conf):
        mock_load_conf.return_value = configparser.RawConfigParser()
        res = Resource.get_cpu_limit('')
        self.assertEqual(None, res)

    @mock.patch('ceres.manages.resource_manage.load_conf')
    def test_get_cpu_limit_should_return_null_when_config_file_has_no_option_cpuquota(
            self, mock_load_conf):
        parser = configparser.RawConfigParser()
        parser.read_dict({"Service": {'mock': 'mock'}})
        mock_load_conf.return_value = parser
        res = Resource.get_cpu_limit('')
        self.assertEqual(None, res)

    @mock.patch('ceres.manages.resource_manage.load_conf')
    def test_get_memory_limit_should_return_memory_limit_value_when_all_is_right(
            self, mock_load_conf):
        parser = configparser.RawConfigParser()
        parser.read_dict({"Service": {'MemoryHigh': '40M'}})
        mock_load_conf.return_value = parser
        res = Resource.get_memory_limit('')
        self.assertEqual('40M', res)

    @mock.patch('ceres.manages.resource_manage.load_conf')
    def test_get_memory_limit_should_return_null_when_has_no_section_service(
            self, mock_load_conf):
        mock_load_conf.return_value = configparser.RawConfigParser()
        res = Resource.get_memory_limit('')
        self.assertEqual(None, res)

    @mock.patch('ceres.manages.resource_manage.load_conf')
    def test_get_memory_limit_should_return_null_when_has_no_option_memory_high(
            self, mock_load_conf):
        parser = configparser.RawConfigParser()
        parser.read_dict({"Service": {'mock': 'mock'}})
        mock_load_conf.return_value = parser
        res = Resource.get_memory_limit('')
        self.assertEqual(None, res)
