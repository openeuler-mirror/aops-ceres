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

from ceres.function.log import LOGGER
from ceres.function.status import FILE_NOT_FOUND, UNKNOWN_ERROR, SUCCESS, PARAM_ERROR


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

        if not os.path.exists(directory_path):
            return FILE_NOT_FOUND, {"resp": file_list_res}

        if os.path.isfile(directory_path):
            return PARAM_ERROR, {"resp": file_list_res}

        try:
            file_list_res = [os.path.join(directory_path, file) for file in os.listdir(directory_path)]
            return SUCCESS, {"resp": file_list_res}
        except OSError as e:
            LOGGER.error(f"Failed to read the file list under the path with message {e}")
            return UNKNOWN_ERROR, {"resp": list()}
