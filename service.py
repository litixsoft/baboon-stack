#-------------------------------------------------------------------------------
# Name:        service
# Purpose:     Helper for Windows specified services
#
# Author:      Thomas Scheibe
#
# Created:     05.08.2013
# Copyright:   (c) Litixsoft GmbH 2014
# Licence:     Licensed under the MIT license.
#-------------------------------------------------------------------------------
import subprocess
import os

# lxManager Modules
import lxtools
import nvm

# Some global variables
lxBasePath = lxtools.getBaboonStackDirectory()
lxMgrPath = os.path.join(lxBasePath, 'bbs')
lxServiceBinary = os.path.join(lxMgrPath, 'lxservice.exe')

def getIfServiceBinaryExits():
    if not os.path.isfile(lxServiceBinary):
        print('lxService Binary is missing! Abort!')
        return False

    return True

# Installs a service
def installService(servicename, nodeversion, app):
    # Check if lxservice.exe available
    if not getIfServiceBinaryExits():
        return False

    # Check if Admin
    if not lxtools.getIfAdmin():
        print('Sorry, administrator rights required.')
        return False

    # If correct Node Version Format
    if not nvm.getIfNodeVersionFormat(nodeversion):
        print('{0} is not a Node Version Format.'.format(nodeversion))
        return False

    # If Node Version installed
    if not nvm.getIfNodeVersionInstalled(nodeversion):
        print('Node v{0} is not installed yet.'.format(nodeversion))
        return False

    # Get the application directory
    nodeBinary = os.path.join(nvm.lxNodePath, nodeversion, 'node.exe')
    appBasePath = os.path.dirname(app)

    # Log Files
    appServiceLog = os.path.join(appBasePath, servicename + '.log')
    appStdOutLog = os.path.join(appBasePath, servicename + '.output.log')

    # Register
    execCommand = '{0} "{1} {2}" -install {3} -log {4} -stdout {5}'.format(lxServiceBinary, nodeBinary, app, servicename, appServiceLog, appStdOutLog)

    print('Register Service...\n')
    try:
        retCode = subprocess.call(execCommand, shell=False)

        # Report error if occured
        if retCode != 0:
            print('lxService reports Error. Exitcode {0}'.format(retCode))
            return False

    except:
        return False

    # Show help
    print('\nEnter "bbs service start {0}" to start service...'.format(servicename))
    return True

# Unregister the service from registry
def removeService(servicename):
    # Check if lxservice.exe available
    if not getIfServiceBinaryExits():
        return False

    # Check if Admin
    if not lxtools.getIfAdmin():
        print('Sorry, administrator rights required.')
        return False

    # Unregister
    execCommand = '{0} -remove {1}'.format(lxServiceBinary, servicename)

    print('Unregister Service...\n')
    try:
        retCode = subprocess.call(execCommand, shell=False)

        # Report error if occured
        if retCode != 0:
            print('lxService reports Error. Exitcode {0}'.format(retCode))
            return False

    except:
        return False

    # All fine
    return True

# Starts a Service
def startService(servicename):
    # Check if lxservice.exe available
    if not getIfServiceBinaryExits():
        return False

    # Check if Admin
    if not lxtools.getIfAdmin():
        print('Sorry, administrator rights required.')
        return False

    # Start
    execCommand = 'net start {0}'.format(servicename)

    print('Start Service...\n')
    try:
        retCode = subprocess.call(execCommand, shell=False)

        # Report error if occured
        if retCode != 0:
            print('Error reported. Exitcode {0}'.format(retCode))
            return False

    except:
        return False

    return True

# Stopps a Service
def stopService(servicename):
    # Check if lxservice.exe available
    if not getIfServiceBinaryExits():
        return False

    # Check if Admin
    if not lxtools.getIfAdmin():
        print('Sorry, administrator rights required.')
        return False

    # Stop
    execCommand = 'net stop {0}'.format(servicename)

    print('Stop Service...\n')
    try:
        retCode = subprocess.call(execCommand, shell=False)

        # Report error if occured
        if retCode != 0:
            print('Error reported. Exitcode {0}'.format(retCode))
            return False

    except:
        return False

    return True