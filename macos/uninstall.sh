#!/bin/bash
# Install Script for BaboonStack
echo "BaboonStack De-Installer"
echo
FILE="/tmp/out.$$"
GREP="/bin/grep"

function request {
  read -p "$1: [Y/n] " answer
  case "$answer" in
    Yes|yes|Y|y|"") return 0 ;;
    No|no|N|n) return 1 ;;
        *) return 1 ;;
  esac
}

# Some variables
LXHOMEPATH="$(pwd)"
LXBINPATH="/usr/bin"
LXMODE=""


# Make sure only root can run our script
if [[ $EUID -ne 0 ]]; then
  echo "This script must be run as root" 1>&2
  echo
  exit 1
fi

if ( request "Remove Databases, Configuration files, etc?" ) then
  LXMODE="all"
fi

# Execute every lxscript.sh
files=`find "$LXHOMEPATH" -maxdepth 2 -type f -name "lxscript.sh"`
for scriptfile in $files; do
  if [ -x "$scriptfile" ]; then
    if [ $(head -n 1 "$scriptfile") = "#!/bin/bash" ]; then
      bash "$scriptfile" remove $bsmode
    else
      sh "$scriptfile" remove $bsmode
    fi
  fi
done

# Remove Node.JS
if [ -d "$LXHOMEPATH/node" ]; then
  # Remove Symlink
  echo "Remove Node.JS"
  rm "$LXBINPATH/node"
  rm "$LXBINPATH/npm"
  rm -rf "$LXHOMEPATH/node"
fi

# Remove lxManager
if [ -d "$LXHOMEPATH/lxm" ]; then
  # Remove Symlink
  echo "Remove lxManager"
  rm "$LXBINPATH/lxm"
  rm -rf "$LXHOMEPATH/lxm"
fi

if [ "$LXMODE" = "all" ]; then
  echo "Remove $LXHOMEPATH"
  rm -rf "$LXHOMEPATH"
fi

echo "Done! Bye..."
echo