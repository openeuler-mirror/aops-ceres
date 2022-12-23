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
import re
import json
import os
import grp
import pwd
from socket import socket, AF_INET, SOCK_DGRAM
from typing import Any, Dict, Union, List

from ceres.models.custom_exception import InputError
from ceres.function.log import LOGGER
from ceres.function.util import get_shell_data


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
        host_info = {"resp": {}}

        for info_name in info_type:
            func_name = getattr(self, f"_get_{info_name}_info")
            host_info["resp"][info_name] = func_name()

        return host_info

    @staticmethod
    def get_system_info() -> str:
        """
            get system name and its version

        Returns:
            str: e.g openEuler 21.09
        """
        try:
            os_data = get_shell_data(['cat', '/etc/os-release'])
        except InputError:
            LOGGER.error('Failed to get system version info,linux has no command!')
            return ''

        res = re.search('(?=PRETTY_NAME=).+', os_data)
        if res:
            return res.group()[12:].strip('"').replace(' ', '-')
        LOGGER.warning('Failed to get os version info, '
                       'please check file /etc/os-release and try it again')
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
        res = {
            'os_version': self.get_system_info(),
            'bios_version': self.__get_bios_version(),
            'kernel': self.__get_kernel_version()
        }
        return res

    @staticmethod
    def __get_bios_version() -> str:
        """
            get bios version number

        Returns:
            str
        """
        try:
            bios_data = get_shell_data(['dmidecode', '-t', 'bios'])
        except InputError:
            LOGGER.error('Failed to get system info,linux has no command dmidecode!')
            return ''

        res = re.search('(?=Version:).+', bios_data)

        if res:
            return res.group()[8:].strip()
        LOGGER.warning('Failed to get bios version, please check dmidecode and try it again')
        return ''

    @staticmethod
    def __get_kernel_version() -> str:
        """
            get kernel version number

        Returns:
            str
        """
        try:
            kernel_data = get_shell_data(['uname', '-r'])
        except InputError:
            LOGGER.error('Failed to get kernel version info,linux has no command!')
            return ''
        res = re.search(r'[\d\.]+-[\d\.]+[\d]', kernel_data)
        if res:
            return res.group()
        LOGGER.warning('Failed to get kernel version, please check dmidecode and try it again')
        return ''

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
        try:
            lscpu_data = get_shell_data(['lscpu'], env={"LANG": "en_US.utf-8"})
        except InputError:
            LOGGER.error('Failed to get cpu info,linux has no command lscpu or grep.')
            return {}

        info_list = re.findall('.+:.+', lscpu_data)
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
            "l3_cache": cpu_info.get('L3 cache')
        }

        return res

    @staticmethod
    def __get_total_online_memory() -> str:
        """
        get memory size by lsmem

        Returns:
            str: memory size
        """
        try:
            lsmem_data = get_shell_data(['lsmem'])
        except InputError:
            LOGGER.error('Failed to get  host memory info, Linux has no command dmidecode')
            return ''

        res = re.search("(?=Total online memory:).+", lsmem_data)
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
        res = {}
        if self.__get_total_online_memory():
            res['size'] = self.__get_total_online_memory()

        try:
            memory_data = get_shell_data(['dmidecode', '-t', 'memory']).split('Memory Device')
        except InputError:
            LOGGER.error('Failed to get host memory info, Linux has no command dmidecode')
            return res

        if len(memory_data) == 1:
            LOGGER.warning('Failed to read memory info by dmidecode')
            return res

        info = []
        for module in memory_data:
            module_info_list = re.findall('.+:.+', module)

            module_info_dict = {}
            for module_info in module_info_list:
                part_info = module_info.split(':')
                module_info_dict[part_info[0].strip()] = part_info[1].strip()

            if module_info_dict.get('Size') is None or \
                    module_info_dict.get('Size') == 'No Module Installed':
                continue

            memory_info = {
                "size": module_info_dict.get('Size'),
                "type": module_info_dict.get('Type'),
                "speed": module_info_dict.get('Speed'),
                "manufacturer": module_info_dict.get('Manufacturer')
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
        try:
            lshw_data = get_shell_data(['lshw', '-json', '-c', 'disk'])
        except InputError:
            LOGGER.error('Failed to get hard disk info, Linux has no command lshw')
            return []

        # Convert the command result to a json string
        # lshw_data e.g  "{...},{...},{...}"
        lshw_data = f"[{lshw_data}]"

        try:
            disk_info_list = json.loads(lshw_data)
        except json.decoder.JSONDecodeError:
            LOGGER.warning("Json conversion error, "
                           "please check command 'lshw -json -c disk'")
            disk_info_list = []

        res = []
        if disk_info_list:
            for disk_info in disk_info_list:
                tmp = {
                    "model": disk_info.get('product'),
                    "capacity": f"{disk_info.get('size', 0) // 10 ** 9}GB"
                }
                res.append(tmp)

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
        except UnicodeDecodeError:
            LOGGER.error(f'{file_path} may not be a text file')
            return {}
        file_attr = os.stat(file_path)
        file_mode = oct(file_attr.st_mode)[4:]
        file_owner = pwd.getpwuid(file_attr.st_uid)[0]
        file_group = grp.getgrgid(file_attr.st_gid)[0]
        info = {
            'path': file_path,
            'file_attr': {
                'mode': file_mode,
                'owner': file_owner,
                'group': file_group
            },
            'content': content
        }
        return info

    @staticmethod
    def get_uuid() -> str:
        """
            get uuid about disk

        Returns:
            uuid(str)
        """
        try:
            fstab_info = get_shell_data(['dmidecode'], key=False)
            uuid_info = get_shell_data(['grep', 'UUID'], stdin=fstab_info.stdout)
            fstab_info.stdout.close()
        except InputError:
            LOGGER.error(f'Failed to get system uuid!')
            return ""
        uuid = uuid_info.replace("-", "").split(':')[1].strip()
        return uuid

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
            list: e.g
                [ pcakage-version-1,pcakage-version-2]
        """
        try:
            package_info = get_shell_data(['rpm', '-qai'], key=False)
            pkg_src_name = get_shell_data(["grep", "Source RPM"], stdin=package_info.stdout)
        except InputError:
            LOGGER.error("Failed to query installed packages.")
            return []

        package_list = set()
        for package_source_name in pkg_src_name.splitlines():
            package_list.add(package_source_name.rsplit("-", 2)[0].split(':')[1].strip())
        return list(package_list)
