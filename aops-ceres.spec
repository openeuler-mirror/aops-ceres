Name:		aops-ceres
Version:	v2.0.0
Release:	1
Summary:	An agent which needs to be adopted in client, it managers some plugins, such as gala-gopher(kpi collection), fluentd(log collection) and so on.
License:	MulanPSL2
URL:		https://gitee.com/openeuler/%{name}
Source0:	%{name}-%{version}.tar.gz


BuildRequires:  python3-setuptools
Requires:   python3-requests python3-flask python3-connexion python3-configparser python3-jsonschema
Requires:   python3-flask-testing python3-libconf python3-swagger-ui-bundle
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
%attr(0755,root,root) %{_unitdir}/aops-ceres.service
%{python3_sitelib}/aops_ceres*.egg-info
%{python3_sitelib}/ceres/*
%{_bindir}/aops-ceres


%changelog
* Tue Oct 11 2022 zhuyuncheng<zhuyuncheng@huawei.com> - v2.0.0-1
- Package init
