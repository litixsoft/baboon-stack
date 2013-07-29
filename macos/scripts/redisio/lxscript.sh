#!/bin/bash
# BaboonStack Install Script
# Os     : MacOS
# Package: RedisIO
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
  echo "lxScript for MacOS"
  exit 1
fi

case $1 in
  "install" )
    echo "Install RedisIO..."

    # RedisIO Binarys
    ln -s "$LXCURDIR/bin/redis-cli" "$LXBINPATH/redis-cli"
    ln -s "$LXCURDIR/bin/redis-server" "$LXBINPATH/redis-server"

    # RedisIO Daemon
    if ( installDaemon redisd ); then
      echo "Start Service..."
    fi
  ;;
  "update" )

  ;;
  "remove" )
    # Remove Redis Daemon
    echo "Remove RedisIO..."
    
    if ( removeDaemon redisd ); then
      echo "Okay, Delete"
    fi

    # Remove symbolic links
    rm $LXBINPATH/redis-cli
    rm $LXBINPATH/redis-server

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
