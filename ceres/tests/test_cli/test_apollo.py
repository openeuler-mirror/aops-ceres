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
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from ceres.cli.apollo import VulnerabilityCommand

MOCK_VALIDATE_PATH = "ceres.cli.apollo.validate_data"


def make_namespace(**kwargs):
    return SimpleNamespace(**kwargs)


class TestVulnerabilityCommand(unittest.TestCase):
    """Tests for VulnerabilityCommand handlers."""

    @patch(MOCK_VALIDATE_PATH, return_value=(False, None))
    def test_set_repo_handle_should_exit_when_data_invalid(self, _):
        with patch("ceres.cli.apollo.sys") as mock_sys:
            mock_sys.exit.side_effect = RuntimeError("exit")
            with self.assertRaises(RuntimeError):
                VulnerabilityCommand.set_repo_handle("{}")
        mock_sys.exit.assert_called_once_with(1)

    @patch("builtins.print")
    @patch(
        "ceres.cli.apollo.StatusCode.make_response_body",
        return_value={"code": "200", "msg": "succeed"},
    )
    @patch("ceres.cli.apollo.SetRepoManage.set_repo", return_value="200")
    @patch(MOCK_VALIDATE_PATH, return_value=(True, {"repo": {"name": "everything"}}))
    def test_set_repo_handle_should_print_result_when_succeed(
        self, _, mock_set_repo, mock_response, mock_print
    ):
        VulnerabilityCommand.set_repo_handle("{}")
        mock_set_repo.assert_called_once()
        printed = json.loads(mock_print.call_args[0][0])
        self.assertEqual("200", printed["code"])

    @patch(MOCK_VALIDATE_PATH, return_value=(False, None))
    def test_scan_handle_should_exit_when_data_invalid(self, _):
        with patch("ceres.cli.apollo.sys") as mock_sys:
            mock_sys.exit.side_effect = RuntimeError("exit")
            with self.assertRaises(RuntimeError):
                VulnerabilityCommand.scan_handle("{}")
        mock_sys.exit.assert_called_once_with(1)

    @patch("ceres.cli.apollo.PreCheck.kernel_consistency_check", return_value=(True, ""))
    @patch("ceres.cli.apollo.Collect.get_installed_packages", return_value=["unzip"])
    @patch("ceres.cli.apollo.Collect.get_os_version", return_value="openEuler 22.03")
    @patch(
        "ceres.cli.apollo.CveScanManage.cve_scan",
        return_value=(
            0,
            {"check_items": [], "unfixed_cves": [{"cve_id": "CVE-1"}], "fixed_cves": []},
        ),
    )
    @patch("builtins.print")
    @patch(MOCK_VALIDATE_PATH, return_value=(True, {"check_items": []}))
    def test_scan_handle_should_print_scan_info_when_succeed(
        self, _, mock_print, mock_scan, mock_os, mock_pkgs, __
    ):
        VulnerabilityCommand.scan_handle("{}")
        printed = json.loads(mock_print.call_args[0][0])
        self.assertEqual([{"cve_id": "CVE-1"}], printed["unfixed_cves"])
        self.assertEqual("openEuler 22.03", printed["os_version"])
        self.assertEqual(["unzip"], printed["installed_packages"])
        self.assertFalse(printed["reboot"])

    @patch("ceres.cli.apollo.PreCheck.kernel_consistency_check", return_value=(False, ""))
    @patch("ceres.cli.apollo.Collect.get_installed_packages", return_value=[])
    @patch("ceres.cli.apollo.Collect.get_os_version", return_value="openEuler 22.03")
    @patch("ceres.cli.apollo.CveScanManage.cve_scan", return_value=(0, {}))
    @patch("builtins.print")
    @patch(MOCK_VALIDATE_PATH, return_value=(True, {"check_items": []}))
    def test_scan_handle_should_flag_reboot_when_kernel_inconsistent(
        self, _, mock_print, mock_scan, mock_os, mock_pkgs, __
    ):
        VulnerabilityCommand.scan_handle("{}")
        printed = json.loads(mock_print.call_args[0][0])
        self.assertTrue(printed["reboot"])

    @patch(MOCK_VALIDATE_PATH, return_value=(False, None))
    def test_fix_handle_should_exit_when_data_invalid(self, _):
        with patch("ceres.cli.apollo.sys") as mock_sys:
            mock_sys.exit.side_effect = RuntimeError("exit")
            with self.assertRaises(RuntimeError):
                VulnerabilityCommand.fix_handle("{}")
        mock_sys.exit.assert_called_once_with(1)

    @patch("builtins.print")
    @patch(
        "ceres.cli.apollo.CveFixManage.cve_fix",
        return_value={"status": "succeed", "rpms": []},
    )
    @patch(MOCK_VALIDATE_PATH, return_value=(True, {"fix_type": "coldpatch", "rpms": []}))
    def test_fix_handle_should_print_fix_result_when_succeed(self, _, mock_fix, mock_print):
        VulnerabilityCommand.fix_handle("{}")
        mock_fix.assert_called_once()
        printed = json.loads(mock_print.call_args[0][0])
        self.assertEqual("succeed", printed["status"])

    @patch(MOCK_VALIDATE_PATH, return_value=(False, None))
    def test_remove_hotpatch_handle_should_exit_when_data_invalid(self, _):
        with patch("ceres.cli.apollo.sys") as mock_sys:
            mock_sys.exit.side_effect = RuntimeError("exit")
            with self.assertRaises(RuntimeError):
                VulnerabilityCommand.remove_hotpatch_handle("{}")
        mock_sys.exit.assert_called_once_with(1)

    @patch("builtins.print")
    @patch(
        "ceres.cli.apollo.HotpatchRemoveManage.remove_hotpatch",
        return_value={"status": "succeed", "cves": []},
    )
    @patch(MOCK_VALIDATE_PATH, return_value=(True, {"cves": ["CVE-2023-1111"]}))
    def test_remove_hotpatch_handle_should_print_result_when_succeed(
        self, _, mock_remove, mock_print
    ):
        VulnerabilityCommand.remove_hotpatch_handle("{}")
        mock_remove.assert_called_once_with(["CVE-2023-1111"])
        printed = json.loads(mock_print.call_args[0][0])
        self.assertEqual("succeed", printed["status"])

    @patch(MOCK_VALIDATE_PATH, return_value=(False, None))
    def test_rollback_handle_should_exit_when_data_invalid(self, _):
        with patch("ceres.cli.apollo.sys") as mock_sys:
            mock_sys.exit.side_effect = RuntimeError("exit")
            with self.assertRaises(RuntimeError):
                VulnerabilityCommand.rollback_handle("{}")
        mock_sys.exit.assert_called_once_with(1)

    @patch("builtins.print")
    @patch(
        "ceres.cli.apollo.RollbackManage.rollback",
        return_value={"status": "succeed", "log": ""},
    )
    @patch(MOCK_VALIDATE_PATH, return_value=(True, {"rollback_type": "hotpatch"}))
    def test_rollback_handle_should_print_result_when_succeed(self, _, mock_rollback, mock_print):
        VulnerabilityCommand.rollback_handle("{}")
        mock_rollback.assert_called_once()
        printed = json.loads(mock_print.call_args[0][0])
        self.assertEqual("succeed", printed["status"])

    @patch("builtins.print")
    def test_execute_should_call_handler_when_option_matched(self, mock_print):
        command = VulnerabilityCommand.__new__(VulnerabilityCommand)
        command.command_handlers = {"scan": VulnerabilityCommand.scan_handle}
        with patch(MOCK_VALIDATE_PATH, return_value=(True, {})), patch(
            "ceres.cli.apollo.CveScanManage.cve_scan", return_value=(0, {})
        ), patch(
            "ceres.cli.apollo.PreCheck.kernel_consistency_check", return_value=(True, "")
        ), patch(
            "ceres.cli.apollo.Collect.get_os_version", return_value=""
        ), patch(
            "ceres.cli.apollo.Collect.get_installed_packages", return_value=[]
        ):
            command.execute(make_namespace(scan="{}"))
        mock_print.assert_called_once()

    @patch("builtins.print")
    def test_execute_should_exit_when_no_option_matched(self, mock_print):
        command = VulnerabilityCommand.__new__(VulnerabilityCommand)
        command.command_handlers = {"scan_handle": VulnerabilityCommand.scan_handle}
        with patch("ceres.cli.apollo.sys") as mock_sys:
            mock_sys.exit.side_effect = RuntimeError("exit")
            with self.assertRaises(RuntimeError):
                command.execute(make_namespace(scan=None))
        mock_sys.exit.assert_called_once_with(1)


if __name__ == "__main__":
    unittest.main()
