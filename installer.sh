#!/bin/sh
# Baboonstack Online Installer
# curl http://packages.litixsoft.de/installer.sh | sudo sh
# Platform: Linux x86
#           Linux x86_64
#           MacOSX x86_64

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

# Reads local Server Packets
lxm_ls_local() {
 VERSIONS=`find . -maxdepth 1 -name "baboonstack-v*-$LXOS-$LXARCH.tar.gz" -exec basename '{}' ';' | sort | tail -n1`

 if [ ! "$VERSIONS" ]; then
    echo "N/A"
    return
  fi

  echo "$VERSIONS"
  return
}

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

# Installer Help Options
showHelp() {
  echo "Unknow Parameter: $1"
  echo
  echo "Available Parameters:"
  echo
  echo " --without-mongodb                   Exclude MongoDB from Installation"
  echo " --without-redisio                   Exclude RedisIO from Installation"
  echo
  exit 2
}

echo "BaboonStack Installer for Linux/MacOS"
echo

# Make sure only root can run our script
if  [ ! $(id -u) = 0 ]; then
  echo "This script must be run as root" 1>&2
  echo
  exit 1
fi

# Parse Commando Line Arguments to exclude BaboonStack Parts
EXCLUDES=
if [ $# -gt 0 ]; then
  for param in $@; do
    if echo "${param}" | grep -q "\-\-without\-*" ; then
      case "$param" in
        # No MongoDB
        *mongo* )
          echo "Exclude MongoDB..."
          EXCLUDES="$EXCLUDES --exclude=mongo"
        ;;
        # No RedisIO
        *redis* )
          echo "Exclude RedisIO..."
          EXCLUDES="$EXCLUDES --exclude=redisio"
        ;;
        *) showHelp $param ;;
      esac
    else
      showHelp $param
    fi
  done
fi

# First, search locally
BSPACKAGE=`lxm_ls_local`
BSSOURCE=0

# No local Packet found, then try online
if [ "$BSPACKAGE" = "N/A" ]; then
  # Get latest Baboonstack Version from Server
  BSPACKAGE=`lxm_ls_remote | sort | tail -n1 | tr -d ' '`
  BSSOURCE=1

  # Packet available
  if [ "$BSPACKAGE" = "N/A" ]; then
    echo "Ups, sorry. No package found on server."
    echo
    exit 2
  fi

  echo "Download $BSPACKAGE..."

  # Download Packet from Server
  if !(curl -C - --progress-bar "$LXSERVER/$BSPACKAGE" -o "$BSPACKAGE") then
    echo "Sorry, a error occured. Please try again."
    echo
    exit 2
  fi
else
  echo "Local Packet found..."
fi

echo "Install $BSPACKAGE..."

# Create Directory
if [ ! -d "$LXHOMEPATH" ]; then
  echo "Create $LXHOMEPATH..."
  mkdir -p $LXHOMEPATH
fi

# Extract Files with $EXCLUDES
echo "Extract Files..."
tar -zxf "$BSPACKAGE" -C "$LXHOMEPATH" $EXCLUDES

# Files succesfully extracted?
if [ $? -ne 0 ]; then
  echo "Uuuh, error while extract files. Abort!"
  exit 2
fi

# If Remote Packet then delete
if [ $BSSOURCE = 1 ]; then
  rm $BSPACKAGE
fi

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
    if [ $(head -n 1 "$LXHOMEPATH/$dir/lxscript.sh") = "#!/bin/bash" ]; then
      bash "$LXHOMEPATH/$dir/lxscript.sh" install
    else
      sh "$LXHOMEPATH/$dir/lxscript.sh" install
    fi
  fi
done

echo "BaboonStack installed to $LXHOMEPATH"
echo "Done! Bye..."
echo
echo "Enter 'lxm' for more informations" 
echo
