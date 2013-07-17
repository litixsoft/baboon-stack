#!/bin/bash
# BaboonStack Install Script
# Package: mongodb
LXCURDIR=$(dirname $(readlink -f $0))

if [ $# -lt 1 ]; then
  echo "lxScript for Linux"
  return
fi

case $1 in
  "install" )
    # Link
    ln -s "$LXCURDIR/bin/mongo" "/bin/mongo"
    ln -s "$LXCURDIR/bin/mongod" "/bin/mongod"

    # Register Services
    echo "Register MongoDB Daemon 'mongod'..."
    ln -s "$LXCURDIR/mongod" "/etc/init.d/mongod"
    update-rc.d mongod defaults
    
    echo Start Service
    /etc/init.d/mongod start
  ;;
  "update" )
  
  ;;
  "remove" )
    # Remove MongoDB Daemon
    /etc/init.d/mongod stop
    update-rc.d -f mongod remove
    rm /etc/init.d/mongod

    # Remove symbolic links
    rm /bin/mongo
    rm /bin/mongod
    
    # Delete Binarys
    rm -rf "$LXCURDIR/bin/"
    
    # Remove all
    if [ $2 = "all" ]; then
      rm -rf "$LXCURDIR/"
    fi
  ;;
  * )
    echo "Unknow Command $1"
  ;;
esac
