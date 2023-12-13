#!/usr/bin/python3
# ******************************************************************************
# Copyright (c) Huawei Technologies Co., Ltd. 2023-2023. All rights reserved.
# licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN 'AS IS' BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# ******************************************************************************/
import os
from typing import Optional, Tuple

from ceres.conf.constant import CommandExitCode, CveFixTaskType, TaskExecuteRes
from ceres.function.check import PreCheck
from ceres.function.log import LOGGER
from ceres.function.util import execute_shell_command
from ceres.manages.vulnerability_manage import VulnerabilityManage


class RollbackManage:
    """
    Rollback operation.
    """

    BOOT_FILE = "/boot/vmlinuz-%s"

    def rollback(self, rollback_info: dict) -> dict:
        """
        Rollback for hotpatch/coldpatch transaction.

        Args:
            rollback_info(dict): rollback transaction info
            e.g.
            {
                rollback_type(str): "hotpatch"
                check_items: ["network"],
                installed_rpm(str): "kernel-4.19.90-2206.1.0.0153.oe1.x86_64",
                target_rpm(str): "kernel-4.19.90-2112.8.0.0131.oe1.x86_64",
                dnf_event_start(int): 1,
                dnf_event_end(int): 2,
            }

        Returns:
            {
                "check_items": [
                    {
                        "item": "network",
                        "result":true,
                        "log":"xxxx"
                    }
                ],
                "result": TaskExecuteRes.SUCCEED/TaskExecuteRes.FAIL,
                "log":"rollback log"
            }
        """
        rollback_result = {}
        check_result, items_check_log = PreCheck.execute_check(rollback_info.get("check_items"))
        if not check_result:
            LOGGER.warning("The pre-check is failed before execute command!")
            rollback_result.update(
                {
                    "check_items": items_check_log,
                    "status": TaskExecuteRes.FAIL,
                    "log": "The pre-check is failed before execute command.",
                }
            )
            return rollback_result

        rollback_type = rollback_info.get("rollback_type")
        installed_rpm = rollback_info.get("installed_rpm")
        target_rpm = rollback_info.get("target_rpm")
        dnf_event_start = rollback_info.get("dnf_event_start")
        dnf_event_end = rollback_info.get("dnf_event_end")

        result, log = self._rollback(rollback_type, installed_rpm, target_rpm, dnf_event_start, dnf_event_end)

        rollback_result.update({"check_items": items_check_log, "status": result, "log": log})
        return rollback_result

    def _rollback(
        self,
        rollback_type: str,
        installed_rpm: str,
        target_rpm: str,
        dnf_event_start: Optional[int] = None,
        dnf_event_end: Optional[int] = None,
    ) -> Tuple[str, str]:
        """
        Process rollback operation.

        Args:
            rollback_type(str): hotpatch or coldpatch
            installed_rpm(str): the installed rpm in executed fix task
            target_rpm(str): the target kernel for rollback task
            dnf_event_start(int): dnf event start
            dnf_event_end(int): dnf event end

        Returns:
            Tuple[str, str]: a tuple containing two elements (rollback result, log).
        """

        if rollback_type == CveFixTaskType.HOTPATCH:
            check_result, check_log = self._check_if_dnf_transaction_id_valid(dnf_event_start, dnf_event_end)
            if check_result != TaskExecuteRes.SUCCEED:
                return TaskExecuteRes.FAIL, check_log
            return self._rollback_for_hotpatch(dnf_event_start)

        elif rollback_type == CveFixTaskType.COLDPATCH:
            check_result, check_log = self._check_if_rpm_str_vaild(installed_rpm, target_rpm)
            if check_result != TaskExecuteRes.SUCCEED:
                return TaskExecuteRes.FAIL, check_log
            return self._rollback_for_coldpatch(installed_rpm, target_rpm)

        return TaskExecuteRes.FAIL, f"Rollback type should be {CveFixTaskType.COLDPATCH} or {CveFixTaskType.HOTPATCH}"

    def _check_if_dnf_transaction_id_valid(
        self, dnf_event_start: Optional[int] = None, dnf_event_end: Optional[int] = None
    ) -> Tuple[str, str]:
        """
        Check if the dnf_event_start id and the dnf_event_end id are vaild.

        Args:
            dnf_event_start(int): dnf event start transaction-id
            dnf_event_end(int): dnf event end transaction-id

        Returns:
            Tuple[str, str]: a tuple containing two elements (check result, log)
        """
        if not all((dnf_event_start, dnf_event_end)):
            tmp_log = (
                f"Args of dnf_event_start '{dnf_event_start}' and dnf_event_end '{dnf_event_end}' "
                "should not be null."
            )
            LOGGER.error(tmp_log)
            return TaskExecuteRes.FAIL, tmp_log

        if dnf_event_end != VulnerabilityManage._query_latest_dnf_transaction_id():
            tmp_log = f"Not the last executed dnf trasnaction, failed to process rollback operation."
            LOGGER.error(tmp_log)
            return TaskExecuteRes.FAIL, tmp_log

        if dnf_event_start > dnf_event_end:
            tmp_log = f"Failed to process dnf transaction-id range of '{dnf_event_start} - {dnf_event_end}'."
            LOGGER.error(tmp_log)
            return TaskExecuteRes.FAIL, tmp_log
        elif dnf_event_start == dnf_event_end:
            tmp_log = f"No rollback operation need process."
            return TaskExecuteRes.FAIL, tmp_log

        return TaskExecuteRes.SUCCEED, ""

    def _rollback_for_hotpatch(self, dnf_event_start: int) -> Tuple[str, str]:
        """
        Process rollback operation for hotpatch.

        Args:
            dnf_event_start(int): dnf event start

        Returns:
            Tuple[str, str]: a tuple containing two elements (rollback result, log)
        """
        cmd = f"dnf history rollback {dnf_event_start} -y"
        # 'dnf history rollback transaction-id' command can revert all dnf transactions performed after transaction-id
        code, stdout, stderr = execute_shell_command(cmd)
        if code != CommandExitCode.SUCCEED:
            LOGGER.error(f"Failed to process 'dnf history rollback {dnf_event_start}'.")
            LOGGER.error(stderr)
            return TaskExecuteRes.FAIL, f"Command:{cmd}{os.linesep}{stdout}{os.linesep}{stderr}"

        return TaskExecuteRes.SUCCEED, f"Command:{cmd}{os.linesep}{stdout}{os.linesep}"

    def _check_if_rpm_str_vaild(self, installed_rpm: str, target_rpm: str) -> Tuple[str, str]:
        """
        Check if the rpm str is vaild.

        Args:
            installed_rpm(str): the installed kernel in executed fix task
            target_rpm(str): the target kernel for rollback task

        Returns:
            Tuple[str, str]: a tuple containing two elements (check result, log)
        """

        def get_rpm_name(rpm: str):
            arch_pos = rpm.rindex('.')
            release_pos = rpm.rindex('-', 0, arch_pos)
            version_pos = rpm.rindex('-', 0, release_pos)
            name = rpm[0:version_pos]
            return name

        try:
            installed_rpm_name = get_rpm_name(installed_rpm)
            target_rpm_name = get_rpm_name(target_rpm)
        except ValueError as e:
            rpm_str_format = "{name}-{version}-{release}.{arch}"
            tmp_log = f"Parse rpm info failed. The rpm str format should be {rpm_str_format}"
            LOGGER.error(tmp_log)
            return TaskExecuteRes.FAIL, tmp_log

        if installed_rpm_name != target_rpm_name:
            tmp_log = f"The rpm name of '{installed_rpm_name}' and '{target_rpm_name}' consistency check failed."
            LOGGER.error(tmp_log)
            return TaskExecuteRes.FAIL, tmp_log

        return TaskExecuteRes.SUCCEED, ""

    def _rollback_for_coldpatch(self, installed_rpm: str, target_rpm: str) -> Tuple[str, str]:
        """
        Process rollback operation for coldpatch.

        Args:
            installed_rpm(str): the installed kernel in executed fix task
            target_rpm(str): the target kernel for rollback task

        Returns:
            Tuple[str, str]: a tuple containing two elements (rollback result, log)
        """
        log = []

        result_code, result_log = self._check_boot_kernel_version(installed_rpm)
        if result_log:
            log.append(result_log)
        if result_code != TaskExecuteRes.SUCCEED:
            return TaskExecuteRes.FAIL, os.linesep.join(log)

        result_code, result_log = self._check_current_kernel_version(installed_rpm, target_rpm)
        if result_log:
            log.append(result_log)
        if result_code != TaskExecuteRes.SUCCEED:
            return TaskExecuteRes.FAIL, os.linesep.join(log)

        result_code, result_log = self._check_if_target_rpm_installed(target_rpm)
        if result_log:
            log.append(result_log)
        if result_code != TaskExecuteRes.SUCCEED:
            return TaskExecuteRes.FAIL, os.linesep.join(log)

        result_code, result_log = self._change_boot_kernel_version(target_rpm)
        if result_log:
            log.append(result_log)
        if result_code != TaskExecuteRes.SUCCEED:
            return TaskExecuteRes.FAIL, os.linesep.join(log)

        return TaskExecuteRes.SUCCEED, os.linesep.join(log)

    def _check_boot_kernel_version(self, installed_rpm: str) -> Tuple[str, str]:
        """
        Check if the boot kernel version is consistent with the installed kernel version. If not, it indicates
        that the executed fix task has been tampered.

        Args:
            installed_rpm(str): the installed rpm in executed fix task

        Returns:
            Tuple[str, str]: a tuple containing two elements (check result, log)
        """
        code, stdout, stderr = execute_shell_command(f"grubby --default-kernel")
        # 'grubby --default-kernel' shows boot default kernel version in the system
        # e.g.
        # [root@openEuler ~]# grubby --default-kernel
        # /boot/vmlinuz-4.19.90-2112.8.0.0131.oe1.x86_64
        if code != CommandExitCode.SUCCEED:
            LOGGER.error(stderr)
            return TaskExecuteRes.FAIL, stdout + stderr

        # version-release.arch
        evra = installed_rpm.split("-", 1)[1]
        if evra not in stdout:
            tmp_log = (
                "The grubby default kernel version is not consistent with installed kernel version. "
                "The executed fix task has been tampered."
            )
            LOGGER.error(tmp_log)
            return TaskExecuteRes.FAIL, tmp_log

        return TaskExecuteRes.SUCCEED, ""

    def _check_current_kernel_version(self, installed_rpm: str, target_rpm: str) -> Tuple[str, str]:
        """
        Check if the current kernel version is consistent with the installed kernel version or target kernel
        version. If not, it indicates that the executed fix task has been tampered.

        Args:
            installed_rpm(str): the installed rpm in executed fix task
            target_rpm(str): the target rpm for rollback task

        Returns:
            Tuple[str, str]: a tuple containing two elements (check result, log)
        """
        code, current_evra, stderr = execute_shell_command(f"uname -r")
        # 'uname -r' show the kernel version-release.arch of the current system
        # e.g.
        # [root@openEuler ~]# uname -r
        # 5.10.0-136.12.0.86.oe2203sp1.x86_64
        if code != CommandExitCode.SUCCEED:
            LOGGER.error(stderr)
            return TaskExecuteRes.FAIL, current_evra + stderr

        installed_evra = installed_rpm.split("-", 1)[1]
        target_evra = target_rpm.split("-", 1)[1]

        if installed_evra != current_evra and target_evra != current_evra:
            tmp_log = (
                "The current kernel version is not consistent with installed kernel version or target kernel version. "
                "The executed fix task has been tampered."
            )
            LOGGER.error(tmp_log)
            return TaskExecuteRes.FAIL, tmp_log

        return TaskExecuteRes.SUCCEED, ""

    def _check_if_target_rpm_installed(self, target_rpm: str) -> Tuple[str, str]:
        """
        Check if the target kernel is installed. If not, it indicates that the executed fix task has been tampered.

        Args:
            target_rpm(str): the target rpm for rollback task

        Returns:
            Tuple[str, str]: a tuple containing two elements (check result, log)
        """
        code, stdout, stderr = execute_shell_command(f"rpm -qa | grep {target_rpm}")
        # 'rpm -qa' shows installed rpm
        # e.g.
        # [root@openEuler ~]# rpm -qa | grep kernel-4.19.90-2112.8.0.0131.oe1.x86_64
        # kernel-4.19.90-2112.8.0.0131.oe1.x86_64
        if code != CommandExitCode.SUCCEED or target_rpm not in stdout:
            tmp_log = "The target kernel of rollback task is not installed. The executed fix task has been tampered."
            LOGGER.error(tmp_log)
            return TaskExecuteRes.FAIL, tmp_log

        return TaskExecuteRes.SUCCEED, ""

    def _change_boot_kernel_version(self, target_rpm: str) -> Tuple[str, str]:
        """
        Change the grubby default kernel version to target kernel version.

        Args:
            target_rpm(str): the target rpm for rollback task

        Returns:
            Tuple[str, str]: a tuple containing two elements (change result, log)
        """
        # version-release.arch
        evra = target_rpm.split("-", 1)[1]
        boot_file = self.BOOT_FILE % (evra)
        if not os.path.isfile(boot_file):
            tmp_log = "Target boot file not exists."
            LOGGER.error(tmp_log)
            return TaskExecuteRes.FAIL, tmp_log

        # 'grubby --set-default=/boot/vmlinuz-xxx' changes the default boot entry
        code, stdout, stderr = execute_shell_command(f"grubby --set-default={boot_file}")
        if code != CommandExitCode.SUCCEED:
            LOGGER.error(stderr)
            return TaskExecuteRes.FAIL, stdout + stderr

        return TaskExecuteRes.SUCCEED, f"Change boot kernel version to {target_rpm} successfully."
