package=python-mjf
version=0.0.1
all: rpm

clean: 
	rm -fr dist mjf.egg-info python-mjf-*.tar.gz

prepare: 
	python setup.py sdist
	cp dist/mjf-${version}.tar.gz ./${package}-${version}.tar.gz

rpm: prepare
	cp ${package}-${version}.tar.gz /tmp
	gunzip /tmp/${package}-${version}.tar.gz
	tar -rf /tmp/${package}-${version}.tar *.spec
	gzip /tmp/${package}-${version}.tar
	if [ -e *.patch ] ; then cp -f *.patch /tmp; fi 
	rpmbuild -ta /tmp/${package}-${version}.tar.gz
	rm /tmp/${package}*
sources: prepare
	cp ${package}-${version}.tar.gz /tmp
	gunzip /tmp/${package}-${version}.tar.gz
	tar -rf /tmp/${package}-${version}.tar *.spec
	if [ -e *.patch ] ; then cp -f *.patch /tmp; fi 
	gzip /tmp/${package}-${version}.tar
	rpmbuild -ts  --define 'dist .ai6' /tmp/${package}-${version}.tar.gz
	rm /tmp/${package}*
