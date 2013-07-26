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
LXHOMEPATH=""
LXBINPATH="/bin"

case "$LXOS" in
  linux)
    LXHOMEPATH=/opt/litixsoft/baboonstack
    LXBINPATH="/bin"
  ;;
  darwin)    
    LXHOMEPATH=/usr/share/litixsoft/baboonstack
    LXBINPATH="/usr/bin"
  ;;
esac

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
if [ ! -d "$LXHOMEPATH" ]; then
  echo "Create $LXHOMEPATH..."
  mkdir -p $LXHOMEPATH
fi

# Extract Files
echo "Extract Files..."
tar -zxf "$REMOTEPACKET" -C "$LXHOMEPATH"
rm $REMOTEPACKET

# Link Node.JS Binarys
echo "Register Node.JS..."

# Find the current Node Version
nodedir=`find "$LXHOMEPATH/node/" -maxdepth 1 -type d -name "*.*.*" | sort | tail -n1`

# Map current
ln -s "$nodedir/bin/node" "$LXBINPATH/node"
ln -s "$nodedir/bin/npm" "$LXBINPATH/npm"

# Write global NPM Configuration
NPMRC="/etc/npmrc"

if [ -d "/etc" ] && [ ! -e "$NPMRC" ]; then
  echo "Create global 'npmrc' configuration file..."
  echo "tmp=/tmp" > $NPMRC
  echo "cache=$LXHOMEPATH/node/npm" >> $NPMRC
else
  echo "Global 'npmrc' configuration file exists, no changes made..."
fi

echo "Register lxManager..."
# Link lxManager Script
ln -s "$LXHOMEPATH/lxm/lxm.sh" "$LXBINPATH/lxm"

# Okay execute every lxscript.sh for completed the installation
dirs=`find "$LXHOMEPATH" -maxdepth 1 -type d -exec basename '{}' ';'`
for dir in $dirs; do
  # If Directory AND lxscript.sh exists
  if [ -x "$LXHOMEPATH/$dir/lxscript.sh" ]; then
    # Execute Script
    echo "Execute Installscript $dir/lxscript.sh..."
    bash "$LXHOMEPATH/$dir/lxscript.sh" install
  fi    
done    

echo "BaboonStack installed to $LXHOMEPATH"
echo "Done! Bye..."
echo
echo "Enter 'lxm' for more informations" 
echo
