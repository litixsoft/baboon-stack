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
import re as regex
import sys
import os
from distutils.version import StrictVersion

# Platform specified modules
if sys.platform.startswith('linux') or sys.platform == 'darwin':
    import tarfile

if sys.platform == 'win32':
    import zipfile

# lxManager modules
import config
import lxtools

class BaboonStackPackage:

    def __init__(self, packagedata={}):
        self.__name = None
        self.__fullname = None
        self.__installed = False
        self.__packagedata = packagedata.copy()

        self.refresh()

    def getIfInstalled(self):
        return self.__installed

    def getVersion(self):
        return self.__packagedata.get('version', '0.0.0')

    def getPackageName(self):
        return self.__name

    def getFullname(self):
        return self.__fullname

    def getPackageInfo(self):
        return {
            'name': self.__name,
            'version': self.getVersion(),
            'dirname': self.__packagedata.get('dirname', self.__name),
            'saferemove': self.__packagedata.get('saferemove', False),
            'nodownload': self.__packagedata.get('nodownload', False),
            'script': self.__packagedata.get('script', {}),
            'dependencies': self.__packagedata.get('dependencies', False)
        }

    def loadPackage(self, filename):
            if os.path.isfile(filename):
                self.__packagedata = lxtools.loadjson(filename)
                self.refresh()

    def refresh(self):
        rootdir = lxtools.getBaboonStackDirectory()
        dirname = self.__packagedata.get('dirname', None)

        self.__name = self.__packagedata.get('packagename', self.__packagedata.get('name', '(unknow)'))
        self.__fullname = self.__packagedata.get('fullname', self.__name)
        self.__installed = False

        # If package locally installed
        if dirname and os.path.exists(os.path.join(rootdir, dirname)):
            binlist = self.__packagedata.get('binary', False)
            self.__installed = True

            # Check if binarys exists
            if binlist:
                dirname = os.path.join(rootdir, dirname)

                if isinstance(binlist, str):
                    binlist = [binlist]

                if isinstance(binlist, list):
                    for binname in binlist:
                        if not os.path.exists(os.path.join(dirname, binname)):
                            self.__installed = False
                            break


# Returns a list, with all avaible package on server for this os
def getServerFileList():
    # Download Filelist
    data = lxtools.getRemoteData(config.lxServer + '/')

    # If Exception occured
    if data == -1:
        return []

    # Gets the Package Name Mask for this OS
    packagenamemask = str(
        config.getConfigKey('package')
    ).format(
        lxtools.getOsArchitecture()
    )

    # Get the available packages for this OS
    filelist = regex.findall('">(' + packagenamemask + ')<\/a', data)
    filelist.sort()

    # Returns the LAST entry
    return filelist


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


# Returns the Remote Package Catalog
def getRemoteCatalog():
    filelist = getServerFileList()
    catalog = dict()

    for entry in filelist:
        a = os.path.splitext(entry)[0].split('-')

        if a[0] not in catalog:
            catalog[a[0]] = {
                'version': [a[1][1:]]
            }
        else:
            catalog[a[0]]['version'].append(a[1][1:])

    return catalog


def getLocalCatalog():
    rootdir = lxtools.getBaboonStackDirectory()
    catalog = dict()
    files = os.listdir(rootdir)

    # First, try to read local package file if not exists then
    if os.path.exists(os.path.join(rootdir, 'baboonstack.package.conf')):
        catalogdata = lxtools.loadjson(os.path.join(rootdir, 'baboonstack.package.conf'))
        pkgdata = catalogdata.get('packages', {})

        for pkgname in pkgdata:
            pkginfo = pkgdata.get(pkgname, {})
            pkginfo['name'] = pkgname

            catalog[pkgname] = BaboonStackPackage(pkginfo)

    for entry in files:
        fullpath = os.path.join(rootdir, entry)

        if not os.path.isdir(fullpath):
            continue

        packagefile = os.path.join(fullpath, 'package.bbs.conf')

        if os.path.isfile(packagefile):
            pkgdata = BaboonStackPackage()
            pkgdata.loadPackage(packagefile)
            packagename = pkgdata.getPackageName()

            if packagename is None or not pkgdata.getIfInstalled():
                continue

            catalog[packagename] = pkgdata

    return catalog


def getLastVersion(pkgdata):
    versionlist = pkgdata.get('version', []).copy()

    if len(versionlist) == 0 or not isinstance(versionlist, list):
        return ''

    return versionlist.pop()


def getAvailableUpdates(local, remote):
    updatelist = dict()

    for packagename in local:
        if packagename in remote:
            localversion = local[packagename].getVersion()
            remoteversion = getLastVersion(remote[packagename])

            if StrictVersion(localversion) < StrictVersion(remoteversion):
                updatelist[packagename] = {
                    'fullname': local[packagename].getFullname(),
                    'local': localversion,
                    'remote': remoteversion
                }

    return updatelist


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


localcatalog = getLocalCatalog()
remotecatalog = getRemoteCatalog()
updatelist = getAvailableUpdates(localcatalog, remotecatalog)


# Main
def main():
    for packagename in localcatalog:
        package = localcatalog.get(packagename)

        if packagename in updatelist:
            updatehintstring = '=> v' + updatelist.get(packagename, {}).get('remote', '?.?.?')
        else:
            updatehintstring = ''

        print(
            ' ',
            package.getFullname().ljust(30, ' '),
            str('(' + packagename + ')').ljust(15),
            'v' + package.getVersion().ljust(10),
            updatehintstring
        )

    return True


# Show available Packages
def remotelist(pkgname, options=list()):
    print('Remote available Packages:\n')
    for packagename in remotecatalog:
        if packagename not in localcatalog:
            package = remotecatalog.get(packagename, {})
            print(
                ' ',
                packagename.ljust(20, ' '),
                'v' + getLastVersion(package)
            )

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
    # TODO: Change this
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
        if sys.platform.startswith('linux') or sys.platform == 'darwin':
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

# TODO: Change this
def update():
    return False
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