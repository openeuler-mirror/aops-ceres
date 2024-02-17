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
import unittest
import dnf.cli
import dnf.sack
import hawkey
from unittest import mock
from dnf.cli.commands.updateinfo import UpdateInfoCommand
from .advisory import Advisory
from .hot_updateinfo import HotpatchUpdateInfo, HotUpdateinfoCommand, DisplayItem

SUCCEED = 0
FAIL = 255


def get_available_apkg_adv_insts_generator_mock():
    redis_2_pkg = mock.MagicMock(evr="6.2.5-2", arch="x86_64")
    redis_2_pkg.name = "redis"
    ref_cve_1111 = mock.MagicMock(id="CVE-2023-1111", type=hawkey.REFERENCE_CVE)
    ref_cve_1112 = mock.MagicMock(id="CVE-2023-1112", type=hawkey.REFERENCE_CVE)
    ref_cve_1113 = mock.MagicMock(id="CVE-2023-1113", type=hawkey.REFERENCE_CVE)
    adv_1_references = [ref_cve_1111, ref_cve_1112, ref_cve_1113]
    advisory_1 = mock.MagicMock(
        references=adv_1_references, updated="1970-01-01 08:00:00", type=hawkey.ADVISORY_SECURITY, severity="Important"
    )
    yield redis_2_pkg, advisory_1, False

    redis_3_pkg = mock.MagicMock(evr="6.2.5-3", arch="x86_64")
    redis_3_pkg.name = "redis"
    ref_cve_2221 = mock.MagicMock(id="CVE-2023-2221", type=hawkey.REFERENCE_CVE)
    ref_cve_2222 = mock.MagicMock(id="CVE-2023-2222", type=hawkey.REFERENCE_CVE)
    adv_2_references = [ref_cve_2221, ref_cve_2222]
    advisory_2 = mock.MagicMock(
        references=adv_2_references, updated="1970-01-01 08:00:00", type=hawkey.ADVISORY_SECURITY, severity="Critical"
    )
    yield redis_3_pkg, advisory_2, False

    redis_4_pkg = mock.MagicMock(evr="6.2.5-4", arch="x86_64")
    redis_4_pkg.name = "redis"
    ref_cve_3331 = mock.MagicMock(id="CVE-2023-3331", type=hawkey.REFERENCE_CVE)
    ref_cve_3332 = mock.MagicMock(id="CVE-2023-3332", type=hawkey.REFERENCE_CVE)
    adv_3_references = [ref_cve_3331, ref_cve_3332]
    advisory_3 = mock.MagicMock(
        references=adv_3_references, updated="1970-01-01 08:00:00", type=hawkey.ADVISORY_SECURITY, severity="Low"
    )
    yield redis_4_pkg, advisory_3, False

    redis_5_pkg = mock.MagicMock(evr="6.2.5-5", arch="x86_64")
    redis_5_pkg.name = "redis"
    ref_cve_4441 = mock.MagicMock(id="CVE-2023-4441", type=hawkey.REFERENCE_CVE)
    adv_4_references = [ref_cve_4441]
    advisory_4 = mock.MagicMock(
        references=adv_4_references, updated="1970-01-01 08:00:00", type=hawkey.ADVISORY_SECURITY, severity="Low"
    )
    yield redis_5_pkg, advisory_4, False


def get_mapping_nevra_cve_mock():
    mapping_nevra_cve_mock = {
        (('redis', '6.2.5-2', 'x86_64'), '1970-01-01 08:00:00'): {
            'CVE-2023-1111': (1, 'Important'),
            'CVE-2023-1112': (1, 'Important'),
            'CVE-2023-1113': (1, 'Important'),
        },
        (('redis', '6.2.5-3', 'x86_64'), '1970-01-01 08:00:00'): {
            'CVE-2023-2221': (1, 'Critical'),
            'CVE-2023-2222': (1, 'Critical'),
        },
        (('redis', '6.2.5-4', 'x86_64'), '1970-01-01 08:00:00'): {
            'CVE-2023-3331': (1, 'Low'),
            'CVE-2023-3332': (1, 'Low'),
        },
        (('redis', '6.2.5-5', 'x86_64'), '1970-01-01 08:00:00'): {'CVE-2023-4441': (1, 'Low')},
    }
    return mapping_nevra_cve_mock


