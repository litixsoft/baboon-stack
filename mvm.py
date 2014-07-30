#-------------------------------------------------------------------------------
# Name:        mvm
# Purpose:     MongoDB Version Manager
#
# Author:      Thomas Scheibe
#
# Created:     30.06.2014
# Copyright:   (c) Litixsoft GmbH 2014
# Licence:     Licensed under the MIT license.
#-------------------------------------------------------------------------------
from distutils.version import StrictVersion
import re as regex
import subprocess
import tempfile
import sys
import os

# Baboonstack modules
import config
import lxtools
import package
import patch

# Global
mongosymlink = os.path.join(lxtools.getBaboonStackDirectory(), 'mongo')
mongobasedir = os.path.join(lxtools.getBaboonStackDirectory(), 'mongodb')


# Returns if mongoversion the correct format
def getIfMongoVersionFormat(mongoversion):
    return regex.match('[0-9]+\.[0-9]+\.[0-9]+', mongoversion) is not None


def getIfMongoVersionAvailable(mongoversion):
    if os.path.exists(os.path.join(mongobasedir, mongoversion)):
        pkginfo = lxtools.loadjson(
            os.path.join(mongobasedir, mongoversion, config.getConfigKey('configfile')),
            reporterror=False
        )

        # has package file
        if pkginfo:
            binlist = pkginfo.get('binary', None)

            # Check if binarys exists
            if binlist:
                if isinstance(binlist, str):
                    binlist = [binlist]

                if isinstance(binlist, list):
                    for binname in binlist:
                        if not os.path.exists(os.path.join(mongobasedir, mongoversion, binname)):
                            return False

                return True

    # No installed
    return False


# Returns the actual linked Version
def getActiveMongoVersion():
    # Check if symbolic link
    if not os.path.isdir(mongosymlink):
        return ''

    if not lxtools.getIfSymbolicLink(mongosymlink):
        return False

    try:
        # Read symbolic Link
        path = os.readlink(mongosymlink)

        # Splits the Seperator and Returns the last Pathname (mongoversion)
        return path.rsplit(os.sep).pop()
    except Exception as e:
        print('ERROR:', e)
        return ''


# Retrives local available Mongo Versions
def getLocalMongoVersionList(filter=''):
    srcMongoList = os.listdir(mongobasedir)
    tarMongoList = []

    # Filter the non confirm Versions :D
    for entry in srcMongoList:
        if getIfMongoVersionFormat(entry):
            # If filter, then MUST match
            if filter and regex.match(filter + '.*', entry) is None:
                continue

            tarMongoList.append(entry)

    # Sort list FROM oldest Version TO newer Version
    tarMongoList.sort(key=StrictVersion)
    return tarMongoList


def resetMongo():
    # If User Admin?
    if not lxtools.getIfAdmin():
        print(config.getMessage('REQUIREADMIN'))
        return False

    # Delete old LINK Directory when exits
    if os.path.exists(mongosymlink):

        # If Directory a Symbolic Link
        if not lxtools.getIfSymbolicLink(mongosymlink):
            print('ERROR: Mongo folder is not a link and can not be removed.')
            return False

        # Remove Link
        try:
            os.remove(mongosymlink)
        except BaseException as e:
            print('ERROR:', e)
            return False

    return True


