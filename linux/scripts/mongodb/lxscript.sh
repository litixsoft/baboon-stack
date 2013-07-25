#!/bin/bash
# BaboonStack Install Script
# Package: mongodb
LXCURDIR=$(dirname $(readlink -f $0))

function installDaemon() {
  local srcbinary="$LXCURDIR/$1"
  local desbinary="/etc/init.d/$1"

  # If Debian system?
  if [ `which update-rc.d 2>/dev/null` ]; then
    ln -s "$srcbinary.debian" "$desbinary"
    update-rc.d $1 defaults
    return 0
  fi

  # If Fedora system?
  if [ `which chkconfig 2>/dev/null` ]; then
    ln -s "$srcbinary.fedora" "$desbinary"
    chkconfig --add $1
    chkconfig $1 on
    return 0
  fi
  
  return 1
}

function removeDaemon() {
  local srcbinary="$LXCURDIR/$1"
  local desbinary="/etc/init.d/$1"

  # If Debian system?
  if [ `which update-rc.d 2>/dev/null` ]; then   
    update-rc.d -f $1 remove    
    return 0
  fi

  # If Fedora system?
  if [ `which chkconfig 2>/dev/null` ]; then
    chkconfig $1 off
    chkconfig --del $1
    return 0
  fi
  
  return 1
}

if [ $# -lt 1 ]; then
  echo "lxScript for Linux"
  exit 1
fi

case $1 in
  "install" )
    # Link
    ln -s "$LXCURDIR/bin/mongo" "/bin/mongo"
    ln -s "$LXCURDIR/bin/mongod" "/bin/mongod"

    # Register Services
    echo "Register MongoDB Daemon 'mongod'..."
    if ( installDaemon mongod ); then
      echo "Start Service..."
      /etc/init.d/mongod start
    fi
  ;;
  "update" )
  
  ;;
  "remove" )
  # Remove MongoDB Daemon
    echo "Remove MongoDB Daemon..."
    /etc/init.d/mongod stop
    
    if ( removeDaemon mongod ); then
      # Remove Link
      rm /etc/init.d/mongod   
    fi

    # Remove symbolic links
    rm /bin/mongo
    rm /bin/mongod
    
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
