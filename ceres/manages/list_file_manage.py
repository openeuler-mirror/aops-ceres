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
# Author: Lay
# Description: default
# Date: 2023/6/14 16:31
import os
import subprocess

from ceres.function.log import LOGGER
from ceres.function.status import (
    UNKNOWN_ERROR,
    SUCCESS
)
from ceres.function.util import execute_shell_command


class ListFileManage:
    """
       list directory file
    """

    @staticmethod
    def list_file(directory_path: str):
        """
        list the pam.d file
        Args:
            directory_path: the path of directory
        Returns:
            str: status code
        """
        file_list_res = []
        try:
            command = "ls -l " + directory_path + " | awk '{print $9}'"
            _, stdout, _ = execute_shell_command(command)
            file_list = stdout.split("\n")
            for file in file_list:
                if file:
                    file_path_res = os.path.join(directory_path, file)
                    file_list_res.append(file_path_res)
            return SUCCESS, {"resp": file_list_res}
        except Exception as e:
            LOGGER.error("list the pam.d file failed, with msg{}".format(e))
            return UNKNOWN_ERROR, {"resp": list()}
