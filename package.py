#-------------------------------------------------------------------------------
# Name:        package
# Purpose:
#
# Author:      Thomas Scheibe
#
# Created:     04.12.2013
# Copyright:   (c) Thomas Scheibe 2013
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import tempfile
import json
import re as regex
import sys
import os

# Platform specified modules
if sys.platform == 'linux' or sys.platform == 'darwin':
    import tarfile

# lxManager modules
import version
import lxtools


class BaboonStackPackage:

    def __init__(self):
        self.__packagename = os.path.join(lxtools.getBaboonStackDirectory(), version.lxPackage)
        self.__packagedata = {}

        self.loadpackage(self.__packagename)
        pass

    def loadpackage(self, filename):
        try:
            cfgfile = open(filename, mode='r')
            data = cfgfile.read()
            cfgfile.close()
        except BaseException as e:
            print('>> ERROR: Unable to open package catalog...')
            print('>>', e)
            return False

        try:
            self.__packagedata = json.loads(data)
        except BaseException as e:
            print('>> JSON ERROR: Unable to parse package catalog...')
            print('>>', e)
            return False

        return True

    def getpackageversion(self):
        return self.__packagedata.get('version', '<unknow>')

    def getpackagelist(self):
        pkglist = []
        if 'packages' in self.__packagedata:
            for packagename in self.__packagedata['packages']:
                pkglist.append(packagename)

        return pkglist

    def getpackagesinfo(self):
        pkglist = []
        rootdir = lxtools.getBaboonStackDirectory()

        for packagename in self.getpackagelist():
            pkgdata = self.__packagedata['packages'][packagename]

            # If pkgdata
            if not isinstance(pkgdata, dict):
                continue

            # Info
            pkginfo = {
                'name': packagename,
                'version': pkgdata.get('version', ''),
                'dirname': pkgdata.get('dirname', packagename),
                'saferemove': pkgdata.get('saferemove', False)
            }

            # If package locally installed
            if os.path.exists(os.path.join(rootdir, pkgdata.get('dirname', 'none'))):
                binlist = pkgdata.get('binary', False)
                pkgexists = True

                # Check if binarys exists
                if binlist:
                    dirname = os.path.join(rootdir, pkgdata.get('dirname'))

                    if isinstance(binlist, str):
                        binlist = [binlist]

                    for binname in binlist:
                        if not os.path.exists(os.path.join(dirname, binname)):
                            pkgexists = False
                            break

                if pkgexists:
                    pkginfo['installed'] = 'Installed'

            # Add package info to list
            pkglist.append(pkginfo)

        # Return list
        return pkglist


# Load default
package = BaboonStackPackage()


# Returns the LATEST available Version on Server
def getLatestRemoteVersion(packagename=''):
    # Download Filelist
    data = lxtools.getRemoteData(version.lxServer + '/')

    # If Exception occured
    if data == -1:
        return ''

    # Get the available packages for this OS
    versionlist = regex.findall('">(' + packagename + ')<\/a', data)
    versionlist.sort()

    # If list empty?
    if len(versionlist) == 0:
        return False

    # Returns the LAST entry
    return versionlist.pop()


# Returns Checksum for specified file from Remote Checksumlist
def getRemoteChecksum(filename):
    # Download from URL
    data = lxtools.getRemoteData(version.lxServer + '/SHASUMS.txt')

    # Exception or Abort
    if data == -1:
        return False

    # Split data in to array and find checksum for file
    for checksumEntry in data.split('\n'):
        value = checksumEntry.split('  ')

        if len(value) != 2:
            continue

        if value[1] == filename:
            return value[0]

    # No checksum for this file, return empty string
    return False


# Main
def main():
    for pkg in package.getpackagesinfo():
        print(' ' + pkg.get('name', '').ljust(20, ' '),
              'v' + pkg.get('version', 'x.x').ljust(10, ' '),
              pkg.get('installed', 'Not installed')
        )

    return True


