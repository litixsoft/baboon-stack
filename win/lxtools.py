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
import ctypes
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
            self.removeDirectory(directory, baseName)

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
    #return ctypes.windll.kernel32.CreateSymbolicLinkW(str(lpSymlinkName, 'utf-8'), str(lpTargetName, 'utf-8'), 1) != 0

# Removes a symbolic link
def rmLinkDirectory(directory):
    return

def main():
    pass

if __name__ == '__main__':
    main()
