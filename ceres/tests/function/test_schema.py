#!/usr/bin/python3
# ******************************************************************************
# Copyright (c) Huawei Technologies Co., Ltd. 2024-2024. All rights reserved.
# licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN 'AS IS' BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# ******************************************************************************/
import unittest

from ceres.function.schema import (
    CHANGE_COLLECT_ITEMS_SCHEMA,
    CONF_SYNC_SCHEMA,
    CVE_FIX_SCHEMA,
    CVE_ROLLBACK_SCHEMA,
    CVE_SCAN_SCHEMA,
    HOST_INFO_SCHEMA,
    REGISTER_SCHEMA,
    REMOVE_HOTPATCH_SCHEMA,
    REPO_SET_SCHEMA,
)
from ceres.function.util import validate_data

VALID_REGISTER_DATA = {
    "zeus_ip": "127.0.0.1",
    "zeus_port": 11111,
    "access_token": "token",
    "host_name": "host01",
    "host_group_name": "group01",
    "management": False,
    "ssh_user": "root",
    "password": "changeme",
    "ssh_port": 22,
}


class TestRegisterSchema(unittest.TestCase):
    """Tests for REGISTER_SCHEMA via validate_data."""

    def test_register_schema_should_accept_valid_data(self):
        result, data = validate_data(VALID_REGISTER_DATA, REGISTER_SCHEMA)
        self.assertTrue(result)
        self.assertEqual("host01", data["host_name"])

    def test_register_schema_should_reject_data_missing_required_field(self):
        data = dict(VALID_REGISTER_DATA)
        del data["zeus_ip"]
        result, _ = validate_data(data, REGISTER_SCHEMA)
        self.assertFalse(result)

    def test_register_schema_should_reject_invalid_management_type(self):
        data = dict(VALID_REGISTER_DATA, management="yes")
        result, _ = validate_data(data, REGISTER_SCHEMA)
        self.assertFalse(result)

    def test_register_schema_should_reject_invalid_zeus_port(self):
        data = dict(VALID_REGISTER_DATA, zeus_port=0)
        result, _ = validate_data(data, REGISTER_SCHEMA)
        self.assertFalse(result)


class TestRepoSetSchema(unittest.TestCase):
    """Tests for REPO_SET_SCHEMA via validate_data."""

    def test_repo_set_schema_should_accept_valid_data(self):
        data = {
            "repo_info": {"name": "repo", "repo_content": "content", "dest": "/tmp"},
            "check_items": ["network"],
        }
        result, _ = validate_data(data, REPO_SET_SCHEMA)
        self.assertTrue(result)

    def test_repo_set_schema_should_reject_data_missing_repo_content(self):
        data = {"repo_info": {"name": "repo", "dest": "/tmp"}, "check_items": []}
        result, _ = validate_data(data, REPO_SET_SCHEMA)
        self.assertFalse(result)

    def test_repo_set_schema_should_reject_empty_repo_name(self):
        data = {
            "repo_info": {"name": "", "repo_content": "content", "dest": "/tmp"},
            "check_items": [],
        }
        result, _ = validate_data(data, REPO_SET_SCHEMA)
        self.assertFalse(result)


class TestCveScanSchema(unittest.TestCase):
    """Tests for CVE_SCAN_SCHEMA via validate_data."""

    def test_cve_scan_schema_should_accept_valid_data(self):
        result, _ = validate_data({"check_items": ["network"], "kernel": True}, CVE_SCAN_SCHEMA)
        self.assertTrue(result)

    def test_cve_scan_schema_should_reject_data_missing_check_items(self):
        result, _ = validate_data({"kernel": True}, CVE_SCAN_SCHEMA)
        self.assertFalse(result)

    def test_cve_scan_schema_should_reject_invalid_kernel_value(self):
        result, _ = validate_data({"check_items": [], "kernel": "yes"}, CVE_SCAN_SCHEMA)
        self.assertFalse(result)


