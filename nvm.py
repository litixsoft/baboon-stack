#-------------------------------------------------------------------------------
# Name:        nvm
# Purpose:     NodeJS Version Manager
#
# Author:      Thomas Scheibe
#
# Created:     01.08.2013
# Copyright:   (c) Litixsoft GmbH 2014
# Licence:     Licensed under the MIT license.
#-------------------------------------------------------------------------------
from distutils.version import StrictVersion
import re as regex
import subprocess
import tempfile
import sys
import os

# Platform specified modules
if sys.platform.startswith('linux') or sys.platform == 'darwin':
    import tarfile

# Baboonstack modules
import config
import lxtools

# Global
msiexecArguments = 'msiexec /quiet /a {0} /qb targetdir={1}'

# NodeJS
tempNodeDir = os.path.join(tempfile.gettempdir(), 'node')

# Node Directory
lxBasePath = lxtools.getBaboonStackDirectory()
lxNodePath = os.path.join(lxBasePath, 'node')

if sys.platform == 'win32':
    lxBinPath = os.path.join(lxBasePath, 'bbs', 'Node')
else:
    # Unix Systems are below
    lxBinPath = os.path.join(config.getConfigKey('node.links.node.target'), 'node')

# CleanUp
def cleanUp():
    # Remove temporary internet files
    lxtools.cleanUpTemporaryFiles()

    # Clear temporary node directory
    if os.path.exists(tempNodeDir):
        lxtools.rmDirectory(tempNodeDir)

# Returns if nodeversion the correct format
def getIfNodeVersionFormat(nodeversion):
    return regex.match('[0-9]+\.[0-9]+\.[0-9]+', nodeversion) is not None

# Returns if nodeversion installed
def getIfNodeVersionInstalled(nodeversion):
    return os.path.exists(os.path.join(lxNodePath, nodeversion))

# Returns the remote available Files with RegEx Filter
def getRemoteList(url, filter=''):
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
def getRemoteNodeVersionList(filter=''):
    versionList = getRemoteList("http://nodejs.org/dist/", filter)
    versionList.sort(key=StrictVersion) # Sort list FROM oldest Version TO newer Version
    return versionList

# Returns, if remote Node Version for Windows available
def getRemoteNodeVersion(nodeversion, options):
    # Check if admin
    if not lxtools.getIfAdmin():
        print(config.getMessage('REQUIREADMIN'))
        return False

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
        return False

    # Get the Os specified Node Remote Package
    remoteFilename = config.lxConfig['node']['package'][lxtools.getOsArchitecture()].format(nodeversion)

    # Get Checksumlist from remote Server
    print('Retrieve Checksum list...')
    checksumList = getRemoteChecksumList("http://nodejs.org/dist/v" + nodeversion)
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
    tempRemoteFile = lxtools.getRemoteFile("http://nodejs.org/dist/v" + nodeversion + '/' + remoteFilename)

    # Abort or Exception
    if tempRemoteFile == -1:
        return False

    # Generate Checksum of downloaded Binary
    print('Generate Checksum...')
    localChecksum = lxtools.getSHAChecksum(tempRemoteFile)

    # Check Checksum
    if (localChecksum == remoteChecksum):
        print('Checksum correct...')
    else:
        print('Checksum missmatch... Abort!')
        print('Filename  ' + remoteFilename)
        print('Remote SHA' + remoteChecksum)
        print('Local  SHA' + localChecksum)
        return False

    # Default temp Directory
    moveNodeDir = tempNodeDir

    # Remove temp, if exists
    if os.path.exists(tempNodeDir):
        try:
            lxtools.rmDirectory(tempNodeDir)
        except Exception as e:
            raise e

    # Windows specified stuff
    if sys.platform == 'win32':
        moveNodeDir = os.path.join(tempNodeDir, 'nodejs')

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

    # Unix specified stuff
    if sys.platform.startswith('linux') or sys.platform == 'darwin':
        moveNodeDir = os.path.join(tempNodeDir, remoteFilename.rstrip('.tar.gz'))

        # Extract TAR Package
        try:
            tar = tarfile.open(tempRemoteFile)
            tar.extractall(tempNodeDir)
            tar.close()
        except BaseException as e:
            print('ERROR:', e)
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

    if not 'noswitch' in options:
        return setLocalNodeVersion(nodeversion)
    else:
        return True

# Retrives local available Node Versions
def getLocalNodeVersionList(filter=''):
    srcNodeList = os.listdir(lxNodePath)
    tarNodeList = []

    # Filter the non confirm Versions :D
    for entry in srcNodeList:
        if getIfNodeVersionFormat(entry):
            # If filter, then MUST match
            if filter and regex.match(filter + '.*', entry) is None:
                continue

            tarNodeList.append(entry)

    # Sort list FROM oldest Version TO newer Version
    tarNodeList.sort(key=StrictVersion)
    return tarNodeList

