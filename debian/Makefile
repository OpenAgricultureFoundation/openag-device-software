# This makefile is used to make our debian package.  Don't mess with it.
prefix = /opt
appdir = $(prefix)/openagbrain

all: 
	echo "Makefile $@ target"

clean: 
	echo "Makefile $@ target"

install:
	echo "Makefile $@ target"
	# copy all the dirs and files we will install
	./scripts/debian/copy_files_for_deb_pkg.sh $(DESTDIR)$(appdir)
