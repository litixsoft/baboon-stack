#-------------------------------------------------------------------------------
# Name:        patch
# Purpose:     Simple ascii file patch utility
#
# Author:      Thomas Scheibe
#
# Created:     11.07.2014
# Copyright:   (c) Litixsoft GmbH 2014
# Licence:     Licensed under the MIT license.
#-------------------------------------------------------------------------------
import os
import lxtools


def doPatch(basedir, patches):
    if not patches:
        return None

    print('Patch files')
    for patchitem in patches:
        fullname = os.path.join(basedir, patchitem)
        resultstr = '...failed!'

        if os.path.exists(fullname):
            hashsum = patches[patchitem].get('sha1', None)

            if hashsum is not None:
                file_sha1 = lxtools.getSHAChecksum(fullname)

                if file_sha1 == hashsum:
                    # Load file
                    filehandle = open(fullname, 'r')
                    filelines = filehandle.readlines()
                    filehandle.close()

                    # Patch operations, simple
                    for patchop in patches[patchitem].get('action', []):
                        linenumber = patchop.get('line', None)
                        lineoperation = patchop.get('action', None)

                        if linenumber is None or lineoperation is None:
                            continue

                        if lineoperation == 'remove' and len(filelines) >= linenumber:
                            filelines[linenumber] = None

                    # Save file
                    filehandle = open(fullname, 'w')
                    for line in filelines:
                        if isinstance(line, str):
                            filehandle.write(line)
                    filehandle.close()

                    resultstr = '...success!'
                else:
                    resultstr = '...invalid file hash!'
        else:
            resultstr = '...missing!'

        print(' Patch', patchitem, resultstr)