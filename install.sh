#!/bin/bash
# Install Script for BaboonStack
echo "BaboonStack Installer"
echo
FILE="/tmp/out.$$"
GREP="/bin/grep"

# Try to figure out the os and arch for binary fetching
uname="$(uname -a)"
os=
arch="$(uname -m)"
case "$uname" in
  Linux\ *) os=linux ;;
  Darwin\ *) os=darwin ;;
  SunOS\ *) os=sunos ;;
  FreeBSD\ *) os=freebsd ;;
esac
case "$uname" in
  *x86_64*) arch=x64 ;;
  *i*86*) arch=x86 ;;
  *armv6l*) arch=arm-pi ;;
esac

# Some variables
bshome=/opt/litixsoft/baboonstack
bspacket=baboonstack-v1.0.0-linux-$arch.tar.gz

# Check, if packet available
if [ ! -e "$bspacket" ]; then
  echo "Packet '$bspacket' not found. Abort."
  echo
  exit 1
fi

# Make sure only root can run our script
if [[ $EUID -ne 0 ]]; then
  echo "This script must be run as root" 1>&2
  echo
  exit 1
fi

# Create Directory
if [ ! -d "$bshome" ]; then
  echo "Create $bshome..."
  mkdir -p $bshome
fi

# Extract Files
echo "Extract Files..."
tar -zxvf "$bspacket" -C "$bshome"

# Link Binarys

# Node.JS Binarys
ln -s "$bshome/node/0.10.12/bin/node" "/bin/node"
ln -s "$bshome/node/0.10.12/bin/npm" "/bin/npm"

# MongoDB Binarys
ln -s "$bshome/mongo/bin/mongo" "/bin/mongo"
ln -s "$bshome/mongo/bin/mongod" "/bin/mongod"

# RedisIO Binarys
ln -s "$bshome/redisio/bin/redis-cli" "/bin/redis-cli"
ln -s "$bshome/redisio/bin/redis-server" "/bin/redis-server"

# Register Services
# MongoDB
echo "Register MongoDB Daemon..."
ln -s "$bshome/mongo/mongod" "/etc/init.d/mongod"
update-rc.d mongod defaults

# RedisIO
echo "Register RedisIO Daemon..."
ln -s "$bshome/redisio/redisd" "/etc/init.d/redisd"
update-rc.d redisd defaults

# Starts Daemon...
echo "Start MongoDB Daemon..."
service mongod start

echo "Start RedisIO Daemon..."
service redisd start

echo "Done! Bye..."
echo