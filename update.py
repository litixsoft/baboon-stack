#-------------------------------------------------------------------------------
# Name:        update
# Purpose:     Baboonstack Self Update Manager
#
# Author:      Thomas Scheibe
#
# Created:     05.08.2013
# Copyright:   (c) Litixsoft GmbH 2014
# Licence:     Licensed under the MIT license.
#-------------------------------------------------------------------------------
import tempfile
import re as regex
import sys
import os

# Platform specified modules
if sys.platform.startswith('linux') or sys.platform == 'darwin':
    import tarfile
    import subprocess

# lxManager Modules
import config
import lxtools


# Returns the LATEST available Version on Server
def getLatestRemoteVersion():
    # Download Filelist
    data = lxtools.getRemoteData(config.lxServer + '/')

    # If Exception occured
    if data == -1:
        return ''

    # Get the available BaboonStack Packages for this OS
    packageName = str(config.getConfigKey('update', '')).format(lxtools.getOsArchitecture())
    versionList = regex.findall('">(' + packageName + ')<\/a', data)
    versionList.sort()

    # If list empty?
    if len(versionList) == 0:
        return ''

    # Returns the LAST entry
    return versionList.pop()


# Returns Checksum for specified file from Remote Checksumlist
def getRemoteChecksum(filename):
    # Download from URL
    data = lxtools.getRemoteData(config.lxServer + '/SHASUMS.txt')

    # Exception or Abort
    if data == -1:
        return ''

    # Split data in to array and find checksum for file
    for checksumEntry in data.split('\n'):
        value = checksumEntry.split('  ')

        if len(value) != 2:
            continue

        if value[1] == filename:
            return value[0]

    # No checksum for this file, return empty string
    return ''


def doPackagesUpdate():
    pass


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
    packageName = str(config.getConfigKey('update', '')).replace('{0}', '{1}').replace('.*', 'v{0}')
    versionLocal = packageName.format(config.lxVersion, lxtools.getOsArchitecture())

    # Update required?
    if not versionRemote.lower() > versionLocal.lower():
        # No Update required
        print('No Baboonstack Update available...')
        return False

    # Check if admin
    if not lxtools.getIfAdmin():
        print(config.getMessage('REQUIREADMIN'))
        return False

    # Download Update
    print('Update {0} => {1}...'.format(versionLocal, versionRemote))

    # Build
    url = config.lxServer + '/' + versionRemote
    localPacket = os.path.join(tempfile.gettempdir(), versionRemote)

    # Download Packet with Progressbar
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
            print('Checksum correct...')
        else:
            print('Checksum missmatch... Abort!')
            print('Filename  ' + versionRemote)
            print('Remote SHA' + remoteChecksum)
            print('Local  SHA' + localChecksum)
            return False

    # Run Installation and exit under Windows
    if sys.platform == 'win32':
        print('Execute installer...')
        os.startfile(localPacket)
        print('Installation routine will start separately, exit now...')
        return True

    # Under Unix we must do all stuff
    if sys.platform.startswith('linux') or sys.platform == 'darwin':
        tempupdatedir = os.path.join(tempfile.gettempdir(), localPacket.rstrip('.tar.gz'))

        # Extract TAR Package
        try:
            tar = tarfile.open(localPacket)
            tar.extractall(tempupdatedir)
            tar.close()
        except BaseException as e:
            lxtools.cleanUpTemporaryFiles()
            print('ERROR:', e)
            return False

        updatescriptfile = os.path.join(tempupdatedir, 'lxupdate.sh')
        if os.path.exists(updatescriptfile):
            # Rename package catalog file
            if os.path.exists(config.lxPackage):
                os.rename(
                    os.path.join(lxtools.getBaboonStackDirectory(), config.lxPackage),
                    os.path.join(lxtools.getBaboonStackDirectory(), config.lxPreviousPackage)
                )

            # Execute Update script
            print('Execute Update...')
            subprocess.Popen([updatescriptfile, tempupdatedir, lxtools.getBaboonStackDirectory()])
            sys.exit(23)
        else:
            # Clean up temporary internet files
            lxtools.cleanUpTemporaryFiles()

            # Clean up temporary update files
            lxtools.rmDirectory(tempupdatedir)

        return True

    # No Update method found for that system
    return False