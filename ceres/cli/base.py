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
import argparse
import sys


class BaseCommand:
    """
    ceres command line related classes
    """

    parser = argparse.ArgumentParser(description="ceres tools")
    subparsers = parser.add_subparsers(description="sub-command ")

    def __init__(self):
        self.parser = None

    def _add_common_arguments(self):
        """
        Add public parameters and set execution method to subcommands


        Returns:
            None
        """
        pass

    def _add_arguments(self):
        pass

    @staticmethod
    def register_command(sub_instance):
        """
        Initialize each sub-command class and set the execution method

        Args:
            sub_instance: sub class instance

        Returns:
            None
        """
        sub_instance.parser.set_defaults(func=sub_instance.execute)

    @classmethod
    def run(cls):
        """
        Command line execution entry

        Returns:
            None
        """
        args = cls.parser.parse_args()
        if not vars(args):
            print("No command provided. Please enter a valid command.\n", file=sys.stderr)
            cls.parser.print_help(file=sys.stderr)
            sys.sys.exit(1)
        args.func(args)