def get_hotpatches_mock():
    hotpatches_mock = dict()
    advisory_1 = Advisory(id='', adv_type='', title='', severity="Important", description='')
    advisory_2 = Advisory(id='', adv_type='', title='', severity="Critical", description='')
    advisory_3 = Advisory(id='', adv_type='', title='', severity="Low", description='')
    advisory_4 = Advisory(id='', adv_type='', title='', severity="Low", description='')
    acc_hotpatch_1_1_mock = mock.MagicMock(
        state=HotpatchUpdateInfo.INSTALLABLE,
        hotpatch_name="ACC",
        src_pkg="redis-6.2.5-1",
        version="1",
        release="1",
        nevra="patch-redis-6.2.5-1-ACC-1-1.x86_64",
        advisory=advisory_1,
        required_pkgs_str='redis-6.2.5-1',
        cves=['CVE-2023-1111', 'CVE-2023-1112'],
    )
    acc_hotpatch_1_1_mock.advisory = advisory_1
    acc_hotpatch_1_2_mock = mock.MagicMock(
        state=HotpatchUpdateInfo.INSTALLABLE,
        hotpatch_name="ACC",
        src_pkg="redis-6.2.5-1",
        version="1",
        release="2",
        nevra="patch-redis-6.2.5-1-ACC-1-2.x86_64",
        advisory=advisory_2,
        required_pkgs_str='redis-6.2.5-1',
        cves=['CVE-2023-2221', 'CVE-2023-2222'],
    )
    sgl_hotpatch_mock = mock.MagicMock(
        state=HotpatchUpdateInfo.INSTALLABLE,
        hotpatch_name="SGL_CVE_2023_1111",
        src_pkg="redis-6.2.5-1",
        version="1",
        release="1",
        nevra="patch-redis-6.2.5-1-SGL_CVE_2023_1111-1-1.x86_64",
        advisory=advisory_3,
        required_pkgs_str='redis-6.2.5-1',
        cves=['CVE-2023-1111'],
    )
    acc_hotpatch_1_3_mock = mock.MagicMock(
        state=HotpatchUpdateInfo.UNINSTALLABLE,
        hotpatch_name="ACC",
        src_pkg="redis-6.2.5-2",
        version="1",
        release="3",
        nevra="patch-redis-6.2.5-2-ACC-1-3.x86_64",
        advisory=advisory_4,
        required_pkgs_str='redis-6.2.5-2',
        cves=['CVE-2023-3331', 'CVE-2023-3332'],
    )

    hotpatches_mock['acc_hotpatch_1_1_mock'] = acc_hotpatch_1_1_mock
    hotpatches_mock['acc_hotpatch_1_2_mock'] = acc_hotpatch_1_2_mock
    hotpatches_mock['sgl_hotpatch_mock'] = sgl_hotpatch_mock
    hotpatches_mock['acc_hotpatch_1_3_mock'] = acc_hotpatch_1_3_mock

    return hotpatches_mock


