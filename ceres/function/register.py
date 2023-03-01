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
import json
from typing import Dict

import requests

from ceres.function.log import LOGGER
from ceres.function.schema import REGISTER_SCHEMA
from ceres.function.status import HTTP_CONNECT_ERROR, SUCCESS, PARAM_ERROR
from ceres.function.util import validate_data
from ceres.manages.collect_manage import Collect


def register_info_to_dict(string: str) -> dict:
    """
    Convert JSON string to dictionary
    Args:
        string(str)

    Returns:
        dict
    """
    try:
        res = json.loads(string)
    except json.decoder.JSONDecodeError:
        LOGGER.error('Json conversion error, the data entered is not'
                     ' json format.')
        res = {}
    if not isinstance(res, dict):
        res = {}
    return res


def register(register_info: dict) -> int:
    """
    register on manager
    Args:
        register_info(dict): It contains the necessary information to register an account
        for example:
            {
              "ssh_user": "root",
              "password": "password",
              "zeus_ip": "127.0.0.1",
              "zeus_port": 11111,
              "host_name": "host_name",
              "host_group_name": "aops",
              "management": true,
              "ssh_port":22,
              "access_token": "token-string"
            }

    Returns:
        str: status code
    """
    if not validate_data(register_info, REGISTER_SCHEMA):
        return PARAM_ERROR

    headers = {'content-type': 'application/json',
               "access_token": register_info.pop('access_token')}
    register_info['host_ip'] = Collect.get_host_ip()
    url = f'http://{register_info.pop("zeus_ip")}:{register_info.pop("zeus_port")}/manage/host/add'
    try:
        ret = requests.post(url, data=json.dumps(register_info),
                            headers=headers, timeout=5)
    except requests.exceptions.RequestException as e:
        LOGGER.error(e)
        return HTTP_CONNECT_ERROR

    if ret.status_code != SUCCESS:
        LOGGER.warning(ret.text)
        return ret.status_code

    ret_data = json.loads(ret.text)
    if ret_data.get('code') == SUCCESS:
        return SUCCESS
    LOGGER.error(ret_data)
    return int(ret_data.get('code'))
