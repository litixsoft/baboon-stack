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
tempNodeDir = tempfile.gettempdir() + '\\node'
moveNodeDir = tempNodeDir + '\\nodejs'

# Node Directory
lxBasePath = os.environ['LXPATH']
lxNodePath = lxBasePath + '\\Node'
lxBinPath = lxBasePath + '\\lxm\\Node'

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

# Download a Remote File to a temporary File and returns the filename
# Displays a Progress Bar during Download
def getRemoteFile(url):
    showProgress(0);
    local_filename, headers = urlrequest.urlretrieve(url, reporthook=reporthook)
    showProgress(1);

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
    local_filename, headers = urlrequest.urlretrieve(url)

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

    # Returns list
    return regex.findall('">' + filter + '<\/a', data)

def getRemoteChecksumList(url):
    # Download from URL
    data = getRemoteData(url + '/SHASUMS.txt')

    # Split Data and returns Array
    return data.split('\n')

# Returns the remote available Node Version Directories
def getRemoteNodeVersionList():
    return getRemoteList("http://nodejs.org/dist/", "(v.*)\/")

# Returns, if remote Node Version for Windows available
def getRemoteNodeVersion(nodeversion):
    checksum = ''
    targetDirectory = lxNodePath + '\\' + nodeversion

    # Check if already installed
    if os.path.exists(targetDirectory):
        print('Version already installed.')
        return

    # Check if version available on remote server
    versionList = getRemoteNodeVersionList()

    if 'v' + nodeversion not in versionList:
        print('Node v{0} not found on remote server.'.format(nodeversion))
        return

    print('Retrieve Node.JS Version v{0}...'.format(nodeversion))

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
    subprocess.call(msiexecArguments.format(tempRemoteFile, tempNodeDir), shell=False)

    # Now copies node
    print('Copy files...')
    if os.path.exists(moveNodeDir):
        # MOVE
        os.rename(moveNodeDir, targetDirectory)
    else:
        print('Uuuh! Something is wrong! Abort!')
        return

    # Deletes the shit of temporary files
    print('Clean up...')
    cleanUp()
    return

# Retrives local available Node.JS Versions
def getLocalNodeVersionList():
    srcNodeList = os.listdir(lxNodePath)
    tarNodeList = []

    # Filter the non confirm Versions :D
    for entry in srcNodeList:
        if regex.match('[0-9]+\.[0-9]+\.[0-9]+', entry) != None:
            tarNodeList.append(entry)

    return tarNodeList

# Activate a local available Node.JS Version
def setLocalNodeVersion():

    return

def main():
    pass

if __name__ == '__main__':
    main()
