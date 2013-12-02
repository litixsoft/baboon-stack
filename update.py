#-------------------------------------------------------------------------------
# Name:        update
# Purpose:
#
# Author:      Thomas Scheibe
#
# Created:     05.08.2013
# Copyright:   (c) Thomas Scheibe 2013
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import tempfile
import re as regex
import os

# lxManager Modules
import version
import lxtools

# Returns the LATEST available Version on Server
def getLatestRemoteVersion():
    # Download Filelist
    data = lxtools.getRemoteData(version.lxServer + '/')

    # If Exception occured
    if data == -1:
        return ''

    # Get the available BaboonStack Packages for this OS
    versionList = regex.findall('">(baboonstack-.*-windows-' + lxtools.getOsArchitecture() + '.exe)<\/a', data)
    versionList.sort()

    # If list empty?
    if len(versionList) == 0:
        return ''

    # Returns the LAST entry
    return versionList.pop()

# Returns Checksum for specified file from Remote Checksumlist
def getRemoteChecksum(filename):
    # Download from URL
    data = lxtools.getRemoteData(version.lxServer + '/SHASUMS.txt')

    # Exception or Abort
    if data == -1:
        return ''

    # Split data in to array and find checksum for file
    for checksumEntry in data.split('\n'):
        value = checksumEntry.split('  ')

        if value[1] == filename:
            return value[0]

    # No checksum for this file, return empty string
    return ''

# Check for Update
def doUpdate():
    # Get latest Version on Server
    print('Check for update...')
    versionRemote = getLatestRemoteVersion()

    # No files?
    if versionRemote == '':
        print('No Baboonstack Update available...')
        return False

    # Get local version
    versionLocal = version.lxPacket.format(version.lxVersion, lxtools.getOsArchitecture())

    # Update required?
    if not versionRemote.lower() > versionLocal.lower():
        # No Update required
        print('No Baboonstack Update available...')
        return False

    # Download Update
    print('Update {0} => {1}...'.format(versionLocal, versionRemote))

    # Build
    url = version.lxServer + '/' + versionRemote
    localPacket = os.path.join(tempfile.gettempdir(), versionRemote)

    # Downlaod Packet with Progressbar
    result = lxtools.getRemoteFile(url, localPacket)

    # Exception or canceled
    if result == -1:
        return False

    # Verify (if availabled)
    print('Get Checksum from Server...')
    remoteChecksum = getRemoteChecksum(versionRemote)

    if remoteChecksum != '':
        print('Verify Checksum...')
        localChecksum = lxtools.getSHAChecksum(localPacket)

        # Check Checksum
        if (localChecksum == remoteChecksum):
            print('Checksum are correct...')
        else:
            print('Checksum missmatch... Abort!')
            print('Filename  ' + remoteFilename)
            print('Remote SHA' + remoteChecksum)
            print('Local  SHA' + localChecksum)
            return False

    # Run Installation and exit
    print('Execute installer...')
    os.startfile(localPacket)
    print('Installation routine will start separately, exit now...')
    return True