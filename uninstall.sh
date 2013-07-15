#!/bin/bash
# Install Script for BaboonStack
echo "BaboonStack De-Installer"
echo
FILE="/tmp/out.$$"
GREP="/bin/grep"

function request {
  read -p "$1: [Y/n] " answer
  case "$answer" in
    Yes|yes|Y|y|"") return 0 ;;
    No|no|N|n) return 1 ;;
        *) return 1 ;;
  esac
}

# Some variables
bshome=/opt/litixsoft/baboonstack

# Make sure only root can run our script
if [[ $EUID -ne 0 ]]; then
  echo "This script must be run as root" 1>&2
  echo
  exit 1
fi

# Remove Node.JS
if [ -d "$bshome/node/0.10.12" ]; then
  # Remove Symlink
  rm /bin/node
  rm /bin/npm
  rm -r "$bshome/node"
fi

# Remove MongoDB
service mongod stop
update-rc.d -f mongod remove

rm /bin/mongo
rm /bin/mongod

# Remove RedisIO
service redisd stop
update-rc.d -f redisd remove

rm /bin/redis-cli
rm /bin/redis-server

if ( request "Remove BaboonStack Directory, include Databases?" ) then
  echo "Remove $bshome"
  rm -r "$bshome"
fi

echo "Done! Bye..."
echo