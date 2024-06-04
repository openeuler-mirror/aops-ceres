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
import copy
import re
from dataclasses import dataclass
from typing import List, Dict, Tuple

import libconf

from ceres.conf import configuration
from ceres.conf.constant import INSTALLABLE_PLUGIN, CommandExitCode
from ceres.function.log import LOGGER
from ceres.function.status import SUCCESS, FAIL
from ceres.function.util import execute_shell_command, load_gopher_config, plugin_status_judge


@dataclass
class Plugin:
    """
    Provide some functions to control plugin,
    such as  start, stop, get running info and so on.

    Attributes:
        _rpm_name: the rpm package name
    """

    __slots__ = "_rpm_name"
    _rpm_name: str

    @property
    def rpm_name(self) -> str:
        return self._rpm_name

    def start_service(self) -> str:
        """
        make plugin running

        Returns:
            str: status code
        """
        plugin_status = self.get_plugin_status()
        if "running" in plugin_status:
            return SUCCESS

        code, _, _ = execute_shell_command([f"systemctl start {self.rpm_name}"])
        if code != CommandExitCode.SUCCEED:
            return FAIL
        return SUCCESS

    def stop_service(self) -> str:
        """
        make plugin stopping

        Returns:
            str: status code
        """
        plugin_status = self.get_plugin_status()
        if "inactive" in plugin_status:
            return SUCCESS

        code, _, _ = execute_shell_command([f"systemctl stop {self.rpm_name}"])
        if code != CommandExitCode.SUCCEED:
            return FAIL
        return SUCCESS

    @classmethod
    def get_installed_plugin(cls) -> List[str]:
        """
        get plugin list is which installed

        Returns:
            List[str]: list about rpm package name
            For example:
                [app1, app2, app3]
        """
        installed_plugin = INSTALLABLE_PLUGIN.copy()
        if len(installed_plugin) == 0:
            return []

        for plugin_name in INSTALLABLE_PLUGIN:
            if not plugin_status_judge(plugin_name):
                installed_plugin.remove(plugin_name)
        return installed_plugin

    def get_plugin_status(self) -> str:
        """
        Get plugin running status which is installed

        Returns:
            str: dead or running

        """
        code, stdout, _ = execute_shell_command([f"systemctl show --property ActiveState --property SubState --value {self.rpm_name}"])
        if code == CommandExitCode.SUCCEED:
            return stdout
        LOGGER.error(f'Failed to get service {self.rpm_name} status!')
        return ""

    @classmethod
    def get_pid(cls, rpm_name) -> str:
        """
        Get main process id when plugin is running

        Returns:
            The str type of main process id
        """
        code, main_pid, _ = execute_shell_command([f"systemctl show --property MainPID --value {rpm_name}"])
        if code == CommandExitCode.SUCCEED:
            return main_pid
        LOGGER.error(f"Failed to get {rpm_name} pid")
        return ""


@dataclass
class GalaGopher(Plugin):
    """
    Some methods only available to Gopher
    """

    _rpm_name: str = 'gala-gopher'

    @classmethod
    def get_collect_items(cls) -> set:
        """
        Get gopher probes name and extend_probes name

        Returns:
            A set which includes probe's name and extend_probe's name
        """
        cfg = load_gopher_config(configuration.gopher.get('CONFIG_PATH'))
        if len(cfg) == 0:
            return set()
        probes = set()
        for probe_list in (cfg.get("probes", ()), cfg.get("extend_probes", ())):
            for probe in probe_list:
                probe_name = probe.get("name", "")
                if probe_name:
                    probes.add(probe_name)
        return probes

    @staticmethod
    def __judge_probe_can_change(probe: libconf.AttrDict, probe_status: Dict[str, str]) -> bool:
        """
            Determine which probe can be changed.
            It must meet the following conditions
            1. probe name in gopher config file, the status is on or off.
            2. probe name in gopher config file, the status is auto and
               it has an option named 'start_check'.

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
        elif probe.get('name', "") in probe_status and probe_status[probe['name']] == 'auto' and 'start_check' in probe:
            return True
        return False

    def __change_probe_status(
        self, probes: Tuple[libconf.AttrDict], gopher_probes_status: dict, res: dict
    ) -> Tuple[dict, dict]:
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
            if self.__judge_probe_can_change(probe, gopher_probes_status):
                probe['switch'] = gopher_probes_status[probe['name']]
                res['success'].append(probe['name'])
                failure_list.pop(probe['name'])
        return res, failure_list

    def change_items_status(self, gopher_probes_status: Dict[str, str]) -> Dict[str, List[str]]:
        """
        Change running status about probe

        Args:
            A dict type data about some probe's status
            for example:

            gopher_probes_status:   {probe1: xx,
                                    probe2: xx,
                                    probe3: xx}

        Returns:
            Dict[str, List[str]]
            for example:
                {
                'success': ['probe1','probe2','probe3'].
                'failure': ['probe1','probe2','probe3'].
                }

        Raises:
            PermissionError: create file failure
        """
        res = {'success': []}
        cfg = load_gopher_config(configuration.gopher.get('CONFIG_PATH'))
        if len(cfg) == 0:
            res['failure'] = list(gopher_probes_status.keys())
            return res

        probes = cfg.get("probes", ())
        extend_probes = cfg.get('extend_probes', ())
        res, failure = self.__change_probe_status(probes, gopher_probes_status, res)
        res, failure = self.__change_probe_status(extend_probes, failure, res)
        res['failure'] = list(failure.keys())

        with open(configuration.gopher.get('CONFIG_PATH'), 'w', encoding='utf8') as cf:
            cf.write(libconf.dumps(cfg))
        return res

    @classmethod
    def get_collect_status(cls) -> List[dict]:
        """
        get probe status

        Returns:
            dict which contains status code,data or error info
        """
        cfg = load_gopher_config(configuration.gopher.get('CONFIG_PATH'))
        if len(cfg) == 0:
            return []
        porbe_list = []
        for probes in (cfg.get('probes', ()), cfg.get('extend_probes', ())):
            for probe in probes:
                probe_info = {'support_auto': False}
                if 'start_check' in probe:
                    probe_info['support_auto'] = True
                if 'name' in probe and 'switch' in probe:
                    probe_info['probe_name'] = probe['name']
                    probe_info['probe_status'] = probe['switch']
                    porbe_list.append(probe_info)
        return porbe_list
