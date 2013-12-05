#-------------------------------------------------------------------------------
# Name:        lxtools
# Purpose:
#
# Author:      Thomas Scheibe
#
# Created:     02.08.2013
# Copyright:   (c) Thomas Scheibe 2013
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import platform
import hashlib
import urllib.request as urlrequest
import ctypes
import sys
import os

import version

class Arguments:

    def __init__(self):
        self.args = sys.argv.copy()
        self.args.pop(0) # Remove the first Argument

    # Returns item count
    def count(self):
        return len(self.args)

    # Get the FIRST element and remove it from list
    def get(self, defaultvalue=''):
        if self.count() != 0:
            return self.args.pop(0)
        else:
            return defaultvalue

    # Returns TRUE or FALSE if NAME in list, if TRUE then removes element
    def find(self, name):
        if name in self.args:
            self.args.pop(self.args.index(name))
            return True
        else:
            return False

# Returns if x86 or x64
def getOsArchitecture():
    if platform.machine().endswith('64'):
        return 'x64'
    else:
        return 'x86'

# Returns if User an Admin
def getIfAdmin():
    if sys.platform == 'win32':
        return ctypes.windll.shell32.IsUserAnAdmin() != 0

    if sys.platform == 'linux' or sys.platform == 'darwin':
        return os.geteuid() == 0

    return False

# Removes a Directory from System with all files
def rmDirectory(directory):
    nodes = os.listdir(directory)

    for item in nodes:
        itemName = os.path.join(directory, item)

        if os.path.isfile(itemName):
            try:
                os.remove(itemName)
            except IOError as e:
                print("Remove File error. I/O error({0}): {1}".format(e.errno, e.strerror))
        elif os.path.isdir(itemName):
            rmDirectory(itemName)

    try:
        os.rmdir(directory)
    except IOError as e:
        print("Remove Directory error. I/O error({0}): {1}".format(e.errno, e.strerror))

# Returns the SHA1 Checksum of specified File
def getSHAChecksum(filename):
    sha = hashlib.sha1()
    tmpFile = open(filename, 'rb')
    while True:
        datFile = tmpFile.read(8192)

        # End of File
        if not datFile:
            break

        sha.update(datFile)

    # Returns Digest
    return sha.hexdigest()

# Creates a symbolic link of Directory
def setDirectoryLink(lpSymlinkName, lpTargetName):
    if os.path.exists(lpSymlinkName):
        return False

    # Windows
    if sys.platform == 'win32':
        CreateSymbolicLink = ctypes.windll.kernel32.CreateSymbolicLinkW
        CreateSymbolicLink.argtypes = (ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_uint32)
        CreateSymbolicLink.restype = ctypes.c_bool

        return CreateSymbolicLink(lpSymlinkName, lpTargetName, 1)

    if sys.platform == 'linux' or sys.platform == 'darwin':
        try:
            os.symlink(lpTargetName, lpSymlinkName)
            return True
        except BaseException as e:
            print('ERROR: ', e)
            return False

    raise Exception('ERROR: No API for setDirectoryLink.')

# Returns if lpFilename a Directory AND Reparse Point (Symbolic Link)
# FILE_ATTRIBUTE_DIRECTORY or FILE_ATTRIBUTE_REPARSE_POINT
def getIfSymbolicLink(lpFilename):
    if sys.platform == 'win32':
        return (ctypes.windll.kernel32.GetFileAttributesW(lpFilename) | 1040) == 1040

    if sys.platform == 'linux' or sys.platform == 'darwin':
        return os.path.isdir(lpFilename) & os.path.islink(lpFilename)

    raise Exception('ERROR: No API for getIfSymbolicLink.')

# Displays a Progress bar
def showProgress(amtDone):
    sys.stdout.write("\rProgress: [{0:50s}] {1:.1f}% ".format('#' * int(amtDone * 50), amtDone * 100))
    sys.stdout.flush()

# Callback for urlretrieve (Downloadprogress)
def reporthook(blocknum, blocksize, filesize):
    if (blocknum != 0):
        percent =  blocknum / (filesize / blocksize)
    else:
        percent = 0

    showProgress(percent)

# Download a Remote File to a temporary File and returns the filename
# Displays a Progress Bar during Download
def getRemoteFile(url, tempfile=''):
    showProgress(0)
    try:
        local_filename, headers = urlrequest.urlretrieve(url, tempfile, reporthook=reporthook)
        showProgress(1)
        print('Done!')
    except KeyboardInterrupt:
        print('Abort!')
        return -1
    except IOError as e:
        print('Error!')
        print('IO Error! Abort!\n')
        print(e)
        return -1
    except:
        print('Error!')
        print('Unknow Error occured! Abort!')
        return -1

    return local_filename

# Clear temporary internet files
def cleanUpTemporaryFiles():
    urlrequest.urlcleanup()

# Downloads a Remote File to a temporary File and returns the data
def getRemoteData(url):
    # Download from URL
    try:
        local_filename, headers = urlrequest.urlretrieve(url)
    except IOError as e:
        print('IO Error! Abort!\n')
        print(e)
        return -1
    except:
        print('Unknow Error occured! Abort!')
        return -1

    # Open and Read local temporary File
    html = open(local_filename)
    data = html.read()
    html.close()

    # Delete temporary Internet File
    urlrequest.urlcleanup()
    return data

# Returns the HOMEPATH of Baboonstack
def getBaboonStackDirectory():
    if sys.platform == 'win32':
        if 'LXPATH' in os.environ:
            return os.environ['LXPATH']

    if sys.platform == 'linux' or sys.platform == 'darwin':
        if os.path.exists(version.lxConfig['basedir']):
            return version.lxConfig['basedir']

    return os.path.dirname(os.getcwd())

# Returns if NODE.JS Module (NVM/SERVICE) enabled
# Checks only if %LXPATH%\node exits
def getIfNodeModuleEnabled():
    nodePath = os.path.join(getBaboonStackDirectory(), 'node')
    return os.path.exists(nodePath)

def getIfMongoModuleEnabled():
    mongoPath = os.path.join(getBaboonStackDirectory(), 'mongo')
    return os.path.exists(mongoPath)

def getIfRedisModuleEnabled():
    redisPath = os.path.join(getBaboonStackDirectory(), 'redisio')
    return os.path.exists(redisPath)

def readkey(prompt, keys='Yn'):
    keymap = []
    defaultkey = None

    # Build keymap
    for key in keys:
        if key.isupper() and not defaultkey:
            defaultkey = key.lower()

        keymap.append(key)

    # Output message
    msg = str('{0} ({1})').format(prompt, '/'.join(keymap))
    keys = keys.lower()

    while True:
        inp = input(msg).lower()

        # if RETURN pressed, then use default
        if len(inp) == 0:
            if defaultkey:
                return defaultkey
        else:
            if inp[0] in keys:
                return inp[0]
