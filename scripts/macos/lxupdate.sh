#!/bin/bash
# Update Script for Baboonstack
# Parameters: source target

# Some variables
LXHOMEPATH="$(pwd)"
LXBINPATH="/usr/bin"
LXLIBPATH="/usr/lib"
LXMODE=""

# Make sure only root can run our script
if [[ $EUID -ne 0 ]]; then
  echo "This script must be run as root" 1>&2
  echo
  exit 1
fi

# Remove old lxm
if [ -d "$LXHOMEPATH/lxm" ]; then
	rm -f "$LXBINPATH/lxm"
	rm -rf "$LXHOMEPATH/lxm"
fi

# Link bbs
ln -s "$LXHOMEPATH/bbs/bbs" "$LXBINPATH/bbs"