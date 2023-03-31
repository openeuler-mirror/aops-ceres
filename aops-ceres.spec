Name:		aops-ceres
Version:	v1.2.0
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


%prep
%autosetup -n %{name}-%{version}


# build for aops-ceres
%py3_build


# install for aops-ceres
%py3_install


%files
%doc README.*
%attr(0644,root,root) %{_sysconfdir}/aops/ceres.conf
%attr(0644,root,root) /opt/aops/register_example.json
%{python3_sitelib}/aops_ceres*.egg-info
%{python3_sitelib}/ceres/*
%{_bindir}/aops-ceres


%changelog
* Fri Mar 24 2023 wenixn<shusheng.wen@outlook.com> - v1.2.0-1
- change usage of the ceres, don't used it as a service
- update function: scan cve and fix cve

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
