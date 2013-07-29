#!/bin/bash
# BaboonStack for MacOS
# Includes Code from NVM - https://github.com/creationix/nvm

# Try to figure out the arch
LXUNNAME="$(uname -a)"
LXARCH="$(uname -m)"
LXOS=

case "$LXUNNAME" in
  Linux\ *) LXOS=linux ;;
  Darwin\ *) LXOS=darwin ;;
  SunOS\ *) LXOS=sunos ;;
  FreeBSD\ *) LXOS=freebsd ;;
esac

case "$LXUNNAME" in
  *x86_64*) LXARCH=x64 ;;
  *i*86*) LXARCH=x86 ;;
  *armv6l*) LXARCH=arm-pi ;;
esac

LXVERSION="1.0.0"
LXSERVER="http://packages.litixsoft.de"
LXPACKET="baboonstack-v$LXVERSION-$LXOS-$LXARCH.tar.gz"
LXCURRPATH="$(dirname $(readlink ${BASH_SOURCE[0]} || echo ${BASH_SOURCE[0]#*/}))"
LXBASEPATH="$(cd "$LXCURRPATH"; cd ..; pwd -P)"
LXNODEPATH=$LXBASEPATH/node

lxmHeader() {
  echo
  echo "lxManager by Litixsoft GmbH 2013"
  echo
}

lxmVersion() {
  echo "$LXVERSION $LXARCH"
}

lxmHelp() {
  echo "Usage:"
  echo "    lxm version                       Displays the version number"
  echo "    lxm update                        Search and Installs BaboonStack Updates"
  echo
  echo "    lxm node                          Node Module Controls"
  echo
  echo "    Some operations required root access."
}

## Begin NVM

# Expand a version using the version cache
nvm_version() {
    local PATTERN=$1
    # The default version is the current one
    if [ ! "$PATTERN" ]; then
        PATTERN='current'
    fi

    VERSION=`nvm_ls $PATTERN | tail -n1`
    echo "$VERSION"

    if [ "$VERSION" = 'N/A' ]; then
        return
    fi
}

nvm_remote_version() {
    local PATTERN=$1
    VERSION=`nvm_ls_remote $PATTERN | tail -n1`
    echo "$VERSION"

    if [ "$VERSION" = 'N/A' ]; then
        return
    fi
}

nvm_ls() {
    local PATTERN=$1
    local VERSIONS=''

    if [ "$PATTERN" = 'current' ]; then
        result=`node -v 2>/dev/null`
        echo ${result:1}
        return
    fi

    # If it looks like an explicit version, don't do anything funny
    if [[ "$PATTERN" == v?*.?*.?* ]]; then
        VERSIONS="$PATTERN"
    else
        VERSIONS=`find "$LXNODEPATH/" -maxdepth 1 -type d -name "$PATTERN*" -exec basename '{}' ';' \
                    | sort -t. -u -k 1.2,1n -k 2,2n -k 3,3n`
    fi

    if [ ! "$VERSIONS" ]; then
        echo "N/A"
        return
    fi
    echo "$VERSIONS"
    return
}

nvm_ls_remote() {
    local PATTERN=$1
    local VERSIONS
    if [ "$PATTERN" ]; then
        if echo "${PATTERN}" | \grep -v '^v' ; then
            PATTERN=v$PATTERN
        fi
    else
        PATTERN=".*"
    fi
    VERSIONS=`curl -s http://nodejs.org/dist/ \
                  | \egrep -o 'v[0-9]+\.[0-9]+\.[0-9]+' \
                  | \grep -w "${PATTERN}" \
                  | sort -t. -u -k 1.2,1n -k 2,2n -k 3,3n`
    if [ ! "$VERSIONS" ]; then
        echo "N/A"
        return
    fi
    echo "$VERSIONS"
    return
}

nvm_checksum() {
    if [ "$1" = "$2" ]; then
        return
    elif [ -z $2 ]; then
        echo 'Checksums empty' #missing in raspberry pi binary
        return
    else
        echo 'Checksums do not match.'
        return 1
    fi
}

## End NVM

## LXM Module

# Reads remote Server Packets
lxm_ls_remote() {
    local PATTERN=$1
    local VERSIONS

    if [ ! "$PATTERN" ]; then
        PATTERN=".*"
    fi

    if [ "$PATTERN" = "update" ]; then
        PATTERN="baboonstack-v.*-$LXOS-$LXARCH.tar.gz"
    fi

    VERSIONS=`curl -s "$LXSERVER/" | sed -n 's/.*">\(.*\)<\/a>.*/\1/p' | grep -w "${PATTERN}"`

    if [ ! "$VERSIONS" ]; then
        echo "N/A"
        return
    fi

    echo "$VERSIONS"
    return
}

