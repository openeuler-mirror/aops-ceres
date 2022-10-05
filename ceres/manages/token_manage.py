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
import threading
import json
from typing import NoReturn, Any

import connexion
from flask import jsonify

from ceres.conf.constant import DEFAULT_TOKEN_PATH
from ceres.function.log import LOGGER
from ceres.function.status import StatusCode, TOKEN_ERROR


class TokenManage:
    _mutex = threading.Lock()
    token = ''
    flag = False

    def __init__(self):
        """
        Class instance initialization.
        """
        if TokenManage.flag:
            return
        TokenManage.token = ''
        TokenManage.flag = True

    @classmethod
    def load_token(cls) -> NoReturn:
        """
            load token from file
        """
        try:
            with open(DEFAULT_TOKEN_PATH, "r") as f:
                row_data = json.load(f)
                cls.token = row_data.get('access_token', '')
        except FileNotFoundError:
            cls.token = ''
        except json.decoder.JSONDecodeError:
            cls.token = ''

    @classmethod
    def set_value(cls, value: str) -> NoReturn:
        """
            update _TOKEN
        Args:
            value: token string
        """
        TokenManage._mutex.acquire()
        cls.token = value
        TokenManage._mutex.release()

    @classmethod
    def get_value(cls) -> str:
        """
            get token
        """
        TokenManage._mutex.acquire()
        if cls.token == "":
            cls.load_token()
        cls._mutex.release()
        return cls.token

    @classmethod
    def validate_token(cls, func) -> Any:
        """
        validate if the token is correct

        Returns:
            return func when token is correct,
            return error info when token is incorrect.
        """

        def wrapper(*arg, **kwargs):
            token = cls.get_value()
            access_token = connexion.request.headers.get('access_token')
            if token == '' or access_token != token:
                LOGGER.warning("token is incorrect when request %s" % connexion.request.path)
                return jsonify(StatusCode.make_response_body(TOKEN_ERROR))
            return func(*arg, **kwargs)

        return wrapper
