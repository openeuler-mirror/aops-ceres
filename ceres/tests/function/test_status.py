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

from ceres.function.status import SUCCESS, StatusCode


class TestStatus(unittest.TestCase):
    def test_make_response_body_should_return_response_body_when_input_status_code_and_the_code_in_mapping(self):
        expect_res = {'code': SUCCESS, 'msg': 'operate success'}
        res = StatusCode.make_response_body(SUCCESS)
        self.assertEqual(expect_res, res)

    def test_make_response_body_should_return_response_body_and_data_when_input_status_code_and_data(self):
        expect_res = {'code': SUCCESS, 'msg': 'operate success', "mock": "mock"}
        res = StatusCode.make_response_body((SUCCESS, {"mock": "mock"}))
        self.assertEqual(expect_res, res)

    def test_make_response_body_should_return_response_body_and_data_when_input_status_code_and_data_and_code_is_not_in_mapping(self):
        expect_res = {'code': 900, 'msg': 'unknown error'}
        res = StatusCode.make_response_body(900)
        self.assertEqual(expect_res, res)
