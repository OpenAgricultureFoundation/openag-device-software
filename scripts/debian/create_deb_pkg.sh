#!/bin/bash

# This script creates a debian package of the OpenAg Brain python app for
# installation on a Beaglebone that controls a Food Computer.

# TODO: Clean up debian scripts to use the same conventions used by the other bash scripts 
# in this project -- only need to do this if plan to make more debian packages as opposed
# to distributing images and ota-updates with a service like mender.io

if [ $# -lt 2 ]; then
    echo "Error: missing two mandatory command line args."
    echo "Usage: major.minor patch"
    echo "Example to produce version 2.3.1 (or 2.3-1 in deb format):  2.3 1"
    exit 1
fi

if [[ "$OSTYPE" != "linux"* ]]; then
    echo "This script can only be run on a BBB."
    exit 1
fi 

# Get the path to THIS script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Have we setup the local python environment we need?
if [[ "$DIR" != "/opt/openagbrain/scripts" ]]; then
    echo ''
    echo 'Error: Go pull the source in /opt/openagbrain and try again.
Exiting.'
    echo ''
    exit 1
fi

# Have we setup the local python environment we need?
if ! [ -d $DIR/../venv ]; then
    echo ''
    echo 'Error: please run: ./scripts/setup_python.sh
Exiting.'
    echo ''
    exit 1
fi

# Downloaded the packages we need
# Save the path to THIS script (before we go changing dirs)
TOPDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# The top of our source tree is the parent of this scripts dir
TOPDIR+=/..
pip3.6 download -d $TOPDIR/venv/pip_download -r $TOPDIR/requirements.txt

# Install any new python modules
echo 'Installing any new python modules into the virtual env we package...'
echo ''
source venv/bin/activate
pip3 install -f venv/pip_download -r requirements.txt 


echo 'Caching static web files (bootstrap, FA, etc.)'
echo ''
python3.6 manage.py collectstatic --clear --link --noinput


echo "Your editor will open in a minute, you should summarize why you are making this release, then save and close the editor to continue building the package."
echo ""


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
./scripts/debian/copy_files_for_deb_pkg.sh $SUBDIR/$VERDIR

# Create the source tarball that the deb pkg tools require.
# NOTE: dir uses a '_' between package and major.minor
cd $SUBDIR
TARBALL=$PACKAGE\_$MAJMIN.orig.tar.gz
rm -f $TARBALL 
tar czvf $TARBALL $VERDIR

# Update the debian/changelog (will open vi)
cd $VERDIR
DEBFULLNAME='rob baynes' \
DEBEMAIL='rbaynes@mit.edu' \
dch --distribution stable -v $MAJMIN-$PATCH

# Save the changes to the debian changelog back to the git repo
cp debian/changelog $TOPDIR/debian/

# Build the .deb package file (puts a bunch of files in the parent dir).
# Skip the package checks (lintian) and sign the source and changes.
#No signing: debuild --no-lintian -us -uc 
debuild --no-lintian 

PKG=$SUBDIR/$PACKAGE\_$MAJMIN-$PATCH\_armhf.deb
echo ""
echo "TEST this package: sudo dpkg -i $PKG"

echo ""
echo "The package you want to upload is in $PKG"

echo ""
echo "Remember to VERIFY, git add, commit, push change to the $TOPDIR/debian/changelog"
echo ""

echo "Then run scripts/debian/git_tag_deb_package.sh"
echo ""
