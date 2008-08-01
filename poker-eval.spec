%bcond_without          java

%if %with java
%define gcj_support     1
%endif

%define lib_major       1
%define lib_name_orig   %mklibname %{name}
%define lib_name        %{lib_name_orig}%{lib_major}

Name:           poker-eval
Version:        134.0
Release:        %mkrel 8
Epoch:          0
Summary:        Poker hand evaluator library
Group:          System/Libraries
License:        GPL
URL:            http://pokersource.org/poker-eval/
Source0:        http://download.gna.org/pokersource/sources/poker-eval-%{version}.tar.gz
Source1:        %{name}-java.tar.bz2
Source2:        %{name}.Makefile-java
Source3:        %{name}-saie.script
Patch0:         %{name}-java-junit.patch
Patch1:         %{name}-java-load-library.patch
BuildRequires:  valgrind
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root

%description
This package is a free (GPL) toolkit for writing programs which
simulate or analyze poker games.

%package -n %{lib_name}
Summary:        Main library for %{name}
Group:          System/Libraries
Provides:       %{lib_name_orig} = %{epoch}:%{version}-%{release}
Provides:       %{name} = %{epoch}:%{version}-%{release}

%description -n %{lib_name}
This package is a free (GPL) toolkit for writing programs which
simulate or analyze poker games.

%package -n %{lib_name}-devel
Summary: Poker hand evaluator library development files
Group: System/Libraries
Requires:       %{lib_name} = %{epoch}:%{version}-%{release}
Provides:       %{lib_name_orig}-devel = %{epoch}:%{version}-%{release}
Provides:       %{name}-devel = %{epoch}:%{version}-%{release}
Provides:       lib%{name}-devel = %{epoch}:%{version}-%{release}

%description -n %{lib_name}-devel
This package contains the library needed to run programs dynamically
linked with %{name}.

%if %with java
%package -n pokersource
Summary:        Java library for %{name}
Group:          Development/Java
Provides:       %{lib_name_orig}-java = %{epoch}:%{version}-%{release}
Provides:       %{name}-java = %{epoch}:%{version}-%{release}
BuildRequires:  gnu.getopt
BuildRequires:  java-rpmbuild
BuildRequires:  junit
BuildRequires:  oro
%if %{gcj_support}
BuildRequires:  java-gcj-compat-devel
%else
BuildRequires:  java-devel >= 0:1.4.2
%endif

%description -n pokersource
This package is a free (GPL) toolkit for writing java programs which
simulate or analyze poker games.

%package -n pokersource-javadoc
Summary:        Javadoc for pokersource
Group:          Development/Java

%description -n pokersource-javadoc
Javadoc for pokersource-javadoc.
%endif

%prep
%setup -q
%if %with java
%setup -q -a 1
%patch0 -p1
%patch1 -p1
%{__cp} -a %{SOURCE2} java/Makefile
%{__mkdir_p} java/lib
pushd java/lib
%{__ln_s} %{_javadir}/gnu.getopt.jar gnu.getopt.jar
%{__ln_s} %{_javadir}/junit.jar junit.jar
%{__ln_s} %{_javadir}/jakarta-oro.jar jakarta-oro.jar
popd
%endif

