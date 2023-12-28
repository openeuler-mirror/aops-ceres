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
import sys

from ceres.cli.base import BaseCommand
from ceres.function.check import PreCheck
from ceres.function.schema import (
    CVE_FIX_SCHEMA,
    CVE_ROLLBACK_SCHEMA,
    CVE_SCAN_SCHEMA,
    REMOVE_HOTPATCH_SCHEMA,
    REPO_SET_SCHEMA,
)
from ceres.function.status import StatusCode
from ceres.function.util import validate_data
from ceres.manages.collect_manage import Collect
from ceres.manages.rollback_manage import RollbackManage
from ceres.manages.vulnerability_manage import VulnerabilityManage


class VulnerabilityCommand(BaseCommand):
    """
    Vulnerability management command support
    """

    def __init__(self):
        super().__init__()
        self._sub_command = "apollo"
        self.parser = BaseCommand.subparsers.add_parser("apollo")
        self._add_arguments()
        self.command_handlers = {
            'set_repo': self.set_repo_handle,
            'scan': self.scan_handle,
            'fix': self.fix_handle,
            'remove_hotpatch': self.remove_hotpatch_handle,
            'rollback': self.rollback_handle,
        }

    def get_command_name(self):
        return self._sub_command

    def _add_arguments(self):
        command_group = self.parser.add_mutually_exclusive_group(required=True)
        command_group.add_argument("--set-repo", type=str)
        command_group.add_argument("--scan", type=str)
        command_group.add_argument("--fix", type=str)
        command_group.add_argument("--remove-hotpatch", type=str)
        command_group.add_argument("--rollback", type=str)

    def execute(self, namespace):
        """
        Command execution entry
        """
        for option, arguments in vars(namespace).items():
            if option in self.command_handlers and arguments:
                self.command_handlers[option](arguments)
                return

        print("Please check the input parameters!", file=sys.stderr)
        sys.exit(1)

    @staticmethod
    def set_repo_handle(arguments):
        """
        set repo method
        """
        result, data = validate_data(arguments, REPO_SET_SCHEMA)
        if not result:
            sys.exit(1)

        res = StatusCode.make_response_body(VulnerabilityManage().repo_set(data))
        print(json.dumps(res))

    @staticmethod
    def scan_handle(arguments):
        """
        vulnerability scan method
        """
        result, data = validate_data(arguments, CVE_SCAN_SCHEMA)
        if not result:
            sys.exit(1)
        _, cve_scan_info = VulnerabilityManage().cve_scan(data)
        kernel_check, _ = PreCheck.kernel_consistency_check()
        print(
            json.dumps(
                {
                    "check_items": cve_scan_info.get("check_items", []),
                    "unfixed_cves": cve_scan_info.get("unfixed_cves", []),
                    "fixed_cves": cve_scan_info.get("fixed_cves", []),
                    "os_version": Collect.get_os_version(),
                    "installed_packages": Collect.get_installed_packages(),
                    "reboot": not kernel_check,
                }
            )
        )

    @staticmethod
    def fix_handle(arguments):
        """
        cve fix method
        """
        result, data = validate_data(arguments, CVE_FIX_SCHEMA)
        if not result:
            sys.exit(1)
        cve_fix_result = VulnerabilityManage().cve_fix(data)
        print(json.dumps(cve_fix_result))

    @staticmethod
    def remove_hotpatch_handle(arguments):
        """
        remove hotpatch method
        """
        result, data = validate_data(arguments, REMOVE_HOTPATCH_SCHEMA)
        if not result:
            sys.exit(1)
        print(json.dumps(VulnerabilityManage().remove_hotpatch(data.get("cves"))))

    @staticmethod
    def rollback_handle(arguments):
        """
        cve rollback method
        """
        result, data = validate_data(arguments, CVE_ROLLBACK_SCHEMA)
        if not result:
            sys.exit(1)
        cve_rollback_result = RollbackManage().rollback(data)
        print(json.dumps(cve_rollback_result))
