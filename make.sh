#!/bin/bash
LXOS=
LXTEMP="bbs-package"
case "$(uname -a)" in
  Linux\ *) LXOS=linux ;;
  Darwin\ *) LXOS=darwin ;;
  *) 
    echo "Sorry! Unsupported OS."
    exit 5
  ;;
esac

case "$(uname -m)" in
  *x86_64*) LXARCH=x64 ;;
  *i*86*) LXARCH=x86 ;;
  *armv6l*) LXARCH=arm-pi ;;
esac

if [ -d "build" ]; then
 echo "Remove Build Folder..."
 rm -R build
fi

echo "Build..."
case "$LXOS" in
  "darwin" ) python3 build.py bbs.py --target-dir "build" --icon "ressources/baboonstack.ico" --compress ;;
  "linux" ) cxfreeze bbs.py --target-dir "build" --icon "ressources/baboonstack.ico" --compress ;;
esac

echo "Change permissions..."
chmod 644 build/*
chmod +x build/bbs

#echo "Build Baboonstack Package..."
#mkdir bbs-package

#cp scripts/macos/ bbs-package/.
#Copy Script
#rem Copy package.conf
#cd bbs-package
#rem tar
#cd ..

echo "Done..."
