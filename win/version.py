#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Thomas Scheibe
#
# Created:     05.08.2013
# Copyright:   (c) Thomas Scheibe 2013
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import platform
import sys

lxVersion = '1.1.0'
lxServer = 'http://packages.litixsoft.de'
#lxServer = 'http://localhost'
lxPacket = 'baboonstack-v{0}-windows-{1}.exe'

lxInfo = {
    'linux': {
            'osname': 'linux',
            'version': lxVersion,
            'package': 'baboonstack-.*-linux-{0}.tar.gz',
            'node': {
                'x32': 'node-v{0}-linux-x86.tar.gz',
                'x64': 'node-v{0}-linux-x64.tar.gz'
            }
        },
    'darwin': {
            'osname': 'darwin',
            'version': lxVersion,
            'package': 'baboonstack-.*-darwin-{0}.tar.gz',
            'node': {
                'x32': 'node-v{0}-darwin-x86.tar.gz',
                'x64': 'node-v{0}-darwin-x64.tar.gz'
            }
        },
    'win32': {
            'osname': 'windows',
            'version': lxVersion,
            'package': 'baboonstack-.*-windows-{0}.exe',
            'node': {
                'x32': 'node-v{0}-x86.msi',
                'x64': 'x64/node-v{0}-x64.msi'
            }
        }
}



def getConfig():
    if sys.platform in lxInfo:
        return lxInfo[sys.platform]
    else:
        return {}

lxConfig = getConfig()