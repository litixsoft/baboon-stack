#-------------------------------------------------------------------------------
# Name:        nvm
# Purpose:
#
# Author:      Thomas Scheibe
#
# Created:     01.08.2013
# Copyright:   (c) Thomas Scheibe 2013
# Licence:     <your licence>
#-------------------------------------------------------------------------------
from distutils.version import StrictVersion
import re as regex
import subprocess
import tempfile
import version
import sys
import os

# lxManager Modules
import lxtools

# Global

msiexecArguments = 'msiexec /quiet /a {0} /qb targetdir={1}'

# NodeJS
tempNodeDir = os.path.join(tempfile.gettempdir(), 'node')
moveNodeDir = os.path.join(tempNodeDir, 'nodejs')

# Node Directory
lxBasePath = lxtools.getBaboonStackDirectory()
lxNodePath = os.path.join(lxBasePath, 'Node')
lxBinPath = os.path.join(lxBasePath, 'lxm', 'Node')

# CleanUp
def cleanUp():
    # Remove temporary internet files
    lxtools.cleanUpTemporaryFiles()

    # Clear temporary node directory
    if os.path.exists(tempNodeDir):
        lxtools.rmDirectory(tempNodeDir)

# Returns if nodeversion the correct format
def getIfNodeVersionFormat(nodeversion):
    return regex.match('[0-9]+\.[0-9]+\.[0-9]+', nodeversion) != None

# Returns if nodeversion installed
def getIfNodeVersionInstalled(nodeversion):
    return os.path.exists(os.path.join(lxNodePath, nodeversion))

# Returns the remote available Files with RegEx Filter

def getRemoteList(url, filter = ''):
    # Download from URL
    data = lxtools.getRemoteData(url)

    # Exception or Abort
    if data == -1:
        return []

    # FIX: Changes on node.js distribution site
    # Find all with correct Node Version Format
    srvNodeList = regex.findall('">v([0-9]+\.[0-9]+\.[0-9]+)\/<\/a', data)

    # If filter given, then
    if filter != '':
        srvNodeList = '\n'.join(srvNodeList)
        srvNodeList = regex.findall('(' + filter + '.*)\n', srvNodeList)

    # Return List
    return srvNodeList

def getRemoteChecksumList(url):
    # Download from URL
    data = lxtools.getRemoteData(url + '/SHASUMS.txt')

    # Exception or Abort
    if data == -1:
        return []

    # Split Data and returns Array
    return data.split('\n')

# Returns the remote available Node Version Directories

def getRemoteNodeVersionList(filter = ''):
    versionList = getRemoteList("http://nodejs.org/dist/", filter)
    versionList.sort(key=StrictVersion) # Sort list FROM oldest Version TO newer Version

    return versionList # Return sorted Versionlist

# Returns, if remote Node Version for Windows available
def getRemoteNodeVersion(nodeversion):
    # Check if admin
    if not lxtools.getIfAdmin():
        print('This operation required Administrator rights!')
        return

    # Check if version available on remote server
    print('Retrieve available version...')
    versionList = getRemoteNodeVersionList(nodeversion + '.*')

    # No Version found
    if len(versionList) == 0:
        print('Node v{0} not found on remote server.'.format(nodeversion))
        return

    # Get the last element from list
    nodeversion = versionList.pop()

    # Inform User about the version choose (only if more items exists)
    if len(versionList) != 0:
        print('Take Node v{0}...'.format(nodeversion))

    # Build target Path
    targetDirectory = os.path.join(lxNodePath, nodeversion)

    # Check if already installed
    if os.path.exists(targetDirectory):
        print('Version already installed.')
        return


    # Get the Os specified Node Remote Package
    remoteFilename = version.lxConfig['node'][lxtools.getOsArchitecture()].format(nodeversion)

    # Get Checksumlist from remote Server
    print('Retrieve Checksum list...')

    checksumList = getRemoteChecksumList('http://nodejs.org/dist/v' + nodeversion)
    remoteChecksum = ''

    # Find Checksum for the Binary
    if len(checksumList) != '':
        for checksumEntry in checksumList:
            value = checksumEntry.split('  ')

            if len(value) > 1 and value[1] == remoteFilename:
                remoteChecksum = value[0]
                break

    # If Checksum found?
    if remoteChecksum == '':
        print('No checksum for remote Binary, if exists?\nTry to retrieve...')

    # Download Binary from Server
    print('Retrieve Node Version v{0} Installation packet...'.format(nodeversion))

    tempRemoteFile = lxtools.getRemoteFile('http://nodejs.org/dist/v' + nodeversion + '/' + remoteFilename)

    # Abort or Exception
    if tempRemoteFile == -1:
        return False

    # Generate Checksum of downloaded Binary
    print('Generate Checksum...')
    localChecksum = lxtools.getSHAChecksum(tempRemoteFile)

    # Check Checksum
    if (localChecksum == remoteChecksum):
        print('Checksum are correct...')
    else:
        print('Checksum missmatch... Abort!')
        print('Filename  ' + remoteFilename)
        print('Remote SHA' + remoteChecksum)
        print('Local  SHA' + localChecksum)
        return

    # Extract MSI Package
    print('Execute installation package...')
    try:
        retcode = subprocess.call(msiexecArguments.format(tempRemoteFile, tempNodeDir), shell=False)

        # If return code otherwise then 0, ERROR
        if retcode != 0:
            print('ABORT: Huh? Installer reports error!\n\nDo you canceled it? Returncode {0}'.format(retcode))
            cleanUp()
            return False
    except:
        print('ERROR: Install package error!')
        cleanUp()
        return False

    # Now copies node
    print('Copy files...')
    if os.path.exists(moveNodeDir):
        # MOVE
        os.rename(moveNodeDir, targetDirectory)
    else:
        print('Uuuh! Something is wrong! Abort!')
        return False

    # Deletes the shit of temporary files
    print('Clean up...')
    cleanUp()
    return setLocalNodeVersion(nodeversion)

