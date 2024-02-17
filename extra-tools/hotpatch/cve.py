#!/usr/bin/python3
# ******************************************************************************
# Copyright (c) Huawei Technologies Co., Ltd. 2023-2023. All rights reserved.
# licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# ******************************************************************************/
from .hotpatch import Hotpatch


class Cve(object):
    __slots__ = ['_cve_id', '_hotpatches']

    def __init__(self, id, **kwargs):
        """
        id(str): cve id
        """
        self._cve_id = id
        self._hotpatches = []

    @property
    def hotpatches(self):
        return self._hotpatches

    def add_hotpatch(self, hotpatch: Hotpatch):
        self._hotpatches.append(hotpatch)

    @property
    def cve_id(self):
        return self._cve_id