# Returns the latest Remote Version
lxm_update_available() {
  VERSION=`lxm_ls_remote update | sort | tail -n1 | tr -d ' '`

  local TEST="$VERSION\n$LXPACKET"
  TEST=`echo "${TEST}" | sort | tail -n1`

  if [ $VERSION = 'N/A' ]; then
    return
  fi

  if [ $VERSION = $LXPACKET ]; then
    return
  fi

  echo $VERSION
}

# Update BaboonStack
lxmUpdate() {
  local VERSION=`lxm_update_available`

  # Update available?
  if [ ! $VERSION ]; then
    echo "No Baboonstack Update available..."
    return
  fi

  # Make sure only root can run our script
  if [[ $EUID -ne 0 ]]; then
    echo "This operation must be run as root" 1>&2
    echo
    exit 1
  fi

  local tmpdir="$LXBASEPATH/.update"
  local tmptar="$tmpdir/$VERSION"

  echo "Update $LXPACKET => $VERSION..."

  # Create Update Directory, Download, Extract and Remove Packet
  if (
    mkdir -p "$tmpdir" && \
    echo "Download File..." && \
    curl -C - --progress-bar "$LXSERVER/$VERSION" -o "$tmptar" && \
    echo "Extract File..." && \
    tar -xzf "$tmptar" -C "$tmpdir" && \
    rm -f "$tmptar"
    )
  then
    # Get all Directorys from Update Packet
    local dirs=`find "$tmpdir" -maxdepth 1 -type d -exec basename '{}' ';'`
    for dir in $dirs; do
      if [ "$dir" = ".update" ]; then
        continue
      fi

      # If Directory AND lxscript.sh exists
      if [ -x "$LXBASEPATH/$dir/lxscript.sh" ]; then
        # Execute Script
        sh "$LXBASEPATH/$dir/lxscript.sh" remove
      fi

      # Copy Content
      echo "Copy Content from $dir..."
      cp -f -R "$tmpdir/$dir/" "$LXBASEPATH"

      # If Directory AND lxscript.sh exists
      if [ -x "$LXBASEPATH/$dir/lxscript.sh" ]; then
        # Execute Script
        sh "$LXBASEPATH/$dir/lxscript.sh" install
      fi
    done

    echo "YEAH, done..."
  else
    echo "Uhh, there is error..."
  fi

  # Remove Update Directory
  if [ -d "$LXBASEPATH/.update" ]; then
    echo "Cleaning up..."
    rm -rf "$LXBASEPATH/.update"
  fi
  
  exit 2
}

## End LXM

## Node Module

nodeHelp() {
  echo "Usage:"
  echo "    lxm node install [version]       Install a specific version number"
  echo "    lxm node switch [version]        Switch to Version"
  echo "    lxm node run <version> [<args>]  Run <version> with <args> as arguments"
  echo "    lxm node ls                      View locally available version"
  echo "    lxm node remotels                View remote available version"
  echo
  echo "Example:"
  echo "    lxm node install 0.10.12         Install a specific version"
  echo "    lxm node switch 0.10             Use the latest available 0.10.x release"
  echo "    lxm node remove 0.10.12          Removes a specific version from Disc"
  echo "    lxm node ls 0.10                 Lists all locally available 0.10.x releases"
  echo "    lxm node remotels 0.10           Lists all remote available 0.10.x releases"
  echo
}

# Download and switch to specified Node.JS Version
nodeInstall() {
  if [ $# -lt 1 ]; then
    nodeHelp
    return
  fi

  # We need curl
  if [ ! `which curl` ]; then
    echo 'LXM needs curl to proceed.' >&2;
    return
  fi

  # Make sure only root can run our script
  if [[ $EUID -ne 0 ]]; then
    echo "This operation must be run as root" 1>&2
    echo
    exit 1
  fi

  # initialize local variables
  local binavail
  local t
  local url
  local sum
  local tarball
  local shasum='shasum'
  local nobinary

  if [ -z "`which shasum 2>/dev/null`" ]; then
    shasum='sha1sum'
  fi

  # Returns the Version on Server
  VERSION=`nvm_remote_version v$1`

  # Returns the locally Versions
  LOCALVERSION=`nvm_ls $1`


  # Check if Version available on server
  if [ "$VERSION" = 'N/A' ]; then
    echo "Node v$1 not found on server..."
    return
  fi

  # Check if Directory exists
  if [ -d "$LXNODEPATH/${VERSION:1}" ] ; then
    echo "$VERSION is already installed."
    return
  fi

  # shortcut - try the binary if possible.
  if [ -n "$LXOS" ]; then
    binavail=

    # binaries started with node 0.8.6
    case "$VERSION" in
      v0.8.[012345]) binavail=0 ;;
      v0.[1234567].*) binavail=0 ;;
      *) binavail=1 ;;
    esac

    if [ $binavail -eq 1 ]; then
      t="$VERSION-$LXOS-$LXARCH"
      url="http://nodejs.org/dist/$VERSION/node-${t}.tar.gz"
      sum=`curl -s http://nodejs.org/dist/$VERSION/SHASUMS.txt | \grep node-${t}.tar.gz | awk '{print $1}'`

      local tmpdir="$LXNODEPATH/${VERSION:1}"
      local tmptarball="$tmpdir/node-${t}.tar.gz"

      echo "Download $VERSION Binary..."
      # Create Directory & Download Node Binary & Test Checksum & Extract Files & Remove Archive
      if (
        mkdir -p "$tmpdir" && \
        curl -C - --progress-bar $url -o "$tmptarball" && \
        nvm_checksum `${shasum} "$tmptarball" | awk '{print $1}'` $sum && \
        tar -xzf "$tmptarball" -C "$tmpdir" --strip-components 1 && \
        rm -f "$tmptarball"
        )
      then
        nodeSwitch $1
        return;
      else
        echo "No binary download available, sorry." >&2
      fi
    fi
  fi

  echo
}

