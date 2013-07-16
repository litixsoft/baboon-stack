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
bshome=$(dirname $(readlink -f $0))
bsmode=""

# Make sure only root can run our script
if [[ $EUID -ne 0 ]]; then
  echo "This script must be run as root" 1>&2
  echo
  exit 1
fi

if ( request "Remove BaboonStack Directory, include Databases?" ) then
  bsmode="all"
fi

# Execute every lxscript.sh
files=`find "$bshome" -maxdepth 2 -type f -name "lxscript.sh"`
for scriptfile in $files; do
  if [ -x "$scriptfile" ]; then
    sh "$scriptfile" remove $bsmode
  fi
done

# Remove Node.JS
if [ -d "$bshome/node" ]; then
  # Remove Symlink
  echo "Remove Node.JS"
  rm /bin/node
  rm /bin/npm
  rm -r "$bshome/node"
fi

if ( bsmode="all" ) then
  bsmode="all"
  echo "Remove $bshome"
  rm -r "$bshome"
fi

echo "Done! Bye..."
echo