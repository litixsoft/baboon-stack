#!/bin/bash

# Make sure only root can run our script
if [[ $EUID -ne 0 ]]; then
  echo "This script must be run as root" 1>&2
  echo
  exit 1
fi

echo "Update..."

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

if [[ -z "$1" ]]; then
  SOURCEPATH="$(dirname $(readlink ${BASH_SOURCE[0]} || echo ${BASH_SOURCE[0]}))"

  case "$LXOS" in
	  linux)
	    TARGETPATH="/opt/litixsoft/baboonstack"
	  ;;
	  darwin)
	    TARGETPATH="/usr/share/litixsoft/baboonstack"
	  ;;
  esac

else
	SOURCEPATH="$1"
	TARGETPATH="$2"
fi

# Check if source exists
if [[ ! -d "$SOURCEPATH" ]]; then
	echo "Source Path not exists."
	exit 1
fi

# Check if target exists
if [[ ! -d "$TARGETPATH" ]]; then
	echo "Target Path not exists."
	exit 2
fi

# Move bbs folder
if [[ -d "$SOURCEPATH/bbs" && -d "$TARGETPATH/bbs" ]]; then
	echo "Copy ´bbs´ folder..."
	# Rename old
	mv "$TARGETPATH/bbs" "$TARGETPATH/bbs.backup"

	# Copy/Move new bbs
	mv "$SOURCEPATH/bbs" "$TARGETPATH/bbs"

	# Remove backup
	rm -rf "$TARGETPATH/bbs.backup"
fi

# Replace uninstall.sh script
if [[ -e "$SOURCEPATH/uninstall.sh" ]]; then
	echo "Create ´uninstall´ script..."
	mv "$SOURCEPATH/uninstall.sh" "$TARGETPATH/uninstall.sh"
	chmod +x "$TARGETPATH/uninstall.sh"
fi

# Some variables
LXCATALOG="baboonstack.package.conf"
LXOLDCATALOG="baboonstack.previous.package.conf"

# Replace catalog file
if [[ -e "$TARGETPATH/bbs/$LXCATALOG" ]]; then

	# Rename old catalog file
	if [[ -e "$TARGETPATH/$LXCATALOG" ]]; then
		echo "Rename old ´catalog´ file..."
		mv "$TARGETPATH/$LXCATALOG" "$TARGETPATH/$LXOLDCATALOG"
	fi

	echo "Create ´catalog´ file..."
	cp "$TARGETPATH/bbs/$LXCATALOG" "$TARGETPATH/$LXCATALOG"
fi

echo -e "\033[32mSUCCESS: Enter ´bbs package´ for package updates.\033[0m"