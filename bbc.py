#-------------------------------------------------------------------------------
# Name:        BaboonStack
# Purpose:
#
# Author:      Thomas Scheibe
#
# Created:     31.07.2013
# Copyright:   (c) Thomas Scheibe 2013
# Licence:     <your licence>
#-------------------------------------------------------------------------------
# Litixsoft Modules
import package
import lxtools
import service
import version
import update
import nvm

# Command Line
args = lxtools.Arguments()

# Header, the only one
def bbcHeader():
    print('\nlxManager for BaboonStack - Litixsoft GmbH 2013\n')
    pass

# Prints the lxManager Version
def bbcHelp():
    print('Usage:\n')

    print('    bbc version                       Displays the version number')
    print('    bbc update                        Search and Installs BaboonStack Updates')
    #print('    bbc packages                      Add Baboobstack Components')
    #print('    bbc uninstall                     Uninstall Baboonstack')
    print('')

    # Enable NVM und SERVICE module only if Node Component installed
    if lxtools.getIfNodeModuleEnabled():
        print('    bbc node                          Node Module Controls')
        print('    bbc service                       Service Module Controls for Node.JS')

    # Enable MONGO module only if MongoDB installed
    if lxtools.getIfMongoModuleEnabled():
        print('    bbc mongo                         Mongo Module Controls')

    # Enable REDIS module only if RedisIO installed
    if lxtools.getIfRedisModuleEnabled():
        print('    bbc redis                         Redis Module Controls')

    print('')
    print('    Some operations required "{0}" rights.'.format(version.getMessage('ADMINNAME')))
    pass


# Prints Baboonstack Version
def bbcVersion():
    print('Version {0}\n'.format(version.lxConfig['version']))
    pass

# Node Operations

def bbcNodeHelp():
    print('Usage:\n')
    print('    bbc node install [version]       Install a specific version number')
    print('    bbc node use [version]           Switch to Version')
    print('    bbc node run <version> [<args>]  Run <version> with <args> as arguments')
    print('    bbc node ls                      View available version\n')
    print('Example:\n')
    print('    bbc node install 0.10.12         Install 0.10.12 release')
    print('    bbc node install 0.10            Install the latest available 0.10 release')
    print('    bbc node switch 0.10             Use the latest available 0.10 release')
    print('    bbc node remove 0.10.12          Removes a specific version from System')
    print('    bbc node ls                      Lists all locally available 0.10 releases')
    print('    bbc node ls remote 0.10          Lists all remote available 0.10 releases\n')
    pass

def bbcNode():
    if args.count() == 0:
        bbcNodeHelp()
        return

    # Get First Command
    command = args.get().lower()

    # Download a specified Version from Node.JS remote Server and activated it locally
    if command == 'install' and args.count() != 0:
        return nvm.getRemoteNodeVersion(args.get().lower())

    # Switch to a local available Node.JS version
    if command == 'use' and args.count() != 0:
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

    # No Command found, show Help
    bbcNodeHelp()

# Service Operations

def bbcServiceHelp():
    print('Usage:\n')
    print('    bbc service install [name] [version] [app] Install a Node.JS Service')
    print('    bbc service remove [name]                  Removes a Node.JS Service')
    print('    bbc service start [name]                   Start Service')
    print('    bbc service stop [name]                    Stop Service\n')
    print('Example:\n')
    print('    bbc service install lxappd 0.10.12 c:\\projects\\web\app.js')
    print('    bbc service remove lxappd\n')
    pass

def bbcService():
    if args.count() == 0:
        bbcServiceHelp()
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
    bbcServiceHelp()

# Update Operations
def bbcUpdate():
    return update.doUpdate()

# Default
def main():
    moduleName = args.get().lower()

    # Node.JS Module
    if moduleName == 'node' and lxtools.getIfNodeModuleEnabled():
        return bbcNode()

    # Service Module
    if moduleName == 'service' and lxtools.getIfNodeModuleEnabled():
        return bbcService()

    # Prints the Baboonstack Version
    if moduleName == 'version':
        return bbcVersion()

    # Check if update on remote Server
    if moduleName == 'update':
        return bbcUpdate()

    # TODO: Remove this test operation
    if moduleName == 'package':
        # Get First Command
        command = args.get().lower()

        # Install
        if command == 'install':
            return package.install(args.get().lower())

        # Remove
        if command == 'remove':
            return package.remove(args.get().lower())

        return package.main()

    # Show Help
    bbcHelp()

# lxManager Main
if __name__ == '__main__':
    # Shows the Header
    bbcHeader()

    # Execute main() and catch all Exceptions
    try:
        main()
    except KeyboardInterrupt:
        print('Abort! Bye!')
    except Exception as e:
        print('Exception occured!')
        print(e)

    print('')