# Retrives local available Node Versions
def getLocalNodeVersionList(filter = ''):
    srcNodeList = os.listdir(lxNodePath)
    tarNodeList = []

    # Filter the non confirm Versions :D
    for entry in srcNodeList:
        if getIfNodeVersionFormat(entry):
            # If filter, then MUST match
            if filter != '' and regex.match(filter + '.*', entry) == None:
                continue

            tarNodeList.append(entry)

    # Sort list FROM oldest Version TO newer Version
    tarNodeList.sort(key=StrictVersion)
    return tarNodeList

# Activate a local available Node Version
def setLocalNodeVersion(nodeversion):
    # Retrive local available Version
    versionList = getLocalNodeVersionList(nodeversion)

    # No Version found
    if len(versionList) == 0:
        print('Sorry, no existing Node version {0} found locally.'.format(nodeversion))
        return

    # Get the last element from list
    nodeversion = versionList.pop()

    # Inform User about the version choose (only if more items exists)
    if len(versionList) != 0:
        print('Take Node v{0}...'.format(nodeversion))

    # If version already active?
    if getIfNodeVersionActive(nodeversion):
        print('Node v{0} already active.'.format(nodeversion))
        return False

    # Get original Path
    nodeDir = os.path.join(lxNodePath, nodeversion)

    # If Node Version installed?
    if not os.path.exists(nodeDir):
        print('Node v{0} not found locally.'.format(nodeDir))
        return False

    # If User Admin?
    if not lxtools.getIfAdmin():
        print('Required administrator Rights.')
        return False

    # Delete old LINK Directory when exits
    if os.path.exists(lxBinPath):
        # If Directory a Symbolic Link
        if not lxtools.getIfSymbolicLink(lxBinPath):
            print('ERROR: Target Directory is not a link and can not be removed.')
            return False

        # Remove Link
        try:
            os.remove(lxBinPath)
        except:
            return False

    # Set new link
    if not lxtools.setDirectoryLink(lxBinPath, nodeDir):
        print('ERROR while link to new Node Version.')
        return False

    print('Switched to Node v{0}...'.format(nodeversion))
    return True

# Returns the actual linked Version
def getLocalNodeVersion():
    # Check if symbolic link
    if not lxtools.getIfSymbolicLink(lxBinPath):
        return ''

    try:
        path = os.readlink(lxBinPath) # Read symbolic Link
        return path.rsplit('\\').pop() # Splits the Seperator and Returns the last Pathname (nodeversion)
    except:
        return ''

# Returns if the nodeversion active
def getIfNodeVersionActive(nodeversion):
    curVersion = getLocalNodeVersion()
    return curVersion != '' and curVersion == nodeversion

# Removes a local installed Version
def rmLocalNodeVersion(nodeversion):
    # Check if admin
    if not lxtools.getIfAdmin():
        print('This operation required Administrator rights!')
        return

    # Check if syntax correct
    if not getIfNodeVersionFormat(nodeversion):
        print('{0} is not a Node Version Format.'.format(nodeversion))
        return False

    # Get original Path
    nodeDir = os.path.join(lxNodePath, nodeversion)

    # If Node Version installed?
    if not os.path.exists(nodeDir):
        print('Node v{0} not found locally.'.format(nodeversion))
        return False

    # If Version active then abort
    if getIfNodeVersionActive(nodeversion):
        print('Cannot uninstall currently-active node version v{0}'.format(nodeversion))
        return False

    # Removes the Directory
    print('Remove Node v{0} from System.'.format(nodeversion))
    try:
        lxtools.rmDirectory(nodeDir)
        return True
    except Exception as e:
        print('ERROR: Node v{0} could not be removed.'.format(nodeversion))
        return False

def runSpecifiedNodeVersion(nodeversion, app, arg=''):
    # Retrive local available Version
    versionList = getLocalNodeVersionList(nodeversion)

    # No Version found
    if len(versionList) == 0:
        print('Sorry, no existing Node version {0} found locally.'.format(nodeversion))
        return

    # Get the last element from list
    nodeversion = versionList.pop()

    # Inform User about the version choose (only if more items exists)
    if len(versionList) != 0:
        print('Take Node v{0}...'.format(nodeversion))

    # Get original Path
    nodeDir = os.path.join(lxNodePath, nodeversion)

    # If Node Version installed?
    if not os.path.exists(nodeDir):
        print('Node v{0} not found locally.'.format(nodeDir))
        return False

    # If Application exits? ;)
    if not os.path.isfile(app):
        print('Application not found!')
        return False

    exeName = os.path.join(nodeDir, 'node.exe')
    # RUN
    print('Run Application with Node v{0}...'.format(nodeversion))
    try:
        subprocess.call('"{0}" "{1}"'.format(exeName, app), shell=True)
    except KeyboardInterrupt:
        print('Abort!')

    return True