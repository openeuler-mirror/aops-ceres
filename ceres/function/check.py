#!/usr/bin/python3
# ******************************************************************************
# Copyright (c) Huawei Technologies Co., Ltd. 2021-2023. All rights reserved.
# licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN 'AS IS' BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# ******************************************************************************/
from typing import List, Tuple


class PreCheck(object):
    """
    Provide some inspection methods for the specific indicators.

    """

    @classmethod
    def execute_check(cls, check_items: List[str]) -> Tuple[bool, list]:
        """
        execute items check func

        Args:
            check_items(list): list of check items

        Return:
            Tuple[bool, list]: check result and all items check result
        """
        check_result, check_items_result = [], []
        for check_item in check_items:
            check_func = getattr(cls, f"{check_item}_check", None)
            if check_func:
                check_items_result.append({"item": check_item, "result": check_func()[0], "log": check_func()[1]})

            else:
                check_items_result.append(
                    {"item": check_item, "result": False, "log": f"No check method is provided fo {check_item}!"}
                )
                check_result.append(False)
        return all(check_result), check_items_result
