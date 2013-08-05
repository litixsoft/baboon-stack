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

# Returns if x86 or x64
def getOsArchitecture():
    if platform.machine().endswith('64'):
        return 'x64'
    else:
        return 'x86'

# Returns if User an Admin
def getIfAdmin():
    return ctypes.windll.shell32.IsUserAnAdmin() != 0

# Removes a Directory from System with all files
def rmDirectory(directory, subdirectory = ''):
    fulldirectory = os.path.join(directory, subdirectory)
    nodes = os.listdir(fulldirectory)

    for item in nodes:
        itemName = os.path.join(fulldirectory, item)
        baseName = os.path.join(subdirectory, item)

        if os.path.isfile(itemName):
            try:
                os.remove(itemName)
            except IOError as e:
                print("Remove File error. I/O error({0}): {1}".format(e.errno, e.strerror))
        elif os.path.isdir(itemName):
            rmDirectory(directory, baseName)

    try:
        os.rmdir(fulldirectory)
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
        print(lpSymlinkName)
        return False

    CreateSymbolicLink = ctypes.windll.kernel32.CreateSymbolicLinkW
    CreateSymbolicLink.argtypes = (ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_uint32)
    CreateSymbolicLink.restype = ctypes.c_bool

    return CreateSymbolicLink(lpSymlinkName, lpTargetName, 1)

# Returns if lpFilename a Directory AND Reparse Point (Symbolic Link)
# FILE_ATTRIBUTE_DIRECTORY or FILE_ATTRIBUTE_REPARSE_POINT
def getIfSymbolicLink(lpFilename):
    return (ctypes.windll.kernel32.GetFileAttributesW(lpFilename) | 1040)  == 1040

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
    showProgress(0);
    try:
        local_filename, headers = urlrequest.urlretrieve(url, tempfile, reporthook=reporthook)
        showProgress(1);
    except KeyboardInterrupt:
        print('Abort!')
        return -1
    except e as Exception:
        print('Exception occured!')
        print(e)
        return -1

    return local_filename

# Clear temporary internet files
def cleanUpTemporaryFiles():
    urlrequest.urlcleanup

# Downloads a Remote File to a temporary File and returns the data
def getRemoteData(url):
    # Download from URL
    try:
        local_filename, headers = urlrequest.urlretrieve(url)
    except e as Exception:
        print('Exception occured!')
        print(e)
        return -1

    # Open and Read local temporary File
    html = open(local_filename)
    data = html.read()
    html.close()

    # Delete temporary Internet File
    urlrequest.urlcleanup()
    return data