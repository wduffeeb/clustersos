
Summary: Capture sosreports from multiple nodes simultaneously
Name: clustersos
Version: 1.1.1
Release: 1%{?dist}
Source0: http://people.redhat.com/jhunsake/clustersos/releases/%{name}-%{version}.tar.gz
License: GPLv2
BuildArch: noarch
BuildRequires: python2-devel
Url: https://github.com/TurboTurtle/clustersos
Requires: python >= 2.6
Requires: sos >= 3.0
Requires: python-six
Requires: python2dist(paramiko) >= 1.6


%description
Clustersos is a utility designed to capture sosreports from multiple nodes 
at once and collect them into a single archive. If the nodes are part of 
a cluster, profiles can be used to configure how the sosreport command 
is run on the nodes.

%prep
%setup -q

%build
%py2_build

%install
mkdir -p ${RPM_BUILD_ROOT}%{_mandir}/man1
mkdir -p ${RPM_BUILD_ROOT}%{license}
install -m444 ${RPM_BUILD_DIR}/%{name}-%{version}/LICENSE ${RPM_BUILD_ROOT}%{license}
install -m644 ${RPM_BUILD_DIR}/%{name}-%{version}/man/en/clustersosreport.1 ${RPM_BUILD_ROOT}%{_mandir}/man1/
%py2_install



%check
%{__python2} setup.py test

%files
%{_bindir}/clustersosreport
%{python2_sitelib}/*
%{_mandir}/man1/*

%license LICENSE

%changelog
* Fri Jul 28 2017 Jake Hunsaker <jhunsake@redhat.com> 1.1.1-1
- Added ovirt profile
- Fixed sosreport option handling
- Improved error reporting
- Packaging aligned for distribution

* Tue Jul 18 2017 Jake Hunsaker <jhunsake@redhat.com> 1.1.0-1
- Basic profiles now available

* Tue Jun 20 2017 Jake Hunsaker <jhunsake@redhat.com> 1.0.0-1
- Initial build
