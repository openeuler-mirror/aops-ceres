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
    },
    "minItems": 1
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
        "zeus_ip",
        "zeus_port",
        "access_token",
        "host_name",
        "host_group_name",
        "management",
        "ssh_user",
        "password",
        "ssh_port"
    ],
    "properties": {
        "host_name": {"type": "string", "minLength": 1},
        "host_group_name": {"type": "string", "minLength": 1},
        "ssh_user": {"type": "string", "minLength": 1},
        "password": {"type": "string", "minLength": 1},
        "management": {"enum": [True, False]},
        "zeus_ip": {"type": "string", "minLength": 8},
        "zeus_port": {"type": "integer", "minimum": 1},
        "ssh_port": {"type": "integer", "minimum": 1},
        "access_token": {"type": "string", "minLength": 1}
    }
}

REPO_SET_SCHEMA = {
    "type": "object",
    "required": [
        "repo_info",
        "check_items",
        "check"
    ],
    "properties": {
        "repo_info": {
            "type": "object",
            "required": ["name", "repo_content", "dest"],
            "properties": {
                "name": {"type": "string", "minLength": 1},
                "repo_content": {"type": "string", "minLength": 1},
                "dest": {"type": "string", "minLength": 1}
            }
        },
        "check_items": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },
        "check": {"enum": [True, False]}
    }
}

CVE_SCAN_SCHEMA = {
    "type": "object",
    "required": [
        "check",
        "check_items",
        "basic"
    ],
    "properties": {
        "check_items": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },
        "check": {"enum": [True, False]},
        "basic": {"enum": [True, False]},
    }
}

CVE_FIX_SCHEMA = {
    "type": "object",
    "required": [
        "check",
        "check_items",
        "cves"
    ],
    "properties": {
        "check_items": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },
        "check": {"enum": [True, False]},
        "cves": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["cve_id", "hotpatch"],
                "properties": {
                    "cve_id": {"type": "string", "minLength": 1},
                    "hotpatch": {"enum": [True, False]}
                }

            }
        }
    }
}

HOST_INFO_SCHEMA = {
    "type": "array",
    "items": {
        "enum": ["os", "cpu", "memory", "disk"]
    }
}
