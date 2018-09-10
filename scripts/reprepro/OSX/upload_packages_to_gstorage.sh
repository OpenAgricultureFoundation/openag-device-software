#!/bin/bash
gsutil -m cp -r conf/ db/ dists/ pool/ rbaynes@mit.edu.gpg.key gs://openag-v1-debian-packages