def get_hotpatch_cves_mock(hotpatches_mock):
    hotpatch_cves = dict()
    cve_1111_mock = mock.MagicMock(
        hotpatches=[hotpatches_mock['acc_hotpatch_1_1_mock'], hotpatches_mock['sgl_hotpatch_mock']]
    )
    cve_1112_mock = mock.MagicMock(
        hotpatches=[hotpatches_mock['acc_hotpatch_1_1_mock'], hotpatches_mock['sgl_hotpatch_mock']]
    )
    cve_1113_mock = mock.MagicMock(hotpatches=[])
    cve_2221_mock = mock.MagicMock(hotpatches=[hotpatches_mock['acc_hotpatch_1_2_mock']])
    cve_2222_mock = mock.MagicMock(hotpatches=[hotpatches_mock['acc_hotpatch_1_2_mock']])
    cve_3331_mock = mock.MagicMock(hotpatches=[hotpatches_mock['acc_hotpatch_1_3_mock']])
    cve_3332_mock = mock.MagicMock(hotpatches=[hotpatches_mock['acc_hotpatch_1_3_mock']])
    cve_4441_mock = mock.MagicMock(hotpatches=[])
    hotpatch_cves = {
        'CVE-2023-1111': cve_1111_mock,
        'CVE-2023-1112': cve_1112_mock,
        'CVE-2023-1113': cve_1113_mock,
        'CVE-2023-2221': cve_2221_mock,
        'CVE-2023-2222': cve_2222_mock,
        'CVE-2023-3331': cve_3331_mock,
        'CVE-2023-3331': cve_3332_mock,
        'CVE-2023-4441': cve_4441_mock,
    }
    return hotpatch_cves


def get_hotpatch_required_pkg_info_str_mock(hotpatches_mock):
    # dict {required_pkg_info_str: [Hotpatch]}
    hotpatch_required_pkg_info_str_mock = dict()

    hotpatch_required_pkg_info_str_mock['redis-6.2.5-1'] = [
        ['1-1', hotpatches_mock['acc_hotpatch_1_1_mock']],
        ['1-2', hotpatches_mock['acc_hotpatch_1_2_mock']],
        ['1-1', hotpatches_mock['sgl_hotpatch_mock']],
    ]
    hotpatch_required_pkg_info_str_mock['redis-6.2.5-2'] = [['1-3', hotpatches_mock['acc_hotpatch_1_3_mock']]]

    return hotpatch_required_pkg_info_str_mock


