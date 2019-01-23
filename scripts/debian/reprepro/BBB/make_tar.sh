#!/bin/bash
rm -f pkg.tgz 
tar czvf pkg.tgz conf/ db/ dists/ pool/ rbaynes@mit.edu.gpg.key
echo "sum pkg.tgz"
sum pkg.tgz
