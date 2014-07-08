#-------------------------------------------------------------------------------
# Name:        mvm
# Purpose:
#
# Author:      Thomas Scheibe
#
# Created:     30.06.2014
# Copyright:   (c) Litixsoft GmbH 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#from distutils.version import StrictVersion
import re as regex
import subprocess
import tempfile
import signal
import sys
import os

# Baboonstack modules
import config
import lxtools
import package

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
    if not lxtools.getIfSymbolicLink(mongosymlink):
        return False

    try:
        # Read symbolic Link
        path = os.readlink(mongosymlink)

        # Remove bin/node. Only for non win32 platforms
        if sys.platform != 'win32':
            path = path.rsplit(os.sep, 2)[0]

        # Splits the Seperator and Returns the last Pathname (nodeversion)
        return path.rsplit(os.sep).pop()
    except Exception as e:
        print('ERROR: ', e)
        return ''


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


def doUpgrade():
    if os.path.isdir(mongosymlink) and not lxtools.getIfSymbolicLink(mongosymlink):
        # Upgrade
        print('Upgrade needed...')

        # Check if admin
        if not lxtools.getIfAdmin():
            print(config.getMessage('REQUIREADMIN'))
            return

        # Load package file
        pkginfo = lxtools.loadjson(os.path.join(mongosymlink, config.getConfigKey('configfile')))
        mongoversion = pkginfo.get('version', None)

        # Stop Service/Daemon and de-register Service/Daemon, safe-remove
        print('Stop Service/Daemon...')
        package.runScript(pkginfo, ['remove', 'safe', 'hidden'])

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
    os.makedirs(fullmongodir)

    # Move helper files
    lxtools.moveDirectory(hlppath, fullmongodir)

    # Move *all* directories to target directory
    dir_moved = False
    for name in os.listdir(pkgpath):
        if os.path.isdir(os.path.join(pkgpath, name)):
            lxtools.moveDirectory(os.path.join(pkgpath, name), fullmongodir)
            dir_moved = True

    if not dir_moved:
        print('Sorry, no files from binary archive was moved!')
        return

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


def doRemove(version):
    # activeVersion = getLocalMongoVersion()
    #
    # # Admin required
    # if not lxtools.getIfAdmin():
    #     print(config.getMessage('REQUIREADMIN'))
    #     return
    #
    # # Version already active
    # if activeVersion == version:
    #     print('Version already active.')
    #     return
    #
    # # If version locally available
    # if not getIfMongoVersionInstalled(version):
    #     print('Version NOT installed locally.')
    #     return

    pass


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
        print('Version already active.')
        return

    # If version locally available
    if not getIfMongoVersionAvailable(version):
        print('Version not available locally.')
        return

    # Mongo dir
    mongodir = os.path.join(mongobasedir, version)

    # if version already set, then deactivate
    if activeVersion != '':
        print('Deactivate Mongo v' + activeVersion)
        pkginfo = lxtools.loadjson(os.path.join(mongosymlink, config.getConfigKey('configfile')))
        package.runScript(pkginfo, ['remove', 'safe', 'hidden'])

        if not resetMongo():
            return

    # Create Symlink
    print('Activate Mongo v' + version)
    lxtools.setDirectoryLink(mongosymlink, mongodir)

    # Start Daemon/Service
    pkginfo = lxtools.loadjson(os.path.join(mongosymlink, config.getConfigKey('configfile')))
    package.runScript(pkginfo, ['install', 'hidden'])

    print('Done, nice!')
    pass


def doStart(version, port, options):
    if not getIfMongoVersionAvailable(version):
        print('Version not available locally.')
        return

    pidfile = 'mongo-' + version + '.pids'
    pidlist = lxtools.loadFileFromUserSettings(pidfile, returntype=[])

    mongodir = os.path.join(mongobasedir, version)
    mongodaemon = os.path.join(mongodir, config.getConfigKey('mongo.binary.mongod'))

    if not os.path.isfile(mongodaemon):
        print('Mongo daemon binary not found.')
        return

    args = [
        mongodaemon,
        '--port',
        port,
        '--dbpath',
        os.path.join(mongodir, 'db')
    ]

    print('Start Mongo v' + version + '...\n')
    print('*** Please wait for 5 second(s) to validate success ***\n')

    # Start Mongo process
    mongoprocess = subprocess.Popen(
        args,
        cwd=mongodir,
        # stdout=subprocess.DEVNULL,
        # stderr=subprocess.DEVNULL,
        # creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
    )

    # Wait for response for 3 seconds, to validate success
    try:
        mongoprocess.communicate(timeout=3)
    except subprocess.TimeoutExpired:
        print('\nProcess successfully launched, PID #' + str(mongoprocess.pid))

        # Update Output
        mongoprocess.stdout=subprocess
        mongoprocess.stderr=subprocess

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

    # mongodir = os.path.join(mongobasedir, version)
    # mongodaemon = os.path.join(mongodir, config.getConfigKey('mongo.binary.mongod'))

    alive = []
    for pid in pidlist:
        if lxtools.checkIfPidExists(int(pid)):
            alive.append(pid)

    if len(alive) != 0:
        if len(alive) > 1:
            if 'force' not in options:
                key = lxtools.readkey('Would you really kill these ' + str(len(alive)) + ' instances of Mongo?')

                if key == 'n':
                    return

        # Kill
        pidlist = alive

        for pid in alive:
            print('Sending CTRL+C Event to #' + pid)
            try:
                os.kill(int(pid), signal.CTRL_C_EVENT)
                pidlist.remove(pid)
            except OSError as e:
                print('\n***', e, '***\n')

    # Save list
    lxtools.saveFileToUserSettings(pidfile, pidlist)
    print('Done...')