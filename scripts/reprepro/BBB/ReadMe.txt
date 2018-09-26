https://wiki.debian.org/DebianRepository/SetupWithReprepro

https://scotbofh.wordpress.com/2011/04/26/creating-your-own-signed-apt-repository-and-debian-packages/

To clean up if you need to go back a version, or redo an existing version:
  rm -fr db/ dists/ pool/ pkg.tgz


Steps Rob did on an BBB eth:

gpg --gen-key
  Real name: rob baynes
  Email address: rbaynes@mit.edu
  key ends up somewhere in the users ~/.gnupg dir

gpg --armor --export rbaynes@mit.edu > rbaynes@mit.edu.gpg.key

Now run the package building script I made.

mkdir conf
vi conf/distributions

Origin: storage.googleapis.com
Label: apt repository
Codename: stretch
Architectures: armhf source
Components: main
Description: OpenAg debian package repo
SignWith: yes
Pull: stretch

apt-get install reprepro


Run this from the directory containing the conf folder:
  reprepro -Vb . includedeb stretch /home/debian/openag-device-software/build-deb-pkg-tmp/openagbrain_1.0-1_armhf.deb


Upload to the gcloud storage folder from Rob's mac (where gcloud is setup):
tar czvf pkg.tgz conf/ db/ dists/ pool/ rbaynes@mit.edu.gpg.key

Copy pkg.tgz to mac, unpack and do:
gsutil -m cp -r conf/ db/ dists/ pool/ rbaynes@mit.edu.gpg.key gs://openag-v1-debian-packages


-----------------------------------------------------------------------------
Commands to run on a users BBB (put in the image we flash):

wget -O - https://storage.googleapis.com/openag-v1-debian-packages/rbaynes@mit.edu.gpg.key | sudo apt-key add -


sudo bash -c 'echo "deb https://storage.googleapis.com/openag-v1-debian-packages/ stretch main" >> /etc/apt/sources.list'


sudo apt-get update
sudo apt-get install -y openagbrain


-------------------------------------------------------------------------------
To check package status:

dpkg -s openagbrain


-------------------------------------------------------------------------------
To remove the package:

sudo dpkg --purge openagbrain
sudo rm -fr /opt/openagbrain