# Performs a upgrade from Older version
# Returns TRUE if Upgrade successfully performed, FALSE is Upgrade required but abortet and NONE no upgrade required
def doUpgrade():
    if os.path.isdir(mongosymlink) and not lxtools.getIfSymbolicLink(mongosymlink):
        # Upgrade
        print('Upgrade needed...')

        # Check if admin
        if not lxtools.getIfAdmin():
            print(config.getMessage('REQUIREADMIN'))
            return False

        # Load package file
        pkginfo = lxtools.loadjson(os.path.join(mongosymlink, config.getConfigKey('configfile')))
        mongoversion = pkginfo.get('version', None)

        # Execute Patches
        patches = config.getConfigKey('mongo.patches', None)
        patch.doPatch(mongosymlink, patches)

        # Stop Service/Daemon and de-register Service/Daemon, safe-remove
        print('Stop Service/Daemon...')
        package.runScript(pkginfo, ['remove', 'safe', 'hidden'])

        # Check if *all* symbolic links removed, when not remove it
        symlinks = config.getConfigKey('mongo.links', {})
        if symlinks:
            for names in symlinks:
                target = symlinks[names]['target']

                if os.path.exists(target) and lxtools.getIfSymbolicLink(target):
                    os.remove(target)

        # Move Directory to mongodb/{version}/
        print('Move files...')
        mongodir = os.path.join(mongobasedir, mongoversion)

        # Create new mongodb directory and move installed version
        os.makedirs(mongobasedir)
        os.rename(mongosymlink, mongodir)

        # Create Symlink
        print('Create symlinks...')
        lxtools.setDirectoryLink(mongosymlink, mongodir)

        # Start Daemon/Service
        print('Start Service/Daemon...')
        package.runScript(pkginfo, ['install', 'hidden'])

        print('Done')
        return True
    else:
        return None


def doInstall(version, options):
    print("Install mongo version " + version + "...")

    # Check if correct version
    if not getIfMongoVersionFormat(version):
        print('The specified string is not a correct mongo version format.')
        return

    # Check if already installed
    if getIfMongoVersionAvailable(version):
        print('Version already installed, Abort!')
        return

    # Check if admin
    if not lxtools.getIfAdmin():
        print(config.getMessage('REQUIREADMIN'))
        return

    fullmongodir = os.path.join(mongobasedir, version)

    # Download mongo binary
    pkgurl = config.getConfigKey('mongo.package.' + lxtools.getOsArchitecture(), '').format(version)
    pkgfile = tempfile.mktemp('', 'bbs_pkg')
    pkgpath = tempfile.mkdtemp('', 'bbs_pkg')

    # Download mongo helper
    hlpurl = config.getConfigKey('mongo.helper.' + lxtools.getOsArchitecture(), '').format(version)
    hlpfile = tempfile.mktemp('', 'bbs_pkg')
    hlppath = tempfile.mkdtemp('', 'bbs_pkg')

    # Get mongo binarys
    print('Download Mongo binarys...')
    result = lxtools.getRemoteFile(
        pkgurl,
        pkgfile
    )

    if result == -1:
        print('Error while downloading Mongo Binarys. Version really exists?')
        return -1

    # Get Helper file
    print('Download Mongo helpers...')
    result = lxtools.getRemoteFile(
        hlpurl,
        hlpfile
    )

    if result == -1:
        print('Error while downloading Mongo Helpers. Try again later.')
        return -1

    # Extract files
    print('Extract files...')
    lxtools.doExtract(pkgfile, pkgpath)
    lxtools.doExtract(hlpfile, hlppath)

    # Move and Merge files
    print('Move files...')

    # Create target directory
    if not os.path.exists(fullmongodir):
        os.makedirs(fullmongodir)

    fileslist = []

    # Move helper files
    fileslist += lxtools.moveDirectory(hlppath, fullmongodir)

    # Move *all* directories to target directory
    dir_moved = False
    for name in os.listdir(pkgpath):
        if os.path.isdir(os.path.join(pkgpath, name)):
            fileslist += lxtools.moveDirectory(os.path.join(pkgpath, name), fullmongodir)
            dir_moved = True

    if not dir_moved:
        print('Sorry, no files from binary archive was moved!')
        return

    # Save filelist as files.lst
    if len(fileslist) != 0:
        lstname = os.path.join(fullmongodir, 'files.lst')

        try:
            fileslst = open(lstname, 'w')
            fileslst.write('\n'.join(fileslist))
            fileslst.close()
        except BaseException as e:
            print('Error while saving files.lst!')
            print(e)

    # Clen up
    print('Clean up...')
    lxtools.rmDirectory(pkgpath)
    lxtools.rmDirectory(hlppath)

    # Done
    print('Done...')

    # User want to not switch
    if 'noswitch' in options:
        return

    if 'force' in options:
        key = 'y'
    else:
        key = lxtools.readkey('Would you like to activate the new Mongo version?')

    if key == 'y':
        doChange(version)


