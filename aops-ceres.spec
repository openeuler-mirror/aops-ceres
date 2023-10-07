Name:		aops-ceres
Version:	v1.3.3
Release:	1
Summary:	An agent which needs to be adopted in client, it managers some plugins, such as gala-gopher(kpi collection), fluentd(log collection) and so on.
License:	MulanPSL2
URL:		https://gitee.com/openeuler/%{name}
Source0:	%{name}-%{version}.tar.gz


BuildRequires:  python3-setuptools
Requires:   python3-requests  python3-jsonschema python3-libconf
Requires:   python3-concurrent-log-handler dmidecode
Provides:   aops-ceres
Conflicts:  aops-agent


%description
An agent which needs to be adopted in client, it managers some plugins, such as gala-gopher(kpi collection), fluentd(log collection) and so on.


%package -n dnf-hotpatch-plugin
Summary: dnf hotpatch plugin
Requires: python3-hawkey python3-dnf syscare >= 1.1.0


%description -n dnf-hotpatch-plugin
dnf hotpatch plugin, it's about hotpatch query and fix


%prep
%autosetup -n %{name}-%{version}


# build for aops-ceres
%py3_build


# install for aops-ceres
%py3_install


# install for aops-dnf-plugin
cp -r hotpatch %{buildroot}/%{python3_sitelib}/dnf-plugins/


%files
%doc README.*
%attr(0644,root,root) %{_sysconfdir}/aops/ceres.conf
%attr(0644,root,root) /opt/aops/register_example.json
%{python3_sitelib}/aops_ceres*.egg-info
%{python3_sitelib}/ceres/*
%{_bindir}/aops-ceres


%files -n dnf-hotpatch-plugin
%{python3_sitelib}/dnf-plugins/*


%changelog
* Fri Sep 22 2023 wenxin<shusheng.wen@outlook.com> - v1.3.3-1
- add hotpatch plugin

* Wed Sep 20 2023 wenxin<shusheng.wen@outlook.com> - v1.3.2-1
- fix query fixed cves info error by dnf

* Tue Sep 19 2023 wenxin<shusheng.wen@outlook.com> - v1.3.1-5
- update func about querying applied hotpatch info

* Tue Sep 19 2023 wenxin<shusheng.wen@outlook.com> - v1.3.1-4
- update method of querying fixed cves by dnf plugin

* Wed Sep 13 2023 wenxin<shusheng.wen@outlook.com> - v1.3.1-3
- add file sync func

* Wed Sep 13 2023 wenxin<shusheng.wen@outlook.com> - v1.3.1-2
- update func named set_hotpatch_status_by_dnf_plugin

* Mon Sep 11 2023 zhuyuncheng<zhu-yuncheng@huawei.com> - v1.3.1-1
- update rollback task logic, better returned log
- update status code and return None when installed_rpm or available_rpm is empty

* Wed Aug 30 2023 wenxin<shusheng.wen@outlook.com> - v1.3.0-3
- update query disk info func

* Tue Aug 29 2023 wenxin<shusheng.wen@outlook.com> - v1.3.0-2
- fix bug: repeated display of vulnerabilities fixed by hotpatch

* Tue Aug 29 2023 wenxin<shusheng.wen@outlook.com> - v1.3.0-1
- update vulnerability scanning method and vulnerability fix method

* Fri Jun 30 2023 wenxin<shusheng.wen@outlook.com> - v1.2.1-7
- update release

* Fri Jun 30 2023 gongzhengtang<gong_zhengtang@163.com> - v1.2.1-6
- Match the correctly applied hot patches

* Wed Jun 21 2023 wenxin<shusheng.wen@outlook.com> - v1.2.1-5
- update hostpatch info query func

* Fri Jun 09 2023 wenxin<shusheng.wen@outlook.com> - v1.2.1-4
- fix issue: cve fix result doesn't match log

* Fri Jun 02 2023 wenxin<shusheng.wen@outlook.com> - v1.2.1-3
- update cve scan and cve fix

* Thu Jun 01 2023 wenxin<shusheng.wen@outlook.com> - v1.2.1-2
- modify the return result when no hot patch is matched

* Tue May 23 2023 wenixn<shusheng.wen@outlook.com> - v1.2.1-1
- the client supports hot patch cve rollback

* Thu May 11 2023 wenixn<shusheng.wen@outlook.com> - v1.2.0-4
- fix hotpatch fail show succeed bug

* Tue May 9 2023 ptyang<1475324955@qq.com> - v1.2.0-3
- fix hotpatch fail show succeed bug

* Thu Apr 27 2023 wenixn<shusheng.wen@outlook.com> - v1.2.0-2
- fix shell command return error;update registe funciton

* Mon Apr 17 2023 wenixn<shusheng.wen@outlook.com> - v1.2.0-1
- change usage of the ceres, don't used it as a service
- update function: scan cve and fix cve
- udpate cve fix, support for hotpatch

* Fri Dec 23 2022 wenxin<shusheng.wen@outlook.com> - v1.1.0-4
- Handle when the http response result is not 200

* Wed Dec 07 2022 wenxin<shusheng.wen@outlook.com> - v1.1.0-3
- update cve fix

* Wed Dec 07 2022 wenxin<shusheng.wen@outlook.com> - v1.1.0-2
- modify args of register func, add register file template

* Fri Nov 25 2022 wenxin<shusheng.wen@outlook.com> - v1.1.0-1
- remove test cases that use the responses module

* Wed Nov 23 2022 wenxin<shusheng.wen@outlook.com> - v1.0.0-3
- remove test case: remove test case about register

* Wed Nov 23 2022 wenxin<shusheng.wen@outlook.com> - v1.0.0-2
- update register: add field os_version for register

* Tue Nov 22 2022 zhuyuncheng<zhuyuncheng@huawei.com> - v1.0.0-1
- Package init
