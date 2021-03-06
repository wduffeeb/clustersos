
Summary: Capture sosreports from multiple nodes simultaneously
Name: clustersos
Version: 1.2.0
Release: 1%{?dist}
Source0: http://people.redhat.com/jhunsake/clustersos/releases/%{name}-%{version}.tar.gz
License: GPLv2
BuildArch: noarch
BuildRequires: python3-devel
Url: https://github.com/TurboTurtle/clustersos
Requires: python3 >= 3.3
Requires: sos >= 3.0
Requires: python-six
Requires: python3dist(paramiko) >= 2.0


%description
Clustersos is a utility designed to capture sosreports from multiple nodes 
at once and collect them into a single archive. If the nodes are part of 
a cluster, profiles can be used to configure how the sosreport command 
is run on the nodes.

%prep
%setup -q

%build
%py3_build

%install
mkdir -p ${RPM_BUILD_ROOT}%{_mandir}/man1
mkdir -p ${RPM_BUILD_ROOT}%{license}
install -m444 ${RPM_BUILD_DIR}/%{name}-%{version}/LICENSE ${RPM_BUILD_ROOT}%{license}
install -m644 ${RPM_BUILD_DIR}/%{name}-%{version}/man/en/clustersosreport.1 ${RPM_BUILD_ROOT}%{_mandir}/man1/
%py3_install



%check
%{__python3} setup.py test

%files
%{_bindir}/clustersosreport
%{python3_sitelib}/*
%{_mandir}/man1/*

%license LICENSE

%changelog
* Wed Oct 11 2017 Jake Hunsaker <jhunsake@redhat.com> 1.2.0-1
- Moved to using python3 (#8)
- Made Atomic Host checks the default behavior for profiles
- Fixed error reporting from sos on nodes

* Thu Sep 14 2017 Jake Hunsaker <jhunsake@redhat.com> 1.1.3-1
- Fix double enumeration of localhost if localhost is node
- Split OpenShift profile from Kubernetes (#11)
- Fix run failure with cluster-type None

* Sat Aug 19 2017 Jake Hunsaker <jhunsake@redhat.com> 1.1.2-1
- Fix local sosreport command execution
- Fix local node enumeration on some profiles (#6)

* Fri Jul 28 2017 Jake Hunsaker <jhunsake@redhat.com> 1.1.1-1
- Added ovirt profile
- Fixed sosreport option handling
- Improved error reporting
- Packaging aligned for distribution

* Tue Jul 18 2017 Jake Hunsaker <jhunsake@redhat.com> 1.1.0-1
- Basic profiles now available

* Tue Jun 20 2017 Jake Hunsaker <jhunsake@redhat.com> 1.0.0-1
- Initial build
