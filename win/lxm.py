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
import sys
import os
import re as regex

# Litixsoft Modules
import lxtools
import service
import version
import update
import nvm

# Command Line
args = lxtools.Arguments()

# Header, the only one
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
    print('Version {0}\n'.format(version.lxVersion))
    pass

# Node Operations

def lxmNodeHelp():
    print('Usage:\n')
    print('    lxm node install [version]       Install a specific version number')
    print('    lxm node switch [version]        Switch to Version')
    print('    lxm node run <version> [<args>]  Run <version> with <args> as arguments')
    print('    lxm node ls                      View available version\n')
    print('Example:\n')
    print('    lxm node install 0.10.12         Install 0.10.12 release')
    print('    lxm node install 0.10            Install the latest available 0.10 release')
    print('    lxm node switch 0.10             Use the latest available 0.10 release')
    print('    lxm node remove 0.10.12          Removes a specific version from System')
    print('    lxm node ls                      Lists all locally available 0.10 releases')
    print('    lxm node ls remote 0.10          Lists all remote available 0.10 releases\n')
    pass

def lxmNode():
    if args.count() == 0:
        lxmNodeHelp()
        return

    # Get First Command
    command = args.get().lower()

    # Download a specified Version from Node.JS remote Server and activated it locally
    if command == 'install' and args.count() != 0:
        return nvm.getRemoteNodeVersion(args.get().lower())

    # Switch to a local available Node.JS version
    if command == 'switch' and args.count() != 0:
        return nvm.setLocalNodeVersion(args.get().lower())

    # Runs a specified Node.JS Version
    if command == 'run' and args.count() > 1:
        return nvm.runSpecifiedNodeVersion(args.get().lower(), args.get().lower())

    # Removes a local installed Node.JS Version
    if command == 'remove' and args.count() != 0:
        return nvm.rmLocalNodeVersion(args.get().lower())

    # Lists locally or remote available Node.JS Versions
    if command == 'ls':
        # Get current active Version
        curr = nvm.getLocalNodeVersion()

        # show remote available Version?
        if args.find('remote'):
            print('Remote available Node.JS Versions:\n')
            list = nvm.getRemoteNodeVersionList(args.get() + '.*')
        else:
            print('Local available Node.JS Versions:\n')
            list = nvm.getLocalNodeVersionList(args.get())

        # Prints sorted list
        for entry in list:
            if curr != '' and curr == entry:
                print(' * {0}'.format(entry))
            else:
                print('   {0}'.format(entry))

        return True

    # No Command found, show Help
    lxmNodeHelp()

# Service Operations

def lxmServiceHelp():
    print('Usage:\n')
    print('    lxm service install [name] [version] [app] Install a Node.JS Service')
    print('    lxm service remove [name]                  Removes a Node.JS Service')
    print('    lxm service start [name]                   Start Service')
    print('    lxm service stop [name]                    Stop Service\n')
    print('Example:\n')
    print('    lxm service install lxappd 0.10.12 c:\\projects\\web\app.js')
    print('    lxm service remove lxappd\n')
    pass

def lxmService():
    if args.count() == 0:
        lxmServiceHelp()
        return

    # Get First Command
    command = args.get().lower()

    # Installs a Service
    if command == 'install' and args.count() == 3:
        return service.installService(args.get(), args.get(), args.get())

    # Removes a Service
    if command == 'remove' and args.count() != 0:
        return service.removeService(args.get())

    # Starts a Service
    if command == 'start' and args.count() != 0:
        return service.startService(args.get())

    # Stops a Service
    if command == 'stop' and largs.count() != 0:
        return service.stopService(args.get())

    # No Command found, show Help
    lxmServiceHelp()

# Update Operations

def lxmUpdate():
    return update.doUpdate()

# Default Schrottie Schrott Schrott
def main():
    moduleName = args.get().lower()

    # Node.JS Module
    if  moduleName == 'node':
        return lxmNode()

    # Service Module
    if moduleName == 'service':
        return lxmService()

    # Prints the Baboonstack Version
    if moduleName == 'version':
        return lxmVersion()

    # Check if update on remote Server
    if moduleName == 'update':
        return lxmUpdate()

    # Show Help
    lxmHelp()

if __name__ == '__main__':
    lxmHeader()

    try:
        main()
    except KeyboardInterrupt:
        print('Abort! Bye!')
    except Exception as e:
        print('Exception occured!')
        print(e)