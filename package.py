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

version_symbols = '~<>=-|'
version_numbers = '.0123456789'


class BaboonStackPackage:

    def __init__(self, packagedata):
        self.__name = None
        self.__fullname = None
        self.__installed = False

        if not isinstance(packagedata, dict):
            self.__packagedata = {}
        else:
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
            'saferemove': self.__packagedata.get('saferemove', True),
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


def getIfPackageInstalled(pkginfo):
    rootdir = lxtools.getBaboonStackDirectory()
    dirname = pkginfo.get('dirname', None)
    result = (dirname and os.path.exists(os.path.join(rootdir, dirname)))

    # If package locally installed
    if result:
        binlist = pkginfo.get('binary', False)

        # Check if binarys exists
        if binlist:
            dirname = os.path.join(rootdir, dirname)

            if isinstance(binlist, str):
                binlist = [binlist]

            if isinstance(binlist, list):
                for binname in binlist:
                    if not os.path.exists(os.path.join(dirname, binname)):
                        result = False
                        break

    # Return result
    return result


#
def getIfVersionString(version):
    for char in version:
        if char not in str(version_numbers + version_symbols):
            return False

    return True


#
def getVersionString(version):
    result = ''
    for char in version:
        if char in str(version_numbers):
            result += char

        if char == ' ':
            break

    return result


# Returns if dependencies installed
def getIfDependenciesInstalled(pkginfo):
    if not pkginfo:
        print('ERROR: No package description found...')
        return False

    # Check if dirname exists
    if pkginfo.get('dirname') is None:
        print('ERROR: No ´dirname´ in description file...')
        return False

    # Check dependencies, if set
    pkgdependencies = pkginfo.get('dependencies', None)

    if pkgdependencies and isinstance(pkgdependencies, dict):
        bbs_deplist = []
        thirdparty_deplist = []

        for itemname in pkgdependencies:
            # if array, then is binary dependencie
            if isinstance(pkgdependencies[itemname], list):
                for subitem in pkgdependencies[itemname]:
                    if not lxtools.getIfBinaryExists(subitem):
                        thirdparty_deplist.append(itemname)

                        break
                continue

            # if version string, also bbs package
            if not getIfVersionString(pkgdependencies[itemname]):
                # check if binary exists
                if not lxtools.getIfBinaryExists(pkgdependencies[itemname]):
                    thirdparty_deplist.append(itemname)
            else:
                # Check bbs package if installed
                if itemname not in localcatalog or not localcatalog[itemname].getIfInstalled():
                    bbs_deplist.append(itemname)

        # Show deplist
        if bbs_deplist or thirdparty_deplist:
            if bbs_deplist:
                print('\nFollow baboonstack dependencies are required, please install first:\n')
                print(' ' + str(', ').join(bbs_deplist))

            if thirdparty_deplist:
                print('\nFollow THIRD PARTY dependencies are required, please install first:\n')
                print(' ' + str(', ').join(thirdparty_deplist))

            print('\nAbort!')
            return False

    return True


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
def getRemoteCatalog(localcatalogonly=False):
    catalog = dict()
    bbscatalogfile = os.path.join(lxtools.getBaboonStackDirectory(), 'baboonstack.package.conf')

    # First, try to read local package file if not exists then
    if os.path.exists(bbscatalogfile):
        catalogdata = lxtools.loadjson(bbscatalogfile)
        packages = catalogdata.get('packages', {})
        for pkgname in packages:
            catalog[pkgname] = {
                'version': [packages[pkgname].get('version')],
                'source': 'catalog',
                'info': packages[pkgname]
            }

        if localcatalogonly:
            return catalog

    # Download Filelist
    data = lxtools.getRemoteData(config.lxServer + '/')

    # If Exception occured
    if data == -1:
        return []

    # Gets the Package Name Mask for this OS
    packagenamemask = str(
        config.getConfigKey('packagemask')
    ).format(
        lxtools.getOsArchitecture()
    )

    # Get the available packages for this OS
    filelist = regex.findall('">(' + packagenamemask + ')<\/a', data)
    filelist.sort()

    # Add all versions
    for entry in filelist:
        a = os.path.splitext(entry)[0].split('-')

        if a[0] == 'baboonstack':
            continue

        if a[0] not in catalog:
            catalog[a[0]] = {
                'version': [],
                'source': 'server'
            }

        catalog[a[0]]['version'].append(a[1][1:])
        catalog[a[0]]['source'] = 'server'

    return catalog