# Removes a specified Node.JS Version from Disk
nodeRemove() {
  # Parameter is required
  if [ $# -lt 1 ]; then
    nodeHelp
    return
  fi

  # Make sure only root can run our script
  if [[ $EUID -ne 0 ]]; then
    echo "This operation must be run as root" 1>&2
    echo
    exit 1
  fi

  local VERSION=`nvm_version $1`

  if [ ! -d "$LXNODEPATH/$VERSION" ]; then
    echo "$1 version is not installed yet, abort."
    return;
  fi

  # Current selected Version can't be removed
  if [[ $VERSION == `nvm_ls current` ]]; then
    echo "Cannot uninstall currently-active node version, v$VERSION."
    return 1
  fi

  echo "Removing Node $VERSION..."
  rm -rf "$LXNODEPATH/$VERSION"
}

# Switch to specified Node.JS Version globally
nodeSwitch() {
  local nodever=`nvm_ls $1 | sort | tail -n1`
  
  if [ "$nodever" = 'N/A' ]; then
    echo "Node v$1 not found."
    return
  fi
  
  local nodedir="$LXNODEPATH/$nodever"

  if [ ! -d "$nodedir/bin" ] ; then
    echo "Node binary directory (bin/) not found."
    return
  fi

  # Make sure only root can run our script
  if [[ $EUID -ne 0 ]]; then
    echo "This operation must be run as root" 1>&2
    echo
    exit 1
  fi

  echo "Switch to $nodever..."

  # Remove symbolic link for node
  if [ -h "/usr/bin/node" ] ; then
    rm "/usr/bin/node"
  fi

  # Remove symbolic link for npm
  if [ -h "/usr/bin/npm" ] ; then
    rm "/usr/bin/npm"
  fi
  
  # Create link
  ln -s "$nodedir/bin/node" "/usr/bin/node"
  ln -s "$nodedir/bin/npm" "/usr/bin/npm"
}

# Run specified Node.js Version
nodeRun() {
  # run given version of node
  if [ $# -lt 2 ]; then
    nodeHelp
    return
  fi

  local VERSION=`nvm_version v$1`

  if [ ! -d $LXNODEPATH/${VERSION:1} ]; then
    echo "$1 version is not installed yet"
    return;
  fi

  echo "Running node $VERSION"
  $LXNODEPATH/${VERSION:1}/bin/node "${@:2}"
}

nodeList() {
  local CURRENT=`nvm_ls current`

  echo "local available version:"
  echo

  for VERSION in `nvm_ls $1`; do
    if [ -d "$LXNODEPATH/$VERSION" ]; then
      PADDED_VERSION=`printf '%10s' $VERSION`

      if [ "$CURRENT" ] && [ "$CURRENT" = "$VERSION" ] ; then
        echo "* $PADDED_VERSION"
      else
        echo "  $PADDED_VERSION"
      fi
    fi
  done
}

nodeListRemote() {
  echo "remote available version:"
  echo

  for VERSION in `nvm_ls_remote $1`; do
    if [[ "$VERSION" == v?*.?*.?* ]]; then
      PADDED_VERSION=`printf '%10s' $VERSION`
      echo "  $PADDED_VERSION"
    fi
  done
}

# Show Header
lxmHeader 

# No Arguments? Show Help.
if [ $# -lt 1 ]; then
  lxmHelp
  echo
  exit 1
fi

# lxManager Main
case $1 in
  "help" ) lxmHelp ;;
  "version" ) lxmVersion ;;
  "update" ) lxmUpdate ;;
  "node" )
    case $2 in
      "install" ) nodeInstall $3 ;;
      "remove" ) nodeRemove $3 ;;
      "switch" ) nodeSwitch $3 ;;
      "run" ) nodeRun ${@:3} ;;
      "list" ) nodeList $3 ;;
      "ls" ) nodeList $3 ;;
      "remotels" ) nodeListRemote $3 ;;
      *) nodeHelp ;;
    esac
  ;;
  * ) lxmHelp ;;
esac

echo