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
LXHOMEPATH="$(pwd)"
LXBINPATH="/usr/bin"
LXLIBPATH="/usr/lib"
LXMODE="--safe"


# Make sure only root can run our script
if [[ $EUID -ne 0 ]]; then
  echo "This script must be run as root" 1>&2
  echo
  exit 1
fi

echo "HINT: All installed packages are also removed!"

if ( request "Remove Databases, Configuration files, etc?" ) then
  LXMODE="--force"
fi

# Remove *ALL* packages
bbs remove --all $LXMODE

# Remove lxManager
if [ -d "$LXHOMEPATH/bbs" ]; then
  # Remove Symlink
  echo "Remove lxManager"
  rm "$LXBINPATH/bbs"
  rm -rf "$LXHOMEPATH/bbs"
fi

if [ "$LXMODE" = "--force" ]; then
  echo "Remove $LXHOMEPATH"
  rm -rf "$LXHOMEPATH"
fi

echo "Done! Bye..."
echo