# Reads local Catalog
def getLocalCatalog(scanfolders=True):
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

    if scanfolders:
        for entry in files:
            fullpath = os.path.join(rootdir, entry)

            if not os.path.isdir(fullpath):
                continue

            packagefile = os.path.join(fullpath, 'package.bbs.conf')

            if os.path.isfile(packagefile):
                pkgdata = BaboonStackPackage({})
                pkgdata.loadPackage(packagefile)
                packagename = pkgdata.getPackageName()

                if packagename is None or not pkgdata.getIfInstalled():
                    continue

                catalog[packagename] = pkgdata

    return catalog


# Returns latest version in list
def getLastVersion(pkgdata):
    versionlist = pkgdata.get('version', []).copy()
    versionlist.sort()

    if len(versionlist) == 0 or not isinstance(versionlist, list):
        return ''

    result = versionlist[0]
    for version in versionlist:
        if StrictVersion(result) < StrictVersion(version):
            result = version

    return result


def getAvailableUpdates(local, remote):
    updatelist = dict()

    for packagename in local:
        if local[packagename].getIfInstalled() and packagename in remote:
            localversion = local[packagename].getVersion()
            remoteversion = getLastVersion(remote[packagename])

            if StrictVersion(localversion) < StrictVersion(remoteversion):
                updatelist[packagename] = {
                    'fullname': local[packagename].getFullname(),
                    'local': localversion,
                    'remote': remoteversion
                }

    return updatelist


# Execute a Script Section Object
def exec(cmd, cwd, showoutput=True):
    if isinstance(cmd, str):
        return lxtools.run(cmd, str, showoutput)

    if isinstance(cmd, dict) and cmd.get('cmd', None) is not None:

        # If user confirm defined, then ask him
        if cmd.get('confirm') is True:
            key = lxtools.readkey(
                cmd.get('text', 'Do you want to execute "' + cmd.get('cmd') + '"?')
            )

            if key == 'y':
                return runScript(cmd.get('cmd'), cwd, showoutput)

            return True

    # Someting goes wrong
    return False

# Run system specified script
def runScript(pkginfo, scriptoption):
    if not isinstance(scriptoption, list):
        return

    # Hide Script output
    hide_script_output = ('hidden' in scriptoption)

    if hide_script_output is True:
        scriptoption.remove('hidden')

    scriptfile = config.lxConfig.get('scriptfile', None)
    packagedirectory = os.path.join(lxtools.getBaboonStackDirectory(), pkginfo.get('dirname'))

    # Is script file set
    if scriptfile is not None:
        if os.path.isfile(os.path.join(packagedirectory, scriptfile)):
            try:
                # Change working directory to script location
                lxtools.run(
                    os.path.join(packagedirectory, '{0} {1}'.format(scriptfile, ' '.join(scriptoption))),
                    packagedirectory,
                    not hide_script_output
                )
            except BaseException as e:
                print('ERROR while executing script!')
                print(e)

    # Has script sektion, then execute
    script = pkginfo.get('script', None)

    if isinstance(script, dict) and len(scriptoption) > 0:
        script = script.get(scriptoption[0], None)
        osname = lxtools.getPlatformName()

        # Get platform specified script section, if available
        if isinstance(script, list) and osname in script:
            script = script[osname]

        # Now execute the script line or lines
        if isinstance(script, list):
            for item in script:
                exec(item, packagedirectory, not hide_script_output)
        elif isinstance(script, str) or isinstance(script, dict):
            exec(script, packagedirectory, not hide_script_output)

    return

# Collect Data
localcatalog = getLocalCatalog()
remotecatalog = getRemoteCatalog()
updatelist = getAvailableUpdates(localcatalog, remotecatalog)


# localist
def localist(pkgname, options=list):
    print('Installed Packages:\n')
    for packagename in localcatalog:
        package = localcatalog.get(packagename)

        if not package.getIfInstalled():
            continue

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
def remotelist(pkgname, options=list):
    print('Remote available Packages:\n')
    cnt = 0
    for packagename in remotecatalog:
        if packagename not in localcatalog or not localcatalog[packagename].getIfInstalled():
            package = remotecatalog.get(packagename, {})
            print(
                ' ',
                packagename.ljust(20, ' '),
                str('v' + getLastVersion(package)).ljust(12),
                package.get('source', 'server')
            )

            cnt += 1

    if cnt == 0:
        print('No packages available on server.')

    return True


