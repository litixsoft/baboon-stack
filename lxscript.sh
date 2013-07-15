#!/bin/bash
# BaboonStack Install Script
# Package: 
LXCURDIR=`pwd`

if [ $# -lt 1 ]; then
  echo "lxScript for Linux"
  return
fi

case $1 in
  "install" )
  
  ;;
  "update" )
  
  ;;
  "remove" )
      
  ;;
  * )
    echo "Unknow Command $1"
  ;;
esac
