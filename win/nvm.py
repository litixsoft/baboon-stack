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
import urllib.request as urlrequest
import re as regex
import subprocess
import tempfile
import lxtools
import sys
import os

# Global
remotePackage = 'node-v{0}-{1}.msi'
msiexecArguments = 'msiexec /quiet /a {0} /qb targetdir={1}'

# NodeJS
tempNodeDir = os.path.join(tempfile.gettempdir(), 'node')
moveNodeDir = os.path.join(tempNodeDir, 'nodejs')

# Node Directory
lxBasePath = os.environ['LXPATH']
lxNodePath = os.path.join(lxBasePath, 'Node')
lxBinPath = os.path.join(lxBasePath, 'lxm', 'Node')

# Displays a Progress bar
def showProgress(amtDone):
    sys.stdout.write("\rProgress: [{0:50s}] {1:.1f}% ".format('#' * int(amtDone * 50), amtDone * 100))
    sys.stdout.flush()

    pass

# Callback for urlretrieve (Downloadprogress)
def reporthook(blocknum, blocksize, filesize):
    if (blocknum != 0):
        percent =  blocknum / (filesize / blocksize)
    else:
        percent = 0

    showProgress(percent)
    pass

# Returns if nodeversion the correct format
def getIfNodeVersionFormat(nodeversion):
    return regex.match('[0-9]+\.[0-9]+\.[0-9]+', nodeversion) != None

# Returns if nodeversion installed
def getIfNodeVersionInstalled(nodeversion):
    return os.path.exists(os.path.join(lxNodePath, nodeversion))

# Download a Remote File to a temporary File and returns the filename
# Displays a Progress Bar during Download
def getRemoteFile(url):
    showProgress(0);
    try:
        local_filename, headers = urlrequest.urlretrieve(url, reporthook=reporthook)
        showProgress(1);
    except KeyboardInterrupt:
        print('Abort!')
        return -1
    except e as Exception:
        print('Exception occured!')
        print(e)
        return -1

    return local_filename

def cleanUp():
    # Clear temporary internet files
    urlrequest.urlcleanup

    # Clear temporary node directory
    if os.path.exists(tempNodeDir):
        lxtools.rmDirectory(tempNodeDir)

    pass

# Downloads a Remote File to a temporary File and returns the data
def getRemoteData(url):
    # Download from URL
    try:
        local_filename, headers = urlrequest.urlretrieve(url)
    except:
        return -1

    # Open and Read local temporary File
    html = open(local_filename)
    data = html.read()
    html.close()

    # Delete temporary Internet File
    urlrequest.urlcleanup()
    return data

# Returns the remote available Files with RegEx Filter
def getRemoteList(url, filter = "(.*)"):
    # Download from URL
    data = getRemoteData(url)

    # Exception or Abort
    if data == -1:
        return []

    # Returns list
    return regex.findall('">' + filter + '<\/a', data)

def getRemoteChecksumList(url):
    # Download from URL
    data = getRemoteData(url + '/SHASUMS.txt')

    # Exception or Abort
    if data == -1:
        return []

    # Split Data and returns Array
    return data.split('\n')

# Returns the remote available Node Version Directories
def getRemoteNodeVersionList():
    return getRemoteList("http://nodejs.org/dist/", "(v.*)\/")

# Returns, if remote Node Version for Windows available
def getRemoteNodeVersion(nodeversion):
    checksum = ''
    targetDirectory = os.path.join(lxNodePath, nodeversion)

    # Check if already installed
    if os.path.exists(targetDirectory):
        print('Version already installed.')
        return

    # Check if version available on remote server
    versionList = getRemoteNodeVersionList()

    if 'v' + nodeversion not in versionList:
        print('Node v{0} not found on remote server.'.format(nodeversion))
        return

    print('Retrieve Node Version v{0}...'.format(nodeversion))

    # The 64Bit Windows Version of Node is in a seperate Folder on Server
    if lxtools.getOsArchitecture() == 'x86':
        remoteFilename = remotePackage.format(nodeversion, 'x86')
    else:
        remoteFilename = 'x64/' + remotePackage.format(nodeversion, 'x64')

    # Get Checksumlist from remote Server
    print('Download Checksum List...')
    checksumList = getRemoteChecksumList("http://nodejs.org/dist/v" + nodeversion)

    # Find Checksum for the Binary
    for checksumEntry in checksumList:
        value = checksumEntry.split('  ')

        if value[1] == remoteFilename:
            remoteChecksum = value[0]
            break

    # If Checksum found?
    if remoteChecksum == '':
        print('No checksum for remote Binary...')

    # Download Binary from Server
    print('Download installation package...')
    tempRemoteFile = getRemoteFile("http://nodejs.org/dist/v" + nodeversion + '/' + remoteFilename)

    # Abort or Exception
    if tempRemoteFile == -1:
        return False

    print('Done!')

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
def getLocalNodeVersionList():
    srcNodeList = os.listdir(lxNodePath)
    tarNodeList = []

    # Filter the non confirm Versions :D
    for entry in srcNodeList:
        if getIfNodeVersionFormat(entry):
            tarNodeList.append(entry)

    return tarNodeList

# Activate a local available Node Version
def setLocalNodeVersion(nodeversion):
    # Check if syntax correct
    if not getIfNodeVersionFormat(nodeversion):
        print('{0} is not a Node Version Format.'.format(nodeversion))
        return False

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
        except e as Exception:
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
    except e as Exception:
        print('ERROR: Node v{0} could not be removed.'.format(nodeversion))
        return False

def runSpecifiedNodeVersion(nodeversion, app, arg=''):
    # Check if syntax correct
    if not getIfNodeVersionFormat(nodeversion):
        print('{0} is not a Node Version Format.'.format(nodeversion))
        return False

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

    return

def main():
    pass

if __name__ == '__main__':
    main()