# Installs a package
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
        for pkg in localcatalog:
            # Only install if not installed locally
            if not localcatalog[pkg].getIfInstalled():
                pkgname.append(pkg.get('name', None))

        if len(pkgname) == 0:
            print('Sorry, no packages available to install.')
            return False

        # Rerun
        return install(pkgname, options)

    #
    # Start install single package
    #

    # Check, if package available
    if pkgname not in remotecatalog:
        print('Unknow Package "' + pkgname + '"...')
        return False

    pkginfo = {}

    # Collect pkginfo and if package already installed
    if pkgname in localcatalog:
        if localcatalog[pkgname].getIfInstalled():
            print('Package "' + pkgname + '" already installed locally...')
            return False

    pkgdata = remotecatalog[pkgname]
    latestversion = getLastVersion(pkgdata)
    fullpackagename = str(config.getConfigKey('package')).format(
        pkgname,
        latestversion,
        lxtools.getOsArchitecture()
    )

    # print('Source:', pkgdata.get('source', '<unknow>'))

    # Get catalog info
    if pkgdata['source'] == 'catalog':
        pkginfo = pkgdata.get('info', {})

    # Check if admin
    if not lxtools.getIfAdmin():
        print(config.getMessage('REQUIREADMIN'))
        return False

    # Ask
    if 'ask' in options:
        key = lxtools.readkey('Do you really want to install "' + pkgname + '"...', 'Yn')

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

    # # Download Filelist
    # if not getLatestRemoteVersion(fullpackagename):
    #     print('SERVER ERROR: Package not found on server...')
    #     return False

    # Retrieve package checksum
    packagechecksum = getRemoteChecksum(fullpackagename)

    # Build
    url = config.lxServer + '/' + fullpackagename
    dirname = None
    iserror = False
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
        tempdirectory = tempfile.mkdtemp()
        archive_filelist = []

        # Unix specified
        if sys.platform.startswith('linux') or sys.platform == 'darwin':
            # Extract files
            mytar = tarfile.open(localpacketname)

            # Find and Read package description file, if exists
            for tarinfo in mytar:
                if os.path.basename(tarinfo.name) == config.getConfigKey('configfile', 'package.bbs.conf'):
                    print('Read package description file...')
                    try:
                        # Extract file
                        mytar.extract(tarinfo.name, tempdirectory)

                        # Read package
                        pkginfo = lxtools.loadjson(os.path.join(tempdirectory, tarinfo.name), True)
                    except BaseException as e:
                        print(e)
                        return False

                    # Exit
                    break

            # Get dirname
            dirname = os.path.join(pkginfo.get('dirname'), '')

            # Check dependencies, if set
            if getIfDependenciesInstalled(pkginfo):
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
            else:
                iserror = True

            mytar.close()

        # Windows specified
        if sys.platform == 'win32':
            if zipfile.is_zipfile(localpacketname):
                myzip = zipfile.ZipFile(localpacketname, 'r')

                # Find and Read package description file, if exists
                for filename in myzip.namelist():
                    if os.path.basename(filename) == config.getConfigKey('configfile', 'package.bbs.conf'):
                        print('Read package description file...')
                        try:
                            # Extract file
                            myzip.extract(filename, tempdirectory)

                            # Read package
                            pkginfo = lxtools.loadjson(os.path.join(tempdirectory, filename), True)
                        except BaseException as e:
                            print(e)
                            return False

                        # Exit
                        break

                # Get dirname
                dirname = os.path.join(pkginfo.get('dirname'), '')

                # Check dependencies, if set
                if getIfDependenciesInstalled(pkginfo):
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
                else:
                    iserror = True

                myzip.close()
            else:
                print('ERROR: Archive is not a ZIP File.')
                return False

        # Remove temporary directory
        lxtools.rmDirectory(tempdirectory)

        # If error occured
        if iserror:
            return False

        # Has dirname
        if not dirname:
            print('ERROR: No ´dirname´ in description file...')
            return False

        # Some file and directories will be include or exclude for removing
        files_rules = pkginfo.get('files', None)
        if files_rules is not None:
            files_includes = files_rules.get('include', [])
            files_excludes = files_rules.get('exclude', [])

            # Include files or directory
            if files_includes:
                # If single string, then build array
                if isinstance(files_includes, str):
                    files_includes = [files_includes]

                if isinstance(files_includes, list):
                    for fileentry in files_includes:
                        archive_filelist.append(os.path.normpath(fileentry))

            # Exclude files or directory
            if files_excludes:
                # If single string, then build array
                if isinstance(files_excludes, str):
                    files_excludes = [files_excludes]

                if isinstance(files_excludes, list):
                    for fileentry in files_excludes:
                        fullname = os.path.normpath(fileentry)

                        # Remove every item
                        tmpfilelist = archive_filelist.copy()
                        for archiveentry in tmpfilelist:
                            if str(archiveentry).startswith(fullname):
                                archive_filelist.remove(archiveentry)

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
        for pkg in localcatalog:
            # Only remove if installed locally
            if localcatalog[pkg].getIfInstalled():
                pkgname.append(pkg)

        if len(pkgname) == 0:
            print('Sorry, no packages available to remove.')
            return False

        # Rerun
        return remove(pkgname, options)

    # Get package info
    pkginfo = None

    if pkgname in localcatalog:
        # Check, if package already installed
        if not localcatalog[pkgname].getIfInstalled():
            print('Package "' + pkgname + '" NOT installed locally...')
            return False

        pkginfo = localcatalog[pkgname].getPackageInfo()

    # Check, if package available
    if not pkginfo:
        print('Unknow Package "' + pkgname + '"...')
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

    # If saferemove option overwritten?
    if 'force' in options or 'safe' in options:
        if 'force' in options:
            saferemove = False

        if 'safe' in options:
            saferemove = True
    else:
        # Ask for remove databases, cfg if saferemove TRUE
        if saferemove:
            key = lxtools.readkey('Would you like to keep their databases, configuration files?')

            if key != 'y':
                saferemove = False

    if not saferemove:
        scriptoption.append('all')

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


