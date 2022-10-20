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
STRING_ARRAY = {
    "type": "array",
    "items": {
        "type": "string",
        "minLength": 1
    }
}

CHANGE_COLLECT_ITEMS_SCHEMA = {
    "type": "object",
    "additionalProperties": {
        "type": "object",
        "additionalProperties": {
            "enum": ["on", "off", "auto"]
        }
    }
}
REGISTER_SCHEMA = {
    "type": "object",
    "required": [
        "host_name",
        "host_group_name",
        "web_username",
        "web_password",
        "management",
        "manager_ip",
        "manager_port"
    ],
    "properties": {
        "host_name": {"type": "string", "minLength": 1},
        "host_group_name": {"type": "string", "minLength": 1},
        "web_username": {"type": "string", "minLength": 1},
        "web_password": {"type": "string", "minLength": 1},
        "management": {"enum": [True, False]},
        "manager_ip": {"type": "string", "minLength": 8},
        "manager_port": {"type": "string", "minLength": 2},
        "agent_port": {"type": "string", "minLength": 1}
    }
}
