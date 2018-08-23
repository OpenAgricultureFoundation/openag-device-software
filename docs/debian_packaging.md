# Debian apt-package notes

- Don't use chroot - we need to access /var/lib/connman and /dev/video
- https://wiki.debian.org/Packaging/Intro?action=show&redirect=IntroDebianPackaging

## Steps:
1. [Install debian package tools](#step-1).
1. [Make and correctly name upstream tarball from our source](#step-2).
1. [Add debian packaging files](#step-3).
1. [Build the package](#step-4).
1. [Install the package](#step-5).
1. [Upload the package to our public package server](#step-6).
1. [Release a new version of the package](#step-7).

### Step 1 
#### Install debian package tools on Debian 9.3 on a Beaglebone Black.
    sudo apt-get update
    sudo apt-get install -y build-essential devscripts debhelper

### Step 2 
#### Make and correctly name upstream tarball from our source.
- No extra '-' or '_' in filename: 
  - `openagbrain_1.0.orig.tar.gz`
- The above file / tarball needs to unpack to a directory named exactly the same as the start of the tar file. (NOTICE the '_' is now a '-' in dir) 
  - `openagbrain-1.0/`
- Write a script that creates the tarball and ONLY the files we want to ship.  
  - e.g. exclude `.git/ registration/data  config/device.txt`, etc.
  - Include `pyenv/` since it takes so damn long to build.
  - Include `debian/` since it probably won't change much except for versions.

### Step 3 
#### Add debian packaging files.
    tar xzf openagbrain_1.0.orig.tar.gz
    cd openagbrain-1.0
    
- Create `debian/changelog`
  - dch opens vi on the debian/changelog file,
  - remove the Closes... bug stuff and update the comment, 
  - also update the creator.

```
dch --create -v 1.0-1 --package openagbrain
man dch
```

- Create `debian/compat`
  - `echo "10" > debian/compat`
  - Just use number 10
  - `man debhelper` 

- Create `debian/control`
  - __Do we need more dependencies??__  

```
Source: openagbrain
Maintainer: Rob Baynes <rbaynes@mit.edu>
Section: misc
Priority: optional
Standards-Version: 3.9.2
Build-Depends: debhelper (>= 9)

Package: openagbrain
Architecture: any
Depends: ${shlibs:Depends}, ${misc:Depends}
Description: embedded control software for OpenAg food computers
 openagbrain controls the food computer.
```

- Create `debian/copyright`
  - reuse our GPL3 from github repo:
  - `cp ~/openag-device-software/LICENSE debian/copyright`

- Create `debian/rules`
  - It is a Makefile, so use hard TABs before the dh and $(MAKE) commands.
  - We will need to change our install dir?  First see what this does.
  - `vi debian/rules`

```
#!/usr/bin/make -f
%:
        dh $@

override_dh_auto_install:
        $(MAKE) DESTDIR=$$(pwd)/debian/openagbrain prefix=/usr install
```

- Create debian/source/format
  - `mkdir -p debian/source`
  - `echo "3.0 (quilt)" > debian/source/format`

- Create debian/openagbrain.dirs file - __where do we want our code to live??__
```
usr/bin
usr/share/man/man1
```

### Step 4 
#### Build the package.
    debuild -us -uc

- See what is in the package that was built:
  - `dpkg -c openagbrain_1.0-1_armhf.deb`

### Step 5 
#### Install the package.
    sudo dpkg -i openagbrain_1.0-1_armhf.deb

### Step 6 
#### Upload the package to our public package server.
https://wiki.debian.org/DebianRepository/Setup
- Set up public server to host files.
- Can we use openag-v1.appspot.com or gcloud storage public dir?
- Add this package server URL to our sources.list in our BBB image.
- Look at this debian tool: https://packages.debian.org/search?keywords=reprepro

### Step 7
#### Update the package version and release it
- Script to check the last version you released `show_last_deb_pg_ver.sh`

```
#!/bin/bash

LASTVER=`dpkg-parsechangelog --show-field Version`
echo "The last version of this debian package is: $LASTVER"
```

- Script to update the version (major, minor, patch or all) `create_deb_pkg.sh`

```
#!/bin/bash

# Save the path to THIS script (before we go changing dirs)
ORIGDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Do all package building in a subdir, to avoid polluting the parent dir.
# Add this directory to the projects .gitignore file
SUBDIR="deb-pkg"
rm -fr $SUBDIR

if [ $# -lt 2 ]; then
    echo "Error: missing two mandatory command line args."
    echo "Usage: major.minor patch"
    echo "Example to produce version 2.3.1 (or 2.3-1 in deb format):  2.3 1"
    exit 1
fi

PACKAGE="hithere"
MAJMIN=$1
PATCH=$2
echo "package: $PACKAGE"
echo "major.minor: $MAJMIN"
echo "patch: $PATCH"

# Debian packaging tools require a versioned source dir, so make a temp dir.
# Note: dir uses a '-' between package and major.minor
NEWDIR=$PACKAGE-$MAJMIN
mkdir -p $SUBDIR/$NEWDIR

# Copy ONLY the files that we need to deploy. (not this script, .git/, etc.)
cp -R debian/ $SUBDIR/$NEWDIR
cp hithere.1 hithere.c Makefile $SUBDIR/$NEWDIR

# Create the source tarball that the deb pkg tools require.
# Note: dir uses a '_' between package and major.minor
cd $SUBDIR
TARBALL=$PACKAGE\_$MAJMIN.orig.tar.gz
rm -f $TARBALL
tar czvf $TARBALL $NEWDIR

# Update the debian/changelog (will open vi)
cd $NEWDIR
DEBFULLNAME='Rob Baynes' \
DEBEMAIL='rbaynes@mit.edu' \
dch --distribution stable -v $MAJMIN-$PATCH

# Save the changes to the debian changelog back to the git repo
cp debian/changelog $ORIGDIR/debian

# Build the .deb package file (puts a bunch of files in the parent dir).
debuild -us -uc

echo "Remember to VERIFY, git add, commit, push change to the $ORIGDIR/debian/changelog"

echo "The package you want to upload is in $SUBDIR/$PACKAGE\_$MAJMIN-$PATCH_armhf.deb"
```

- In this example, you are releasing version 2.3.1 (debian uses 2.3-1).

```
./create_deb_pkg.sh 2.3 1
```