class HotUpdateInfoTestCase(unittest.TestCase):
    def setUp(self):
        cli = mock.MagicMock()
        self.cmd = HotUpdateinfoCommand(cli)
        self.cmd.cli.base = dnf.cli.cli.BaseCli()

        self.cmd.cli.base._sack = dnf.sack.Sack()

        repo = dnf.repo.Repo(name='local_hotpatch_new_new')
        repo.baseurl = ["file:///root/tmp/local_hotpatch_new_new"]
        repo.enable()
        self.cmd.base.repos.add(repo)

        self.cmd.opts = mock.Mock()
        self.cmd.opts.cves = None
        self.cmd.filter_cves = None
        self.cmd.opts.list = 'list'

        self.cmd.hp_hawkey = HotpatchUpdateInfo(self.cmd.cli.base, self.cmd.cli)
        self.cmd.updateinfo = UpdateInfoCommand(cli)
        self.cmd.updateinfo.opts = mock.Mock()
        self.cmd.updateinfo.opts.availability == 'available'

    @mock.patch.object(UpdateInfoCommand, "available_apkg_adv_insts")
    def test_get_apkg_adv_insts_should_return_correctly(self, mock_available_apkg_adv_insts):
        mock_available_apkg_adv_insts.return_value = []
        res = self.cmd.get_apkg_adv_insts()
        expected_res = []
        self.assertEqual(res, expected_res)

    @mock.patch.object(HotUpdateinfoCommand, "get_apkg_adv_insts")
    def test_get_mapping_nevra_cve(self, mock_get_apkg_adv_insts):
        mock_get_apkg_adv_insts.return_value = get_available_apkg_adv_insts_generator_mock()
        res = self.cmd.get_mapping_nevra_cve()
        expected_res = {
            (('redis', '6.2.5-2', 'x86_64'), '1970-01-01 08:00:00'): {
                'CVE-2023-1111': (1, 'Important'),
                'CVE-2023-1112': (1, 'Important'),
                'CVE-2023-1113': (1, 'Important'),
            },
            (('redis', '6.2.5-3', 'x86_64'), '1970-01-01 08:00:00'): {
                'CVE-2023-2221': (1, 'Critical'),
                'CVE-2023-2222': (1, 'Critical'),
            },
            (('redis', '6.2.5-4', 'x86_64'), '1970-01-01 08:00:00'): {
                'CVE-2023-3331': (1, 'Low'),
                'CVE-2023-3332': (1, 'Low'),
            },
            (('redis', '6.2.5-5', 'x86_64'), '1970-01-01 08:00:00'): {'CVE-2023-4441': (1, 'Low')},
        }
        self.assertEqual(res, expected_res)

    def test_append_fixed_cve_id_and_hotpatch_should_update_fixed_cve_id_and_hotpatch_correctly(self):
        hotpatches_mock = get_hotpatches_mock()
        self.cmd.hp_hawkey._hotpatch_required_pkg_info_str = get_hotpatch_required_pkg_info_str_mock(hotpatches_mock)
        hotpatch_cves_mock = get_hotpatch_cves_mock(hotpatches_mock)
        fixed_cve_id_and_hotpatch = {('CVE-2023-2221', hotpatch_cves_mock['CVE-2023-2221'].hotpatches[0])}
        self.cmd.append_fixed_cve_id_and_hotpatch(fixed_cve_id_and_hotpatch)
        expected_display_lines = {
            ('CVE-2023-1111', hotpatches_mock['acc_hotpatch_1_1_mock']),
            ('CVE-2023-1112', hotpatches_mock['acc_hotpatch_1_1_mock']),
            ('CVE-2023-2221', hotpatches_mock['acc_hotpatch_1_2_mock']),
            ('CVE-2023-2222', hotpatches_mock['acc_hotpatch_1_2_mock']),
        }
        self.assertEqual(fixed_cve_id_and_hotpatch, expected_display_lines)

    def test_get_installed_filtered_display_item_should_return_correctly(self):
        format_lines = {
            ('CVE-2023-1113', 'Important/Sec.', 'redis-6.2.5-2.x86_64', '-'),
            ('CVE-2023-1112', 'Important/Sec.', 'redis-6.2.5-2.x86_64', 'patch-redis-6.2.5-1-ACC-1-1.x86_64'),
            ('CVE-2023-1111', 'Important/Sec.', 'redis-6.2.5-2.x86_64', 'patch-redis-6.2.5-1-ACC-1-1.x86_64'),
            ('CVE-2023-38427', 'Important/Sec.', 'kernel-devel-5.10.0-136.44.0.122.oe2203sp1.x86_64', '-'),
        }

        hotpatches_mock = get_hotpatches_mock()
        self.cmd.hp_hawkey._hotpatch_required_pkg_info_str = get_hotpatch_required_pkg_info_str_mock(hotpatches_mock)
        hotpatch_cves_mock = get_hotpatch_cves_mock(hotpatches_mock)
        fixed_cve_id_and_hotpatch = {
            ('CVE-2023-1111', hotpatch_cves_mock['CVE-2023-1111'].hotpatches[0]),
            ('CVE-2023-1112', hotpatch_cves_mock['CVE-2023-1112'].hotpatches[0]),
        }

        installable_cve_id_and_hotpatch = {}

        res = self.cmd.get_installed_filtered_display_item(
            format_lines, fixed_cve_id_and_hotpatch, installable_cve_id_and_hotpatch
        )
        expected_display_lines = {
            ('CVE-2023-1111', 'Important/Sec.', 'redis-6.2.5-2.x86_64', 'patch-redis-6.2.5-1-ACC-1-1.x86_64'),
            ('CVE-2023-1113', 'Important/Sec.', 'redis-6.2.5-2.x86_64', '-'),
            ('CVE-2023-1112', 'Important/Sec.', 'redis-6.2.5-2.x86_64', 'patch-redis-6.2.5-1-ACC-1-1.x86_64'),
            ('CVE-2023-38427', 'Important/Sec.', 'kernel-devel-5.10.0-136.44.0.122.oe2203sp1.x86_64', '-'),
        }
        expected_display = DisplayItem(idw=14, tiw=14, ciw=49, display_lines=expected_display_lines)
        self.assertEqual(res.idw, expected_display.idw)
        self.assertEqual(res.tiw, expected_display.tiw)
        self.assertEqual(res.ciw, expected_display.ciw)
        self.assertEqual(sorted(res.display_lines), sorted(expected_display.display_lines))

    def test_get_available_filtered_display_item_should_return_correctly(self):
        self.cmd.filter_cves = 'CVE-2023-1111'
        hotpatches_mock = get_hotpatches_mock()
        self.cmd.hp_hawkey._hotpatch_required_pkg_info_str = get_hotpatch_required_pkg_info_str_mock(hotpatches_mock)
        format_lines = {
            ('CVE-2023-1111', 'Important/Sec.', '-', hotpatches_mock['acc_hotpatch_1_1_mock']),
            ('CVE-2023-1112', 'Important/Sec.', '-', hotpatches_mock['acc_hotpatch_1_1_mock']),
            ('CVE-2023-1112', 'Low/Sec.', '-', hotpatches_mock['sgl_hotpatch_mock']),
            ('CVE-2023-1111', 'Low/Sec.', '-', hotpatches_mock['sgl_hotpatch_mock']),
            ('CVE-2023-2221', 'Critical/Sec.', '-', hotpatches_mock['acc_hotpatch_1_2_mock']),
            ('CVE-2023-2222', 'Critical/Sec.', '-', hotpatches_mock['acc_hotpatch_1_2_mock']),
        }

        fixed_cve_id_and_hotpatch = {
            ('CVE-2023-2221', hotpatches_mock['acc_hotpatch_1_2_mock']),
            ('CVE-2023-2222', hotpatches_mock['acc_hotpatch_1_2_mock']),
        }

        iterated_cve_id_and_hotpatch = {}

        res = self.cmd.get_available_filtered_display_item(
            format_lines, fixed_cve_id_and_hotpatch, iterated_cve_id_and_hotpatch
        )
        expected_display_lines = {
            ('CVE-2023-1111', 'Important/Sec.', '-', hotpatches_mock['acc_hotpatch_1_1_mock']),
            ('CVE-2023-1111', 'Low/Sec.', '-', hotpatches_mock['sgl_hotpatch_mock']),
        }
        expected_display = DisplayItem(idw=14, tiw=14, ciw=49, display_lines=expected_display_lines)
        self.assertEqual(sorted(res.display_lines), sorted(expected_display.display_lines))

    def test_add_untraversed_hotpatches_should_update_correctly(self):
        hotpatches_mock = get_hotpatches_mock()
        hotpatches_mock['acc_hotpatch_1_2_mock'].state = self.cmd.hp_hawkey.INSTALLED
        hotpatch_cves_mock = get_hotpatch_cves_mock(hotpatches_mock)
        self.cmd.hp_hawkey._hotpatch_cves = hotpatch_cves_mock

        echo_lines = set()
        fixed_cve_id_and_hotpatch = set()
        installable_cve_id_and_hotpatch = set()
        uninstallable_cve_id_and_hotpatch = {
            ('CVE-2023-3331', hotpatches_mock['acc_hotpatch_1_3_mock']),
            ('CVE-2023-3332', hotpatches_mock['acc_hotpatch_1_3_mock']),
        }
        iterated_cve_id_and_hotpatch = set()

        self.cmd.add_untraversed_hotpatches(
            echo_lines,
            fixed_cve_id_and_hotpatch,
            installable_cve_id_and_hotpatch,
            uninstallable_cve_id_and_hotpatch,
            iterated_cve_id_and_hotpatch,
        )

        expected_echo_lines = {
            ('CVE-2023-1111', 'Important/Sec.', '-', hotpatches_mock['acc_hotpatch_1_1_mock']),
            ('CVE-2023-1112', 'Important/Sec.', '-', hotpatches_mock['acc_hotpatch_1_1_mock']),
            ('CVE-2023-1112', 'Low/Sec.', '-', hotpatches_mock['sgl_hotpatch_mock']),
            ('CVE-2023-1111', 'Low/Sec.', '-', hotpatches_mock['sgl_hotpatch_mock']),
            ('CVE-2023-2221', 'Critical/Sec.', '-', hotpatches_mock['acc_hotpatch_1_2_mock']),
            ('CVE-2023-2222', 'Critical/Sec.', '-', hotpatches_mock['acc_hotpatch_1_2_mock']),
        }
        expected_fixed_cve_id_and_hotpatch = {
            ('CVE-2023-2221', hotpatches_mock['acc_hotpatch_1_2_mock']),
            ('CVE-2023-2222', hotpatches_mock['acc_hotpatch_1_2_mock']),
        }
        expected_installable_cve_id_and_hotpatch = {
            ('CVE-2023-1111', hotpatches_mock['acc_hotpatch_1_1_mock']),
            ('CVE-2023-1112', hotpatches_mock['acc_hotpatch_1_1_mock']),
            ('CVE-2023-1112', hotpatches_mock['sgl_hotpatch_mock']),
            ('CVE-2023-1111', hotpatches_mock['sgl_hotpatch_mock']),
        }
        expected_iterated_cve_id_and_hotpatch = {
            ('CVE-2023-1111', hotpatches_mock['acc_hotpatch_1_1_mock']),
            ('CVE-2023-1112', hotpatches_mock['acc_hotpatch_1_1_mock']),
            ('CVE-2023-1112', hotpatches_mock['sgl_hotpatch_mock']),
            ('CVE-2023-1111', hotpatches_mock['sgl_hotpatch_mock']),
            ('CVE-2023-2221', hotpatches_mock['acc_hotpatch_1_2_mock']),
            ('CVE-2023-2222', hotpatches_mock['acc_hotpatch_1_2_mock']),
        }

        self.assertEqual(expected_echo_lines, echo_lines)
        self.assertEqual(expected_fixed_cve_id_and_hotpatch, fixed_cve_id_and_hotpatch)
        self.assertEqual(expected_installable_cve_id_and_hotpatch, installable_cve_id_and_hotpatch)
        self.assertEqual(expected_iterated_cve_id_and_hotpatch, iterated_cve_id_and_hotpatch)

    @mock.patch.object(HotUpdateinfoCommand, "get_mapping_nevra_cve")
    def test_get_formatting_parameters_and_display_lines_should_return_correctly(self, mock_get_mapping_nevra_cve):
        mock_get_mapping_nevra_cve.return_value = get_mapping_nevra_cve_mock()
        self.cmd.configure()
        res = self.cmd.get_formatting_parameters_and_display_lines()
        expected_display_lines = [
            ('CVE-2023-1113', 'Important/Sec.', 'redis-6.2.5-2.x86_64', '-'),
            ('CVE-2023-1112', 'Important/Sec.', 'redis-6.2.5-2.x86_64', '-'),
            ('CVE-2023-1111', 'Important/Sec.', 'redis-6.2.5-2.x86_64', '-'),
            ('CVE-2023-2221', 'Critical/Sec.', 'redis-6.2.5-3.x86_64', '-'),
            ('CVE-2023-2222', 'Critical/Sec.', 'redis-6.2.5-3.x86_64', '-'),
            ('CVE-2023-3331', 'Low/Sec.', 'redis-6.2.5-4.x86_64', '-'),
            ('CVE-2023-3332', 'Low/Sec.', 'redis-6.2.5-4.x86_64', '-'),
            ('CVE-2023-4441', 'Low/Sec.', 'redis-6.2.5-5.x86_64', '-'),
        ]
        expected_display = DisplayItem(idw=13, tiw=14, ciw=20, display_lines=expected_display_lines)
        self.assertEqual(res.idw, expected_display.idw)
        self.assertEqual(res.tiw, expected_display.tiw)
        self.assertEqual(res.ciw, expected_display.ciw)
        self.assertEqual(sorted(res.display_lines), sorted(expected_display.display_lines))


if __name__ == '__main__':
    unittest.main()
