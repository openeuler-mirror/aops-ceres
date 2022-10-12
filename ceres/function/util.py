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
import json
import os
from typing import Union, List, Any, Dict, NoReturn
from subprocess import Popen, PIPE, STDOUT

from libconf import load, ConfigParseError, AttrDict
from jsonschema import validate, ValidationError

from ceres.conf.constant import INFORMATION_ABOUT_RPM_SERVICE
from ceres.function.log import LOGGER
from ceres.models.custom_exception import InputError
from ceres.function.schema import STRING_ARRAY


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
