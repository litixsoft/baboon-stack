#!/bin/bash
# BaboonStack Install Script
# Package: RedisIO
LXCURDIR=$(dirname $(readlink -f $0))

if [ $# -lt 1 ]; then
  echo "lxScript for Linux"
  return
fi

case $1 in
  "install" )
    # RedisIO Binarys
    ln -s "$bshome/redisio/bin/redis-cli" "/bin/redis-cli"
    ln -s "$bshome/redisio/bin/redis-server" "/bin/redis-server"

    # RedisIO
    echo "Register RedisIO Daemon..."
    ln -s "$bshome/redisio/redisd" "/etc/init.d/redisd"
    update-rc.d redisd defaults

    echo Start Service
    service redisd start
  ;;
  "update" )
  
  ;;
  "remove" )
    # Remove Redis Daemon
    service redisd stop
    update-rc.d -f redisd remove
    rm /etc/init.d/redisd

    # Remove symbolic links
    rm /bin/redis-cli
    rm /bin/redis-server

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
