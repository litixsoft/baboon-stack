#!/bin/bash
# Update Script for Baboonstack from prev Version
# include lxm
# Parameters: no required

# Try to figure out the arch
LXUNNAME="$(uname -a)"
LXARCH="$(uname -m)"
LXOS=

case "$LXUNNAME" in
  Linux\ *) LXOS=linux ;;
  Darwin\ *) LXOS=darwin ;;
  *)
    echo "Sorry! Unsupported OS."
    exit 5
  ;;
esac

# Some OS specified operations to detect current path etc
case "$LXOS" in
  linux )
    # Linux
    LXCURRPATH="$( dirname "$(readlink -f $0)" )"
    LXHOMEPATH="$( cd "$LXCURRPATH" ; cd .. ; pwd )"
    LXBINPATH="/bin"
    LXLIBPATH="/usr/lib"
  ;;

  darwin )
    # MacOSX
    LXCURRPATH="$(dirname $(readlink ${BASH_SOURCE[0]} || echo ${BASH_SOURCE[0]}))"
    LXHOMEPATH="$(cd "$LXCURRPATH"; cd ..; pwd -P)"
    LXBINPATH="/usr/bin"
    LXLIBPATH="/usr/lib"
  ;;
esac

# Some variables
LXCATALOG="baboonstack.package.conf"
LXOLDCATALOG="baboonstack.previous.package.conf"

# Make sure only root can run our script
if [[ $EUID -ne 0 ]]; then
  echo "This script must be run as root" 1>&2
  echo
  exit 1
fi

# Do nothing on remove
if [ "$1" = "remove" ]; then
  exit 0
fi

# Remove old lxm
if [ -d "$LXHOMEPATH/lxm" ]; then
  echo "Remove old lxManager version..."
  # Remove symlink
  rm -f "$LXBINPATH/lxm"

  # Remove old lxManager directory
  rm -rf "$LXHOMEPATH/lxm"

  # Create old catalog file, old version doesnt has one
  cp "$LXHOMEPATH/bbs/lxm.package.conf" "$LXHOMEPATH/$LXOLDCATALOG"
fi

# Remove wrong old NPM symlink
if [ -h "$LXBINPATH/npm" ]; then
  echo "Update global NPM configuration..."
  npm --global config delete cache

  echo "Remove old ´npm´ symlink..."
  rm -f "$LXBINPATH/npm"
fi

# Remove wrong old NODE symlink
if [ -h "$LXBINPATH/node" ]; then
  echo "Remove old ´node´ symlink..."
  rm -f "$LXBINPATH/node"
fi

# Create /usr/lib/node_modules if not exist
if [ ! -d "$LXLIBPATH/node_modules" ]; then
  mkdir "$LXLIBPATH/node_modules"
fi

# Check if /usr/lib/node_modules/npm exists, then remove
if [ -d "$LXLIBPATH/node_modules/npm" ]; then
  rm -rf "$LXLIBPATH/node_modules/npm"
fi

# Link bbs
if [ ! -h "$LXBINPATH/bbs" ]; then
  echo "Create ´bbs´ symlink..."
  ln -s "$LXHOMEPATH/bbs/bbs" "$LXBINPATH/bbs"
fi

# Copy new catalog file
if [ -f "$LXHOMEPATH/$LXCATALOG" ]; then
  mv "$LXHOMEPATH/$LXCATALOG" "$LXHOMEPATH/$LXOLDCATALOG"
fi

# Move new catalog file to root
if [ -f "$LXHOMEPATH/bbs/$LXCATALOG" ]; then
  mv "$LXHOMEPATH/bbs/$LXCATALOG" "$LXHOMEPATH/$LXCATALOG"
fi

# Done
echo -e "\033[32mSUCCESS: Enter ´bbs´ for package updates.\033[0m"