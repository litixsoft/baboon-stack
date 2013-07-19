#!/bin/bash
# BaboonStack Install Script
# Package: RedisIO
LXCURDIR=$(dirname $(readlink -f $0))
LXSERVICEENABLED=`which update-rc.d ; echo $?`

if [ $# -lt 1 ]; then
  echo "lxScript for Linux"
  return
fi

case $1 in
  "install" )
    # RedisIO Binarys
    ln -s "$LXCURDIR/bin/redis-cli" "/bin/redis-cli"
    ln -s "$LXCURDIR/bin/redis-server" "/bin/redis-server"

    # RedisIO
    echo "Register RedisIO Daemon..."
    ln -s "$LXCURDIR/redisd" "/etc/init.d/redisd"
    
    if [ $LXSERVICEENABLED = 0 ]; then
      update-rc.d redisd defaults
    else
    
    fi
    
    echo Start Service
    /etc/init.d/redisd start
  ;;
  "update" )
  
  ;;
  "remove" )
    # Remove Redis Daemon
    /etc/init.d/redisd stop
    if [ $LXSERVICEENABLED = 0 ]; then
      update-rc.d -f redisd remove
    else
    
    fi
      
    rm /etc/init.d/redisd

    # Remove symbolic links
    rm /bin/redis-cli
    rm /bin/redis-server

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
