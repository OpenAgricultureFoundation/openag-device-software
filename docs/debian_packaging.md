# Debian package creation notes

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
    sudo apt-get install -y build-essential devscripts debhelper reprepro

### Step 2 
#### Make and correctly name upstream tarball from our source.
- No extra '-' or '_' in filename: 
  - `openagbrain_1.0.orig.tar.gz`
- The above file / tarball needs to unpack to a directory named exactly the same as the start of the tar file. (NOTICE the '_' is now a '-' in dir) 
  - `openagbrain-1.0/`
- Write a script that creates the tarball and ONLY the files we want to ship.  
  - e.g. exclude `.git/ registration/data  config/device.txt`, etc.
  - Include `pyenv/` since it takes so long to build.
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
  - Add the dependencies of our package (just the big ones).

```
Source: openagbrain
Maintainer: Rob Baynes <rbaynes@mit.edu>
Section: misc
Priority: optional
Standards-Version: 3.9.8
Build-Depends: debhelper (>= 9)

Package: openagbrain
Architecture: any
Depends: ${misc:Depends}, postgresql, python3
Description: OpenAg Brain
 Controls food computers.
```

- Create `debian/copyright`
  - reuse our GPL3 from github repo:
  - `cp ~/openag-device-software/LICENSE debian/copyright`

- Create `debian/rules`
  - It is a Makefile, so use hard TABs before the dh and $(MAKE) commands.

```
#!/usr/bin/make -f
%:
        dh $@
```

- Create debian/source/format
  - `mkdir -p debian/source`
  - `echo "3.0 (quilt)" > debian/source/format`

- Create debian/openagbrain.dirs file 
```
opt/openagbrain
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
- Can we use gcloud storage public dir?
- Add this package server URL to our sources.list in our BBB image.
- Look at the debian reprepro tool.

### Step 7
#### Update the package version and release it
- Script to check the last version you released `scripts/show_last_deb_pg_ver.sh`

- Script to update the version (major, minor, patch or all) `scripts/create_deb_pkg.sh`


- In this example, you are releasing version 2.3.1 (debian uses 2.3-1).

```
./create_deb_pkg.sh 2.3 1
```

# Remove a package
```
sudo dpkg --purge openagbrain
```

# Install a package from a local file
```
sudo dpkg -i deb-pkg/openagbrain_1.0-3_armhf.deb
```


