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
from distutils.version import StrictVersion
import re as regex
import subprocess
import tempfile
import sys
import os

# Platform specified modules
import tarfile
import zipfile

# Baboonstack modules
import config
import lxtools
import package

# Global
mongobasedir = os.path.join(lxtools.getBaboonStackDirectory(), 'mongodb')


# Returns if mongoversion the correct format
def getIfMongoVersionFormat(mongoversion):
    return regex.match('[0-9]+\.[0-9]+\.[0-9]+', mongoversion) != None


def getIfMongoVersionInstalled(mongoversion):
    if os.path.exists(os.path.join(mongobasedir, mongoversion)):
        pkginfo = lxtools.loadjson(os.path.join(mongobasedir, mongoversion, config.getConfigKey('configfile')), reporterror=False)

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


def doUpgrade():
    oldmongopath = os.path.join(lxtools.getBaboonStackDirectory(), 'mongo')

    if os.path.isdir(oldmongopath) and not lxtools.getIfSymbolicLink(oldmongopath):
        # Upgrade
        print('Upgrade needed...')

        # Check if admin
        if not lxtools.getIfAdmin():
            print(config.getMessage('REQUIREADMIN'))
            return

        # Load package file
        pkginfo = lxtools.loadjson(os.path.join(oldmongopath, config.getConfigKey('configfile')))
        mongoversion = pkginfo.get('version', None)

        # Stop Service/Daemon and de-register Service/Daemon, safe-remove
        print('Stop Service/Daemon...')
        package.runScript(pkginfo, ['remove', 'safe', 'hidden'])

        # Move Directory to mongodb/{version}/
        print('Move files...')
        mongodir = os.path.join(mongobasedir, mongoversion)

        # Create new mongodb directory and move installed version
        os.makedirs(mongobasedir)
        os.rename(oldmongopath, mongodir)

        # Create Symlink
        print('Create symlinks...')
        lxtools.setDirectoryLink(oldmongopath, mongodir)

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
    if getIfMongoVersionInstalled(version):
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



def doRemove():
    pass


def doChange(version):
    pass


def doRun(version, port=27017):
    pass
