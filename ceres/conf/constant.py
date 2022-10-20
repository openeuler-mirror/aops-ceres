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
import os

BASE_CONFIG_PATH = '/etc/aops'
BASE_SERVICE_PATH = '/usr/lib/systemd/system'

CERES_CONFIG_PATH = os.path.join(BASE_CONFIG_PATH, 'ceres.conf')
DEFAULT_TOKEN_PATH = os.path.join(BASE_CONFIG_PATH, 'ceres_token.json')

INSTALLABLE_PLUGIN = ['gala-gopher']
INFORMATION_ABOUT_RPM_SERVICE = {
    "gala-gopher": {"rpm_name": "gala-gopher", "service_name": "gala-gopher"},
    "mysql": {"rpm_name": "mysql5", "service_name": "mysqld"},
    "kubernetes": {"rpm_name": "kubernetes", "service_name": "kubernetes"},
    "hadoop": {"rpm_name": "hadoop", "service_name": "hadoop"},
    "nginx": {"rpm_name": "nginx", "service_name": "nginx"},
    "docker": {"rpm_name": "docker", "service_name": "docker"},
}
SCANNED_APPLICATION = ["mysql", "kubernetes", "hadoop", "nginx", "docker", "gala-gopher"]

# provide a dict about plugin name and its class name
PLUGIN_WITH_CLASS = {
    'gala-gopher': "GalaGopher"
}
HOST_COLLECT_INFO_SUPPORT = ["cpu", "disk", "memory", "os"]
REGISTER_HELP_INFO = """
    you can choose start or register in manager,
    if you choose register,you need to provide the following information.
    you can input it by '-d' 'json-string' or 
            input it from file by '-f' '/xxxx/.../xx.json'
    
    Required parameter: All information cannot be empty
    host_name               type: string
    host_group_name         type: string
    web_username            type: string
    web_password            type: string
    management              type: boolean,only True or False
    manager_ip              type: string
    manager_port            type: string
    
    optional parameter: 
    agent_port              type: string
    
    for example:
    {
    "web_username":"xxx",
    "web_password": "xxx",
    "host_name": "xxx",
    "host_group_name": "xxx", 
    "manager_ip":"192.168.xx.xx",
    "management":false,
    "manager_port":"11111",
    "agent_port":"12000"
    }

"""
