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
import os

from ceres.conf.constant import BASE_SERVICE_PATH, CommandExitCode
from ceres.function.log import LOGGER
from ceres.function.util import load_conf, execute_shell_command


class Resource:
    """
    Get cpu and memory info
    """

    @classmethod
    def get_current_memory(cls, pid: str) -> str:
        """
        Get memory value which plugin has used
        Args:
            pid(str): main process id about running plugin
        Returns:
            str:The memory value which has used
        """
        code, stdout, _ = execute_shell_command(f"cat /proc/{pid}/status|grep VmRSS")
        if code == CommandExitCode.SUCCEED:
            return stdout.split(":")[1].strip()
        LOGGER.error(f'Failed to get memory info of process {pid}!')
        return ""

    @classmethod
    def get_memory_limit(cls, rpm_name: str) -> str:
        """
        Get MemoryHigh value from service file

        Args:
            rpm_name (str): rpm package name

        Returns:
            str: memory_high values.

        Raises:
            NoOptionError: The service section has no option "MemoryHigh"
            NoSectionError: Service file has no section "Service"
        """
        service_path = os.path.join(BASE_SERVICE_PATH, f"{rpm_name}.service")
        config = load_conf(service_path)
        try:
            memory_high = config.get("Service", "MemoryHigh")
        except configparser.NoOptionError:
            LOGGER.warning(
                'There is no option "MemoryHigh" in section "Service"'
                f' in file {service_path},please check and try again.'
            )
            memory_high = None
        except configparser.NoSectionError:
            LOGGER.warning(f'There is no section "Service" in file {service_path} ,' 'please check and try again.')
            memory_high = None
        return memory_high

    @staticmethod
    def get_current_cpu(rpm_name: str, pid: str) -> str:
        """
        Get cpu usage by process id

        Args:
            rpm_name(str): rpm package name
            pid(str): main process id about running plugin

        Returns:
            str: cpu usage
        """
        code, stdout, _ = execute_shell_command(f"ps -aux|grep -w {rpm_name}|grep {pid}|awk {{print$3}}")
        if code == CommandExitCode.SUCCEED:
            return f'{stdout.strip()}%'
        LOGGER.error(f'Failed to get plugin cpu info about {rpm_name}.')
        return ''

    @staticmethod
    def get_cpu_limit(rpm_name: str) -> str:
        """
        get limit cpu from plugin service file

        Args:
            rpm_name (str): rpm package name

        Returns:
            str: cpu limit value

        Raises:
            NoOptionError: The service section has no option "CPUQuota"
            NoSectionError: Service file has no section "Service"
        """
        service_path = os.path.join(BASE_SERVICE_PATH, f"{rpm_name}.service")
        config = load_conf(service_path)
        try:
            cpu_limit = config.get("Service", "CPUQuota")
        except configparser.NoOptionError:
            LOGGER.warning(
                'There is no option "CPUQuota" in section "Service"'
                f' in file {service_path},please check and try again.'
            )
            cpu_limit = None
        except configparser.NoSectionError:
            LOGGER.warning(f'There is no section "Service" in file {service_path} ,' 'please check and try again.')
            cpu_limit = None
        return cpu_limit