# Install a package
def install(pkgname):
    # Get package info
    pkginfo = None
    for pkg in package.getpackagesinfo():
        if pkg.get('name') == pkgname:
            pkginfo = pkg
            break

    # Check, if package available
    if not pkginfo:
        print('Unknow Package "' + pkgname + '"...')
        return False

    # Check, if package already installed
    if pkginfo.get('installed'):
        print('Package "' + pkgname + '" already installed locally...')
        return False

    # Check if admin
    if not lxtools.getIfAdmin():
        print(version.getMessage('REQUIREADMIN'))
        return False

    # create full package name
    fullpackagename = str(version.getConfigKey('package')).format(
        pkginfo.get('name'),
        pkginfo.get('version'),
        lxtools.getOsArchitecture()
    )

    # Download Filelist
    if not getLatestRemoteVersion(fullpackagename):
        print('SERVER ERROR: Package not found on server...')
        return False

    # Retrieve package checksum
    packagechecksum = getRemoteChecksum(fullpackagename)

    # Build
    url = version.lxServer + '/' + fullpackagename
    localpacketname = os.path.join(tempfile.gettempdir(), fullpackagename)

    # Download Packet with Progressbar
    print('Download ' + fullpackagename + '...')
    result = lxtools.getRemoteFile(url, localpacketname)

    # Exception or canceled
    if result == -1:
        return False

    # Check package checksum
    if packagechecksum:
        print('Verify Checksum...')
        localchecksum = lxtools.getSHAChecksum(localpacketname)

        # Check Checksum
        if localchecksum == packagechecksum:
            print('Checksum are correct...')
        else:
            print('Checksum missmatch... Abort!')
            print('Filename  ' + fullpackagename)
            print('Remote SHA' + packagechecksum)
            print('Local  SHA' + localchecksum)
            return False
    else:
        print('WARNING: No Checksum for this package available...')

    # Unix specified
    if sys.platform == 'linux' or sys.platform == 'darwin':
        # Extract TAR Package
        try:
            print('Extracting...')

            # Extract files
            tar = tarfile.open(localpacketname)
            tar.extractall(lxtools.getBaboonStackDirectory())
            tar.close()

            print('Installing...')
            scriptoption = ['install']

            # Execute script "lxscript.sh"
            packagedirectory = os.path.join(lxtools.getBaboonStackDirectory(), pkginfo.get('dirname'))

            if os.path.isfile(os.path.join(packagedirectory, 'lxScript.sh')):
                # Only execute script if availabled
                os.system(os.path.join(packagedirectory, 'lxScript.sh {0}'.format(' '.join(scriptoption))))
        except BaseException as e:
            print('ERROR:', e)
            return False

        lxtools.cleanUpTemporaryFiles()
        print('Done...')

    return True


# Removes a package
def remove(pkgname):
    # Get package info
    pkginfo = None
    for pkg in package.getpackagesinfo():
        if pkg.get('name') == pkgname:
            pkginfo = pkg
            break

    # Check, if package available
    if not pkginfo:
        print('Unknow Package "' + pkgname + '"...')
        return False

    # Check, if package already installed
    if not pkginfo.get('installed'):
        print('Package "' + pkgname + '" NOT installed locally...')
        return False

    # Check if admin
    if not lxtools.getIfAdmin():
        print(version.getMessage('REQUIREADMIN'))
        return

    # Script options
    scriptoption = ['remove']

    # Ask for remove databases, cfg if saferemove TRUE
    if pkginfo.get('saferemove'):
        key = lxtools.readkey('Would you like to keep their databases, configuration files?')

        if key != 'y':
            scriptoption.append('all')

    print('Remove package "' + pkgname + '"...')

    # Run remove script
    packagedirectory = os.path.join(lxtools.getBaboonStackDirectory(), pkginfo.get('dirname'))

    if os.path.isfile(os.path.join(packagedirectory, 'lxScript.sh')):
        os.system(os.path.join(packagedirectory, 'lxScript.sh {0}'.format(' '.join(scriptoption))))

    # Delete directory, if not saferemove and exists
    if not pkginfo.get('saferemove') and os.path.exists(packagedirectory):
        print('Remove directory')
        lxtools.rmDirectory(packagedirectory)

    # Done
    print('Done...')

    return True