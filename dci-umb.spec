Name:             dci-umb
Version:          0.4.0
Release:          1.VERS%{?dist}
Summary:          DCI UMB
License:          ASL 2.0
URL:              https://github.com/redhat-cip/%{name}
BuildArch:        noarch
Source0:          %{name}-%{version}.tar.gz

BuildRequires:    python2-devel
BuildRequires:    python2-setuptools
BuildRequires:    python-requests
BuildRequires:    python-qpid-proton
BuildRequires:    systemd
Requires:         python-requests
Requires:         python-qpid-proton
%{?systemd_requires}

%description
DCI UMB used to listen on UMB events for dci-feeder-api

%prep
%autosetup -n %{name}-%{version}

%build
%py2_build

%install
%py2_install
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
%{python2_sitelib}/*
%{_bindir}/%{name}
%{_unitdir}/%{name}.service
%config(noreplace) %{_sysconfdir}/%{name}/config

%changelog
* Tue May 12 2020 Guillaume Vincent <gvincent@redhat.com> - 0.4.0-1
- Add multiple sources
* Fri Mar 27 2020 Guillaume Vincent <gvincent@redhat.com> - 0.3.0-1
- Add sender class
* Thu Dec 19 2019 Guillaume Vincent <gvincent@redhat.com> - 0.2.0-1
- Add config file
* Wed Dec 18 2019 Haïkel Guémar <hguemar@redhat.com> - 0.1.0-1
- Initial release