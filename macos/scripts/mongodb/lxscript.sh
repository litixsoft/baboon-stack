#!/bin/bash
# BaboonStack Install Script
# Os     : MacOS
# Package: MongoDB
LXCURDIR="$(dirname $(readlink ${BASH_SOURCE[0]} || echo ${BASH_SOURCE[0]#*/}))"
LXUSER=`id -n -u`
LXGROUP=`id -n -g`
LXDAEMON="/Library/LaunchDaemons/<filename>.plist"
LXBINPATH="/usr/bin"

function installDaemon() {
  # Return >0 if error  
  return 1
}

function removeDaemon() {
  # Return >0 if error  
  return 1
}

if [ $# -lt 1 ]; then
  echo "lxScript for MAC"
  exit 1
fi

case $1 in
  "install" )
    echo "Install MongoDB..."

    # MongDB Binarys
    ln -s "$LXCURDIR/bin/mongo" "$LXBINPATH/mongo"
    ln -s "$LXCURDIR/bin/mongod" "$LXBINPATH/mongod"

    # Register Services
    if ( installDaemon mongod ); then
      echo "Start Service..."
    fi
  ;;
  "update" )

  ;;
  "remove" )
    echo "Remove MongoDB..."
    
    if ( removeDaemon mongod ); then
      # Remove Link
      echo "Yes... maybe"
    fi

    # Remove symbolic links
    rm "$LXBINPATH/mongo"
    rm "$LXBINPATH/mongod"
    
    # Delete Binarys
    rm -rf "$LXCURDIR/bin"
    
    # Remove all
    if [ "$2" ] && [ "$2" = "all" ]; then
      rm -rf "$LXCURDIR/"
    fi
  ;;
  * )
    echo "Unknow Command $1"
  ;;
esac
