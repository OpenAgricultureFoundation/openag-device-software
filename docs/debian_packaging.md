# Debian package creation 

## Notes
- [Debian packaging detailed instructions](https://wiki.debian.org/Packaging/Intro?action=show&redirect=IntroDebianPackaging).
- Don't use fakeroot or chroot - we need to access /var/lib/connman and /dev/video.
- [Setting up a package repository with reprepro](https://wiki.debian.org/DebianRepository/SetupWithReprepro).
- [Signing packages in your repository](https://scotbofh.wordpress.com/2011/04/26/creating-your-own-signed-apt-repository-and-debian-packages/).


## Steps to build a debian package 
1. [Install debian package tools](#step-1).
1. [One time PGP key creation](#step-2).
1. [Create the debian package](#step-3).
1. [Install the local package file and test it!](#step-4).
1. [Tag the source with this version](#step-5).
1. [Optional: remove the package](#step-6).
1. [Locally rebuild the package repository](#step-7).
1. [Upload the package repository to our gcloud storage folder](#step-8).
1. [Install package on a Beaglebone](#step-9).


### Step 1 
#### Install tools on Debian 9.3 (stretch) on a Beaglebone Black.
```
sudo apt-get update
sudo apt-get install -y build-essential devscripts debhelper reprepro
```

### Step 2 
#### One time key creation on the system where we create the package repository
```
gpg --gen-key
```
Name and email MUST match debian/changelog signature EXACTLY.

> Real name: rob baynes

> Email address: rbaynes@mit.edu

> The key ends up somewhere in the users ~/.gnupg dir

```
gpg --armor --export rbaynes@mit.edu > rbaynes@mit.edu.gpg.key
```

### Step 3 
#### Create the debian package 
- You have tested this release and run it, right?!?
- Create a directory and pull the code (MUST use this dir, and DON'T forget the period at the end of the git command!):
```
cd /opt
sudo mkdir openagbrain
sudo chown debian:debian openagbrain
cd openagbrain
git clone https://github.com/OpenAgInitiative/openag-device-software .
```
- Check the last version you released:
```
cd /opt/openagbrain
./scripts/show_last_deb_pg_ver.sh
```
- Script parameters are: MAJOR.MINOR PATCH
- In this example, you are releasing version 1.0.1 (debian uses 1.0-1).
- NOTE: this script opens vi to allow you to give a description of the release.  It is OK to edit the file, then save it and quit.
- If you create the same version, just make sure the changelog file (the one the editor opens on) has UNIQUE versions and is sane.
```
cd /opt/openagbrain
./scripts/download_pip_packages.sh
./scripts/create_deb_pkg.sh 1.0 1
```
- See what is in the package that was built:
```
dpkg -c build-deb-pkg-tmp/openagbrain_1.0-1_armhf.deb
```

### Step 4 
#### Install the local package file and test it!
```
sudo dpkg -i build-deb-pkg-tmp/openagbrain_1.0-1_armhf.deb
```

### Step 5
#### Tag the source tree with this version
```
./scripts/git_tag_deb_package.sh
```

### Step 6 
#### Optional: remove the package (you may want to leave it to test upgrades)
```
sudo dpkg --purge openagbrain
sudo rm -fr /opt/openagbrain
```

### Step 7 
#### Locally rebuild the package repository
```
mkdir -p ~/package_repo/conf
cd ~/package_repo
vi conf/distributions

  Origin: storage.googleapis.com
  Label: apt repository
  Codename: stretch
  Architectures: armhf source
  Components: main
  Description: OpenAg debian package repo
  SignWith: yes
  Pull: stretch

reprepro -Vb . includedeb stretch /opt/openagbrain/build-deb-pkg-tmp/openagbrain_1.0-1_armhf.deb

tar czvf pkg.tgz conf/ db/ dists/ pool/ rbaynes@mit.edu.gpg.key
```

### Step 8 
#### Upload the package repository to our gcloud storage folder
This step must be done on a machine with gcloud auth to our account, use Robs MIT MBP.
```
scp debian@172.17.2.30:reprepro_test/pkg.tgz .
rm -fr conf/ db/ dists/ pool/ rbaynes@mit.edu.gpg.key
tar xzvf pkg.tgz

gsutil -m cp -r conf/ db/ dists/ pool/ rbaynes@mit.edu.gpg.key gs://openag-v1-debian-packages
```

### Step 9 
#### Install package on a Beaglebone (put in our flasher image) 
```
sudo bash -c 'wget -O - https://storage.googleapis.com/openag-v1-debian-packages/rbaynes@mit.edu.gpg.key | apt-key add - '

sudo bash -c 'echo "deb https://storage.googleapis.com/openag-v1-debian-packages/ stretch main" >> /etc/apt/sources.list'

sudo apt-get update
sudo apt-get install -y openagbrain

dpkg -s openagbrain
```