# Deregister Node
def resetNode():
    # If User Admin?
    if not lxtools.getIfAdmin():
        print(config.getMessage('REQUIREADMIN'))
        return False

    # Windows
    if sys.platform == 'win32':
        # Delete old LINK Directory when exits
        if os.path.exists(lxBinPath):
            # If Directory a Symbolic Link
            if not lxtools.getIfSymbolicLink(lxBinPath):
                print('ERROR: Target Directory is not a link and can not be removed.')
                return False

            # Remove Link
            try:
                os.remove(lxBinPath)
            except BaseException as e:
                print('ERROR:', e)
                return False

        return True

    # Unix
    if sys.platform.startswith('linux') or sys.platform == 'darwin':
        links = config.getConfigKey('node.links')

        # Unlink old version
        for names in links:
            target = os.path.join(links[names]['target'], names)
            options = links[names].get('options', [])

            # Check if link, when true then remove it
            if os.path.islink(target):
                try:
                    os.remove(target)
                except BaseException as e:
                    print('ERROR:', e)
                    return False
            else:
                # Check if "fullname" a real existing path/file, then raise Exception
                if os.path.isdir(target) or os.path.isfile(target):
                    if 'remove_if_exists' in options:
                        try:
                            print('Remove Directory', target)
                            lxtools.rmDirectory(target)
                        except BaseException as e:
                            print('ERROR:', e)
                            return False
                    else:
                        print('UUh, a target is not a link...', target)
                        return False

        return True

    # No operation for that system :(
    return False


# Activate a local available Node Version
def setLocalNodeVersion(nodeversion):
    # Retrive local available Version
    versionList = getLocalNodeVersionList(nodeversion)

    # No Version found
    if len(versionList) == 0:
        print('Sorry, no existing Node version {0} found locally.'.format(nodeversion))
        return False

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
        print(config.getMessage('REQUIREADMIN'))
        return False

    # Windows
    if sys.platform == 'win32':
        # Delete old LINK Directory when exits
        if not resetNode():
            return False

        # Set new link
        if not lxtools.setDirectoryLink(lxBinPath, nodeDir):
            print('ERROR while link to new Node Version.')
            return False

        print('Switched to Node v{0}...'.format(nodeversion))
        return True

    # Unix
    if sys.platform.startswith('linux') or sys.platform == 'darwin':
        links = config.getConfigKey('node.links')

        # check if all required source directories exits
        pathexists = True
        for names in links:
            linkoptions = links[names].get('options', [])

            if 'absolute_source' in linkoptions:
                fullname = links[names]['source']
            else:
                fullname = os.path.join(nodeDir, links[names]['source'], names)

            # absolute_source
            # Check, if required source not found
            if 'no_source_check' not in linkoptions and not os.path.isfile(fullname) and not os.path.isdir(fullname):
                print('ERROR: Required Element "' +
                      os.path.join(links[names]['source'], names) +
                      '" in "' +
                      nodeDir +
                      '" not found...')
                pathexists = False

        # A required Source was not found, abort
        if not pathexists:
            return False

        # Unlink old version
        if not resetNode():
            return False

        # link new version
        for names in links:
            linkoptions = links[names].get('options', [])

            if 'absolute_source' in linkoptions:
                source = links[names]['source']
            else:
                source = os.path.join(nodeDir, links[names]['source'], names)

            target = os.path.join(links[names]['target'], names)
            #source = os.path.join(nodeDir, links[names]['source'], names)

            # Link
            if not lxtools.setDirectoryLink(target, source):
                raise Exception('Link creation failed!\n' + source + ' => ' + target)

        # run Cache fix
        runCacheFix()

        # show hint
        print('Note: Force a ´npm update -g´ to update global modules...')
        print('\nSwitched to Node v{0}...'.format(nodeversion))

        return True

    return False

# Returns the actual linked Version
def getLocalNodeVersion():
    # Check if symbolic link
    if not lxtools.getIfSymbolicLink(lxBinPath):
        return False

    try:
        # Read symbolic Link
        path = os.readlink(lxBinPath)

        # Remove bin/node. Only for non win32 platforms
        if sys.platform != 'win32':
            path = path.rsplit(os.sep, 2)[0]

        # Splits the Seperator and Returns the last Pathname (nodeversion)
        return path.rsplit(os.sep).pop()
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
        print(config.getMessage('REQUIREADMIN'))
        return False

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
        print('EXCEPTION:', e)
        return False

def runSpecifiedNodeVersion(nodeversion, app, arg=''):
    # Retrive local available Version
    versionList = getLocalNodeVersionList(nodeversion)

    # No Version found
    if len(versionList) == 0:
        print('Sorry, no existing Node version {0} found locally.'.format(nodeversion))
        return False

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

# Change the permission of npm cache
def runCacheFix():
    # Under windows os, not needed
    if lxtools.getPlatformName() == 'win32':
        return True

    # Check if admin
    if not lxtools.getIfAdmin():
        print(config.getMessage('REQUIREADMIN'))
        return False

    # Get User home dir and .npm cache
    homedir = os.path.expanduser('~')
    npmcachedir = os.path.join(homedir, '.npm')

    if os.path.isdir(npmcachedir):
        homedir_stat = os.stat(homedir)

        print('Fix ´.npm´ cache permissions...')
        return lxtools.chown(npmcachedir, homedir_stat.st_uid, homedir_stat.st_gid)

    return True