#!/bin/bash
# BaboonStack Install Script
# Os     : MacOS
# Package: MongoDB
LXCURDIR="$(dirname $(readlink ${BASH_SOURCE[0]} || echo ${BASH_SOURCE[0]}))"
LXUSER=`id -n -u`
LXGROUP=`id -n -g`
LXDAEMONFILE="org.baboonstack.mongod.plist"
LXDAEMONPATH="/Library/LaunchDaemons"
LXBINPATH="/usr/bin"

function installDaemon() {
  # Return >0 if error
  if [ -e "$LXCURDIR/$LXDAEMONFILE" ]; then
    # Copy file
    cp "$LXCURDIR/$LXDAEMONFILE" "$LXDAEMONPATH/$LXDAEMONFILE"

    # Change Owner to root
    chown root "$LXDAEMONPATH/$LXDAEMONFILE"

    # Change permission to 644
    chmod 644 "$LXDAEMONPATH/$LXDAEMONFILE"
  
    # Add Daemon 
    launchctl load -w "$LXDAEMONPATH/$LXDAEMONFILE"

    return $?
  fi
  
  return 1
}

function removeDaemon() {
  # Return >0 if error
  if [ -e "$LXDAEMONPATH/$LXDAEMONFILE" ]; then
    launchctl unload -w "$LXDAEMONPATH/$LXDAEMONFILE"
    rm -f "$LXDAEMONPATH/$LXDAEMONFILE"
    return $?
  fi

  return 1
}

if [ $# -lt 1 ]; then
  echo "lxScript for MacOS"
  exit 1
fi

case $1 in
  "install" )
    echo "Install MongoDB [$LXCURDIR]..."

    # MongDB Binarys
    ln -s "$LXCURDIR/bin/mongo" "$LXBINPATH/mongo"
    ln -s "$LXCURDIR/bin/mongod" "$LXBINPATH/mongod"

    # Register Services
    if ( installDaemon mongod ); then
      echo "Daemon successfully installed..."
    fi
  ;;
  "update" )

  ;;
  "remove" )
    echo "Remove MongoDB..."
    
    if ( removeDaemon mongod ); then
      # Remove Link
      echo "Daemon successfully removed..."
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
