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
import argparse
import json
from typing import NoReturn

from ceres.conf.constant import CERES_CONFIG_PATH, INSTALLABLE_PLUGIN, PLUGIN_WITH_CLASS
from ceres.function.log import LOGGER
from ceres.function.register import register, register_info_to_dict
from ceres.function.schema import (
    CHANGE_COLLECT_ITEMS_SCHEMA,
    CVE_FIX_SCHEMA,
    CVE_SCAN_SCHEMA,
    HOST_INFO_SCHEMA,
    REPO_SET_SCHEMA,
    STRING_ARRAY
)
from ceres.function.status import SUCCESS, StatusCode
from ceres.function.util import (
    convert_string_to_json,
    get_dict_from_file,
    plugin_status_judge, update_ini_data_value,
    validate_data
)
from ceres.manages import plugin_manage
from ceres.manages.collect_manage import Collect
from ceres.manages.vulnerability_manage import VulnerabilityManage


def register_on_manager(args: argparse.Namespace) -> NoReturn:
    """
    get args from command-line and register on manager

    Args:
        args(argparse.Namespace): args parser

    Returns:
        NoReturn
    """
    if args.data is not None:
        register_info = register_info_to_dict(args.data)
    else:
        register_info = get_dict_from_file(args.path)

    if register_info and register(register_info) == SUCCESS:
        print('Register Success')
    else:
        print('Register Fail')


def change_collect_items(collect_items_status: dict) -> dict:
    """
    change collect items about plugin

    Args:
        collect_items_status(dict): A dict which contains collect items and its status.
        e.g
            {
                "gala-gopher": {
                    "redis": "on",
                    "system_inode": "on",
                    "tcp": "on",
                    "haproxy": "auto",
                    "lvs": "auto"
                }
            }

    Returns:
        Response which contains update result or error info
    """

    def generate_failed_result(plugin_name: str) -> dict:
        """
        generate plugin items change result

        Returns:
            dict: e.g
                {"success": [], "failure":[items1, items2, ...]}
        """
        return {
            'success': [],
            'failure': list(collect_items_status.get(plugin_name).keys())
        }

    res = {}
    for plugin_name in collect_items_status.keys():
        if plugin_name not in INSTALLABLE_PLUGIN:
            LOGGER.warning(f'{plugin_name} is not supported by ceres')
            res[plugin_name] = generate_failed_result(plugin_name)
            continue

        if not plugin_status_judge(plugin_name):
            LOGGER.warning(f'{plugin_name} is not installed by ceres')
            res[plugin_name] = generate_failed_result(plugin_name)
            continue

        plugin_class_name = PLUGIN_WITH_CLASS.get(plugin_name, '')
        if hasattr(plugin_manage, plugin_class_name):
            plugin = getattr(plugin_manage, plugin_class_name)
            if hasattr(plugin, 'change_items_status'):
                res[plugin_name] = plugin().change_items_status(
                    collect_items_status[plugin_name])
        else:
            LOGGER.warning(f'{plugin_name} is not supported by collect items')
            res[plugin_name] = generate_failed_result(plugin_name)

    return {"resp": res}


def collect_command_manage(args):
    if args.host:
        data = convert_string_to_json(args.host)
        if not validate_data(data, HOST_INFO_SCHEMA):
            exit(1)
        print(json.dumps(Collect().get_host_info(data)))
    elif args.application:
        print(json.dumps(Collect.get_application_info()))
    elif args.file:
        data = convert_string_to_json(args.file)
        if not validate_data(data, STRING_ARRAY):
            exit(1)
        print(json.dumps(Collect.collect_file(data)))
    else:
        print("Please check the input parameters!")
        exit(1)


def plugin_command_manage(args):
    if args.start:
        if args.start not in INSTALLABLE_PLUGIN:
            LOGGER.error("unsupported plugin, please check and try again")
            exit(1)
        print(plugin_manage.Plugin(args.start).start_service())
    elif args.stop:
        if args.stop not in INSTALLABLE_PLUGIN:
            LOGGER.error("unsupported plugin, please check and try again")
            exit(1)
        print(plugin_manage.Plugin(args.stop).stop_service())
    elif args.change_collect_items:
        data = convert_string_to_json(args.change_collect_items)
        if not validate_data(data, CHANGE_COLLECT_ITEMS_SCHEMA):
            exit(1)
        print(json.dumps(change_collect_items(data)))
    elif args.info:
        print(json.dumps(Collect.get_plugin_info()))
    else:
        print("Please check the input parameters!")
        exit(1)

def cve_command_manage(args):
    if args.set_repo:
        data = convert_string_to_json(args.set_repo)
        if not validate_data(data, REPO_SET_SCHEMA):
            exit(1)

        res = StatusCode.make_response_body(VulnerabilityManage().repo_set(data))
        print(json.dumps(res))
    elif args.scan:
        data = convert_string_to_json(args.scan)
        if not validate_data(data, CVE_SCAN_SCHEMA):
            exit(1)
        status_code, cve_scan_info = VulnerabilityManage().cve_scan(data)
        result = {
            "unfixed_cves": cve_scan_info["unfixed_cves"],
            "fixed_cves": cve_scan_info["fixed_cves"],
            "os_version": Collect.get_system_info(),
            "installed_packages": Collect.get_installed_packages()
        }
        print(json.dumps(StatusCode.make_response_body((status_code, {"result": result}))))
    elif args.fix:
        data = convert_string_to_json(args.fix)
        if not validate_data(data, CVE_FIX_SCHEMA):
            exit(1)
        status_code, cve_fix_result = VulnerabilityManage().cve_fix(data.get("cves"))
        res = StatusCode.make_response_body((status_code, {"result": cve_fix_result}))
        print(json.dumps(res))
    else:
        print("Please check the input parameters!")
        exit(1)