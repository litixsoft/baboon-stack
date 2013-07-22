#!/bin/bash
# BaboonStack Install Script
# Package: RedisIO
LXCURDIR=$(dirname $(readlink -f $0))

installDaemon() {
  local srcbinary="$LXCURDIR/$1"
  local desbinary="/etc/init.d/$1"

  # If Debian system?
  if [ `which update-rc.d ; echo $?` ]; then
    ln -s "$srcbinary.debian" "$desbinary"
    update-rc.d $1 defaults
    return 1
  fi

  # If Fedora system?
  if [ `which chkconfig ; echo $?` ]; then
    ln -s "$srcbinary.fedora" "$desbinary"
    chkconfig --add $1
    chkconfig $1 on
    systemctl --system daemon-reload
    return 1
  fi
  
  return 0
}

removeDaemon() {
  local srcbinary="$LXCURDIR/$1"
  local desbinary="/etc/init.d/$1"

  # If Debian system?
  if [ `which update-rc.d ; echo $?` ]; then   
    update-rc.d -f $1 remove    
    return 1
  fi

  # If Fedora system?
  if [ `which chkconfig ; echo $?` ]; then
    chkconfig $1 off
    chkconfig --del $1    
    systemctl --system daemon-reload    
    return 1
  fi
  
  return 0
}

if [ $# -lt 1 ]; then
  echo "lxScript for Linux"
  return
fi

case $1 in
  "install" )
    # RedisIO Binarys
    ln -s "$LXCURDIR/bin/redis-cli" "/bin/redis-cli"
    ln -s "$LXCURDIR/bin/redis-server" "/bin/redis-server"

    # RedisIO Daemon
    echo "Register RedisIO Daemon..."
    if [ `installDaemon redisd` ]; then
      echo "Start Service..."
      /etc/init.d/redisd start
    fi
  ;;
  "update" )
  
  ;;
  "remove" )
    # Remove Redis Daemon
    echo "Remove RedisIO Daemon..."
    /etc/init.d/redisd stop
    
    if [ `removeDaemon redisd`  ]; then
      # Remove Link
      rm /etc/init.d/redisd   
    fi

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
