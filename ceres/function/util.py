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
import configparser
import copy
import json
import os
from socket import socket, AF_INET, SOCK_DGRAM
from typing import Union, List, Any, Tuple, Dict, NoReturn
from subprocess import Popen, PIPE, STDOUT

import requests
from libconf import load, ConfigParseError, AttrDict
from jsonschema import validate, ValidationError

from ceres.manages.token_manage import TokenManage
from ceres.conf import configuration
from ceres.conf.constant import INFORMATION_ABOUT_RPM_SERVICE, DEFAULT_TOKEN_PATH
from ceres.function.log import LOGGER
from ceres.function.status import HTTP_CONNECT_ERROR, SUCCESS, PARAM_ERROR
from ceres.models.custom_exception import InputError
from ceres.function.schema import STRING_ARRAY, REGISTER_SCHEMA


def load_conf(file_path: str) -> configparser.RawConfigParser:
    """
    get ConfigParser object when loads config file
    for example: XX.service

    Returns:
        ConfigParser object
    """
    cf = configparser.RawConfigParser()
    try:
        cf.read(file_path, encoding='utf8')
    except FileNotFoundError:
        LOGGER.error('file not found')
    return cf


def validate_data(data: Any, schema: dict) -> bool:
    """
    validate data type which is expected

    Args:
        data (object): which need to validate
        schema (dict): expected data model

    Returns:
        bool

    Raises:
        ValidationError: the data structure isn't we expected
    """
    try:
        validate(instance=data, schema=schema)
        return True
    except ValidationError:
        return False


def get_shell_data(command_list: List[str], key: bool = True, env=None,
                   stdin: Popen = None) -> Union[str, Popen]:
    """
    execute shell commands

    Args:
        command_list( List[str] ): a list containing the command arguments.
        key (bool): Boolean value
        stdin (Popen): Popen object
        env (Dict[str, str]): temporary environment variables

    Returns:
        get str result when execute shell command success and the key is True or
        get Popen object when execute shell command success and the key is False

    Raises:
        FileNotFoundError: linux has no this command
    """
    if validate_data(command_list, STRING_ARRAY) is False:
        raise InputError('please check your command')
    try:
        res = Popen(command_list, stdout=PIPE, stdin=stdin, stderr=STDOUT, env=env)
    except FileNotFoundError as e:
        raise InputError('linux has no command') from e

    if key:
        return res.stdout.read().decode()
    return res


def load_gopher_config(gopher_config_path: str) -> AttrDict:
    """
    get AttrDict from config file

    Args:
        gopher_config_path(str)

    Returns:
       AttrDict: a subclass of `dict`that exposes string keys as attributes
    """
    try:
        with open(gopher_config_path, 'r', encoding='utf8') as file:
            cfg = load(file)
    except FileNotFoundError:
        LOGGER.error('gopher config not found')
        return AttrDict()
    except ConfigParseError:
        LOGGER.error('gopher config file corrupted')
        return AttrDict()
    return cfg


def plugin_status_judge(plugin_name: str) -> str:
    """
    judge if the plugin is installed

    Args:
        plugin_name(str)

    Returns:
        str: plugin running status
    """
    if plugin_name in INFORMATION_ABOUT_RPM_SERVICE.keys():
        service_name = INFORMATION_ABOUT_RPM_SERVICE.get(plugin_name).get('service_name')
        if service_name is None:
            return ""
    else:
        return ""

    try:
        status_info = get_shell_data(["systemctl", "status", service_name], key=False)
        res = get_shell_data(["grep", "Active"], stdin=status_info.stdout)
        status_info.stdout.close()
    except InputError:
        LOGGER.error(f'Get service {service_name} status error!')
        return ""
    return res


def change_probe_status(probes: Tuple[AttrDict],
                        gopher_probes_status: dict, res: dict) -> Tuple[dict, dict]:
    """
    to change gopher probe status

    Args:
        res(dict): which contains status change success list
        probes(Tuple[AttrDict]): gopher probes info
        gopher_probes_status(dict): probe status which need to change

    Returns:
        Tuple which contains change successful plugin and change fail plugin
    """
    failure_list = copy.deepcopy(gopher_probes_status)
    for probe in probes:
        if judge_probe_can_change(probe, gopher_probes_status):
            probe['switch'] = gopher_probes_status[probe['name']]
            res['success'].append(probe['name'])
            failure_list.pop(probe['name'])
    return res, failure_list


