%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}


Summary: Capture sosreports from multiple nodes simultaneously
Name: clustersos
Version: 1.1
Release: 1%{?dist}
Source0: http://people.redhat.com/jhunsake/clustersos/releases/clustersos-%{version}.tar.gz
License: GPLv2
Group: Applications/System
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
BuildArch: noarch
Url: https://github.com/TurboTurtle/clustersos
Requires: python >= 2.6
Requires: python-argparse
Requires: python-paramiko >= 1.6
Requires: sos >= 3.0


%description
Clustersos is a utility designed to capture sosreports from multiple nodes at once and collect them into a single archive. If the nodes are part of a cluster, profiles can be used to configure how the sosreport command is run on the nodes.

%prep
%setup -q

%build
make

%install
rm -rf ${RPM_BUILD_ROOT}
make DESTDIR=${RPM_BUILD_ROOT} install
%find_lang %{name} || echo 0

%clean
rm -rf ${RPM_BUILD_ROOT}

%files
%defattr(-,root,root,-)
%{_sbindir}/clustersosreport
%{_datadir}/clustersos/
%{python_sitelib}/*
%{_mandir}/man1/*

%changelog
* Tue Jul 18 2017 Jake Hunsaker <jhunsake@redhat.com> 1.1
- Basic profiles now available

* Tue Jun 20 2017 Jake Hunsaker <jhunsake@redhat.com> 1.0
- Initial build
