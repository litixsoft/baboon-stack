#!/usr/bin/env python3
#-------------------------------------------------------------------------------
# Name:        bbs
# Purpose:     Baboonstack Main Application
#
# Author:      Thomas Scheibe
#
# Created:     31.07.2013
# Copyright:   (c) Litixsoft GmbH 2014
# Licence:     Licensed under the MIT license.
#-------------------------------------------------------------------------------
# Litixsoft Modules
import package
import lxtools
import service
import config
import update
import sys
import nvm
import mvm

# Command Line
args = lxtools.Arguments()


# Header, the only one
def bbsHeader():
    print('\nlxManager for BaboonStack - Litixsoft GmbH 2014\n')


# Prints the lxManager Version
def bbsHelp():
    print('Usage:\n')

    print('    bbs version                       Displays the version number')
    print('    bbs upgrade                       Search and Install BaboonStack Updates')
    print('    bbs install [packagename]         Install packages')
    print('    bbs update [packagename]          Update a single packages')
    #print('    bbs search [packagename]          Updates packages')
    print('    bbs remove [packagename]          Removes packages')
    print('    bbs ls                            Lists available packages')
    #print('    bbs uninstall                     Uninstall Baboonstack')
    print('')

    # Enable NVM und SERVICE module only if Node Component installed
    if lxtools.getIfNodeModuleEnabled():
        print('    bbs node                          Node Module Controls')
        print('    bbs service                       Service Module Controls for Node.JS')

    # Enable MONGO module only if MongoDB installed
    if lxtools.getIfMongoModuleEnabled():
        print('    bbs mongo                         Mongo Module Controls')

    # Enable REDIS module only if RedisIO installed
#    if lxtools.getIfRedisModuleEnabled():
#        print('    bbs redis                         Redis Module Controls')

    print('')
    print('    Some operations required "{0}" rights.'.format(config.getMessage('ADMINNAME')))
    pass


# Prints Baboonstack Version
def bbsVersion():
    print('Version {0}'.format(config.lxConfig['version']))

# Node Operations


def bbsNodeHelp():
    print('Usage:\n')
    print('    bbs node install [version]       Install a specific version number')
    print('    bbs node remove [version]        Removes a specific version number')
    print('    bbs node use [version]           Switch to Version')
    print('    bbs node run <version> [<args>]  Run <version> with <args> as arguments')
    print('    bbs node reset                   De-Register Node.js/npm')
    print('    bbs node ls                      View available version')
    print('    bbs node cachefix                Fix NPM cache permissions\n')
    print('Example:\n')
    print('    bbs node install 0.10.12         Install 0.10.12 and switch')
    print('    bbs node install 0.10.12 -ns     Install 0.10.12 and dont switch')
    print('    bbs node install 0.10            Install the latest available 0.10 release')
    print('    bbs node use 0.10                Use the latest available 0.10 release')
    print('    bbs node remove 0.10.12          Removes a specific version from System')
    print('    bbs node ls 0.10                 Lists all locally available 0.10 releases')
    print('    bbs node ls 0.10 --remote        Lists all remote available 0.10 releases\n')
    pass


def bbsNode():
    if args.count() == 0:
        bbsNodeHelp()
        return

    # Get First Command
    command = args.get().lower()
    options = args.getoptions()

    # Download a specified Version from Node.JS remote Server and activated it locally
    if command == 'install' and args.count() != 0:
        return nvm.getRemoteNodeVersion(args.get().lower(), options)

    # Switch to a local available Node.JS version
    if command == 'use' and args.count() != 0:
        return nvm.setLocalNodeVersion(args.get().lower())

    # Switch to a local available Node.JS version; depreated
    # if command == 'switch' and args.count() != 0:
    #     print('WARNING: Parameter "switch" is deprecated!')
    #     return nvm.setLocalNodeVersion(args.get().lower())

    # Runs a specified Node.JS Version
    if command == 'run' and args.count() > 1:
        return nvm.runSpecifiedNodeVersion(args.get().lower(), args.get().lower())

    # Removes a local installed Node.JS Version
    if command == 'remove' and args.count() != 0:
        return nvm.rmLocalNodeVersion(args.get().lower())

    # Reset, de-register node.js
    if command == 'reset':
        print('Unregister Node.js...')
        return nvm.resetNode()

    # Lists locally or remote available Node.JS Versions
    if command == 'ls':
        # Get current active Version
        curr = nvm.getLocalNodeVersion()

        # show remote available Version?
        if 'remote' in options:
            print('Remote available Node.JS Versions:\n')
            nodelist = nvm.getRemoteNodeVersionList(args.get() + '.*')
        else:
            print('Local available Node.JS Versions:\n')
            nodelist = nvm.getLocalNodeVersionList(args.get())

        # Prints sorted list
        for entry in nodelist:
            if curr != '' and curr == entry:
                print(' * {0}'.format(entry))
            else:
                print('   {0}'.format(entry))

        return True

    if command == 'cachefix':
        return nvm.runCacheFix()

    # No Command found, show Help
    bbsNodeHelp()

# MongoDB Version Manager


