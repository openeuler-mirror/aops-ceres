#!/usr/bin/python3
# ******************************************************************************
# Copyright (c) Huawei Technologies Co., Ltd. 2021-2023. All rights reserved.
# licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN 'AS IS' BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# ******************************************************************************/
from typing import List, Tuple

from ceres.conf.constant import CommandExitCode
from ceres.function.log import LOGGER
from ceres.function.util import execute_shell_command


class PreCheck(object):
    """
    Provide some inspection methods for the specific indicators.

    """

    @classmethod
    def execute_check(cls, check_items: List[str]) -> Tuple[bool, list]:
        """
        execute items check func

        Args:
            check_items(list): list of check items

        Return:
            Tuple[bool, list]: check result and all items check result
        """
        check_result, check_items_result = True, []
        for check_item in check_items:
            check_func = getattr(cls, f"{check_item}_check", None)

            if check_func:
                item_check_result, item_check_log = check_func()
                check_items_result.append({"item": check_item, "result": item_check_result, "log": item_check_log})
                check_result = check_result and item_check_result

            else:
                check_items_result.append(
                    {"item": check_item, "result": False, "log": f"No check method is provided fo {check_item}!"}
                )
                check_result = False
        return check_result, check_items_result

    @staticmethod
    def kernel_consistency_check() -> Tuple[bool, str]:
        """
        Determine whether Linux uses the same kernel as the boot kernel

        Returns:
            Tuple[bool, str]
            a tuple containing two elements (check result, operation log).
        """
        # Example of command execution result::
        # /boot/vmlinuz-5.10.0-60.18.0.50.oe2203.x86_64
        code, boot_kernel_version, stderr = execute_shell_command("grubby --default-kernel")
        if code != CommandExitCode.SUCCEED:
            LOGGER.error(stderr)
            return False, "Query boot kernel info failed!"

        # Example of command execution result::
        # 5.10.0-60.18.0.50.oe2203.x86_64
        code, current_kernel_version, stderr = execute_shell_command("uname -r")
        if code != CommandExitCode.SUCCEED:
            LOGGER.error(stderr)
            return False, "Query current kernel info failed!"

        if boot_kernel_version[14:] == current_kernel_version:
            return True, ""

        LOGGER.info(f"The boot kernel information is inconsistent with the current kernel information.")
        return False, "The boot kernel information is inconsistent with the current kernel information."