class TestCveFixSchema(unittest.TestCase):
    """Tests for CVE_FIX_SCHEMA via validate_data."""

    def test_cve_fix_schema_should_accept_valid_data(self):
        data = {
            "accepted": True,
            "check_items": [],
            "fix_type": "hotpatch",
            "rpms": [{"installed_rpm": "kernel-1", "available_rpm": "kernel-2"}],
        }
        result, _ = validate_data(data, CVE_FIX_SCHEMA)
        self.assertTrue(result)

    def test_cve_fix_schema_should_reject_invalid_fix_type(self):
        data = {
            "accepted": False,
            "check_items": [],
            "fix_type": "unknown",
            "rpms": [{"installed_rpm": "kernel-1", "available_rpm": "kernel-2"}],
        }
        result, _ = validate_data(data, CVE_FIX_SCHEMA)
        self.assertFalse(result)

    def test_cve_fix_schema_should_reject_rpm_missing_installed_rpm(self):
        data = {
            "accepted": False,
            "check_items": [],
            "fix_type": "coldpatch",
            "rpms": [{"available_rpm": "kernel-2"}],
        }
        result, _ = validate_data(data, CVE_FIX_SCHEMA)
        self.assertFalse(result)


class TestCveRollbackSchema(unittest.TestCase):
    """Tests for CVE_ROLLBACK_SCHEMA via validate_data."""

    def test_cve_rollback_schema_should_accept_valid_data(self):
        data = {
            "rollback_type": "hotpatch",
            "installed_rpm": "kernel-2",
            "target_rpm": "kernel-1",
            "dnf_event_start": 1,
            "dnf_event_end": 2,
        }
        result, _ = validate_data(data, CVE_ROLLBACK_SCHEMA)
        self.assertTrue(result)

    def test_cve_rollback_schema_should_accept_null_dnf_events(self):
        data = {
            "rollback_type": "coldpatch",
            "installed_rpm": "kernel-2",
            "target_rpm": "kernel-1",
            "dnf_event_start": None,
            "dnf_event_end": None,
        }
        result, _ = validate_data(data, CVE_ROLLBACK_SCHEMA)
        self.assertTrue(result)

    def test_cve_rollback_schema_should_reject_missing_target_rpm(self):
        data = {
            "rollback_type": "hotpatch",
            "installed_rpm": "kernel-2",
            "dnf_event_start": 1,
            "dnf_event_end": 2,
        }
        result, _ = validate_data(data, CVE_ROLLBACK_SCHEMA)
        self.assertFalse(result)


class TestRemoveHotpatchSchema(unittest.TestCase):
    """Tests for REMOVE_HOTPATCH_SCHEMA via validate_data."""

    def test_remove_hotpatch_schema_should_accept_valid_data(self):
        result, _ = validate_data({"cves": ["CVE-2023-1111"]}, REMOVE_HOTPATCH_SCHEMA)
        self.assertTrue(result)

    def test_remove_hotpatch_schema_should_reject_empty_cves(self):
        result, _ = validate_data({"cves": []}, REMOVE_HOTPATCH_SCHEMA)
        self.assertFalse(result)

    def test_remove_hotpatch_schema_should_reject_missing_cves(self):
        result, _ = validate_data({}, REMOVE_HOTPATCH_SCHEMA)
        self.assertFalse(result)


class TestHostInfoSchema(unittest.TestCase):
    """Tests for HOST_INFO_SCHEMA via validate_data."""

    def test_host_info_schema_should_accept_valid_data(self):
        result, _ = validate_data(["os", "cpu"], HOST_INFO_SCHEMA)
        self.assertTrue(result)

    def test_host_info_schema_should_reject_unknown_item(self):
        result, _ = validate_data(["gpu"], HOST_INFO_SCHEMA)
        self.assertFalse(result)


class TestConfSyncSchema(unittest.TestCase):
    """Tests for CONF_SYNC_SCHEMA via validate_data."""

    def test_conf_sync_schema_should_accept_valid_data(self):
        result, _ = validate_data(
            {"file_path": "/etc/hostname", "content": "host"}, CONF_SYNC_SCHEMA
        )
        self.assertTrue(result)

    def test_conf_sync_schema_should_reject_missing_content(self):
        result, _ = validate_data({"file_path": "/etc/hostname"}, CONF_SYNC_SCHEMA)
        self.assertFalse(result)


class TestChangeCollectItemsSchema(unittest.TestCase):
    """Tests for CHANGE_COLLECT_ITEMS_SCHEMA via validate_data."""

    def test_change_collect_items_schema_should_accept_valid_data(self):
        result, _ = validate_data({"baseCollect": {"switch": "on"}}, CHANGE_COLLECT_ITEMS_SCHEMA)
        self.assertTrue(result)

    def test_change_collect_items_schema_should_reject_invalid_switch_value(self):
        result, _ = validate_data({"baseCollect": {"switch": "yes"}}, CHANGE_COLLECT_ITEMS_SCHEMA)
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