def doRemove(version, options):
    activeVersion = getActiveMongoVersion()

    # Admin required
    if not lxtools.getIfAdmin():
        print(config.getMessage('REQUIREADMIN'))
        return

    # Version already active
    if activeVersion == version:
        print('Currently activated version can not be removed.')
        return

    # If version locally available
    if not getIfMongoVersionAvailable(version):
        print('A non-installed version can not be removed. Since there is no magic.')
        return

    mongodir = os.path.join(mongobasedir, version)
    lstname = os.path.join(mongodir, 'files.lst')

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

    #
    saferemove = None

    if 'safe' in options:
        saferemove = True

    if 'force' in options:
        saferemove = False

    # If no safe or force options choosen, then ask user
    if saferemove is None:
        saferemove = (
            lxtools.readkey('Would you like to remove *ALL* files? Includes database/log files/etc', 'yN') != 'y'
        )

    # Has files?
    if len(dir_filelist) != 0:
        # Remove every file from directory and marks directories
        print('Remove files...')
        lxtools.removeFilesFromList(mongodir, dir_filelist, saferemove)

    print('Removed...')
    pass


def doList():
    activeversion = getActiveMongoVersion()
    versions = getLocalMongoVersionList()

    print('Local available MongoDB Versions:\n')

    # Prints sorted list
    for version in versions:
        if activeversion and activeversion == version:
            print(' * {0}'.format(version))
        else:
            print('   {0}'.format(version))


def doReset():
    activeVersion = getActiveMongoVersion()

    # if not a version activated, then abort
    if activeVersion == '':
        print('No currently activated MongoDB Version')
        return

    # Admin required
    if not lxtools.getIfAdmin():
        print(config.getMessage('REQUIREADMIN'))
        return

    # If folder exits but not an symlink, then abort
    if activeVersion is False:
        print('ERROR: Folder is not a symlink.')
        return

    print('Deactivate MongoDB v' + activeVersion)

    # Run Script file
    pkginfo = lxtools.loadjson(os.path.join(mongosymlink, config.getConfigKey('configfile')))
    package.runScript(pkginfo, ['remove', 'safe', 'hidden'])

    # Check if *all* symbolic links removed, when not remove it
    symlinks = config.getConfigKey('mongo.links', None)
    if symlinks:
        for names in symlinks:
            target = os.path.join(symlinks[names]['target'], names)

            if os.path.exists(target) and lxtools.getIfSymbolicLink(target):
                os.remove(target)

    if not resetMongo():
        return


def doChange(version):
    activeVersion = getActiveMongoVersion()

    # Admin required
    if not lxtools.getIfAdmin():
        print(config.getMessage('REQUIREADMIN'))
        return

    # If folder exits but not an symlink, then abort
    if activeVersion is False:
        print('ERROR: Folder is not a symlink.')
        return

    # Version already active
    if activeVersion == version:
        print('Version', version, 'already active.')
        return

    # If version locally available
    if not getIfMongoVersionAvailable(version):
        print('Version', version, 'not available locally.')
        return

    # Check if selected version currently activ in pidlist
    pidfile = 'mongo-' + version + '.pids'
    pidlist = lxtools.loadFileFromUserSettings(pidfile, returntype=[])

    if len(pidlist) != 0:
        # Get a list with active pids from a list with pids
        alive = lxtools.getActiveProcessFromPidList(pidlist)

        if len(alive) != 0:
            print('Version is in use and can not be registered as a service.')
            return False

    # if version already set, then deactivate
    if activeVersion != '':
        doReset()

    # Mongo dir
    mongodir = os.path.join(mongobasedir, version)

    # Create Symlink
    print('Activate Mongo v' + version)
    lxtools.setDirectoryLink(mongosymlink, mongodir)

    # Run Script file
    pkginfo = lxtools.loadjson(os.path.join(mongosymlink, config.getConfigKey('configfile')))
    package.runScript(pkginfo, ['install', 'hidden'])

    # Check if *all* symbolic links successfully linked
    symlinks = config.getConfigKey('mongo.links', None)

    if symlinks is not None:
        print('Create symlinks...')
        for names in symlinks:
            source = os.path.join(mongosymlink, symlinks[names]['source'], names)
            target = os.path.join(symlinks[names]['target'], names)

            # Link
            if not lxtools.setDirectoryLink(target, source):
                raise Exception('Link creation failed!\n' + source + ' => ' + target)

    print('\nDone, nice!')
    pass


