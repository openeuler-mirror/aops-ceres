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
import platform
from unittest import mock
from xml.etree.ElementTree import Element
from .updateinfo_parse import HotpatchUpdateInfo
from .syscare import Syscare
from .hotpatch import Hotpatch


def get_cves_mock():
    cve_mock = mock.MagicMock()
    acc_hotpatch_mock = mock.MagicMock(
        state=HotpatchUpdateInfo.INSTALLABLE,
        hotpatch_name="ACC",
        src_pkg="redis-6.2.5-1",
        version="1",
        release="1",
        nevra="patch-redis-6.2.5-1-ACC-1-1.x86_64",
        required_pkgs_str="redis",
    )
    sgl_hotpatch_mock = mock.MagicMock(
        state=HotpatchUpdateInfo.INSTALLABLE,
        hotpatch_name="SGL_CVE_2023_1111",
        src_pkg="redis-6.2.5-1",
        version="1",
        release="1",
        nevra="patch-redis-6.2.5-1-SGL_CVE_2023_1111-1-1.x86_64",
        required_pkgs_str="redis",
    )
    cve_mock = mock.MagicMock(hotpatches=[acc_hotpatch_mock, sgl_hotpatch_mock])
    return cve_mock


def get_advisory_mock():
    advisory_mock = mock.MagicMock()
    advisory_mock.id = "openEuler-SA-2022-1"
    acc_hotpatch_mock = mock.MagicMock(
        state=HotpatchUpdateInfo.INSTALLABLE,
        hotpatch_name="ACC",
        src_pkg="redis-6.2.5-1",
        version="1",
        release="1",
        nevra="patch-redis-6.2.5-1-ACC-1-1.x86_64",
    )
    sgl_hotpatch_mock = mock.MagicMock(
        state=HotpatchUpdateInfo.INSTALLABLE,
        hotpatch_name="SGL_CVE_2023_1111",
        src_pkg="redis-6.2.5-1",
        version="1",
        release="1",
        nevra="patch-redis-6.2.5-1-SGL_CVE_2023_1111-1-1.x86_64",
    )
    advisory_mock = mock.MagicMock(hotpatches=[acc_hotpatch_mock, sgl_hotpatch_mock])
    return advisory_mock


def get_pkglist_element():
    pkglist = Element('pkglist')
    hot_patch_collection = Element('hot_patch_collection')
    package_acc_redis_x86 = Element('package')
    package_acc_redis_x86.attrib['arch'] = "x86_64"
    package_acc_redis_x86.attrib['name'] = "patch-redis-6.2.5-1-ACC"
    package_acc_redis_x86.attrib['version'] = "1"
    package_acc_redis_x86.attrib['release'] = "1"
    filename_acc_redis_x86 = Element('filename')
    filename_acc_redis_x86.text = "%s-%s-%s.%s.rpm" % (
        package_acc_redis_x86.attrib['name'],
        package_acc_redis_x86.attrib['release'],
        package_acc_redis_x86.attrib['version'],
        package_acc_redis_x86.attrib['arch'],
    )
    package_acc_redis_x86.append(filename_acc_redis_x86)

    package_acc_redis_arm = Element('package')
    package_acc_redis_arm.attrib['arch'] = "aarch64"
    package_acc_redis_arm.attrib['name'] = "patch-redis-6.2.5-1-ACC"
    package_acc_redis_arm.attrib['version'] = "1"
    package_acc_redis_arm.attrib['release'] = "1"
    filename_acc_redis_arm = Element('filename')
    filename_acc_redis_arm.text = "%s-%s-%s.%s.rpm" % (
        package_acc_redis_arm.attrib['name'],
        package_acc_redis_arm.attrib['release'],
        package_acc_redis_arm.attrib['version'],
        package_acc_redis_arm.attrib['arch'],
    )
    package_acc_redis_arm.append(filename_acc_redis_arm)

    package_sgl_redis_x86 = Element('package')
    package_sgl_redis_x86.attrib['arch'] = "x86_64"
    package_sgl_redis_x86.attrib['name'] = "patch-redis-6.2.5-1-SGL_CVE_2023_1111"
    package_sgl_redis_x86.attrib['version'] = "1"
    package_sgl_redis_x86.attrib['release'] = "1"
    filename_sgl_redis_x86 = Element('filename')
    filename_sgl_redis_x86.text = "%s-%s-%s.%s.rpm" % (
        package_sgl_redis_x86.attrib['name'],
        package_sgl_redis_x86.attrib['release'],
        package_sgl_redis_x86.attrib['version'],
        package_sgl_redis_x86.attrib['arch'],
    )
    package_sgl_redis_x86.append(filename_sgl_redis_x86)

    package_sgl_redis_arm = Element('package')
    package_sgl_redis_arm.attrib['arch'] = "aarch64"
    package_sgl_redis_arm.attrib['name'] = "patch-redis-6.2.5-1-SGL_CVE_2023_1111"
    package_sgl_redis_arm.attrib['version'] = "1"
    package_sgl_redis_arm.attrib['release'] = "1"
    filename_sgl_redis_arm = Element('filename')
    filename_sgl_redis_arm.text = "%s-%s-%s.%s.rpm" % (
        package_sgl_redis_arm.attrib['name'],
        package_sgl_redis_arm.attrib['release'],
        package_sgl_redis_arm.attrib['version'],
        package_sgl_redis_arm.attrib['arch'],
    )
    package_sgl_redis_arm.append(filename_sgl_redis_arm)

    hot_patch_collection.append(package_acc_redis_arm)
    hot_patch_collection.append(package_acc_redis_x86)
    hot_patch_collection.append(package_sgl_redis_arm)
    hot_patch_collection.append(package_sgl_redis_x86)

    pkglist.append(hot_patch_collection)
    return pkglist


