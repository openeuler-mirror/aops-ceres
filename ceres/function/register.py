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

from ceres.conf import configuration
from ceres.conf.constant import DEFAULT_TOKEN_PATH
from ceres.function.log import LOGGER
from ceres.function.schema import REGISTER_SCHEMA
from ceres.function.status import HTTP_CONNECT_ERROR, SUCCESS, PARAM_ERROR
from ceres.function.util import save_data_to_file, validate_data
from ceres.manages.collect_manage import Collect
from ceres.manages.token_manage import TokenManage


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
          "username": "admin",
          "password": "admin",
          "zeus_ip": "127.0.0.1",
          "zeus_port": "11111",
          "host_name": "host_name",
          "host_group_name": "host_group_name",
          "management": true,
          "ceres_port": "12000"
        }
    Returns:
        str: status code
    """
    if not validate_data(register_info, REGISTER_SCHEMA):
        return PARAM_ERROR

    data = {}
    data['host_name'] = register_info.get('host_name')
    data['host_group_name'] = register_info.get('host_group_name')
    data['management'] = register_info.get('management') or False
    data['username'] = register_info.get('username')
    data['password'] = register_info.get('password')
    data['host_id'] = Collect.get_uuid()
    data['public_ip'] = Collect.get_host_ip()
    data['agent_port'] = register_info.get('ceres_port') or \
                          configuration.ceres.get('PORT')
    data["os_version"] = Collect.get_system_info()

    zeus_ip = register_info.get('zeus_ip')
    zeus_port = register_info.get('zeus_port')
    url = f'http://{zeus_ip}:{zeus_port}/manage/host/add'
    try:
        ret = requests.post(url, data=json.dumps(data),
                            headers={'content-type': 'application/json'}, timeout=5)
    except requests.exceptions.RequestException as e:
        LOGGER.error(e)
        return HTTP_CONNECT_ERROR
    ret_data = json.loads(ret.text)
    if ret_data.get('code') == SUCCESS:
        TokenManage.set_value(ret_data.get('token'))
        save_data_to_file(json.dumps({"access_token": ret_data.get('token')}),
                          DEFAULT_TOKEN_PATH)
        return SUCCESS
    LOGGER.error(ret_data)
    return int(ret_data.get('code'))
