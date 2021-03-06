#-------------------------------------------------------------------------------
# Name:        buildChecksum
# Purpose:     Builds Checksum of files in specified folder
#
# Author:      Thomas Scheibe
#
# Created:     08.08.2013
# Copyright:   (c) Litixsoft GmbH 2014
# Licence:     Licensed under the MIT license.
#-------------------------------------------------------------------------------
import lxtools
import sys
import os

# Show
def header():
    print('buildChecksum - SHA1 Checksum Generator\n')

def help():
    print('Usage:\n')
    print('  buildchecksum [folder]\n')

def main(folder):
    fileList = os.listdir(folder)
    shasumFilename = os.path.join(folder, 'SHASUMS.txt')
    hashList = []

    for entry in fileList:
        fullFilename = os.path.join(folder, entry)

        if entry.lower() != 'shasums.txt' and os.path.isfile(fullFilename):
            print('Hash {0}'.format(entry))

            result = []
            result.append(lxtools.getSHAChecksum(fullFilename))
            result.append(entry)
            hashList.append(result)

    # Build SHASUMS.TXT
    print('Write SHASUMS File...')
    shasumFile = open(shasumFilename, 'w')
    for entry in hashList:
        shasumFile.write('  '.join(entry) + '\n')
    shasumFile.close()
    print('Done...')
    pass

if __name__ == '__main__':
    header()

    if len(sys.argv) < 2 or not os.path.isdir(sys.argv[1]):
        help()
    else:
        main(sys.argv[1])