def get_reference_element():
    references = Element('references')
    reference = Element('reference')
    reference.attrib['href'] = "https://nvd.nist.gov/vuln/detail/CVE-2021-1111"
    reference.attrib['id'] = "CVE-2021-1111"
    reference.attrib['title'] = "CVE-2021-1111"
    reference.attrib['type'] = "cve"
    references.append(reference)
    return references


def get_advisory_element():
    update = Element('update')
    update.attrib['type'] = "security"
    adv_id = Element('id')
    adv_id.text = "openEuler-SA-2022-1"
    adv_title = Element('title')
    adv_title.text = "An update for mariadb is now available for openEuler-22.03-LTS"
    adv_severity = Element('severity')
    adv_severity.text = "Important"
    adv_release = Element('release')
    adv_release.text = "openEuler"
    adv_issued = Element('issued')
    adv_issued.attrib['date'] = "2023-08-03"
    references = get_reference_element()
    description = Element('description')
    description.text = "Issue summary: "
    pkg_list = get_pkglist_element()
    update.append(adv_id)
    update.append(adv_title)
    update.append(adv_severity)
    update.append(adv_release)
    update.append(adv_issued)
    update.append(references)
    update.append(description)
    update.append(pkg_list)
    return update


class HotpatchUpdateInfoTestCase(unittest.TestCase):
    def setUp(self):
        self.cmd = mock.MagicMock()
        self.cmd.cli.base = dnf.cli.cli.BaseCli()

        self.cmd.cli.base._sack = dnf.sack.Sack()

        repo = dnf.repo.Repo(name='local_hotpatch_new_new')
        repo.baseurl = ["file:///root/tmp/local_hotpatch_new_new"]
        repo.enable()
        self.cmd.base.repos.add(repo)

        self.cmd.opts = mock.Mock()
        self.cmd.opts.cves = None
        self.cmd.opts.filter_cves = None
        self.cmd.opts.list = 'list'
        self.hotpatchUpdateInfo = HotpatchUpdateInfo(self.cmd.cli.base, self.cmd.cli)

        self.machine_arch = platform.machine()

    @mock.patch.object(Syscare, "list")
    def test_init_hotpatch_status_from_syscare_should_change_status_correctly(self, mock_syscare):
        mock_syscare.return_value = [
            {
                'Uuid': 'a6f8c694-5cc4-4887-8aac-fbe7f67fb413',
                'Name': 'redis-6.2.5-1/ACC-1-1/redis-cli',
                'Status': 'ACTIVED',
            }
        ]
        self.hotpatchUpdateInfo._init_hotpatch_status_from_syscare()

        expected_res = {'redis-6.2.5-1/ACC-1-1/redis-cli': 'ACTIVED'}
        self.assertEqual(self.hotpatchUpdateInfo._hotpatch_state, expected_res)

    @mock.patch.object(Syscare, "list")
    def test_get_hotpatch_aggregated_status_in_syscare_should_return_actived_when_syscare_status_are_all_actived(
        self, mock_syscare
    ):
        mock_syscare.return_value = [
            {
                'Uuid': 'a6f8c694-5cc4-4887-8aac-fbe7f67fb413',
                'Name': 'redis-6.2.5-1/ACC-1-1/redis-cli',
                'Status': 'ACTIVED',
            },
            {
                'Uuid': 'a6f8c694-5cc4-4887-8aac-fbe7f67fb414',
                'Name': 'redis-6.2.5-1/ACC-1-1/redis-server',
                'Status': 'ACTIVED',
            },
            {
                'Uuid': 'a6f8c694-5cc4-4887-8aac-fbe7f67fb415',
                'Name': 'redis-6.2.5-1/ACC-1-1/redis-benchmark',
                'Status': 'ACTIVED',
            },
        ]
        self.hotpatchUpdateInfo._init_hotpatch_status_from_syscare()

        hotpatch = Hotpatch(
            name="patch-redis-6.2.5-1-ACC",
            version="1",
            arch="x86_64",
            filename="patch-redis-6.2.5-1-ACC-1-1.x86_64.rpm",
            release="1",
        )
        res = self.hotpatchUpdateInfo._get_hotpatch_aggregated_status_in_syscare(hotpatch)
        expected_res = 'ACTIVED'
        self.assertEqual(res, expected_res)

    @mock.patch.object(Syscare, "list")
    def test_get_hotpatch_aggregated_status_in_syscare_should_return_actived_when_syscare_status_are_not_all_actived(
        self, mock_syscare
    ):
        mock_syscare.return_value = [
            {
                'Uuid': 'a6f8c694-5cc4-4887-8aac-fbe7f67fb413',
                'Name': 'redis-6.2.5-1/ACC-1-1/redis-cli',
                'Status': 'ACTIVED',
            },
            {
                'Uuid': 'a6f8c694-5cc4-4887-8aac-fbe7f67fb414',
                'Name': 'redis-6.2.5-1/ACC-1-1/redis-server',
                'Status': 'ACTIVED',
            },
            {
                'Uuid': 'a6f8c694-5cc4-4887-8aac-fbe7f67fb415',
                'Name': 'redis-6.2.5-1/ACC-1-1/redis-benchmark',
                'Status': 'NOT-APPLIED',
            },
        ]
        self.hotpatchUpdateInfo._init_hotpatch_status_from_syscare()

        hotpatch = Hotpatch(
            name="patch-redis-6.2.5-1-ACC",
            version="1",
            arch="x86_64",
            filename="patch-redis-6.2.5-1-ACC-1-1.x86_64.rpm",
            release="1",
        )
        res = self.hotpatchUpdateInfo._get_hotpatch_aggregated_status_in_syscare(hotpatch)
        expected_res = ''
        self.assertEqual(res, expected_res)

    def test_get_hotpatches_from_advisories_should_return_correctly(self):
        advisories = ['openEuler-SA-2023-1']
        self.hotpatchUpdateInfo._hotpatch_advisories['openEuler-SA-2023-1'] = get_advisory_mock()
        res = self.hotpatchUpdateInfo.get_hotpatches_from_advisories(advisories)
        expected_res = {
            'openEuler-SA-2023-1': [
                'patch-redis-6.2.5-1-ACC-1-1.x86_64',
                'patch-redis-6.2.5-1-SGL_CVE_2023_1111-1-1.x86_64',
            ]
        }
        self.assertEqual(res, expected_res)

    def test_get_hotpatches_from_cve_should_return_correctly_when_priority_is_default(self):
        cves = ["CVE-2023-1111"]
        self.hotpatchUpdateInfo.hotpatch_cves["CVE-2023-1111"] = get_cves_mock()
        res = self.hotpatchUpdateInfo.get_hotpatches_from_cve(cves)
        expected_res = {"CVE-2023-1111": ['patch-redis-6.2.5-1-ACC-1-1.x86_64']}
        self.assertEqual(res, expected_res)

    def test_get_hotpatches_from_cve_should_return_correctly_when_priority_is_SGL(self):
        cves = ["CVE-2023-1111"]
        self.hotpatchUpdateInfo.hotpatch_cves["CVE-2023-1111"] = get_cves_mock()
        res = self.hotpatchUpdateInfo.get_hotpatches_from_cve(cves, priority="SGL")
        expected_res = {
            "CVE-2023-1111": ['patch-redis-6.2.5-1-SGL_CVE_2023_1111-1-1.x86_64'],
        }
        self.assertEqual(res, expected_res)

    def test_update_mapping_cve_hotpatches_should_update_correctly_when_priority_is_SGL(self):
        self.hotpatchUpdateInfo.hotpatch_cves["CVE-2023-1111"] = get_cves_mock()

        cve_id = "CVE-2023-1111"
        map_cve_hotpatches = dict()
        map_cve_hotpatches[cve_id] = []

        self.hotpatchUpdateInfo.update_mapping_cve_hotpatches(
            priority="SGL", mapping_cve_hotpatches=map_cve_hotpatches, cve_id=cve_id
        )
        expected_res = {
            "CVE-2023-1111": ['patch-redis-6.2.5-1-SGL_CVE_2023_1111-1-1.x86_64'],
        }
        self.assertEqual(map_cve_hotpatches, expected_res)

    def test_version_cmp_should_return_correctly(self):
        hotpatch_a = mock.MagicMock(version="1", release="1")
        hotpatch_b = mock.MagicMock(version="1", release="2")
        res = self.hotpatchUpdateInfo.version_cmp(hotpatch_a, hotpatch_b)
        expected_res = 1
        self.assertEqual(res, expected_res)
        res = self.hotpatchUpdateInfo.version_cmp(hotpatch_b, hotpatch_a)
        expected_res = -1
        self.assertEqual(res, expected_res)
        hotpatch_b.version = "1"
        hotpatch_b.release = "1"
        res = self.hotpatchUpdateInfo.version_cmp(hotpatch_a, hotpatch_b)
        expected_res = -1
        self.assertEqual(res, expected_res)

    def test_parse_pkglist_should_return_correctly(self):
        pkglist = get_pkglist_element()
        res = self.hotpatchUpdateInfo._parse_pkglist(pkglist)
        expected_acc_hotpatch = {
            'arch': self.machine_arch,
            'filename': 'patch-redis-6.2.5-1-ACC-1-1.%s.rpm' % self.machine_arch,
            'name': 'patch-redis-6.2.5-1-ACC',
            'release': '1',
            'version': '1',
        }
        expected_sgl_hotpatch = {
            'arch': self.machine_arch,
            'filename': 'patch-redis-6.2.5-1-SGL_CVE_2023_1111-1-1.%s.rpm' % self.machine_arch,
            'name': 'patch-redis-6.2.5-1-SGL_CVE_2023_1111',
            'release': '1',
            'version': '1',
        }
        expected_res = [expected_acc_hotpatch, expected_sgl_hotpatch]
        self.assertEqual(res, expected_res)

    def test_parse_references_should_return_correctly(self):
        references = get_reference_element()
        res = self.hotpatchUpdateInfo._parse_references(references)
        expected_ref = {
            'href': 'https://nvd.nist.gov/vuln/detail/CVE-2021-1111',
            'id': 'CVE-2021-1111',
            'title': 'CVE-2021-1111',
            'type': 'cve',
        }
        expected_res = [expected_ref]
        self.assertEqual(res, expected_res)

    def test_verify_date_str_lawyer_should_return_default_when_date_str_is_illegal(self):
        expected_res = "1970-01-01 08:00:00"
        datetime_str = "19874327981"
        res = self.hotpatchUpdateInfo._verify_date_str_lawyer(datetime_str)
        self.assertEqual(res, expected_res)
        datetime_str = "1970-01-01 08:00"
        res = self.hotpatchUpdateInfo._verify_date_str_lawyer(datetime_str)
        self.assertEqual(res, expected_res)

    def test_verify_date_str_lawyer_should_return_default_when_date_str_is_illegal(self):
        datetime_str = "1691589211"
        res = self.hotpatchUpdateInfo._verify_date_str_lawyer(datetime_str)
        expected_res = "2023-08-09 21:53:31"
        self.assertEqual(res, expected_res)

    def test_parse_advisory_should_return_correctly(self):
        update = get_advisory_element()
        res = self.hotpatchUpdateInfo._parse_advisory(update)
        expected_res = {
            'id': 'openEuler-SA-2022-1',
            'title': 'An update for mariadb is now available for openEuler-22.03-LTS',
            'severity': 'Important',
            'release': 'openEuler',
            'issued': None,
            'references': [
                {
                    'href': 'https://nvd.nist.gov/vuln/detail/CVE-2021-1111',
                    'id': 'CVE-2021-1111',
                    'title': 'CVE-2021-1111',
                    'type': 'cve',
                }
            ],
            'description': 'Issue summary: ',
            'hotpatches': [
                {
                    'arch': self.machine_arch,
                    'name': 'patch-redis-6.2.5-1-ACC',
                    'version': '1',
                    'release': '1',
                    'filename': 'patch-redis-6.2.5-1-ACC-1-1.%s.rpm' % self.machine_arch,
                },
                {
                    'arch': self.machine_arch,
                    'name': 'patch-redis-6.2.5-1-SGL_CVE_2023_1111',
                    'version': '1',
                    'release': '1',
                    'filename': 'patch-redis-6.2.5-1-SGL_CVE_2023_1111-1-1.%s.rpm' % self.machine_arch,
                },
            ],
            'adv_type': 'security',
        }
        self.assertEqual(res, expected_res)

    def test_store_advisory_info_should_update_hotpatch_cves_correctly(self):
        update = get_advisory_element()
        advisory_kwargs = self.hotpatchUpdateInfo._parse_advisory(update)
        self.hotpatchUpdateInfo._store_advisory_info(advisory_kwargs)
        res = self.hotpatchUpdateInfo._hotpatch_cves['CVE-2021-1111'].cve_id
        expected_res = 'CVE-2021-1111'
        self.assertEqual(res, expected_res)

    def test_store_advisory_info_should_update_hotpatch_advisories_correctly(self):
        update = get_advisory_element()
        advisory_kwargs = self.hotpatchUpdateInfo._parse_advisory(update)
        self.hotpatchUpdateInfo._store_advisory_info(advisory_kwargs)
        res_hotpatches = self.hotpatchUpdateInfo._hotpatch_advisories['openEuler-SA-2022-1'].hotpatches
        res_hotpatches_nevra = [res_hotpatches[0].nevra, res_hotpatches[1].nevra]
        expected_res_hotpatches_nevra = [
            'patch-redis-6.2.5-1-ACC-1-1.%s' % self.machine_arch,
            'patch-redis-6.2.5-1-SGL_CVE_2023_1111-1-1.%s' % self.machine_arch,
        ]
        self.assertEqual(res_hotpatches_nevra, expected_res_hotpatches_nevra)

    def test_store_advisory_info_should_update_ACC_hotpatch_src_pkg_correctly(self):
        update = get_advisory_element()
        advisory_kwargs = self.hotpatchUpdateInfo._parse_advisory(update)
        self.hotpatchUpdateInfo._store_advisory_info(advisory_kwargs)
        res = self.hotpatchUpdateInfo._hotpatch_advisories['openEuler-SA-2022-1'].id
        expected_res = 'openEuler-SA-2022-1'
        self.assertEqual(res, expected_res)


if __name__ == '__main__':
    unittest.main()
