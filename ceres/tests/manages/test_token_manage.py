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
import unittest
from unittest import mock

from ceres.manages.token_manage import TokenManage


class TestTokenManage(unittest.TestCase):
    @mock.patch('builtins.open', mock.mock_open(read_data='{"access_token": "The mock token"}'))
    def test_load_token_should_return_token_when_read_token_file_success(self):
        mock_token = TokenManage()
        mock_token.load_token()
        self.assertEqual("The mock token", mock_token.token)

    @mock.patch('builtins.open')
    def test_load_token_should_return_token_is_empty_string_when_token_file_is_not_existed(self, mock_open):
        mock_open.side_effect = FileNotFoundError
        mock_token = TokenManage()
        mock_token.load_token()
        self.assertEqual("", mock_token.token)

    @mock.patch('builtins.open')
    def test_load_token_should_return_token_is_empty_string_when_token_decode_error(self, mock_open):
        mock_open.side_effect = json.decoder.JSONDecodeError('', '', int())
        mock_token = TokenManage()
        mock_token.load_token()
        self.assertEqual("", mock_token.token)

    @mock.patch.object(TokenManage, "load_token")
    def test_get_value_should_get_token_when_token_is_not_been_loaded(self, load_token):
        load_token.return_value = None
        self.assertEqual('', TokenManage.get_value())

    def test_get_value_should_return_token_when_token_has_been_loaded(self):
        TokenManage.token = "mock_token"
        self.assertEqual('mock_token', TokenManage.get_value())