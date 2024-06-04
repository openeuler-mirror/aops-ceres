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
import platform
import pwd
import unittest
import warnings
from unittest import mock
import xml.etree.ElementTree as ET

from ceres.conf.constant import CommandExitCode
from ceres.manages.collect_manage import Collect


class Socket:
    def connect(self):
        pass

    def getsockname(self):
        pass

    def close(self):
        pass


class TestCollectManage(unittest.TestCase):
    def setUp(self) -> None:
        warnings.simplefilter('ignore', ResourceWarning)

    @mock.patch.object(Collect, "_Collect__get_total_online_memory")
    @mock.patch('ceres.manages.collect_manage.execute_shell_command')
    def test_get_memory_info_should_return_memory_info_when_execute_shell_command_is_correct(
        self, mock_execute_shell_command, mock_memory_size
    ):
        mock_shell_stdout = """
            Memory Device
                    Array Handle: 0x0006
                    Error Information Handle: Not Provided
                    Total Width: 72 bits
                    Data Width: 64 bits
                    Size: 16 GB
                    Form Factor: DIMM
                    Set: None
                    Locator: DIMM170 J31
                    Bank Locator: SOCKET 1 CHANNEL 7 DIMM 0
                    Type: DDR4
                    Type Detail: Synchronous Registered (Buffered)
                    Speed: 2000 MT/s
                    Manufacturer: Test1
                    Serial Number: 129C7699
                    Asset Tag: 1939
                    Part Number: HMA82GR7CJR4N-WM
            Memory Device
                    Form Factor: DIMM
                    Set: None
                    Size: 32 GB
                    Locator: DIMM170 J31
                    Bank Locator: SOCKET 1 CHANNEL 7 DIMM 0
                    Type: DDR4
                    Type Detail: Synchronous Registered (Buffered)
                    Speed: 2000 MT/s
                    Manufacturer: Test2
            """
        mock_execute_shell_command.return_value = CommandExitCode.SUCCEED, mock_shell_stdout, ""
        mock_memory_size.return_value = '48G'
        expect_res = {
            'total': 2,
            'size': "48G",
            'info': [
                {'size': '16 GB', 'type': 'DDR4', 'speed': '2000 MT/s', 'manufacturer': 'Test1'},
                {'size': '32 GB', 'type': 'DDR4', 'speed': '2000 MT/s', 'manufacturer': 'Test2'},
            ],
        }

        res = Collect()._get_memory_info()
        self.assertEqual(expect_res, res)

    @mock.patch.object(Collect, "_Collect__get_total_online_memory")
    @mock.patch('ceres.manages.collect_manage.execute_shell_command')
    def test_get_memory_info_should_return_empty_list_when_memory_info_is_not_showed(
        self, mock_execute_shell_command, mock_memory_size
    ):
        mock_shell_stdout = """
                    Memory Device
                    Array Handle: 0x0006
                    Error Information Handle: Not Provided
                    Total Width: Unknown
                    Data Width: Unknown
                    Size: No Module Installed
                    Form Factor: DIMMis
                    Set: None
                    Locator: DIMM171 J32
                    Bank Locator: SOCKET 1 CHANNEL 7 DIMM 1
                    Type: Unknown
                    Type Detail: Unknown Synchronous
                    Speed: Unknown
        """
        mock_execute_shell_command.return_value = CommandExitCode.SUCCEED, mock_shell_stdout, ""
        mock_memory_size.return_value = '4G'
        expect_res = {'info': [], 'total': 0, "size": "4G"}

        res = Collect()._get_memory_info()
        self.assertEqual(expect_res, res)

    @mock.patch.object(Collect, "_Collect__get_total_online_memory")
    @mock.patch('ceres.manages.collect_manage.execute_shell_command')
    def test_get_memory_info_should_return_empty_dict_when_execute_shell_command_failed(
        self, mock_execute_shell_command, mock_memory_size
    ):
        """
        This situation exists in the virtual machine
        """
        mock_execute_shell_command.return_value = CommandExitCode.FAIL, "", ""
        mock_memory_size.return_value = ''
        res = Collect()._get_memory_info()
        self.assertEqual({'info': [], 'size': None, 'total': None}, res)

    @mock.patch.object(Collect, "_Collect__get_total_online_memory")
    @mock.patch('ceres.manages.collect_manage.execute_shell_command')
    def test_get_memory_info_should_return_empty_dict_when_execute_shell_command_failed(
        self, mock_execute_shell_command, mock_memory_size
    ):
        mock_execute_shell_command.return_value = CommandExitCode.FAIL, "", ""
        mock_memory_size.return_value = ''
        res = Collect()._get_memory_info()
        self.assertEqual({'info': [], 'size': None, 'total': None}, res)

    @mock.patch('ceres.manages.collect_manage.execute_shell_command')
    def test_get_memory_size_should_return_memory_size_when_execute_shell_command_succeed(
        self, mock_execute_shell_command
    ):
        mock_shell_stdout = '''
            Memory block size:       128M
            Total online memory:     2.5G
            Total offline memory:      0B
        '''
        mock_execute_shell_command.return_value = CommandExitCode.SUCCEED, mock_shell_stdout, ""
        res = Collect._Collect__get_total_online_memory()
        self.assertEqual('2.5G', res)

    @mock.patch('ceres.manages.collect_manage.execute_shell_command')
    def test_get_memory_size_should_return_empty_str_when_execute_shell_command_succeed_but_get_memory_info_failed(
        self, mock_execute_shell_command
    ):
        mock_shell_stdout = '''
            Memory block size:       128M
        '''
        mock_execute_shell_command.return_value = CommandExitCode.SUCCEED, mock_shell_stdout, ""
        res = Collect._Collect__get_total_online_memory()
        self.assertEqual("", res)

    @mock.patch('ceres.manages.collect_manage.execute_shell_command')
    def test_get_memory_size_should_return_empty_str_when_execute_shell_command_fail(self, mock_execute_shell_command):
        mock_execute_shell_command.return_value = CommandExitCode.FAIL, "", ""
        res = Collect._Collect__get_total_online_memory()
        self.assertEqual("", res)

    @mock.patch('ceres.manages.collect_manage.execute_shell_command')
    def test_get_cpu_info_should_return_correct_info_when_execute_command_successful(self, mock_execute_shell_command):
        mock_shell_stdout = (
            'Architecture:                    x86_64\n'
            'CPU(s):                          1\n'
            'Model name:                      AMD Test\n'
            'Vendor ID:                       AuthenticAMD\n'
            'L1d cache:                       32 KiB\n'
            'L1i cache:                       32 KiB\n'
            'L2 cache:                        512 KiB\n'
            'L3 cache:                        8 MiB\n'
        )
        mock_execute_shell_command.return_value = CommandExitCode.SUCCEED, mock_shell_stdout, ""
        expect_res = {
            "architecture": "x86_64",
            "core_count": "1",
            "model_name": "AMD Test",
            "vendor_id": "AuthenticAMD",
            "l1d_cache": "32 KiB",
            "l1i_cache": "32 KiB",
            "l2_cache": "512 KiB",
            "l3_cache": "8 MiB",
        }
        res = Collect._get_cpu_info()
        self.assertEqual(expect_res, res)

    @mock.patch('ceres.manages.collect_manage.execute_shell_command')
    def test_get_cpu_info_should_return_null_when_execute_command_successful_but_not_get_expected_information(
        self, mock_execute_shell_command
    ):
        mock_execute_shell_command.return_value = CommandExitCode.SUCCEED, "", ""
        expect_res = {
            "architecture": None,
            "core_count": None,
            "model_name": None,
            "vendor_id": None,
            "l1d_cache": None,
            "l1i_cache": None,
            "l2_cache": None,
            "l3_cache": None,
        }
        res = Collect._get_cpu_info()
        self.assertEqual(expect_res, res)

    @mock.patch('ceres.manages.collect_manage.execute_shell_command')
    def test_get_cpu_info_should_return_empty_dict_when_host_has_no_command_lscpu(self, mock_execute_shell_command):
        mock_execute_shell_command.return_value = CommandExitCode.FAIL, "", ""
        res = Collect._get_cpu_info()
        self.assertEqual(
            {
                "architecture": None,
                "core_count": None,
                "model_name": None,
                "vendor_id": None,
                "l1d_cache": None,
                "l1i_cache": None,
                "l2_cache": None,
                "l3_cache": None,
            },
            res,
        )

    @mock.patch.object(platform, "uname")
    def test_get_kernel_version_should_return_cpu_info_when_execute_command_successfully(self, mock_uname_info):
        mock_uname_info.return_value = platform.uname_result(
            "Linux", "localhost", "5.10.0-5.10.0.24.oe1.x86_64", "openeuler", "x86_64"
        )
        res = Collect.get_current_kernel_version()
        self.assertEqual('5.10.0-5.10.0.24.oe1.x86_64', res)

    @mock.patch.object(platform, "uname")
    def test_get_kernel_version_should_return_empty_string_when_get_kernel_version_failed(self, mock_uname_info):
        mock_uname_info.return_value = platform.uname_result("Linux", "localhost", "", "openeuler", "x86_64")
        res = Collect.get_current_kernel_version()
        self.assertEqual('', res)

    @mock.patch('ceres.manages.collect_manage.execute_shell_command')
    def test_get_bios_version_should_return_cpu_info_when_execute_command_successfully(
        self, mock_execute_shell_command
    ):
        mock_execute_shell_command.return_value = CommandExitCode.SUCCEED, "VirtualBox", ""
        expect_res = 'VirtualBox'
        res = Collect._Collect__get_bios_version()
        self.assertEqual(expect_res, res)

    @mock.patch('ceres.manages.collect_manage.execute_shell_command')
    def test_get_bios_version_should_return_cpu_info_when_host_has_no_command_dmidecode(
        self, mock_execute_shell_command
    ):
        mock_execute_shell_command.return_value = CommandExitCode.FAIL, "", ""
        res = Collect._Collect__get_bios_version()
        self.assertEqual('', res)

    @mock.patch('ceres.manages.collect_manage.execute_shell_command')
    def test_get_os_version_should_return_cpu_info_when_execute_command_successfully(self, mock_execute_shell_command):
        mock_shell_stdout = """
                    NAME="openEuler"
                    VERSION="21.09"
                    ID="openEuler"
                    VERSION_ID="21.09"
                    PRETTY_NAME="openEuler 21.09"
                    ANSI_COLOR="0;31"
        """
        mock_execute_shell_command.return_value = CommandExitCode.SUCCEED, mock_shell_stdout, ""
        expect_res = 'openEuler-21.09'
        res = Collect.get_os_version()
        self.assertEqual(expect_res, res)

    @mock.patch('ceres.manages.collect_manage.execute_shell_command')
    def test_get_os_version_should_return_empty_string_when_execute_command_successfully_but_not_get_expected_information(
        self, mock_execute_shell_command
    ):
        mock_execute_shell_command.return_value = CommandExitCode.SUCCEED, 'test_info', ""
        res = Collect.get_os_version()
        self.assertEqual('', res)

    @mock.patch('ceres.manages.collect_manage.execute_shell_command')
    def test_get_system_info_should_return_cpu_info_when_host_has_no_command_cat(self, mock_execute_shell_command):
        mock_execute_shell_command.return_value = CommandExitCode.FAIL, "", ""
        res = Collect.get_os_version()
        self.assertEqual('', res)

    @mock.patch.object(pwd, 'getpwuid')
    @mock.patch.object(grp, 'getgrgid')
    @mock.patch('ceres.function.util.os.stat')
    @mock.patch.object(os.path, 'getsize')
    @mock.patch.object(os, 'access')
    def test_get_file_info_should_return_file_content_when_target_file_exist_and_not_executable_and_less_than_1m(
        self, mock_os_access, mock_getsize, mock_os_stat, mock_getgrgid, mock_getpwduid
    ):
        file_path = mock.Mock(return_value='test')
        mock_os_access.return_value = False
        mock_os_stat.st_mode.return_value = 33198
        mock_os_stat.st_uid.return_value = '123456'
        mock_os_stat.st_gid.return_value = '123456'
        mock_getsize.return_value = 1024
        mock_getgrgid.return_value = (1001,)
        mock_getpwduid.return_value = (1001,)
        with mock.patch('builtins.open', mock.mock_open(read_data='123456')):
            info = Collect.get_file_info(file_path)
        self.assertEqual('123456', info.get('content'))

    @mock.patch.object(os, 'access')
    def test_get_file_info_should_return_empty_dict_when_target_file_can_execute(self, mock_os_access):
        file_path = mock.Mock(return_value='test')
        mock_os_access.return_value = True
        info = Collect.get_file_info(file_path)
        self.assertEqual({}, info)

    @mock.patch.object(os.path, 'getsize')
    @mock.patch.object(os, 'access')
    def test_get_file_info_should_return_empty_dict_when_target_file_is_larger_than_1m(
        self, mock_os_access, mock_getsize
    ):
        file_path = mock.Mock(return_value='test')
        mock_os_access.return_value = False
        mock_getsize.return_value = 1024 * 1024 * 2
        info = Collect.get_file_info(file_path)
        self.assertEqual({}, info)

    @mock.patch.object(os.path, 'getsize')
    @mock.patch.object(os, 'access')
    def test_get_file_info_should_return_empty_dict_when_target_file_is_not_encoded_by_utf8(
        self, mock_os_access, mock_getsize
    ):
        file_path = mock.Mock(return_value='test')
        mock_os_access.return_value = False
        mock_getsize.return_value = 1024 * 1024
        with mock.patch('builtins.open', mock.mock_open()) as mock_file:
            mock_file.side_effect = UnicodeDecodeError('', bytes(), 1, 1, '')
            info = Collect.get_file_info(file_path)
        self.assertEqual({}, info)

    @mock.patch('ceres.manages.collect_manage.execute_shell_command')
    def test_get_uuid_should_return_uuid_string_when_all_is_right(self, mock_execute_shell_command):
        mock_execute_shell_command.return_value = CommandExitCode.SUCCEED, "UUID: m-o-c-k-uuid", ""
        self.assertEqual('mockuuid', Collect.get_uuid())

    @mock.patch('ceres.manages.collect_manage.execute_shell_command')
    def test_get_uuid_should_return_empty_string_when_command_execution_failed(self, mock_execute_shell_command):
        mock_execute_shell_command.return_value = CommandExitCode.FAIL, "", ""
        self.assertEqual('', Collect.get_uuid())

    @mock.patch("ceres.manages.collect_manage.socket")
    def test_get_host_ip_should_return_host_ip_when_all_is_right(self, mock_socket):
        Socket.connect = mock.Mock(return_value='')
        Socket.getsockname = mock.Mock(return_value=('mock_host_ip',))
        Socket.close = mock.Mock(return_value='')
        mock_socket.return_value = Socket()
        self.assertEqual('mock_host_ip', Collect.get_host_ip())

    @mock.patch("ceres.manages.collect_manage.socket")
    def test_get_host_ip_should_return_empty_string_when_socket_connect_failed(self, mock_socket):
        Socket.connect = mock.Mock(side_effect=OSError())
        mock_socket.return_value = Socket()
        self.assertEqual('', Collect.get_host_ip())

    @mock.patch('ceres.manages.collect_manage.execute_shell_command')
    def test_get_installed_package_should_return_installed_packages_when_execute_command_successfully(
        self, mock_execute_shell_command
    ):
        mock_shell_stdout = (
            "Source RPM: perl-Encode-Locale-1.05-12.oe1.src.rpm\n"
            "Source RPM: glib-networking-2.58.0-7.oe1.src.rpm\n"
            "Source RPM: dnf-4.2.15-8.oe1.src.rpm"
        )
        mock_execute_shell_command.return_value = CommandExitCode.SUCCEED, mock_shell_stdout, ""
        expected_result = [
            {"name": "perl-Encode-Locale", "version": "1.05-12"},
            {"name": "glib-networking", "version": "2.58.0-7"},
            {"name": "dnf", "version": "4.2.15-8"},
        ]
        self.assertEqual(expected_result, Collect.get_installed_packages())

    @mock.patch('ceres.manages.collect_manage.execute_shell_command')
    def test_get_installed_package_should_return_empty_list_when_execute_command_failed(
        self, mock_execute_shell_command
    ):
        mock_execute_shell_command.return_value = CommandExitCode.FAIL, "", ""
        self.assertEqual([], Collect.get_installed_packages())

    @mock.patch.object(Collect, "get_current_kernel_version")
    @mock.patch.object(Collect, "_Collect__get_bios_version")
    @mock.patch.object(Collect, "get_os_version")
    def test_get_os_info_should_return_os_info_when_execute_command_failed(
        self, mock_system_info, mock_bios_version, mock_kernel_version
    ):
        mock_system_info.return_value = "mock_os_version"
        mock_bios_version.return_value = "mock_bios_version"
        mock_kernel_version.return_value = "5.10.0-5.10.0.24.oe1.x86_64"
        expected_result = {
            "os_version": "mock_os_version",
            "bios_version": "mock_bios_version",
            "kernel": "5.10.0-5.10.0.24",
        }
        self.assertEqual(expected_result, Collect()._get_os_info())

    @mock.patch.object(Collect, "_get_os_info")
    @mock.patch.object(Collect, "_get_disk_info")
    def test_get_host_info_should_return_host_info_when_input_info_type_is_correct(self, mock_disk_info, mock_os_info):
        os_info = {
            "os_version": "mock_os_version",
            "bios_version": "mock_bios_version",
            "kernel": "mock_kernel_version",
        }
        disk_info = [{"capacity": "40GB", "model": "MOCK HARDDISK"}]
        mock_os_info.return_value = os_info
        mock_disk_info.return_value = disk_info
        expected_result = {"disk": disk_info, "os": os_info}
        self.assertEqual(expected_result, Collect().get_host_info(['os', 'disk']))

    @mock.patch('ceres.manages.collect_manage.execute_shell_command')
    def test_get_disk_info_should_return_disk_info_when_shell_command_execute_succeed_and_only_contain_description(
        self, mock_execute_shell_command
    ):
        cmd_output = """<?xml version="1.0" standalone="yes" ?>
<!-- generated by lshw-B.012.18 -->
<!-- GCC 7.3.0 -->
<!-- Linux 4.19.90-2003.4.0.0036.oe1.x86_64 #1 SMP Mon Mar 23 19:10:41 UTC 2020 x86_64 -->
<!-- GNU libc 2 (glibc 2.28) -->
<list>
  <node id="virtio3" claimed="true" class="disk">
   <description>Virtual I/O device</description>
   <physid>0</physid>
   <businfo>virtio@3</businfo>
   <logicalname>/dev/vda</logicalname>
   <size units="bytes">42949672960</size>
   <configuration>
    <setting id="driver" value="virtio_blk" />
    <setting id="logicalsectorsize" value="512" />
    <setting id="sectorsize" value="512" />
    <setting id="signature" value="64860148" />
   </configuration>
   <capabilities>
    <capability id="partitioned" >Partitioned disk</capability>
    <capability id="partitioned:dos" >MS-DOS partition table</capability>
   </capabilities>
   <hints>
    <hint name="icon" value="disc" />
   </hints>
  </node>
</list>
"""
        mock_execute_shell_command.return_value = CommandExitCode.SUCCEED, cmd_output, ""
        self.assertEqual([{"model": "Virtual I/O device", "capacity": "40.0 GB"}], Collect()._get_disk_info())

    @mock.patch('ceres.manages.collect_manage.execute_shell_command')
    def test_get_disk_info_should_return_disk_info_when_shell_command_execute_succeed_and_has_no_description_or_product(
        self, mock_execute_shell_command
    ):
        cmd_output = """<?xml version="1.0" standalone="yes" ?>
<!-- generated by lshw-B.012.18 -->
<!-- GCC 7.3.0 -->
<!-- Linux 4.19.90-2003.4.0.0036.oe1.x86_64 #1 SMP Mon Mar 23 19:10:41 UTC 2020 x86_64 -->
<!-- GNU libc 2 (glibc 2.28) -->
<list>
  <node id="virtio3" claimed="true" class="disk">
   <physid>0</physid>
   <businfo>virtio@3</businfo>
   <logicalname>/dev/vda</logicalname>
   <size units="bytes">42949672960</size>
   <configuration>
    <setting id="driver" value="virtio_blk" />
    <setting id="logicalsectorsize" value="512" />
    <setting id="sectorsize" value="512" />
    <setting id="signature" value="64860148" />
   </configuration>
   <capabilities>
    <capability id="partitioned" >Partitioned disk</capability>
    <capability id="partitioned:dos" >MS-DOS partition table</capability>
   </capabilities>
   <hints>
    <hint name="icon" value="disc" />
   </hints>
  </node>
</list>
"""
        mock_execute_shell_command.return_value = CommandExitCode.SUCCEED, cmd_output, ""
        self.assertEqual([{"model": "unknown", "capacity": "40.0 GB"}], Collect()._get_disk_info())

    @mock.patch('ceres.manages.collect_manage.execute_shell_command')
    def test_get_disk_info_should_return_disk_info_when_shell_command_execute_succeed_and_contain_description_and_product(
        self, mock_execute_shell_command
    ):
        cmd_output = """<?xml version="1.0" standalone="yes" ?>
<!-- generated by lshw-B.012.18 -->
<!-- GCC 7.3.0 -->
<!-- Linux 4.19.90-2003.4.0.0036.oe1.x86_64 #1 SMP Mon Mar 23 19:10:41 UTC 2020 x86_64 -->
<!-- GNU libc 2 (glibc 2.28) -->
<list>
  <node id="virtio3" claimed="true" class="disk">
   <description>Virtual I/O device</description>
   <product>ATA Disk</product>
   <physid>0</physid>
   <businfo>virtio@3</businfo>
   <logicalname>/dev/vda</logicalname>
   <size units="bytes">42949672960</size>
   <configuration>
    <setting id="driver" value="virtio_blk" />
    <setting id="logicalsectorsize" value="512" />
    <setting id="sectorsize" value="512" />
    <setting id="signature" value="64860148" />
   </configuration>
   <capabilities>
    <capability id="partitioned" >Partitioned disk</capability>
    <capability id="partitioned:dos" >MS-DOS partition table</capability>
   </capabilities>
   <hints>
    <hint name="icon" value="disc" />
   </hints>
  </node>
</list>
"""
        mock_execute_shell_command.return_value = CommandExitCode.SUCCEED, cmd_output, ""
        self.assertEqual([{"model": "ATA Disk", "capacity": "40.0 GB"}], Collect()._get_disk_info())

    @mock.patch('ceres.manages.collect_manage.execute_shell_command')
    def test_get_disk_info_should_return_disk_info_when_shell_command_execute_succeed_and_only_contain_product(
        self, mock_execute_shell_command
    ):
        cmd_output = """<?xml version="1.0" standalone="yes" ?>
<!-- generated by lshw-B.012.18 -->
<!-- GCC 7.3.0 -->
<!-- Linux 4.19.90-2003.4.0.0036.oe1.x86_64 #1 SMP Mon Mar 23 19:10:41 UTC 2020 x86_64 -->
<!-- GNU libc 2 (glibc 2.28) -->
<list>
  <node id="virtio3" claimed="true" class="disk">
   <product>MOCK PRODUCT</product>
   <physid>0</physid>
   <businfo>virtio@3</businfo>
   <logicalname>/dev/vda</logicalname>
   <size units="bytes">42949672960</size>
   <configuration>
    <setting id="driver" value="virtio_blk" />
    <setting id="logicalsectorsize" value="512" />
    <setting id="sectorsize" value="512" />
    <setting id="signature" value="64860148" />
   </configuration>
   <capabilities>
    <capability id="partitioned" >Partitioned disk</capability>
    <capability id="partitioned:dos" >MS-DOS partition table</capability>
   </capabilities>
   <hints>
    <hint name="icon" value="disc" />
   </hints>
  </node>
</list>
"""
        mock_execute_shell_command.return_value = CommandExitCode.SUCCEED, cmd_output, ""
        self.assertEqual([{"model": "MOCK PRODUCT", "capacity": "40.0 GB"}], Collect()._get_disk_info())

    @mock.patch('ceres.manages.collect_manage.execute_shell_command')
    def test_get_disk_info_should_return_disk_info_when_shell_command_execute_fail(self, mock_execute_shell_command):
        mock_execute_shell_command.return_value = CommandExitCode.FAIL, "", ""
        self.assertEqual([], Collect()._get_disk_info())

    @mock.patch.object(ET, "ElementTree")
    @mock.patch('ceres.manages.collect_manage.execute_shell_command')
    def test_get_disk_info_should_return_disk_info_when_shell_command_execute_succeed_but_decode_error(
        self, mock_execute_shell_command, mock_parse_xml
    ):
        mock_cmd_output = """<?xml version="1.0" standalone="yes" ?>
<!-- generated by lshw-B.012.18 -->
<!-- GCC 7.3.0 -->
<!-- Linux 4.19.90-2003.4.0.0036.oe1.x86_64 #1 SMP Mon Mar 23 19:10:41 UTC 2020 x86_64 -->
<!-- GNU libc 2 (glibc 2.28) -->
"""
        mock_execute_shell_command.return_value = CommandExitCode.SUCCEED, mock_cmd_output, ""
        mock_parse_xml.side_effect = ET.ParseError
        self.assertEqual([], Collect()._get_disk_info())
