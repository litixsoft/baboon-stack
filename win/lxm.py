#-------------------------------------------------------------------------------
# Name:        lxManager
# Purpose:
#
# Author:      Thomas Scheibe
#
# Created:     31.07.2013
# Copyright:   (c) Thomas Scheibe 2013
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import urllib.request as urlrequest
import re as regex
import subprocess
import tempfile
import platform
import hashlib
import lxtools
import sys
import os

# Litixsoft Modules
import nvm

# Global
lxVersion = '1.0.0'
lxServer = 'http://packages.litixsoft.de'

# Header
def lxmHeader():
    print('\nlxManager by Litixsoft GmbH 2013\n')

    pass

# Prints the lxManager Version
def lxmHelp():
    print('Usage:\n')

    print('    lxm version                       Displays the version number')
    print('    lxm update                        Search and Installs BaboonStack Updates\n')

    print('    lxm node                          Node Module Controls')
    print('    lxm service                       Service Module Controls for Node.JS\n')

    print('    Some operations required "administrator" rights.')
    pass


# Prints Baboonstack Version
def lxmVersion():
    print('Version {0}\n'.format(lxVersion))
    pass

# Node Operations

def lxmNodeHelp():
    print('Usage:\n')
    print('    lxm node install [version]       Install a specific version number')
    print('    lxm node switch [version]        Switch to Version')
    print('    lxm node run <version> [<args>]  Run <version> with <args> as arguments')
    print('    lxm node ls                      View available version\n')
    print('Example:\n')
    print('    lxm node install 0.10.12         Install a specific version')
    print('    lxm node switch 0.10             Use the latest available 0.10.x release')
    print('    lxm node remove 0.10.12          Removes a specific version from Disc')
    print('    lxm node ls 0.10                 Lists all locally available 0.10.x releases')
    print('    lxm node ls remote 0.10          Lists all remote available 0.10.x releases\n')
    pass

def lxmNode(params):
    if len(params) == 0:
        lxmNodeHelp()
        return

    # Get First Command
    command = params.pop(0).lower()

    # Download a specified Version from Node.JS remote Server and activated it locally
    if command == 'install' and len(params) != 0:
        return nvm.getRemoteNodeVersion(params.pop(0).lower())

    # Switch to a local available Node.JS version
    if command == 'switch' and len(params) != 0:
        return nvm.setLocalNodeVersion(params.pop(0).lower())

    # Runs a specified Node.JS Version
    if command == 'run' and len(params) > 1:
        return nvm.runSpecifiedNodeVersion(params.pop(0).lower(), params.pop(0).lower())

    # Removes a local installed Node.JS Version
    if command == 'remove' and len(params) != 0:
        return nvm.rmLocalNodeVersion(params.pop(0).lower())

    # Lists locally or remote available Node.JS Versions
    if command == 'ls':
        # Get current active Version
        curr = nvm.getLocalNodeVersion()

        # show remote available Version?
        if 'remote' in params:
            print('Remote available Node.JS Versions:\n')
            list = nvm.getRemoteNodeVersionList()
        else:
            print('Local available Node.JS Versions:\n')
            list = nvm.getLocalNodeVersionList()

        # Sort list
        list.sort();

        # Prints sorted list
        for entry in list:
            if curr != '' and curr == entry:
                print(' * {0}'.format(entry))
            else:
                print('   {0}'.format(entry))

        return True

    # No Command found, show Help
    lxmNodeHelp()

# Default Schrottie Schrott Schrott
def main():
    # Check Parameters
    if len(sys.argv) < 2:
        lxmHelp()
        return

    params = sys.argv.copy()
    params.pop(0) # Remove first entry
    moduleName = params.pop(0).lower()

    # Node.JS Module
    if  moduleName == 'node':
        return lxmNode(params)

    # Service Module
    if moduleName == 'service':
        return

    # Prints the Baboonstack Version
    if moduleName == 'version':
        return lxmVersion()

    # Check if update on remote Server
    if moduleName == 'update':
        return

    # Show Help
    lxmHelp()

if __name__ == '__main__':
    lxmHeader()

    try:
        main()
    except KeyboardInterrupt:
        print('Abort! Bye!')
    except e as Exception:
        print('Exception occured!')
        print(e)