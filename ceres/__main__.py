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

from ceres.command import (
    collect_command_manage,
    cve_command_manage,
    plugin_command_manage,
    register_on_manager,
    sync_conf_manage,
    list_file_manage,
)
from ceres.function.log import LOGGER


def main():
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers()

    subparse_register = subparsers.add_parser('register', help='register in aops-zeus')
    register_group = subparse_register.add_mutually_exclusive_group(required=True)
    register_group.add_argument('-f', '--path', type=str, help="file contains data which register need")
    register_group.add_argument('-d', '--data', type=str, help="json data which register need")
    subparse_register.set_defaults(function=register_on_manager)

    subparsers_collection = subparsers.add_parser("collect", help='collect some information')
    collection_group = subparsers_collection.add_mutually_exclusive_group(required=True)
    collection_group.add_argument('--host', type=str)
    collection_group.add_argument('--file', type=str)
    collection_group.add_argument('--application', action="store_true")
    subparsers_collection.set_defaults(function=collect_command_manage)

    subparsers_plugin = subparsers.add_parser("plugin", help='manage plugin')
    plugin_group = subparsers_plugin.add_mutually_exclusive_group(required=True)
    plugin_group.add_argument('--start', type=str)
    plugin_group.add_argument('--stop', type=str)
    plugin_group.add_argument('--change-collect-items', type=str)
    plugin_group.add_argument('--info', action="store_true")
    subparsers_plugin.set_defaults(function=plugin_command_manage)

    subparsers_cve = subparsers.add_parser("apollo", help="cve/bugfix related action")
    cve_group = subparsers_cve.add_mutually_exclusive_group(required=True)
    cve_group.add_argument("--set-repo", type=str)
    cve_group.add_argument("--scan", type=str)
    cve_group.add_argument("--fix", type=str)
    cve_group.add_argument("--remove-hotpatch", type=str)
    subparsers_cve.set_defaults(function=cve_command_manage)

    subparsers_sync = subparsers.add_parser("sync", help='sync conf file')
    sync_group = subparsers_sync.add_mutually_exclusive_group(required=True)
    sync_group.add_argument("--conf", type=str)
    subparsers_sync.set_defaults(function=sync_conf_manage)

    subparsers_list = subparsers.add_parser("ragdoll", help='list pam.d file')
    list_group = subparsers_list.add_mutually_exclusive_group(required=True)
    list_group.add_argument("--list", type=str)
    subparsers_list.set_defaults(function=list_file_manage)

    args = parser.parse_args()
    try:
        args.function(args)
    except AttributeError:
        LOGGER.error('error: you can get help for -h')
        exit(1)


if __name__ == '__main__':
    main()
