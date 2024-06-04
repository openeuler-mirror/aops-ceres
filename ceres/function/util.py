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
import shlex
import subprocess
from typing import Union, Tuple, NoReturn, Sequence, Any

from libconf import load, ConfigParseError, AttrDict
from jsonschema import validate, ValidationError

from ceres.conf.constant import INFORMATION_ABOUT_RPM_SERVICE, CommandExitCode
from ceres.function.log import LOGGER
from ceres.function.status import PARAM_ERROR


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
    except configparser.MissingSectionHeaderError:
        LOGGER.error(f'Failed to parse {file_path}, file contains no section headers.')
    except configparser.ParsingError:
        LOGGER.error(f'Failed to parse {file_path}.')
    return cf


def validate_data(data: Union[str, dict], schema: dict) -> Tuple[bool, Union[dict, Any]]:
    """
    Validate data against JSON schema

    Args:
        data: Data to be validated (JSON string or dictionary)
        schema: json schema

    Returns:
        Tuple[bool, data]
        a tuple containing two elements (validate result, validated data)).
    """
    try:
        if isinstance(data, str):
            data = json.loads(data)
        validate(instance=data, schema=schema)
        return True, data
    except json.decoder.JSONDecodeError:
        LOGGER.error("Params error:\nFailed to parse json, please check whether the input data is correct.")
        return False, {}
    except ValidationError as error:
        LOGGER.error(f"Params error:{error.message}")
        return False, {}


def execute_shell_command(commands: Sequence[str], **kwargs) -> Tuple[int, str, str]:
    """
    execute shell commands

    Args:
        command(List[str]): shell command list which needs to execute
        **kwargs: keyword arguments, it is used to create Popen object.supported options: env, cwd, bufsize, group and
        so on. you can see more options information in annotation of Popen obejct.

    Returns:
        Tuple[int, str, str]
        a tuple containing three elements (return code, standard output, standard error).

    Example usage:
    >>> return_code, stdout, stderr = execute_shell_command(["ls -al", "wc -l"] **{"env": {"LANG": "en_US.utf-8"}})
    >>> print(return_code, stdout, stderr)
    0, 42, ""
    """
    process = None
    stdout_data = ""
    stderr_data = ""

    try:
        for index, cmd in enumerate(commands):
            cmd_list = shlex.split(cmd)
            if index == 0:
                process = subprocess.Popen(
                    cmd_list,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    stdin=subprocess.PIPE,
                    encoding='utf-8',
                    shell=False,
                    **kwargs,
                )
            else:
                process = subprocess.Popen(
                    cmd_list,
                    stdin=process.stdout,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    encoding='utf-8',
                    shell=False,
                    **kwargs,
                )
        stdout, stderr = process.communicate()
        stderr_data += stderr
        stdout_data += stdout
        return process.returncode, stdout_data.strip(), stderr_data.strip()

    except Exception as error:
        LOGGER.error(error)
        return CommandExitCode.FAIL, stdout_data, str(error)


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
        LOGGER.error(f"Can't find file {gopher_config_path}.")
        return AttrDict()
    except ConfigParseError:
        LOGGER.error(f'Failed to parse file {gopher_config_path}.')
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
    service_name = INFORMATION_ABOUT_RPM_SERVICE.get(plugin_name, {}).get('service_name')
    if service_name is None:
        LOGGER.warning(f"Fail to get service name about {plugin_name}")
        return ""
    return_code, stdout, _ = execute_shell_command([f"systemctl status {service_name}", "grep Active"])

    if return_code == CommandExitCode.SUCCEED:
        return stdout
    return ""


def get_dict_from_file(file_path: str) -> dict:
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
    except (IOError, ValueError) as error:
        LOGGER.error(error)
        data = {}
    if not isinstance(data, dict):
        data = {}
    return data


def save_data_to_file(data: str, file_path: str, mode: str = 'w', encoding: str = 'utf-8') -> NoReturn:
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
    cf = load_conf(file_path)
    file_dir_path = os.path.dirname(file_path)
    if not os.path.exists(file_dir_path):
        os.makedirs(file_dir_path)
    cf[section] = {option: value}
    with open(file_path, 'w') as f:
        cf.write(f)