# use examples/ directory for devel package %doc section
%{__mkdir_p} tmp/examples && %{__cp} -a examples/*.c tmp/examples
%{__rm} -f tmp/examples/getopt_w32.c

%build
%{configure2_5x} --disable-static
%{make}
%if %with java
pushd java
export CLASSPATH=.
%{__make} CC="gcc" CFLAGS="-fPIC %{optflags}" JDKHOME=%{java_home} JAVAC="%{javac} -source 1.4" JAVADOC="%{javadoc} -source 1.4" || :
popd
%endif

%install
%{__rm} -rf %{buildroot}
%{makeinstall_std}
%{__rm} -rf %{buildroot}%{_libdir}/*.la

%if %with java
pushd java
%{__mkdir_p} %{buildroot}%{_javadir}
%{__install} -p -m 644 pokersource.jar \
%{buildroot}%{_javadir}/pokersource-%{version}.jar
(cd %{buildroot}%{_javadir} && for jar in *-%{version}*; do %{__ln_s} ${jar} ${jar/-%{version}/}; done)

%{__mkdir_p} %{buildroot}%{_javadocdir}/pokersource-%{version}
# FIXME: javadoc -source 1.4 still doesn't like the enum keyword
%{__cp} -a javadoc/* %{buildroot}%{_javadocdir}/pokersource-%{version} || :
(cd %{buildroot}%{_javadocdir} && %{__ln_s} pokersource-%{version} pokersource)

%{__mkdir_p} %{buildroot}%{_libdir}
%{__install} -m 755 ../lib/libpokerjni.so %{buildroot}%{_libdir}

%{__mkdir_p} %{buildroot}%{_bindir}
%{__install} -m 755 %{SOURCE3} %{buildroot}%{_bindir}/saie
%{__perl} -pi -e 's|/usr/lib|%{_libdir}|g' %{buildroot}%{_bindir}/saie
popd

%multiarch_includes %{buildroot}%{_includedir}/%{name}/poker_config.h

%if %{gcj_support}
%{_bindir}/aot-compile-rpm
%endif
%endif

%check
%{make} check

%if %with java
pushd java
# FIXME: doesn't work, can't find poker-eval library
#%%{make} JDKHOME=%{java_home} JAVA="%{java} -Djava.library.path=%{buildroot}%{_libdir} -cp %{buildroot}%{_javadir}/pokersource.jar:$(build-classpath gnu.getopt jakarta-oro)" test develtest
popd
%endif

%clean
%{__rm} -rf %{buildroot}

%if %mdkversion < 200900
%post -n %{lib_name} -p /sbin/ldconfig
%endif

%if %mdkversion < 200900
%postun -n %{lib_name} -p /sbin/ldconfig
%endif

%if %with java
%if %{gcj_support}
%post -n pokersource
%{update_gcjdb}

%postun -n pokersource
%{clean_gcjdb}
%endif
%endif

%files -n %{lib_name}
%defattr(-,root,root,-)
%doc AUTHORS ChangeLog COPYING NEWS README TODO WHATS-HERE
%{_libdir}/libpoker-eval*.so.*

%files -n %{lib_name}-devel
%defattr(-,root,root,-)
%doc tmp/examples
%dir %{_includedir}/%{name}
%{_includedir}/%{name}/combinations.h
%{_includedir}/%{name}/deck.h
%{_includedir}/%{name}/deck_astud.h
%{_includedir}/%{name}/deck_joker.h
%{_includedir}/%{name}/deck_std.h
%{_includedir}/%{name}/deck_undef.h
%{_includedir}/%{name}/enumdefs.h
%{_includedir}/%{name}/enumerate.h
%{_includedir}/%{name}/enumord.h
%{_includedir}/%{name}/evx_defs.h
%{_includedir}/%{name}/game_astud.h
%{_includedir}/%{name}/game_joker.h
%{_includedir}/%{name}/game_std.h
%{_includedir}/%{name}/handval.h
%{_includedir}/%{name}/handval_low.h
%multiarch %{_includedir}/%{name}/poker_config.h
%{multiarch_includedir}/*
%{_includedir}/%{name}/poker_defs.h
%{_includedir}/%{name}/poker_wrapper.h
%{_includedir}/%{name}/pokereval_export.h
%{_includedir}/%{name}/rules_astud.h
%{_includedir}/%{name}/rules_joker.h
%{_includedir}/%{name}/rules_std.h
%{_includedir}/%{name}/rules_undef.h
%{_includedir}/%{name}/inlines/eval.h
%{_includedir}/%{name}/inlines/eval_astud.h
%{_includedir}/%{name}/inlines/eval_joker.h
%{_includedir}/%{name}/inlines/eval_joker_low.h
%{_includedir}/%{name}/inlines/eval_joker_low8.h
%{_includedir}/%{name}/inlines/eval_low.h
%{_includedir}/%{name}/inlines/eval_low27.h
%{_includedir}/%{name}/inlines/eval_low8.h
%{_includedir}/%{name}/inlines/eval_omaha.h
%{_includedir}/%{name}/inlines/eval_type.h
%{_includedir}/%{name}/inlines/evx5.h
%{_includedir}/%{name}/inlines/evx7.h
%{_includedir}/%{name}/inlines/evx_action.h
%{_includedir}/%{name}/inlines/evx_inlines.h
%{_libdir}/libpoker-eval*.so
%{_libdir}/pkgconfig/%{name}.pc

%if %with java
%files -n pokersource
%defattr(0644,root,root,0755)
%doc WHATS-HERE.Java java/sample1.hho
%attr(0755,root,root) %{_bindir}/saie
%{_javadir}/pokersource.jar
%{_javadir}/pokersource-%{version}.jar
%attr(-,root,root) %{_libdir}/libpokerjni.so
%if %{gcj_support}
%dir %{_libdir}/gcj/%{name}
%attr(-,root,root) %{_libdir}/gcj/%{name}/*.jar.*
%endif

%files -n pokersource-javadoc
%defattr(0644,root,root,0755)
%{_javadocdir}/pokersource-%{version}
%{_javadocdir}/pokersource
%endif


