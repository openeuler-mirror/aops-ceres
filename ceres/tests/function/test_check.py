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
import unittest
from unittest.mock import patch

from ceres.function.check import PreCheck

MOCK_EXECUTE_PATH = "ceres.function.check.execute_shell_command"


class TestPreCheck(unittest.TestCase):
    """Tests for PreCheck."""

    @patch.object(PreCheck, "kernel_consistency_check", return_value=(True, ""))
    def test_execute_check_should_succeed_when_all_items_pass(self, _):
        check_result, items = PreCheck.execute_check(["kernel_consistency"])
        self.assertTrue(check_result)
        self.assertEqual(
            [{"item": "kernel_consistency", "result": True, "log": ""}], items
        )

    @patch.object(PreCheck, "kernel_consistency_check", return_value=(False, "inconsistent"))
    def test_execute_check_should_fail_when_any_item_fails(self, _):
        check_result, items = PreCheck.execute_check(["kernel_consistency"])
        self.assertFalse(check_result)
        self.assertEqual(
            [{"item": "kernel_consistency", "result": False, "log": "inconsistent"}], items
        )

    def test_execute_check_should_fail_when_check_method_not_provided(self):
        check_result, items = PreCheck.execute_check(["unknown_item"])
        self.assertFalse(check_result)
        self.assertEqual("unknown_item", items[0]["item"])
        self.assertFalse(items[0]["result"])
        self.assertIn("No check method is provided", items[0]["log"])

    def test_execute_check_should_succeed_when_check_items_is_empty(self):
        check_result, items = PreCheck.execute_check([])
        self.assertTrue(check_result)
        self.assertEqual([], items)

    @patch("ceres.function.check.platform.uname")
    @patch(MOCK_EXECUTE_PATH)
    def test_kernel_consistency_check_should_succeed_when_kernel_consistent(
        self, mock_execute, mock_uname
    ):
        mock_execute.return_value = (0, "/boot/vmlinuz-4.19.90-2202.1.0.0153.oe1.x86_64", "")
        mock_uname.return_value.release = "4.19.90-2202.1.0.0153.oe1.x86_64"
        check_result, log = PreCheck.kernel_consistency_check()
        self.assertTrue(check_result)
        self.assertEqual("", log)

    @patch("ceres.function.check.platform.uname")
    @patch(MOCK_EXECUTE_PATH)
    def test_kernel_consistency_check_should_fail_when_kernel_inconsistent(
        self, mock_execute, mock_uname
    ):
        mock_execute.return_value = (0, "/boot/vmlinuz-4.19.90-2202.1.0.0153.oe1.x86_64", "")
        mock_uname.return_value.release = "4.19.90-9999.oe1.x86_64"
        check_result, log = PreCheck.kernel_consistency_check()
        self.assertFalse(check_result)
        self.assertIn("inconsistent", log)

    @patch(MOCK_EXECUTE_PATH)
    def test_kernel_consistency_check_should_fail_when_query_boot_kernel_failed(self, mock_execute):
        mock_execute.return_value = (1, "", "grubby error")
        check_result, log = PreCheck.kernel_consistency_check()
        self.assertFalse(check_result)
        self.assertIn("Query boot kernel info failed", log)

    @patch("ceres.function.check.platform.uname")
    @patch(MOCK_EXECUTE_PATH)
    def test_kernel_consistency_check_should_fail_when_current_kernel_is_empty(
        self, mock_execute, mock_uname
    ):
        mock_execute.return_value = (0, "/boot/vmlinuz-4.19.90-2202.1.0.0153.oe1.x86_64", "")
        mock_uname.return_value.release = ""
        check_result, log = PreCheck.kernel_consistency_check()
        self.assertFalse(check_result)
        self.assertIn("Query current kernel info failed", log)


if __name__ == "__main__":
    unittest.main()
