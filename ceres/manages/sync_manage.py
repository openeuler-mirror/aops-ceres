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
from ceres.function.status import (
    FILE_NOT_FOUND,
    UNKNOWN_ERROR,
    SUCCESS
)


class SyncManage:
    """
       Sync managed conf to the host
    """

    @staticmethod
    def sync_contents_to_conf(config: dict) -> str:
        """
        Write conf into file
        Args:
            config(dict): filepath and content for file sync,  only. eg:
            {
                "file_path" = "/tmp/test"
                "content" = "contents for this file"
            }
        Returns:
            str: status code
        """
        file_path = config.get('file_path')

        contents = config.get('content')
        lines = contents.split('\n')
        try:
            with open(file_path, "w", encoding="utf-8") as file:
                for line in lines:
                    file.write(line + "\n")
        except Exception as e:
            LOGGER.error("write sync content to conf failed, with msg{}".format(e))
            return UNKNOWN_ERROR

        return SUCCESS
