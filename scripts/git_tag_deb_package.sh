#!/bin/bash

if [[ "$OSTYPE" == "linux"* ]]; then
  echo "Have you added, committed and pushed debian/changelog? [y/N]: "
  read -n 1 yn
  if [[ $yn != "y" && $yn != "Y"  ]]; then
    exit 1
  fi

  LASTVER=v`dpkg-parsechangelog --show-field Version`

  git tag -a $LASTVER -m "official release"
  git push origin $LASTVER

else
  echo "You have to run this on the BBB you did the debian package build on."
fi
