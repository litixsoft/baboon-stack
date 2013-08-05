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

def getLatestRemoteVersion():
    # Download Filelist
    data = lxtools.getRemoteData(version.lxServer + '/')

    # If Exception occured
    if data == -1:
        return ''

    # Get the available BaboonStack Packages for this OS
    versionList = regex.findall('"> (baboonstack-.*-windows-' + lxtools.getOsArchitecture() + '.exe)<\/a', data)
    versionList.sort()

    # If list empty?
    if len(versionList) == 0:
        return ''

    # Returns the LAST entry
    return versionList.pop()

def doUpdate():
    # Get latest Version on Server
    versionRemote = getLatestRemoteVersion()

    # No files?
    if versionRemote == '':
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


