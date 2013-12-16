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
from distutils.version import StrictVersion

# Platform specified modules
if sys.platform == 'linux' or sys.platform == 'darwin':
    import tarfile

if sys.platform == 'win32':
    import zipfile

# lxManager modules
import config
import lxtools


class BaboonStackPackage:

    @staticmethod
    def loadPackage(filename, reporterror=True):
        try:
            cfgfile = open(filename, mode='r')
            data = cfgfile.read()
            cfgfile.close()
        except BaseException as e:
            if reporterror:
                print('>> ERROR: Unable to open package catalog...')
                print('>>', e)
            return {}

        try:
            return json.loads(data)
        except BaseException as e:
            if reporterror:
                print('>> JSON ERROR: Unable to parse package catalog...')
                print('>>', e)
            return {}

    def __buildPackageList(self):
        self.__packagelist = []
        rootdir = lxtools.getBaboonStackDirectory()

        for packagename in self.__packagedata.get('packages', {}):
            pkgdata = self.__packagedata['packages'].get(packagename, None)

            # If pkgdata
            if not isinstance(pkgdata, dict):
                continue

            # Info
            pkginfo = {
                'name': packagename,
                'version': pkgdata.get('version', ''),
                'dirname': pkgdata.get('dirname', packagename),
                'saferemove': pkgdata.get('saferemove', False),
                'nodownload': pkgdata.get('nodownload', False),
                'script': pkgdata.get('script', {})
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

                    if isinstance(binlist, list):
                        for binname in binlist:
                            if not os.path.exists(os.path.join(dirname, binname)):
                                pkgexists = False
                                break

                # if installed
                if pkgexists:
                    pkginfo['installed'] = 'Installed'

                    # Check if update available
                    prevpackages = self.__previousdata.get('packages', {})

                    if packagename in prevpackages:
                        prevpackage = prevpackages.get(packagename, {})
                        prev_package_version = prevpackage.get('version', '0.0.0')
                        now_package_version = pkgdata.get('version', '0.0.0')

                        if StrictVersion(now_package_version) > StrictVersion(prev_package_version):
                            # Mark package as update available and report global
                            self.__updaterequired = True
                            pkginfo['previous'] = prevpackage

            # Add package info to list
            self.__packagelist.append(pkginfo)

    def __init__(self, packagefilename=config.lxPackage, previouspackagefilename=config.lxPrevPackage):
        self.__previouspackagefilename = os.path.join(lxtools.getBaboonStackDirectory(), previouspackagefilename)
        self.__packagedata = self.loadPackage(os.path.join(lxtools.getBaboonStackDirectory(), packagefilename))
        self.__previousdata = self.loadPackage(self.__previouspackagefilename, False)
        self.__updaterequired = False
        self.__packagelist = []

        # Check, if really prev version
        if len(self.__previousdata) > 0:
            ver_now = self.__packagedata.get('version', '0.0.0')
            ver_prev = self.__previousdata.get('version', '0.0.0')

            if StrictVersion(ver_now) <= StrictVersion(ver_prev):
                # Ignore Update
                self.__previousdata = {}

        self.refresh()

    def getPackageVersion(self):
        return self.__packagedata.get('version', '<unknow>')

    def getPackagesInfoList(self):
        return self.__packagelist

    def getIfUpdateRequired(self):
        return self.__updaterequired

    def refresh(self):
        self.__buildPackageList()

    def removePreviousPackageFile(self):
        if os.path.exists(self.__previouspackagefilename):
            os.remove(self.__previouspackagefilename)
            return True

        return False

# Load default
package = BaboonStackPackage()

# Returns the LATEST available Version on Server
def getLatestRemoteVersion(packagename=''):
    # Download Filelist
    data = lxtools.getRemoteData(config.lxServer + '/')

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
    data = lxtools.getRemoteData(config.lxServer + '/SHASUMS.txt')

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


# Run system specified script
def runScript(pkginfo, scriptoption):
    if not isinstance(scriptoption, list):
        return

    scriptfile = config.lxConfig.get('scriptfile', None)

    # Is script file set
    if not scriptfile is None:
        packagedirectory = os.path.join(lxtools.getBaboonStackDirectory(), pkginfo.get('dirname'))

        if os.path.isfile(os.path.join(packagedirectory, scriptfile)):
            # Get current working directory
            last_wd = os.getcwd()
            try:
                # Change working directory to script location
                os.chdir(packagedirectory)
                lxtools.run(os.path.join(packagedirectory, '{0} {1}'.format(scriptfile, ' '.join(scriptoption))))
            except BaseException as e:
                print('ERROR while executing script!')
                print(e)

            # Back to previous working directory
            os.chdir(last_wd)

    # Has script sektion, then execute
    script = pkginfo.get('script', None)

    if isinstance(script, dict) and len(scriptoption) > 0:
        script = script.get(scriptoption[0], None)

        if isinstance(script, list):
            for item in script:
                lxtools.run(item)

        if isinstance(script, str):
            lxtools.run(script)


# Main
def main():
    for pkg in package.getPackagesInfoList():
        print(' ' + pkg.get('name', '').ljust(20, ' '),
              'v' + pkg.get('version', 'x.x').ljust(10, ' '),
              pkg.get('installed', 'Not installed'))

    return True


# Install a package
def install(pkgname, options=list()):
    if pkgname is None:
        return False

    # if pkgname is list, then install multiple
    if isinstance(pkgname, list):
        pkgcnt = 0
        for name in pkgname:
            print('Install package "' + name + '"...')
            if install(name, options):
                pkgcnt += 1
            print('')

        print(' {0} of {1} packages successfully installed'.format(str(pkgcnt), str(len(pkgname))))
        return True

    # Install ALL packages?
    if pkgname == '':
        if 'force' not in options and 'ask' not in options:
            options.append('ask')

        pkgname = []
        for pkg in package.getPackagesInfoList():
            # Only install if not installed locally
            if pkg.get('installed', None) is None:
                pkgname.append(pkg.get('name', None))

        if len(pkgname) == 0:
            print('Sorry, no packages available to install.')
            return False

        # Rerun
        return install(pkgname, options)

    #
    # Start install single package
    #

    # Get package info
    pkginfo = None
    for pkg in package.getPackagesInfoList():
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
        print(config.getMessage('REQUIREADMIN'))
        return False

    # Ask
    if 'ask' in options:
        key = lxtools.readkey('Really install "' + pkgname + '"...', 'Yn')

        if key == 'n':
            return False

    # Download require
    if pkginfo.get('nodownload', False) is True:
        # No Download require, then create dir and exit
        basedir = os.path.join(lxtools.getBaboonStackDirectory(), pkginfo.get('dirname'))
        print('Create Directory...')
        try:
            os.mkdir(basedir, 0o755)

            # Execute scripts
            runScript(pkginfo, ['install'])
        except BaseException as e:
            print('ERROR:', e)
            return False

        print('Done...')
        return True

    # create full package name
    fullpackagename = str(config.getConfigKey('package')).format(
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
    url = config.lxServer + '/' + fullpackagename
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
            print('Remote SHA' + str(packagechecksum))
            print('Local  SHA' + localchecksum)
            return False
    else:
        print('WARNING: No Checksum for this package available...')

    # Extract Archive Package
    try:
        print('Extracting...')
        dirname = os.path.join(pkginfo.get('dirname'), '')
        archive_filelist = []

        # Unix specified
        if sys.platform == 'linux' or sys.platform == 'darwin':
            # Extract files
            mytar = tarfile.open(localpacketname)

            # Get the filelist from tarfile
            for tarinfo in mytar:
                normpath = os.path.normpath(tarinfo.name)
                if normpath.startswith(dirname):
                    archive_filelist.append(normpath[len(dirname):])

            # Extract files
            try:
                mytar.extractall(lxtools.getBaboonStackDirectory())
            except BaseException as e:
                print('Error in TAR, see error below.')
                print(e)

            mytar.close()

        # Windows specified
        if sys.platform == 'win32':
            if zipfile.is_zipfile(localpacketname):
                myzip = zipfile.ZipFile(localpacketname, 'r')

                # Get the filelist from zipfile
                for filename in myzip.namelist():
                    normpath = os.path.normpath(filename)
                    if normpath.startswith(dirname):
                        archive_filelist.append(normpath[len(dirname):])

                # Extract files
                try:
                    myzip.extractall(lxtools.getBaboonStackDirectory())
                except BaseException as e:
                    print('Error in ZIP, see error below.')
                    print(e)

                myzip.close()
            else:
                print('ERROR: Archive is not a ZIP File.')
                return False

        # Save filelist into program directory for remove
        if len(archive_filelist) != 0:
            lstname = os.path.join(lxtools.getBaboonStackDirectory(), dirname, 'files.lst')
            try:
                fileslst = open(lstname, 'w')
                fileslst.write('\n'.join(archive_filelist))
                fileslst.close()
            except BaseException as e:
                print('Error while saving filelist!')
                print(e)

        print('Installing...')
        scriptoption = ['install']

        # Execute scripts
        runScript(pkginfo, scriptoption)
    except BaseException as e:
        print('ERROR:', e)
        return False

    lxtools.cleanUpTemporaryFiles()
    print('Done...')

    return True


# Removes a package
def remove(pkgname, options=list()):
    if pkgname is None:
        return False

    # if pkgname is list, then remove multiple
    if isinstance(pkgname, list):

        if 'force' not in options and 'ask' not in options:
            options.append('ask')

        pkgcnt = 0
        for name in pkgname:
            if 'ask' in options:
                key = lxtools.readkey('Remove package "' + name + '"...', 'yNa')

                # User selected no, keep package
                if key == 'n':
                    continue

                # User selected abort, stop all
                if key == 'a':
                    print(' Abort!!!')
                    break
            else:
                print('Remove package "' + name + '"...')

            if remove(name, options):
                pkgcnt += 1
            print('')

        print(' {0} of {1} packages successfully removed'.format(str(pkgcnt), str(len(pkgname))))
        return True

    # Removes ALL packages?
    if pkgname == '':
        pkgname = []
        for pkg in package.getPackagesInfoList():
            # Only remove if installed locally
            if pkg.get('installed', None) is not None:
                pkgname.append(pkg.get('name', None))

        if len(pkgname) == 0:
            print('Sorry, no packages available to remove.')
            return False

        # Rerun
        return remove(pkgname, options)

    # Get package info
    pkginfo = None
    for pkg in package.getPackagesInfoList():
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
        print(config.getMessage('REQUIREADMIN'))
        return

    # Ask
    if 'ask' in options:
        key = lxtools.readkey('Really remove "' + pkgname + '"...', 'Ny')

        if key == 'n':
            return False

    # Script options
    scriptoption = ['remove']
    saferemove = pkginfo.get('saferemove') is True

    # Ask for remove databases, cfg if saferemove TRUE
    if saferemove and 'force' not in options:
        key = lxtools.readkey('Would you like to keep their databases, configuration files?')

        if key != 'y':
            scriptoption.append('all')
            saferemove = False

    print('Remove package "' + pkgname + '"...')

    # Run remove script
    runScript(pkginfo, scriptoption)

    # Delete files
    dirname = os.path.join(pkginfo.get('dirname'), '')
    basedir = os.path.join(lxtools.getBaboonStackDirectory(), dirname)
    lstname = os.path.join(basedir, 'files.lst')

    # Load files.lst, if exists
    if os.path.exists(lstname):
        dir_filelist = ['files.lst']
        try:
            fileslst = open(lstname, 'r')
            for line in fileslst.readlines():
                dir_filelist.append(line.rstrip('\n'))
            fileslst.close()
        except BaseException as e:
            print('Error while saving filelist!')
            print(e)
    else:
        dir_filelist = []

    # Has files?
    if len(dir_filelist) != 0:
        dirlist = []

        # Remove every file from directory and marks directories
        print('Remove files...')
        for filename in dir_filelist:
            fullpath = os.path.join(basedir, filename)
            if os.path.exists(fullpath):
                if os.path.isdir(fullpath):
                    # Add dir to list, will be removed later
                    dirlist.append(fullpath)
                else:
                    # Remove file
                    try:
                        os.remove(fullpath)
                    except BaseException as e:
                        print(e)

        # Remove directory if empty
        for directory in dirlist:
            if len(os.listdir(directory)) == 0:
                os.rmdir(directory)

    # Remove base directory if exists and empty
    if os.path.exists(basedir):
        if len(os.listdir(basedir)) == 0:
            os.rmdir(basedir)
        else:
            # Remove directory with all files if not safe remove
            if not saferemove is True:
                lxtools.rmDirectory(basedir)

    # Done
    print('Done...')

    return True


def update():
    if not package.getIfUpdateRequired():
        return False

    packagelist = []

    print('Following package(s) required a update:\n')

    # List packages
    for packagedata in package.getPackagesInfoList():
        prevpackagedata = packagedata.get('previous', None)

        if prevpackagedata is None:
            continue

        info = {
            'name': packagedata.get('name', '<unnamed>'),
            'from_version': prevpackagedata.get('version', '?.?.?'),
            'to_version': packagedata.get('version', '?.?.?')
        }

        print(' ' + info.get('name').ljust(20, ' '),
              'v' + info.get('from_version').ljust(10, ' '),
              '=> v', info.get('to_version'))

        packagelist.append(info)

    print('')

    # Get if is Admin
    if not lxtools.getIfAdmin():
        print(config.getMessage('REQUIREADMIN'))
        return True

    key = lxtools.readkey('Start package update?')

    # User abort operation
    if key == 'n':
        print('Abort!')
        return True

    # Perform update
    iserror = False
    for packagedata in packagelist:
        packagename = packagedata.get('name')

        # Remove
        if not remove(packagename, ['force']):
            iserror = True
            break

        # Update Package list
        package.refresh()

        # Install
        if not install(packagename, ['force']):
            iserror = True
            break

    # Error occured, abort!
    if iserror:
        return True

    # All Updates taken, remove old package file
    if not package.removePreviousPackageFile():
        print('Error: Previous catalog file could not be deleted.')

    return True