def bbsMongoHelp():
    print('Usage:\n')
    print('    bbs mongo install [version]                 Install a specific version number')
    print('    bbs mongo remove [version]                  Removes a specific version number')
    print('    bbs mongo use [version]                     Install specified version as Service')
    print('    bbs mongo ls                                List installed mongo versions')
    print('    bbs mongo start [version] [[port]] [[path]] Start Mongo')
    print('    bbs mongo stop [version]                    Stop Mongo\n')
    print('Example:\n')
    print('    bbs mongo install 2.4.10                    Install 2.4.10 and switch')
    print('    bbs mongo install 2.4.10 -ns                Install 2.4.10 and explicit dont switch')
    print('    bbs mongo use 2.4.9                         Switch to installed version 2.4.9')
    print('    bbs mongo remove 2.4.10                     Removes the specific version from System')
    print('    bbs mongo start 2.6.2 27020                 Start MongoDB 2.6.2 on port 27020')
    print('    bbs mongo stop 2.6.2                        Stops all MongoDB 2.6.2 Servers in Userspace\n')
    pass


def bbsMongo():
    if mvm.doUpgrade() is not None:
        return

    if args.count() == 0:
        bbsMongoHelp()
        return

    # Get First Command
    command = args.get().lower()
    options = args.getoptions()

    # Download a specified Version from MongoDB remote Server and activated it locally
    if command == 'install' and args.count() != 0:
        return mvm.doInstall(args.get().lower(), options)

    # Removes a local and non-activated mongodb version
    if command == 'remove' and args.count() != 0:
        return mvm.doRemove(args.get().lower(), options)

    # Starts a specified mongo version in user space
    if command == 'start' and args.count() != 0:
        return mvm.doStart(args.get().lower(), args.get('27017').lower(), args.get(None), options)

    # Stopps a specified mongo version thats run in user space
    if command == 'stop' and args.count() != 0:
        return mvm.doStop(args.get().lower(), options)

    # Stopps a specified mongo version thats run in user space
    if command == 'ls':
        return mvm.doList()

    # Stopps a specified mongo version thats run in user space
    if command == 'use' and args.count() != 0:
        return mvm.doChange(args.get().lower())

    # Reset, de-register node.js
    if command == 'reset':
        return mvm.doReset()

    # No Command found, show Help
    bbsMongoHelp()

# Service Operations


def bbsServiceHelp():
    print('Usage:\n')
    print('    bbs service install [name] [version] [app] Install a Node.JS Service')
    print('    bbs service remove [name]                  Removes a Node.JS Service')
    print('    bbs service start [name]                   Start Service')
    print('    bbs service stop [name]                    Stop Service\n')
    print('Example:\n')
    print('    bbs service install lxappd 0.10.12 c:\\projects\\web\\app.js')
    print('    bbs service remove lxappd\n')
    pass


def bbsService():
    if args.count() == 0:
        bbsServiceHelp()
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
    if command == 'stop' and args.count() != 0:
        return service.stopService(args.get())

    # No Command found, show Help
    bbsServiceHelp()


# Packages
def bbsPackage(command):
    options = args.getoptions()

    # Perform a catalog upgrade if required
    if package.upgrade():
        return True

    # Do nothing, only for perform package upgrade
    if command == 'package':
        return True

    # Use local catalog for installation/updates
    if 'local' in options:
        package.remotecatalog = package.getRemoteCatalog(True)
        package.updatelist = package.getAvailableUpdates(package.localcatalog, package.remotecatalog)

    # Install
    if command == 'install' and args.count() != 0:
        return package.install(args.get(count=-1), options)

    # Remote File List
    if command == 'ls':
        if 'remote' in options:
            return package.remotelist(args.get(count=-1), options)
        else:
            return package.localist(args.get(count=-1), options)

    # Update packages
    if command == 'update':
        return package.update(args.get(count=-1), options)

    # Remove
    if command == 'remove':
        if args.count() != 0:
            return package.remove(args.get(count=-1), options)
        elif 'all' in options:
            return package.remove('', options)

    # Show Help
    bbsHelp()
    return False


# Update Operations
def bbsUpdate():
    return update.doUpdate()


# Default
def main():
    # # First! Check if package update required and perform it when required
    # if package.bbsupdate():
    #     return True

    moduleName = args.get().lower()

    # Node.JS Module
    if moduleName == 'node' and lxtools.getIfNodeModuleEnabled():
        return bbsNode()

    # Mongo Module
    if moduleName == 'mongo' and lxtools.getIfMongoModuleEnabled():
        return bbsMongo()

    # Service Module
    if moduleName == 'service' and lxtools.getIfNodeModuleEnabled():
        return bbsService()

    # Prints the Baboonstack Version
    if moduleName == 'version':
        return bbsVersion()

    # Check if update on remote Server
    if moduleName == 'upgrade':
        return bbsUpdate()

    # Package operations
    return bbsPackage(moduleName)

# lxManager Main
if __name__ == '__main__':
    # Shows the Header
    if args.isoption('noheader') is False:
        bbsHeader()

    # Execute main() and catch all Exceptions
    exitNormally = False
    try:
        exitNormally = main()
    except KeyboardInterrupt:
        print('Abort! Bye!')
    except Exception as e:
        print('Exception occured!')
        print(e)

    if args.isoption('noheader') is False:
        print('')

    if not exitNormally:
        sys.exit(1)