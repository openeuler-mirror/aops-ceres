#!/usr/bin/python3
# ******************************************************************************
# Copyright (c) Huawei Technologies Co., Ltd. 2023-2023. All rights reserved.
# licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# ******************************************************************************/
import gzip
import subprocess
from typing import Optional

import dnf
from dnf.cli import commands
from dnf.cli.commands.upgrade import UpgradeCommand
from dnf.cli.option_parser import OptionParser
from dnfpluginscore import _, logger

SUCCEED = 0
FAIL = 255


def cmd_output(cmd):
    try:
        result = subprocess.Popen(cmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        result.wait()
        return result.stdout.read().decode('utf-8'), result.returncode
    except Exception as e:
        print("error: ", e)
        return str(e), FAIL


@dnf.plugin.register_command
class UpgradeEnhanceCommand(dnf.cli.Command):
    SYMVERS_FILE = "/boot/symvers-%s.gz"
    previous_boot_kernel = None

    aliases = ['upgrade-en']
    summary = _(
        'upgrade with KABI(Kernel Application Binary Interface) check. If the loaded kernel modules \
                have KABI compatibility with the new version kernel rpm, the kernel modules can be installed \
                and used in the new version kernel without recompling.'
    )

    @staticmethod
    def set_argparser(parser):
        parser.add_argument(
            'packages',
            nargs='*',
            help=_('Package to upgrade'),
            action=OptionParser.ParseSpecGroupFileCallback,
            metavar=_('PACKAGE'),
        )
        parser.add_argument(
            "-f",
            dest='force',
            default=False,
            action='store_true',
            help=_('force retain kernel rpm package if kernel kabi check fails'),
        )

    def configure(self):
        """Verify that conditions are met so that this command can run.

        These include that there are enabled repositories with gpg
        keys, and that this command is being run by the root user.
        """
        demands = self.cli.demands
        demands.sack_activation = True
        demands.available_repos = True
        demands.resolving = True
        demands.root_user = True
        commands._checkGPGKey(self.base, self.cli)
        if not self.opts.filenames:
            commands._checkEnabledRepo(self.base)
        self.upgrade_minimal = None
        self.all_security = None
        self.skipped_grp_specs = None

    def run(self):
        # if kernel kabi check failed, need change back to the default boot kernel version
        self.previous_boot_kernel = self.get_default_boot_kernel()
        self.upgrade()

    @staticmethod
    def get_default_boot_kernel() -> Optional[str]:
        """
        Get default boot kernel version.

        Returns:
            str: default boot kernel
        """
        cmd = ["grubby", "--default-kernel"]
        # 'grubby --default-kernel' shows boot default kernel version in the system
        # e.g.
        # [root@openEuler ~]# grubby --default-kernel
        # /boot/vmlinuz-4.19.90-2112.8.0.0131.oe1.x86_64
        output, return_code = cmd_output(cmd)
        default_boot_kernel = output.split('\n')[0]
        if return_code != SUCCEED:
            return None
        return default_boot_kernel

    @staticmethod
    def restore_default_boot_kernel(target_boot_kernel: str):
        """
        Restore default boot kernel version.

        Args:
            target_boot_kernel(str): target boot kernel
        """
        # 'grubby --set-default=/boot/vmlinuz-4.19.90-2112.8.0.0131.oe1.x86_64' can set default boot kernel version
        # to kernel-4.19.90-2112.8.0.0131.oe1.x86_64
        if not target_boot_kernel:
            print("Get default boot kernel before upgrade failed.")
            return

        cmd = ["grubby", "--set-default=%s" % target_boot_kernel]
        try:
            # e.g. 4.19.90-2112.8.0.0131.oe1.x86_64
            target_boot_kernel_vere = target_boot_kernel.split('-', 1)[1]
            target_boot_kernel_nevra = "kernel-%s" % target_boot_kernel_vere
        except IndexError as e:
            print(
                "Parse target boot kernel failed. Please check if target boot kernel path is correct: %s."
                % target_boot_kernel,
                "\nRestore the default boot kernel failed. Please manually check the default boot kernel to prevent unexpected kernel switching after reboot.",
            )
            return

        output, return_code = cmd_output(cmd)
        if return_code != SUCCEED:
            print(
                "Restore the default boot kernel failed: %s. Please manually check the default boot kernel to prevent unexpected kernel switching after reboot."
                % target_boot_kernel_nevra
            )
            return
        print("Restore the default boot kernel succeed: %s." % target_boot_kernel_nevra)

    def run_transaction(self):
        """
        Process kabi check for kernel rpm package installed this time. If the kernel rpm pakcgae fails kabi check,
        uninstall it.
        """
        for ts_item in self.base.transaction:
            if ts_item.action not in dnf.transaction.FORWARD_ACTIONS:
                continue
            if ts_item.pkg.name == 'kernel':
                kernel_pkg = str(ts_item.pkg)
                success = self.kabi_check(kernel_pkg)
                if not success and not self.opts.force:
                    print('Gonna remove %s due to kabi check failed.' % kernel_pkg)
                    # rebuild rpm database for processing kernel rpm remove operation
                    self.rebuild_rpm_db()
                    # when processing remove operation, do not achieve the expected result of installing related rpm,
                    # it indicates that the upgrade task failed
                    self.remove_rpm(kernel_pkg)
                    # change back to the default boot kernel version before upgrade
                    self.restore_default_boot_kernel(self.previous_boot_kernel)
                    exit(1)

    def remove_rpm(self, pkg: str):
        """
        Remove rpm package via command line.

        Args:
            pkg(str): package name
            e.g.
            kernel-5.10.0-153.18.0.94.oe2203sp2.x86_64
        """
        remove_cmd = ["dnf", "remove", pkg, "-y"]
        output, return_code = cmd_output(remove_cmd)
        if return_code != SUCCEED:
            print('Remove package failed: %s.' % pkg)
            print(output)
        else:
            print('Remove package succeed: %s.' % pkg)

    def rebuild_rpm_db(self):
        """
        Rebuild rpm database for processing kernel rpm remove operation.
        """
        rebuilddb_cmd = ["rpm", "--rebuilddb"]
        output, return_code = cmd_output(rebuilddb_cmd)
        if return_code != SUCCEED:
            print('Rebuild rpm database failed.')
        else:
            print('Rebuild rpm database succeed.')

    def kabi_check(self, pkg: str) -> bool:
        """
        Process kabi check after upgrading kernel rpm.

        Args:
            pkg(str): package name
            e.g.
            kernel-5.10.0-153.18.0.94.oe2203sp2.x86_64

        Returns:
            bool: kabi check result
        """
        print("Kabi check for %s:" % pkg)
        # version-release.arch
        evra = pkg.split("-", 1)[1]
        symvers_file = self.SYMVERS_FILE % (evra)

        target_symvers_symbol_crc_mapping, return_code = self.get_target_symvers_symbol_crc_mapping(symvers_file)
        if return_code != SUCCEED:
            print('[Fail] Cannot find the symvers file of %s.', pkg)
            return False
        module_actual_symbol_crc_mapping = self.get_module_actual_symbol_crc_mapping()

        module_different_symbol_crc_mapping = self.compare_actual_and_target_symvers_symbol_crc_mapping(
            module_actual_symbol_crc_mapping, target_symvers_symbol_crc_mapping
        )

        sum_module_num = len(module_actual_symbol_crc_mapping)
        fail_module_num = len(module_different_symbol_crc_mapping)
        pass_module_num = sum_module_num - fail_module_num

        reminder_statement = "Here are %s loaded kernel modules in this system, %s pass, %s fail." % (
            sum_module_num,
            pass_module_num,
            fail_module_num,
        )

        if fail_module_num > 0:
            print('[Fail] %s' % reminder_statement)
            self.output_symbol_crc_difference_report(module_different_symbol_crc_mapping)
            return False

        print('[Success] %s' % reminder_statement)
        return True

    def output_symbol_crc_difference_report(self, module_different_symbol_crc_mapping: dict):
        """
        Format the output for symbol crc difference report.
        The output is as follows:

            Failed modules are as follows:
            No. Module           Difference
            1   upatch           ipv6_chk_custom_prefix : 0x0c994af2 != 0x0c994af3
                                 pcmcia_reset_card      : 0xe9bed965 != null
            2   crct10dif_pclmul crypto_unregister_shash: 0x60f5b0b7 != 0x0c994af3
                                 __fentry__             : 0xbdfb6dbb != null
        """
        print('Failed modules are as follows:')

        title = ['No.', 'Module', 'Difference']
        # column width
        sequence_width = len(title[0])
        module_width = len(title[1])
        symbol_width = crc_info_width = 0

        for seq, module_name in enumerate(module_different_symbol_crc_mapping):
            # the sequence starts from 1
            seq = seq + 1
            sequence_width = max(sequence_width, len(str(seq)))
            different_symbol_crc_mapping = module_different_symbol_crc_mapping[module_name]
            module_width = max(module_width, len(module_name))
            for symbol, crc_list in different_symbol_crc_mapping.items():
                symbol_width = max(symbol_width, len(symbol))
                crc_info = "%s != %s" % (crc_list[0], crc_list[1])
                crc_info_width = max(crc_info_width, len(crc_info))

        # print title
        print('%-*s %-*s %s' % (sequence_width, title[0], module_width, title[1], title[2]))

        for seq, module_name in enumerate(module_different_symbol_crc_mapping):
            seq = seq + 1
            print('%-*s %-*s' % (sequence_width, seq, module_width, module_name), end='')
            different_symbol_crc_mapping = module_different_symbol_crc_mapping[module_name]
            is_first_symbol = True
            for symbol, crc_list in different_symbol_crc_mapping.items():
                crc_info = "%s != %s" % (crc_list[0], crc_list[1])
                if is_first_symbol:
                    print(' %-*s: %s' % (symbol_width, symbol, crc_info), end='')
                    is_first_symbol = False
                else:
                    print(
                        ' %-*s %-*s: %s' % (sequence_width + module_width, "", symbol_width, symbol, crc_info), end=''
                    )
                print('')

    def compare_actual_and_target_symvers_symbol_crc_mapping(
        self, module_actual_symbol_crc_mapping: dict, target_symvers_symbol_crc_mapping: dict
    ) -> dict:
        """
        Compare the actual symbol crc mapping with the target symvers symbol crc mapping.

        Args:
            module_actual_symbol_crc_mapping(dict): module actual symbol crc mapping
            e.g.
            {
                'upatch': {
                    'ipv6_chk_custom_prefix': '0x0c994af3',
                    'pcmcia_reset_card': '0xe9bed965',
                }
            }

            target_symvers_symbol_crc_mapping(dict): target symvers symbol crc mapping
            e.g.
            {
                'ipv6_chk_custom_prefix': '0x0c994af2',
                'pcmcia_reset_card': '0xe9bed965',
            }

        Returns:
            dict: module different symbol crc mapping
            e.g.
            {
                'upatch': {
                    'ipv6_chk_custom_prefix': ['0x0c994af3', '0x0c994af2'].
                }
            }
        """
        module_different_symbol_crc_mapping = dict()
        for module_name, actual_symbol_crc_mapping in module_actual_symbol_crc_mapping.items():
            different_symbol_crc_mapping = dict()
            for actual_symbol, actual_crc in actual_symbol_crc_mapping.items():
                if actual_symbol not in target_symvers_symbol_crc_mapping:
                    continue
                elif target_symvers_symbol_crc_mapping[actual_symbol] != actual_symbol_crc_mapping[actual_symbol]:
                    different_symbol_crc_mapping[actual_symbol] = [
                        actual_crc,
                        target_symvers_symbol_crc_mapping[actual_symbol],
                    ]
            if not different_symbol_crc_mapping:
                continue
            module_different_symbol_crc_mapping[module_name] = different_symbol_crc_mapping
        return module_different_symbol_crc_mapping

    def get_module_actual_symbol_crc_mapping(self) -> dict:
        """
        Get the module actual symbol crc mapping of the driver modules currently being loaded in the system.

        Returns:
            dict: module actual symbol crc mapping
            e.g.
            {
                'upatch': {
                    'ipv6_chk_custom_prefix': '0x0c994af3',
                    'pcmcia_reset_card': '0xe9bed965',
                }
            }
        """
        module_actual_symbol_crc_mapping = dict()
        lsmod_cmd = ["lsmod"]
        # 'lsmod' shows all modules loaded in the system
        # e.g.
        # [root@openEuler ~]# lsmod
        # Module                  Size  Used by
        # upatch                 53248  0
        # nft_fib_inet           16384  1
        # nft_fib_ipv4           16384  1 nft_fib_inet
        list_output, return_code = cmd_output(lsmod_cmd)
        if return_code != SUCCEED:
            return module_actual_symbol_crc_mapping

        content = list_output.split('\n')
        for line in content[1:]:
            if not line:
                continue
            module_name = line.split()[0]
            modinfo_cmd = ['modinfo', module_name, '-n']
            # 'modinfo module_name -n' shows module path information
            # e.g.
            # [root@openEuler ~]# modinfo upatch -n
            # /lib/modules/5.10.0-153.12.0.92.oe2203sp2.x86_64/weak-updates/syscare/upatch.ko
            module_path_output, return_code = cmd_output(modinfo_cmd)
            if return_code != SUCCEED:
                continue

            module_path = module_path_output.split('\n')[0]
            actual_symbol_crc_mapping, return_code = self.get_actual_symbol_crc_mapping(module_path)
            if return_code != SUCCEED:
                continue

            module_actual_symbol_crc_mapping[module_name] = actual_symbol_crc_mapping
        return module_actual_symbol_crc_mapping

    def get_actual_symbol_crc_mapping(self, module_path: str) -> (dict, int):
        """
        Get actual symbol crc mapping for specific module.

        Args:
            module_path(str): loaded module path

        Returns:
            dict, bool: actual symbol crc mapping, return code
        """
        actual_symbol_crc_mapping = dict()
        modprobe_cmd = ['modprobe', '--dump', module_path]
        # 'modprobe --dump module_path' shows module related kabi information
        # e.g.
        # [root@openEuler ~]# modprobe --dump \
        # /lib/modules/5.10.0-153.12.0.92.oe2203sp2.x86_64/weak-updates/syscare/upatch.ko
        # 0xe32130cf	module_layout
        # 0x9c4befaf	kmalloc_caches
        # 0xeb233a45	__kmalloc
        # 0xd6ee688f	vmalloc
        # 0x349cba85	strchr
        # 0x754d539c	strlen
        crc_symbol_output_lines, return_code = cmd_output(modprobe_cmd)
        if return_code != SUCCEED:
            return actual_symbol_crc_mapping, return_code

        crc_symbol_output = crc_symbol_output_lines.split('\n')
        for crc_symbol_line in crc_symbol_output:
            if not crc_symbol_line:
                continue
            crc_symbol_line = crc_symbol_line.split()
            crc, symbol = crc_symbol_line[0], crc_symbol_line[1]
            actual_symbol_crc_mapping[symbol] = crc
        return actual_symbol_crc_mapping, return_code

    def get_target_symvers_symbol_crc_mapping(self, symvers_file: str) -> (dict, int):
        """
        Get target symbol crc mapping from symvers file of kernel rpm package. The symvers file content is
        as follows(e.g.):

            0x0c994af3	ipv6_chk_custom_prefix	vmlinux	EXPORT_SYMBOL
            0xe9bed965	pcmcia_reset_card	vmlinux	EXPORT_SYMBOL
            0x55417264	unregister_vt_notifier	vmlinux	EXPORT_SYMBOL_GPL
            0x8c8905c0	set_anon_super	vmlinux	EXPORT_SYMBOL
            0x3ba051a9	__cleancache_invalidate_page	vmlinux	EXPORT_SYMBOL

        the first column is crc(Cyclic Redundancy Check), and the second column is symbol.

        Args:
            symvers_file(str): symvers file path

        Returns:
            dict, int: target symvers symbol crc mapping, return_code
            e.g.
            {
                'ipv6_chk_custom_prefix': '0x0c994af3',
                'pcmcia_reset_card': '0xe9bed965',
            },
            SUCCEED
        """
        symvers_symbol_crc_mapping = dict()
        try:
            content = gzip.open(symvers_file, 'rb')
        except FileNotFoundError as e:
            print("error: ", e)
            return symvers_symbol_crc_mapping, FAIL

        for line in content.readlines():
            line = line.decode()
            line = line.split()
            crc, symbol = line[0], line[1]
            symvers_symbol_crc_mapping[symbol] = crc
        content.close()
        return symvers_symbol_crc_mapping, SUCCEED

    def upgrade(self):
        """
        Use UpgradeCommand to process the upgrade operation.
        """
        upgrade = UpgradeCommand(self.cli)
        upgrade.upgrade_minimal = self.upgrade_minimal
        upgrade.opts = self.opts
        upgrade.opts.filenames = self.opts.filenames
        upgrade.opts.pkg_specs = self.opts.pkg_specs
        upgrade.opts.grp_specs = self.opts.grp_specs

        upgrade.upgrade_minimal = None
        upgrade.all_security = None
        upgrade.skipped_grp_specs = None

        upgrade.run()
