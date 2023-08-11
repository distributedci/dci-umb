%if 0%{?rhel} && 0%{?rhel} < 8
%global with_python2 1
%else
%global with_python3 1
%endif

Name:             dci-umb
Version:          SEMVER
Release:          1.VERS%{?dist}
Summary:          DCI UMB
License:          ASL 2.0
URL:              https://github.com/redhat-cip/%{name}
BuildArch:        noarch
Source0:          %{name}-%{version}.devDATE.tar.gz

BuildRequires:    systemd
%if 0%{?with_python2}
BuildRequires:    python2-devel
BuildRequires:    python2-setuptools
Requires:         python-requests
Requires:         python-qpid-proton
%else
BuildRequires:    python3-devel
Requires:         python3-requests
Requires:         python3-qpid-proton
%endif
%{?systemd_requires}

%description
DCI UMB used to listen on UMB events for dci-feeder-api

%prep
%autosetup -n %{name}-%{version}.devDATE

%build
%if 0%{?with_python2}
%py2_build
%else
%py3_build
%endif

%install
%if 0%{?with_python2}
%py2_install
%else
%py3_install
%endif
install -p -D -m0644 systemd/config %{buildroot}%{_sysconfdir}/%{name}/config
install -p -D -m0644 systemd/%{name}.service %{buildroot}%{_unitdir}/%{name}.service

%post
%systemd_post %{name}.service

%preun
%systemd_preun %{name}.service

%postun
%systemd_postun_with_restart %{name}.service

%files
%license LICENSE
%doc README.md
%if 0%{?with_python2}
%{python2_sitelib}/*
%else
%{python3_sitelib}/*
%endif
%{_bindir}/%{name}
%{_unitdir}/%{name}.service
%config(noreplace) %{_sysconfdir}/%{name}/config

%changelog
* Mon Nov 07 2022 Guillaume Vincent <gvincent@redhat.com> - 0.4.2-1
- Fix build for EL9
* Tue Nov 03 2020 Guillaume Vincent <gvincent@redhat.com> - 0.4.1-1
- Close connection after sending UMB event
* Thu Oct 22 2020 Haïkel Guémar <hguemar@fedoraproject.org> - 0.4.0-2
- Add EL8 support
* Tue May 12 2020 Guillaume Vincent <gvincent@redhat.com> - 0.4.0-1
- Add multiple sources
* Fri Mar 27 2020 Guillaume Vincent <gvincent@redhat.com> - 0.3.0-1
- Add sender class
* Thu Dec 19 2019 Guillaume Vincent <gvincent@redhat.com> - 0.2.0-1
- Add config file
* Wed Dec 18 2019 Haïkel Guémar <hguemar@redhat.com> - 0.1.0-1
- Initial release
