#!/bin/bash

echo "Have you added, committed and pushed debian/changelog? [y/N]: "
read -n 1 yn
if [[ $yn != "y" && $yn != "Y"  ]]; then
  exit 1
fi

LASTVER=v`dpkg-parsechangelog --show-field Version`

git tag -a $LASTVER -m "official release"
git push origin $LASTVER
