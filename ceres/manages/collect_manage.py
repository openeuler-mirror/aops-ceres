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
import grp
import os
import pwd
import re
import platform
from socket import AF_INET, SOCK_DGRAM, socket
from typing import Any, Dict, List, Union
import xml.etree.ElementTree as ET

from ceres.conf.constant import (
    HOST_COLLECT_INFO_SUPPORT,
    INFORMATION_ABOUT_RPM_SERVICE,
    INSTALLABLE_PLUGIN,
    PLUGIN_WITH_CLASS,
    SCANNED_APPLICATION,
    CommandExitCode,
)
from ceres.function.log import LOGGER
from ceres.function.util import execute_shell_command, plugin_status_judge
from ceres.manages import plugin_manage
from ceres.manages.resource_manage import Resource


class Collect:
    """
    Provides functions to collect information.
    """

    def get_host_info(self, info_type: List[str]) -> dict:
        """
        get basic info about machine

        Args:
            info_type(list): e.g [memory, os, cpu, disk]

        Returns:
            int: status code
            dict: e.g
                {
                    'resp':
                        {
                            'os': {
                                'os_version': os_version,
                                'bios_version': bios_version,
                                'kernel': kernel_version
                                },
                            "cpu": {
                                "architecture": string,
                                "core_count": string,
                                "model_name": string,
                                "vendor_id": string,
                                "l1d_cache": string,
                                "l1i_cache": string,
                                "l2_cache": string,
                                "l3_cache": string
                                },
                            'memory':{
                            "size": "xx GB",
                            "total": int,
                            "info": [
                                {
                                    "size": "xx GB",
                                    "type": "DDR4",
                                    "speed": "xxxx MT/s",
                                    "manufacturer": "string"
                                }
                                ...
                                ]
                            }
                            'disk':[
                                {
                                  "capacity": xx GB,
                                  "model": "string",
                                }
                            ]
                        }
                }
        """
        host_info = {}
        if not info_type:
            info_type = HOST_COLLECT_INFO_SUPPORT
        for info_name in info_type:
            func_name = getattr(self, f"_get_{info_name}_info")
            host_info[info_name] = func_name()

        return host_info

    @staticmethod
    def get_os_version() -> str:
        """
            get system name and its version

        Returns:
            str: e.g openEuler 21.09
        """
        _, stdout, _ = execute_shell_command(["cat /etc/os-release"])
        res = re.search('(?=PRETTY_NAME=).+', stdout)

        if res:
            return res.group()[12:].strip('"').replace(' ', '-')
        LOGGER.warning('Failed to get os version info, ' 'please check file /etc/os-release and try it again')
        return ''

    def _get_os_info(self) -> Dict[str, str]:
        """
            get os info

        Returns:
                {
                    'os_version': string,
                    'bios_version': string,
                    'kernel': string
                }
        """
        kernel_info = re.search(r'[\d\.]+-[\d\.]+[\d]', self.get_current_kernel_version())

        res = {
            'os_version': self.get_os_version(),
            'bios_version': self.__get_bios_version(),
            'kernel': kernel_info.group() if kernel_info else "",
        }
        return res

    @staticmethod
    def __get_bios_version() -> str:
        """
            get bios version number

        Returns:
            str
        """
        _, stdout, _ = execute_shell_command(["dmidecode -s bios-version"])

        return stdout

    @staticmethod
    def get_current_kernel_version() -> str:
        """
            get current kernel version info

        Returns:
            str
        """
        return platform.uname().release

    @staticmethod
    def _get_cpu_info() -> Dict[str, str]:
        """
        get cpu info by command lscpu

        Returns:
            dict: e.g
                {
                    "architecture": string,
                    "core_count": string,
                    "model_name": string,
                    "vendor_id": string,
                    "l1d_cache": string,
                    "l1i_cache": string,
                    "l2_cache": string,
                    "l3_cache": string
                }
        """
        _, stdout, _ = execute_shell_command(["lscpu"], **{"env": {"LANG": "en_US.utf-8"}})

        info_list = re.findall('.+:.+', stdout)

        if not info_list:
            LOGGER.warning('Failed to read cpu info by lscpu, please check it and try again.')

        cpu_info = {}
        for info in info_list:
            tmp = info.split(":")
            cpu_info[tmp[0]] = tmp[1].strip()

        res = {
            "architecture": cpu_info.get('Architecture'),
            "core_count": cpu_info.get('CPU(s)'),
            "model_name": cpu_info.get('Model name'),
            "vendor_id": cpu_info.get('Vendor ID'),
            "l1d_cache": cpu_info.get('L1d cache'),
            "l1i_cache": cpu_info.get('L1i cache'),
            "l2_cache": cpu_info.get('L2 cache'),
            "l3_cache": cpu_info.get('L3 cache'),
        }

        return res

    @staticmethod
    def __get_total_online_memory() -> str:
        """
        get memory size by lsmem

        Returns:
            str: memory size
        """
        _, stdout, _ = execute_shell_command(["lsmem"])

        res = re.search("(?=Total online memory:).+", stdout)
        if res:
            return res.group()[20:].strip()
        LOGGER.warning('Failed to get total online memory, please check lsmem and try it again')
        return ''

    def _get_memory_info(self) -> Dict[str, Union[int, List[Dict[str, Any]]]]:
        """
        get memory detail info and memory stick count

        Returns:
            dict: e.g
                {
                    "size": "xx GB",
                    "total": int,
                    "info": [
                        {
                            "size": "xx GB",
                            "type": "DDR4",
                            "speed": "xxxx MT/s",
                            "manufacturer": "string"
                        }
                        ...
                        ]
                }

        """
        res = {'size': self.__get_total_online_memory() or None, "total": None, "info": []}

        code, memory_data, _ = execute_shell_command(["dmidecode -t memory"])

        # dmidecode -t memory
        # e.g
        # dmidecode 3.2
        # Getting SMBIOS data from sysfs.
        # SMBIOS 2.8 present.
        #
        # Physical Memory Array
        #       Location: Other
        #       Use: System Memory
        #       ...
        # Memory Device
        #       Array Handle
        #       ...
        # Memory Device
        #       Array Handle
        #       ...
        if code != CommandExitCode.SUCCEED or len(memory_data.split('Memory Device')) == 1:
            LOGGER.warning('Failed to read memory info by dmidecode')
            return res

        info = []
        for module in memory_data.split('Memory Device'):
            module_info_list = re.findall('.+:.+', module)

            module_info_dict = {}
            for module_info in module_info_list:
                part_info = module_info.split(':')
                module_info_dict[part_info[0].strip()] = part_info[1].strip()

            if module_info_dict.get('Size') is None or module_info_dict.get('Size') == 'No Module Installed':
                continue

            memory_info = {
                "size": module_info_dict.get('Size'),
                "type": module_info_dict.get('Type'),
                "speed": module_info_dict.get('Speed'),
                "manufacturer": module_info_dict.get('Manufacturer'),
            }
            info.append(memory_info)

        res['total'] = len(info)
        res['info'] = info

        return res

    @staticmethod
    def _get_disk_info() -> List[dict]:
        """
            get disk capacity and model

        Returns:
            list: e.g
                [
                    {
                      "capacity": string,
                      "model": "string",
                    }
                ]
        """
        code, stdout, _ = execute_shell_command(["lshw -xml -c disk"])
        if code != CommandExitCode.SUCCEED:
            LOGGER.error(stdout)
            return []

        try:
            tree = ET.ElementTree(ET.fromstring(stdout))
        except ET.ParseError as error:
            LOGGER.error(error)
            LOGGER.warning("Disk info parse error, please check command 'lshw -xml -c disk'")
            return []

        disk_list = tree.findall("node")

        if not disk_list:
            return []

        res = []
        for node in disk_list:
            model = node.find("description") if node.find("product") is None else node.find("product")
            size = node.find("size")
            res.append(
                {
                    "model": model.text if model is not None else "unknown",
                    "capacity": f"{int(size.text) / (1024**3)} GB" if size is not None else "unknown",
                }
            )

        return res

    @staticmethod
    def get_file_info(file_path: str) -> dict:
        """
            get file content and attribute
        Args:
            file_path(str): file absolute path

        Returns:
            dict: { path: file_path,
                    file_attr: {
                    mode:  0755(-rwxr-xr-x),
                    owner: owner,
                    group: group},
                    content: content}
        """
        if os.access(file_path, os.X_OK):
            LOGGER.warning(f"{file_path} is an executable file")
            return {}

        if os.path.getsize(file_path) > 1024 * 1024 * 1:
            LOGGER.warning(f"{file_path} is too large")
            return {}

        try:
            with open(file_path, 'r', encoding='utf8') as f:
                content = f.read()
        except (OSError, ValueError) as error:
            LOGGER.error(f'Failed to read file named {file_path} with error message:\n {error}')
            return {}
        file_attr = os.stat(file_path)
        file_mode = oct(file_attr.st_mode)[4:]
        file_owner = pwd.getpwuid(file_attr.st_uid)[0]
        file_group = grp.getgrgid(file_attr.st_gid)[0]
        info = {
            'path': file_path,
            'file_attr': {'mode': file_mode, 'owner': file_owner, 'group': file_group},
            'content': content,
        }
        return info

    @staticmethod
    def get_uuid() -> str:
        """
            get uuid about disk

        Returns:
            uuid(str)
        """
        code, stdout, _ = execute_shell_command(["dmidecode", "grep UUID"])
        if code == CommandExitCode.SUCCEED:
            return stdout.replace("-", "").split(':')[1].strip()
        return ""

    @staticmethod
    def get_host_ip() -> str:
        """
            get host ip by create udp package
        Returns:
            host ip(str)
        """
        sock = socket(AF_INET, SOCK_DGRAM)
        try:
            sock.connect(('8.8.8.8', 80))
            host_ip = sock.getsockname()[0]
        except OSError:
            LOGGER.error("Failed to get host ip, please check internet and try again.")
            host_ip = ''
        finally:
            sock.close()
        return host_ip

    @staticmethod
    def get_installed_packages():
        """
        query installed packages

        Returns:
            list: list of dict, each dict is package_name and package_version. e.g
                [{
                    "name": "kernel",
                    "version": "4.19.90-2022.1.1"
                }]
        """

        code, source_name_info, _ = execute_shell_command(["rpm -qi kernel", "grep .src.rpm"])
        if code != CommandExitCode.SUCCEED:
            LOGGER.error("Failed to query installed packages.")
            return []

        package_info_dict = {}
        for package_source_name in source_name_info.splitlines():
            package_info = package_source_name.rsplit("-", 2)
            if len(package_info) == 1:
                continue
            package = package_info[0].split(':')[1].strip()
            pkg_version = f"{package_info[1]}-{package_info[-1].split('.')[0]}"
            key = package + pkg_version
            if key not in package_info_dict:
                package_info_dict[key] = {"name": package, "version": pkg_version}

        return list(package_info_dict.values())

    @staticmethod
    def get_application_info() -> list:
        """
            get the running applications in the target list

        Returns:
            List[str]:applications which is running
        """
        running_apps = []
        for application_name in SCANNED_APPLICATION:
            status_info = plugin_status_judge(application_name)
            if status_info != '':
                status = re.search(r':.+\(', status_info).group()[1:-1].strip()
                if status == 'active':
                    running_apps.append(application_name)
        return running_apps

    @staticmethod
    def get_plugin_info():
        """
        get all plugin info about ceres

        Returns:
            a list which contains cpu,memory,collect items of plugin,running status and so on.
            for example
                [{
                    "plugin_name": "string",
                    "is_installed": true,
                    "status": "string",
                    "collect_items": [{
                        "probe_name": "string",
                        "probe_status": "string"
                    }],
                    "resource": [{
                        "name": "string",
                        "limit_value": "string",
                        "current_value": "string
                    }]
                }]

        """
        plugin_list = INSTALLABLE_PLUGIN
        if len(plugin_list) == 0:
            return []

        res = []
        for plugin_name in plugin_list:
            plugin_running_info = {"plugin_name": plugin_name, "collect_items": [], "status": None, "resource": []}

            if not plugin_status_judge(plugin_name):
                plugin_running_info["is_installed"] = False
                res.append(plugin_running_info)
                continue
            plugin_running_info["is_installed"] = True

            service_name = INFORMATION_ABOUT_RPM_SERVICE.get(plugin_name).get("service_name")
            plugin = plugin_manage.Plugin(service_name)

            status = plugin.get_plugin_status()
            if status == "active":
                pid = plugin_manage.Plugin.get_pid(service_name)
                cpu_current = Resource.get_current_cpu(service_name, pid)
                memory_current = Resource.get_current_memory(pid)
            else:
                cpu_current = None
                memory_current = None
            cpu_limit = Resource.get_cpu_limit(service_name)
            memory_limit = Resource.get_memory_limit(service_name)

            collect_items_status = []
            plugin_class_name = PLUGIN_WITH_CLASS.get(plugin_name, '')
            if hasattr(plugin_manage, plugin_class_name):
                plugin_obj = getattr(plugin_manage, plugin_class_name)
                if hasattr(plugin_obj, "get_collect_status"):
                    collect_items_status = plugin_obj.get_collect_status()

            resource = []
            cpu = {"name": "cpu", "current_value": cpu_current, "limit_value": cpu_limit}
            memory = {"name": "memory", "current_value": memory_current, "limit_value": memory_limit}
            resource.append(cpu)
            resource.append(memory)
            plugin_running_info["status"] = status
            plugin_running_info["collect_items"] = collect_items_status
            plugin_running_info["resource"] = resource
            res.append(plugin_running_info)
        return res

    @staticmethod
    def collect_file(config_path_list: list) -> dict:
        result = {"success_files": [], "fail_files": [], "infos": []}

        for file_path in config_path_list:
            if not os.path.exists(file_path) or not os.path.isfile(file_path):
                result['fail_files'].append(file_path)
                LOGGER.error(f"File:{file_path} cannot be found or is not a file")
                continue

            info = Collect.get_file_info(file_path)
            if not info:
                result['fail_files'].append(file_path)
                continue
            result['success_files'].append(file_path)
            result['infos'].append(info)
        return result
