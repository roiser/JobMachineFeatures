%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
%{!?python_version: %global python_version %(%{__python} -c "import sys ; print sys.version[:3]")}

Name:           python-mjf
Version:        0.0.1
Release:        1%{?dist}
Summary:        WLCG machine job features wrapper module
Group:          Development/Languages
License:        ASL 2.0
URL:            https://github.com/roiser/JobMachineFeatures
Source0:        http://cern.ch/uschwick/software/python-mjf-0.0.1.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:      noarch
BuildRequires:  python-devel
BuildRequires:  python-setuptools
Requires:       python-setuptools

%description
This module provides an easy to use 
wrapper module to retrieve job and host 
features on WLCG sites

%prep
%setup -q -n mjf-%{?version} 

%build
%{__python} setup.py build

%install
rm -rf %{buildroot}

%{__python} setup.py install --skip-build --root %{buildroot} \
           --install-data=%{_datadir}

mkdir -p %{buildroot}/usr/bin
cp  %{buildroot}/%{python_sitelib}/mjf/mjf.py %{buildroot}/usr/bin/mjf
chmod +x %{buildroot}/usr/bin/mjf
#%check
#{__python} selftest.py

%clean
rm -rf %{buildroot}


%files
%defattr(-,root,root,-)
#doc AUTHORS CHANGELOG lgpl.txt NEWS README.txt
%{python_sitelib}/mjf*
/usr/bin/mjf
%doc %{python_sitelib}/mjf-%{version}-*-info

%changelog
* Tue Oct 08 2013 Ulrich Schwickerath <ulrich.schwickerath at cern dot ch> - 0.0.1-1
- initial build
