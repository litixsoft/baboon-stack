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

def lxmHelp():
    print('Usage:\n')

    print('    lxm version                       Displays the version number')
    print('    lxm update                        Search and Installs BaboonStack Updates\n')

    print('    lxm node                          Node Module Controls')
    print('    lxm service                       Service Module Controls for Node.JS\n')

    print('    Some operations required "administrator" rights.')
    pass

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
    #ver = '5.a.0'
    #print(regex.match('[0-9]+\.[0-9]+\.[0-9]+', ver)) == None
    if params.count == 0:
        lxmNodeHelp()
        return

    command = params.pop(0).lower()

    # Download a specified Version from Node.JS remote Server and activated it locally
    if command == 'install':
        return nvm.getRemoteNodeVersion("0.10.15")

    # Switch to a local available Node.JS version
    if command == 'switch':
        return

    # Runs a specified Node.JS Version
    if command == 'run':
        return

    # Removes a local installed Node.JS Version
    if command == 'remove':
        return

    # Lists locally or remote available Node.JS Versions
    if command == 'ls':
        # show remote available Version?
        if 'remote' in params:
            list = nvm.getRemoteNodeVersionList()
        else:
            list = nvm.getLocalNodeVersionList()

        # Sort list
        list.sort();

        # Prints sorted list
        for entry in list:
            print('  {0}'.format(entry))
        return

    pass

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

    lxmHelp()

    pass

if __name__ == '__main__':

    if lxtools.getIfAdmin():
        print(lxtools.setDirectoryLink('C:\\litixsoft\\baboonstack\\lxm\\test', 'C:\\litixsoft\\baboonstack\\node\\0.10.15'));

    #lxmHeader()
    #main()