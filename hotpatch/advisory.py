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


class Advisory(object):
    __slots__ = ['_id', '_adv_type', '_title', '_severity', '_description', '_updated', '_hotpatches', '_cves']

    def __init__(self, id, adv_type, title, severity, description, updated="1970-01-01 08:00:00", **kwargs):
        """
        id(str): the id of advisory
        adv_type(str): advisory type
        title(str): advisory title
        severity(str): advisory severity
        description(str): advisory description
        updated(str): advisory updated time
        """
        self._id = id
        self._adv_type = adv_type
        self._title = title
        self._severity = severity
        self._description = description
        self._updated = updated
        self._cves = {}
        self._hotpatches = []

    @property
    def id(self):
        return self._id

    @property
    def adv_type(self):
        return self._adv_type

    @property
    def title(self):
        return self._title

    @property
    def severity(self):
        return self._severity

    @property
    def description(self):
        return self._description

    @property
    def updated(self):
        return self._updated

    @property
    def cves(self):
        return self._cves

    @cves.setter
    def cves(self, advisory_cves):
        self._cves = advisory_cves

    @property
    def hotpatches(self):
        return self._hotpatches

    def add_hotpatch(self, hotpatch: Hotpatch):
        self._hotpatches.append(hotpatch)
