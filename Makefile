
NAME	= clustersos
VERSION := $(shell echo `awk '/^Version:/ {print $$2}' clustersos.spec`)
MAJOR   := $(shell echo $(VERSION) | cut -f 1 -d '.')
MINOR   := $(shell echo $(VERSION) | cut -f 2 -d '.')
RELEASE := $(shell echo `awk '/^Release:/ {gsub(/\%.*/,""); print $2}' clustersos.spec`)

DIRS = clustersosreport clustersosreport/profiles
PYFILE = $(wildcard *.py)


DIST_BUILD_DIR = dist-build
RPM_DEFINES = --define "_topdir %(pwd)/$(DIST_BUILD_DIR)" \
	--define "_builddir %{_topdir}" \
	--define "_rpmdir %{_topdir}" \
	--define "_srcrpmdir %{_topdir}" \
	--define "_specdir %{_topdir}" \
	--define "_sourcedir %{_topdir}"
RPM = rpmbuild
RPM_CMD = $(RPM) $(RPM_DEFINES)
PKG_DIR = $(DIST_BUILD_DIR)/$(NAME)-$(VERSION)

SRC_BUILD = $(DIST_BUILD_DIR)/srcdist

install:
	mkdir -p $(DESTDIR)/usr/sbin
	mkdir -p $(DESTDIR)/usr/share/man/man1
	mkdir -p $(DESTDIR)/usr/share/$(NAME)
	@gzip -c man/en/clustersos.1 > clustersos.1.gz
	install -m755 clustersos $(DESTDIR)/usr/sbin/clustersos
	install -m644 clustersos.1.gz $(DESTDIR)/usr/share/man/man1/.
	install -m644 README.md $(DESTDIR)/usr/share/$(NAME)/.
	for d in $(DIRS); do make DESTDIR=`cd $(DESTDIR); pwd` -C $$d install; [ $$? = 0 ] || exit ; done

$(NAME)-$(VERSION).tar.gz: clean
	@mkdir -p $(PKG_DIR)
	@tar -cv clustersos clustersosreport man LICENSE README.md clustersos.spec Makefile | tar -x -C $(PKG_DIR)
	@tar Ccvzf $(DIST_BUILD_DIR) $(DIST_BUILD_DIR)/$(NAME)-$(VERSION).tar.gz $(NAME)-$(VERSION) --exclude-vcs

build:
	for d in $(DIRS); do make -C $$d; [ $$? = 0 ] || exit 1 ; done

rpm: clean $(NAME)-$(VERSION).tar.gz
	$(RPM_CMD) -tb $(DIST_BUILD_DIR)/$(NAME)-$(VERSION).tar.gz
	

srpm: clean $(NAME)-$(VERSION).tar.gz
	$(RPM_CMD) -ts $(DIST_BUILD_DIR)/$(NAME)-$(VERSION).tar.gz

clean:
	$(RM) -rf dist/
	$(RM) -rf build/ *.rpm
	$(RM) -rf $(DIST_BUILD_DIR)
