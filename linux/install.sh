#!/bin/bash
# Install Script for BaboonStack
echo
echo "BaboonStack Installer"
echo
FILE="/tmp/out.$$"
GREP="/bin/grep"

# Try to figure out the os and arch for binary fetching
uname="$(uname -a)"
os=
arch="$(uname -m)"
case "$uname" in
  Linux\ *) os=linux ;;
  Darwin\ *) os=darwin ;;
  SunOS\ *) os=sunos ;;
  FreeBSD\ *) os=freebsd ;;
esac
case "$uname" in
  *x86_64*) arch=x64 ;;
  *i*86*) arch=x86 ;;
  *armv6l*) arch=arm-pi ;;
esac

# Some variables
bshome=/opt/litixsoft/baboonstack
bspacket=baboonstack-v1.0.0-linux-$arch.tar.gz

# Check, if packet available
if [ ! -e "$bspacket" ]; then
  echo "Packet '$bspacket' not found. Abort."
  echo
  exit 1
fi

# Make sure only root can run our script
if [[ $EUID -ne 0 ]]; then
  echo "This script must be run as root" 1>&2
  echo
  exit 1
fi

# Create Directory
if [ ! -d "$bshome" ]; then
  echo "Create $bshome..."
  mkdir -p $bshome
fi

# Extract Files
echo "Extract Files..."
tar -zxf "$bspacket" -C "$bshome"

# Link Node.JS Binarys
ln -s "$bshome/node/0.10.12/bin/node" "/bin/node"
ln -s "$bshome/node/0.10.12/bin/npm" "/bin/npm"

# Link lxManager Script
ln -s "$bshome/lxm/lxm.sh" "/bin/lxm"

# Okay execute every lxscript.sh for completed the installation
dirs=`find "$bshome" -maxdepth 1 -type d -exec basename '{}' ';'`
for dir in $dirs; do
  # If Directory AND lxscript.sh exists
  if [ -x "$bshome/$dir/lxscript.sh" ]; then
    # Execute Script
    echo "Execute Installscript $dir/lxscript.sh..."
    sh "$bshome/$dir/lxscript.sh" install
  fi    
done    

echo "BaboonStack installed to $bshome"
echo "Done! Bye..."
echo
echo "Enter 'lxm' for more informations" 
echo