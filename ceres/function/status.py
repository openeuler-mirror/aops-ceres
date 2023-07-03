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
SUCCESS = "Succeed"
FILE_CORRUPTED = "File.Structure.Corrupted"
PARTIAL_SUCCEED = "Partial.Succeed"
FILE_NOT_FOUND = "File.Not.Found"
PARAM_ERROR = "Param.Error"
SERVER_ERROR = "Server.Error"
HTTP_CONNECT_ERROR = "Http.Connect.Error"
UNKNOWN_ERROR = "Unknown.Error"
SERVICE_NOT_EXIST = "Service.Not.Exist"
TOKEN_ERROR = "Token.Error"
REPO_CONTENT_INCORRECT = "Repo.Content.Incorrect"
REPO_NOT_SET = "Repo.Not.Set"
NO_COMMAND = "No.Command"
NOT_PATCH = "Not.Patch"

COMMAND_EXEC_ERROR = "Command.Error"


class StatusCode:
    """
    status code with related message
    """

    mapping = {
        SUCCESS: {'msg': 'operate success'},
        FILE_CORRUPTED: {'msg': 'file structure corrupted'},
        PARTIAL_SUCCEED: {'msg': 'request partial succeed'},
        FILE_NOT_FOUND: {'msg': 'file not found'},
        PARAM_ERROR: {'msg': 'parameter error'},
        HTTP_CONNECT_ERROR: {'msg': 'url connection error'},
        UNKNOWN_ERROR: {"msg": "unknown error"},
        TOKEN_ERROR: {"msg": "the session is invalid"},
        SERVICE_NOT_EXIST: {"msg": "the service is not found"},
        REPO_CONTENT_INCORRECT: {"msg": "repo content cannot parse by yum"},
        REPO_NOT_SET: {"msg": "repo source named aops-update is not set"},
        NO_COMMAND: {"msg": "command not found"},
        NOT_PATCH: {"msg": "no valid hot patch is matched"},
        COMMAND_EXEC_ERROR: {"msg": "the input command is incorrect"},
    }

    @classmethod
    def make_response_body(cls, res) -> dict:
        """
        make response body from mapping

        Args:
            res (int or tuple)

        Returns:
            dict: response body
        """
        if isinstance(res, tuple):
            response_body = cls.make_response_body(res[0])
            response_body.update(res[1])
        else:
            message = cls.mapping.get(res) or cls.mapping.get(UNKNOWN_ERROR)
            response_body = {
                "code": res,
                "msg": message.get("msg"),
            }
        return response_body
