#!/bin/bash
rm -fr conf/ db/ dists/ pool/ rbaynes@mit.edu.gpg.key pkg.tgz
scp debian@172.17.2.30:reprepro/pkg.tgz .
tar xzvf pkg.tgz
echo "sum pkg.tgz"
sum pkg.tgz