# Updates a package
def update(pkgname, options=list()):
    if pkgname is None:
        return False

    # Update all packages, if available
    if pkgname == '':
        if not updatelist:
            print('No package updates available.')
            return True
        else:
            # Ask, if update
            if 'force' not in options:
                for itemname in updatelist:
                    package = updatelist.get(itemname, {})
                    print(
                        ' ',
                        package.get('fullname', itemname).ljust(30, ' '),
                        'v' + package.get('local', '0.0.0').ljust(10, ' '),
                        '=>',
                        'v' + package.get('remote', '0.0.0').ljust(10, ' ')
                    )

                key = lxtools.readkey('\nWould you like to update this packages?')

                if key == 'n':
                    return False

            pkgname = []
            for itemname in updatelist:
                pkgname.append(itemname)

            return update(pkgname, options)

    # Update multiple
    if isinstance(pkgname, list):
        pkgcnt = 0
        for name in pkgname:
            print('Update package "' + name + '"...\n')

            if update(name, options):
                pkgcnt += 1
            print('')

        print(' {0} of {1} packages successfully updated'.format(str(pkgcnt), str(len(pkgname))))
        return True

    # Update single package
    if pkgname not in updatelist:
        print('No update for ´' + pkgname + '´ available.')
        return False

    # Remove
    if not remove(pkgname, ['safe']):
        return False

    # Update Package list
    del localcatalog[pkgname]

    # Install
    if not install(pkgname, ['safe']):
        return False

    return True

# Upgrade local catalog file
def upgrade():
    rootdir = lxtools.getBaboonStackDirectory()
    prev_catalogfilename = os.path.join(rootdir, config.lxPreviousPackage)

    # No Upgrade required
    if not os.path.isfile(prev_catalogfilename):
        return False

    # Check if admin
    if not lxtools.getIfAdmin():
        print('Catalog Upgrade required!', config.getMessage('REQUIREADMIN'))
        return True

    catalogdata = lxtools.loadjson(prev_catalogfilename, False)
    pkgdata = catalogdata.get('packages', {})

    for pkgname in pkgdata:
        if getIfPackageInstalled(pkgdata[pkgname]):
            pkgfilename = os.path.join(rootdir, pkgdata[pkgname].get('dirname'), config.getConfigKey('configfile'))
            if not os.path.isfile(pkgfilename):
                pkginfo = pkgdata[pkgname].copy()

                # Add some informations
                pkginfo['name'] = pkgname
                pkginfo['bbsversion'] = catalogdata.get('version', '0.0.0')

                if not lxtools.savejson(pkgfilename, pkginfo):
                    print('Upgrade failure...')
                    return False

    os.remove(prev_catalogfilename)
    print('Upgrade successfull...')
    return True