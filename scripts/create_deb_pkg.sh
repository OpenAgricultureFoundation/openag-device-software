#!/bin/bash

# This script creates a debian package of the OpenAg Brain python app for
# installation on a Beaglebone that controls a Food Computer.

if [ $# -lt 2 ]; then
    echo "Error: missing two mandatory command line args."
    echo "Usage: major.minor patch"
    echo "Example to produce version 2.3.1 (or 2.3-1 in deb format):  2.3 1"
    exit 1
fi

PACKAGE="openagbrain"
MAJMIN=$1
PATCH=$2
echo "Package: $PACKAGE"
echo "Major.Minor: $MAJMIN"
echo "Patch: $PATCH"

# Save the path to THIS script (before we go changing dirs)
TOPDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# The top of our source tree is the parent of this scripts dir
TOPDIR+=/..
cd $TOPDIR

# Do all package building in a subdir, to avoid polluting the parent dir.
# Add this directory to the projects .gitignore file
SUBDIR=$TOPDIR/"build-deb-pkg-tmp"
rm -fr $SUBDIR

# Debian packaging tools require a versioned source dir, so make a temp dir.
# NOTE: dir uses a '-' between package and major.minor
VERDIR=$PACKAGE-$MAJMIN
mkdir -p $SUBDIR/$VERDIR

# Copy the debian package building control files to the versioned dir.
cp -R debian/ $SUBDIR/$VERDIR
cp debian/Makefile $SUBDIR/$VERDIR

# Copy ONLY the dirs & files that we need to deploy. 
# (not this script, .git/, etc.)
./scripts/copy_files_for_deb_pkg.sh $SUBDIR/$VERDIR

# Create the source tarball that the deb pkg tools require.
# NOTE: dir uses a '_' between package and major.minor
cd $SUBDIR
TARBALL=$PACKAGE\_$MAJMIN.orig.tar.gz
rm -f $TARBALL 
tar czvf $TARBALL $VERDIR

# Update the debian/changelog (will open vi)
cd $VERDIR
DEBFULLNAME='Rob Baynes' \
DEBEMAIL='rbaynes@mit.edu' \
dch --distribution stable -v $MAJMIN-$PATCH

# Save the changes to the debian changelog back to the git repo
cp debian/changelog $TOPDIR/debian/

# Build the .deb package file (puts a bunch of files in the parent dir).
# Skip the package checks (lintian) and don't sign source or changes (-us -uc).
debuild --no-lintian -us -uc 

PKG=$SUBDIR/$PACKAGE\_$MAJMIN-$PATCH\_armhf.deb
echo ""
echo "TEST this package: sudo dpkg -i $PKG"

echo ""
echo "Remember to VERIFY, git add, commit, push change to the $TOPDIR/debian/changelog"

echo ""
echo "The package you want to upload is in $PKG"