def judge_probe_can_change(probe: AttrDict, probe_status: Dict[str, str]) -> bool:
    """
        Determine which probe can be changed.
        It must meet the following conditions
        1. probe name in gopher config file, the status is on or off.
        2. probe name in gopher config file, the status is auto and it has an option named 'start_check'.

    Args:
        probe(AttrDict):
            e.g AttrDict([('name', 'test'),
                           ('command', ''),
                           ('param', ''),
                           ('start_check', ''),
                           ('check_type', 'count'),
                           ('switch', 'on')])
        probe_status(Dict[str, str]): modification results we expect
            e.g {
                    'probe_name1':on,
                    'probe_name2':off,
                    'probe_name3':auto,
                    ...
                }

    Returns:
        bool
    """
    if probe.get('name', "") in probe_status and probe_status[probe['name']] != 'auto':
        return True
    elif probe.get('name', "") in probe_status and probe_status[
        probe['name']] == 'auto' and 'start_check' in probe:
        return True
    return False


def get_uuid() -> str:
    """
        get uuid about disk

    Returns:
        uuid(str)
    """
    try:
        fstab_info = get_shell_data(['dmidecode'], key=False)
        uuid_info = get_shell_data(['grep', 'UUID'], stdin=fstab_info.stdout)
        fstab_info.stdout.close()
    except InputError:
        LOGGER.error(f'Get system uuid error!')
        return ""
    uuid = uuid_info.replace("-", "").split(':')[1].strip()
    return uuid


def get_host_ip() -> str:
    """
        get host ip by create udp package
    Returns:
        host ip(str)
    """
    sock = socket(AF_INET, SOCK_DGRAM)
    try:
        sock.connect(('8.8.8.8', 80))
        host_ip = sock.getsockname()[0]
    except OSError:
        LOGGER.error("please check internet")
        host_ip = ''
    finally:
        sock.close()
    return host_ip


def get_dict_from_file(file_path: str) -> Dict:
    """
        Get json data from file and return related dict
    Args:
        file_path(str): the json data file absolute path

    Returns:
        dict(str)
    """
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        LOGGER.error('file not found')
        data = {}
    except json.decoder.JSONDecodeError:
        LOGGER.error('file structure is not json')
        data = {}
    if not isinstance(data, dict):
        data = {}
    return data


def register_info_to_dict(string: str) -> Dict:
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
        LOGGER.error('Parameter error')
        res = {}
    if not isinstance(res, dict):
        res = {}
    return res


def save_data_to_file(data: str,
                      file_path: str, mode: str = 'w', encoding: str = 'utf-8') -> NoReturn:
    """
        save data to specified path,create it if it doesn't exist

    Args:
        data:
        file_path(str): file absolute path
        mode(str): select write mode, default 'w'
        encoding(str): select encoding mode, default utf8
    """
    file_dir_path = os.path.dirname(file_path)
    if not os.path.exists(file_dir_path):
        os.makedirs(file_dir_path)
    with open(file_path, mode=mode, encoding=encoding) as f:
        f.write(data)


def update_ini_data_value(file_path: str, section: str, option: str, value) -> NoReturn:
    """
    modify or create an option
    Args:
        file_path(str): file absolute path
        section(str):   section name
        option(str):    option name
        value(str)      section value


    """
    cf = configparser.ConfigParser()
    try:
        cf.read(file_path, encoding='utf8')
    except FileNotFoundError:
        LOGGER.error('ceres config file has been deleted')
    except configparser.MissingSectionHeaderError:
        LOGGER.error('ceres config file has been damaged')
    except configparser.ParsingError:
        LOGGER.error('ceres config file has been damaged')
    file_dir_path = os.path.dirname(file_path)
    if not os.path.exists(file_dir_path):
        os.makedirs(file_dir_path)
    cf[section] = {option: value}
    with open(file_path, 'w') as f:
        cf.write(f)


def register(register_info: dict) -> int:
    """
    register on manager
    Args:
        register_info(dict): It contains the necessary information to register an account
        for example:
        {
          "web_username": "string",
          "web_password": "string",
          "manager_ip": "string",
          "manager_port": "string",
          "host_name": "string",
          "host_group_name": "string",
          "management": true,
          "client_port": "12000"
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
    data['username'] = register_info.get('web_username')
    data['password'] = register_info.get('web_password')
    data['host_id'] = get_uuid()
    data['public_ip'] = get_host_ip()
    data['client_port'] = register_info.get('client_port') or \
                         configuration.ceres.get('PORT')

    manager_ip = register_info.get('manager_ip')
    manager_port = register_info.get('manager_port')
    url = f'http://{manager_ip}:{manager_port}/manage/host/add'
    try:
        ret = requests.post(url, data=json.dumps(data),
                            headers={'content-type': 'application/json'}, timeout=5)
    except requests.exceptions.ConnectionError as e:
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
