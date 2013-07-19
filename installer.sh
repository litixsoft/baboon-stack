#!/bin/sh
# Baboonstack Online Installer
# curl http://packages.litixsoft.de/installer.sh | sudo sh

# Try to figure out the arch
LXUNNAME="$(uname -a)"
LXARCH="$(uname -m)"
LXOS=

case "$LXUNNAME" in
  Linux\ *) LXOS=linux ;;
  Darwin\ *) LXOS=darwin ;;
  SunOS\ *) LXOS=sunos ;;
  FreeBSD\ *) LXOS=freebsd ;;
esac

case "$LXUNNAME" in
  *x86_64*) LXARCH=x64 ;;
  *i*86*) LXARCH=x86 ;;
  *armv6l*) LXARCH=arm-pi ;;
esac

# Remote Server
LXSERVER="http://packages.litixsoft.de"

# Some variables
bshome=/opt/litixsoft/baboonstack

# Reads remote Server Packets
lxm_ls_remote() {
  VERSIONS=`curl -s "$LXSERVER/" | sed -n 's/.*">\(.*\)<\/a>.*/\1/p' | grep -w "baboonstack-v.*-$LXOS-$LXARCH.tar.gz"`

  if [ ! "$VERSIONS" ]; then
    echo "N/A"
    return
  fi

  echo "$VERSIONS"
  return
}

echo "BaboonStack Online Installer"
echo

# Make sure only root can run our script
if  [ ! $(id -u) = 0 ]; then
  echo "This script must be run as root" 1>&2
  echo
  exit 1
fi

# Get latest Baboonstack Version from Server
REMOTEPACKET=`lxm_ls_remote | sort | tail -n1 | tr -d ' '`

# Packet available
if [ "$REMOTEPACKET" = "N/A" ]; then
  echo "Ups, sorry. No package found on server."
  echo
  exit 2
fi

echo "Download $REMOTEPACKET..."

# Download Packet from Server
if !(curl -C - --progress-bar "$LXSERVER/$REMOTEPACKET" -o "$REMOTEPACKET") then
  echo "Sorry, a error occured. Please try again."
  echo
  exit 2
fi

echo "Install $REMOTEPACKET..."

# Create Directory
if [ ! -d "$bshome" ]; then
  echo "Create $bshome..."
  mkdir -p $bshome
fi

# Extract Files
echo "Extract Files..."
tar -zxf "$REMOTEPACKET" -C "$bshome"

# Link Node.JS Binarys
echo "Register Node.JS..."

# Find the current Node Version
nodedir=`find "$bshome/node/" -maxdepth 1 -type d -name "*.*.*" | sort | tail -n1`

# Map current
ln -s "$nodedir/bin/node" "/bin/node"
ln -s "$nodedir/bin/npm" "/bin/npm"

echo "Register lxManager..."
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