def doStart(version, params):
    if not getIfMongoVersionAvailable(version):
        print('Version not available locally.')
        return

    print('Start MongoDB Instance v' + version + '...')

    pidfile = 'mongo-' + version + '.pids'
    pidlist = lxtools.loadFileFromUserSettings(pidfile, False, returntype=[])

    mongodir = os.path.join(mongobasedir, version)
    mongodaemon = os.path.join(mongodir, config.getConfigKey('mongo.binary.mongod'))

    # Check if binary exists
    if not os.path.isfile(mongodaemon):
        print('Mongo daemon binary not found.')
        return

    mongodatadir = mongodir

    # Create db and log folder if not exists
    try:
        if not os.path.exists(os.path.join(mongodatadir, 'db')):
            os.makedirs(os.path.join(mongodatadir, 'db'))

        if not os.path.exists(os.path.join(mongodatadir, 'log')):
            os.makedirs(os.path.join(mongodatadir, 'log'))
    except IOError as e:
        print('ERROR:', e)
        print('Abort and exit!')
        return False

    args = [
        mongodaemon,
    ]

    defaultargs = {
        '--port': '27017',
        '--dbpath': os.path.join(mongodatadir, 'db')
        # '--logpath': os.path.join(mongodatadir, 'log', 'db.log')
    }

    if not isinstance(params, list):
        params = []

    # Lower case parameters
    plist = []
    for i in range(0, len(params) - 1):
        if params[i][0] == '-':
            plist.append(params[i].lower())

    # Merge
    args.extend(params)

    # Fill with default values
    for argv in defaultargs:
        if argv not in plist:
            print(' Add parameter:', argv, defaultargs[argv])
            args.append(argv)
            args.append(defaultargs[argv])

    print('Start MongoDB v' + version + '...')
    # print('Mongod parameters:', str(' ').join(args[1:]))
    print('*** Please wait for 5 second(s) to validate success ***')

    # if sys.platform == 'win32':
    #     creationflags = 0
    # else:
    #     creationflags = 0

    # Start Mongo process
    mongoprocess = subprocess.Popen(
        args,
        cwd=mongodir,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
        # creationflags=creationflags
    )

    # # Update Output
    # mongoprocess.stdout = subprocess.PIPE
    # mongoprocess.stderr = subprocess.PIPE

    # Wait for response for 3 seconds, to validate success
    try:
        mongoprocess.communicate(timeout=3)
    except subprocess.TimeoutExpired:
        print('\nProcess successfully launched, PID #' + str(mongoprocess.pid))

        # Save pid to file
        if str(mongoprocess.pid) not in pidlist:
            pidlist.append(str(mongoprocess.pid))
            lxtools.saveFileToUserSettings(pidfile, pidlist)
    else:
        print('\nProcess exits, Mongo returns', mongoprocess.returncode)

    pass


def doStop(version, options):
    if not getIfMongoVersionAvailable(version):
        print('Version not available locally.')
        return

    pidfile = 'mongo-' + version + '.pids'
    pidlist = lxtools.loadFileFromUserSettings(pidfile, returntype=[])

    # Get a list with active pids from a list with pids
    alive = lxtools.getActiveProcessFromPidList(pidlist)

    # Send to all active processes exit signal
    if len(alive) != 0:
        if len(alive) > 1:
            if 'force' not in options:
                key = lxtools.readkey('Would you really kill these ' + str(len(alive)) + ' instances of Mongo?')

                if key == 'n':
                    return

        # Kill
        pidlist = alive

        for pid in alive:
            if lxtools.killProcess(int(pid)):
                print('Pid #' + pid + ' successfully killed')
            else:
                print('ERROR: Pid #' + pid + ' could not be killed')
    else:
        print('No active processes found...')

    # Save list
    lxtools.saveFileToUserSettings(pidfile, pidlist)
    print('Done...')